# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from game.models import Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState

from run_simulation import BackupSimulation

import numpy as np
import argparse
from tqdm import tqdm

from backup import backup
from analysis.separate import separate
from analysis.pool import distance, prices_and_profits


def load_data_from_db(exclude):

    backups = []

    rms = Room.objects.filter(state="end")

    for rm in tqdm(rms):

        t_max = rm.ending_t
        r = rm.radius
        display_opponent_score = rm.display_opponent_score

        rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

        for rd in rds:

            positions = np.zeros((t_max, 2), dtype=int)
            prices = np.zeros((t_max, 2), dtype=int)
            profits = np.zeros((t_max, 2), dtype=int)

            position_entries = FirmPosition.objects.filter(round_id=rd.id)
            price_entries = FirmPrice.objects.filter(round_id=rd.id)
            profits_entries = FirmProfit.objects.filter(round_id=rd.id)

            for t in range(t_max):
                positions[t, :] = \
                    [i[0] for i in position_entries.values_list("value").filter(t=t).order_by("agent_id")]
                prices[t, :] = \
                    [i[0] for i in price_entries.values_list("value").filter(t=t).order_by("agent_id")]

            for t in range(1, t_max + 1):
                profits[t - 1] = \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t).order_by("agent_id")]) - \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t - 1).order_by("agent_id")])

            round_composition = RoundComposition.objects.filter(round_id=rd.id).order_by("firm_id")
            user_id = ["bot" if rc.bot else rc.user_id for rc in round_composition]

            # Exclude room with bad players
            player_id = [rc.firm_id for rc in round_composition if not rc.bot][0]
            cond0 = exclude and "bot" in user_id
            cond1 = np.mean(profits[:, player_id]) < _get_mean_profits(r=r)

            active_player_t0 = RoundState.objects.filter(round_id=rd.id, t=0).first().firm_active

            if active_player_t0 == 1:
                cond = positions[0, 0] == 0 and prices[0, 0] == 5
            else:
                cond = positions[0, 1] == 20 and prices[0, 1] == 5

            if cond:

                b = backup.Backup(
                    t_max=t_max, r=r, display_opponent_score=display_opponent_score,
                    positions=positions, prices=prices, profits=profits,
                    room_id=rm.id, round_id=rd.id, pvp=rd.pvp, user_id=user_id,
                    active_player_t0=active_player_t0, exclude=cond0 * cond1)

                backups.append(b)

    backup.save(backups)

    return backups


def main(force, exclude):

    if not os.path.exists("data/data.p") or force:
        backups = load_data_from_db(exclude=exclude)

    else:
        backups = backup.load()

    # For naming
    str_os_cond = {
        True: "opp_score",
        False: "no_opp_score"
    }

    str_pvp_cond = {
        True: "PVP",
        False: "PVE"
    }

    # Compare with r respectively to pvp condition
    tqdm.write("Effect of r given opp score/no opp score and pvp/pve...\n")

    for os_condition in (True, False):

        for pvp_condition in (True, False):

            str_pvp = str_pvp_cond[pvp_condition]
            str_os = str_os_cond[os_condition]

            fig_name_args = "effect_r", str_os, str_pvp, str_pvp, str_os

            tqdm.write("Effect r: {} {}".format(str_os, str_pvp))

            bkp = [b for b in backups if
                   b.pvp is pvp_condition and
                   b.display_opponent_score is os_condition]

            distance.distance(
                backups=bkp,
                fig_name="fig/{}/{}/{}/pool_distance_{}_{}.pdf".format(*fig_name_args))

            prices_and_profits.prices_and_profits(
                backups=bkp,
                fig_name="fig/{}/{}/{}/prices_and_profits_{}_{}.pdf".format(*fig_name_args))

            tqdm.write("\n")

    # Compare with 'display_opponent_score' respectively to pvp condition
    tqdm.write("Effect of displaying opponent score given r and pvp condition...\n")

    for r in (0.25, 0.50):
        for pvp_condition in (True, False):

            str_pvp = str_pvp_cond[pvp_condition]
            str_r = "{}".format(int(r*100))

            fig_name_args = "effect_score_opp", str_r, str_pvp, str_pvp, str_r

            tqdm.write("Effect opp score: {} {}".format(str_r, str_pvp))

            bkp = [b for b in backups
                   if b.pvp is pvp_condition and b.r == r]

            distance.distance(
                backups=bkp,
                fig_name="fig/{}/{}/{}/pool_distance_{}_{}.pdf".format(*fig_name_args),
                attr="display_opponent_score"
            )

            prices_and_profits.prices_and_profits(
                backups=bkp,
                fig_name="fig/{}/{}/{}/prices_and_profits_{}_{}.pdf".format(*fig_name_args),
                attr="display_opponent_score"
            )

            tqdm.write("\n")

    # Separate: Plot figure for every round
    tqdm.write("Create a figure for every round...\n")
    for b in tqdm(backups):

        str_pvp = str_pvp_cond[b.pvp]
        str_os = str_os_cond[b.display_opponent_score]

        fig_name_args = "separate", str_os, str_pvp, b.room_id, b.round_id, str_os, str_pvp

        fig_name = "fig/{}/{}/{}/room{}_round{}_{}_{}_separate.pdf".format(*fig_name_args)
        separate.separate(backup=b, fig_name=fig_name)


def _get_mean_profits(r):

    obj = backup.load(
        file_name="data/simulation_r_{}_random_strategy_vs_profit_strategy.p".format(r))

    profits = []

    for i in obj:
        profits.append(np.mean(i.profits[:, 0]))

    return np.mean(profits)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parser.add_argument('-e', '--exclude', action="store_true", default=False,
                        help="Exclude bad players.")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force, exclude=parsed_args.exclude)

