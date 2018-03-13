import os
import numpy as np
import argparse
from tqdm import tqdm

from backup import backup
from analysis.separate import separate
from analysis.pool import distance, prices_and_profits


def main(force):

    backups = backup.get_data(force)

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)

