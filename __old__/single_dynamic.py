import argparse
from tqdm import tqdm

from behavior import backup
from analysis.dynamics import separate


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

    # Separate: Plot figure for every round
    tqdm.write("Create a figure for every round...\n")
    for b in tqdm(backups):

        str_pvp = str_pvp_cond[b.pvp]
        str_os = str_os_cond[b.display_opponent_score]

        fig_name_args = "separate", str_os, str_pvp, b.room_id, b.round_id, str_os, str_pvp

        fig_name = "fig/{}/{}/{}/room{}_round{}_{}_{}_separate.pdf".format(*fig_name_args)
        separate.plot(backup=b, fig_name=fig_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
