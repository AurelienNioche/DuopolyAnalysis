import numpy as np
from tqdm import tqdm

from game.models import Room, FirmProfit, RoundComposition, Round

from backup import backup


def exclude():

    rms = Room.objects.filter(state="end")
    filtered_rms = []

    tqdm.write("Filtering rooms containing bad players...")

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
            cond1 = np.mean(profits[:, player_id]) > _get_mean_profits(r=r)

            if cond0 and cond1:
                if rm not in filtered_rms:
                    filtered_rms.append(rm)

    return filtered_rms


def _get_mean_profits(r):

    obj = backup.load(
        file_name="data/simulation_r_{}_random_strategy_vs_profit_strategy.p".format(r))

    profits = []

    for i in obj:
        profits.append(np.mean(i.profits[:, 0]))

    return np.mean(profits)