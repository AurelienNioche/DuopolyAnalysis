import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import numpy as np
from tqdm import tqdm
import argparse

from game.models import Room, FirmProfit, RoundComposition, Round

from backup import backup
from analysis.pool import prices_and_profits, distance
from analysis.separate import separate


def exclude():

    rms = Room.objects.filter(state="end")

    filtered_rd = []

    means = {}

    means[0.25], means[0.5] = _get_random_bot_mean_profits()

    tqdm.write("Filtering round containing bad players...")

    for rm in tqdm(rms):

        t_max = rm.ending_t
        r = rm.radius

        rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

        for rd in rds:

            profits = np.zeros((t_max, 2), dtype=int)

            profits_entries = FirmProfit.objects.filter(round_id=rd.id)

            for t in range(1, t_max + 1):
                profits[t - 1] = \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t).order_by("agent_id")]) - \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t - 1).order_by("agent_id")])

            round_composition = RoundComposition.objects.filter(round_id=rd.id).order_by("firm_id")
            user_id = ["bot" if rc.bot else rc.user_id for rc in round_composition]

            # Exclude room with bad players
            player_id = [rc.firm_id for rc in round_composition if not rc.bot][0]
            cond0 = "bot" in user_id
            cond1 = np.mean(profits[:, player_id]) < means[r]

            if cond0 and cond1:
                if rd.id not in filtered_rd:
                    filtered_rd.append(rd.id)

    return filtered_rd


def _get_random_bot_mean_profits():

    backups = backup.load(
        file_name="data/simulation_random_strategy_vs_profit_strategy.p")

    means = []

    for r in (0.25, 0.5):
        profits = []
        for b in backups:
            if b.r == r:
                profits.append(np.mean(b.profits[:, 0]))
        means.append(np.mean(profits))

    return means


def main(force):

    excluded_rd = exclude()

    backups = backup.get_data(force)

    filtered_backups = []

    for b in backups:
        if b.round_id in excluded_rd:
            filtered_backups.append(b)

    # plots(filtered_backups)
    # prices_and_profits.prices_and_profits(backups=filtered_backups, fig_name="fig/excluded/prices_and_profits.pdf")
    print("N excluded players in 0.25 radius condition: ", len([b for b in filtered_backups if b.r == 0.25]))
    print("N excluded players in 0.5 radius condition: ", len([b for b in filtered_backups if b.r == 0.5]))


def plots(backups):

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
            str_r = "{}".format(int(r * 100))

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
