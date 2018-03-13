import argparse

from backup import backup


def main(force):

    backups = backup.get_data(force)

    n = {
        0.25: {True: 0, False: 0},
        0.50: {True: 0, False: 0}
    }
    for b in backups:
        if b.pvp:
            n[b.r][b.display_opponent_score] += 1

    print(
        "Rooms 0.25 with opp score:    {}\n"
        "Rooms 0.25 without opp score: {}\n"
        "Rooms 0.50 with opp score:    {}\n"
        "Rooms 0.50 without opp score: {}\n"
        "N subjects:                   {}\n".format(
            n[0.25][True],
            n[0.25][False],
            n[0.50][True],
            n[0.50][False],
            (n[0.25][True] + n[0.25][False] + n[0.50][True] + n[0.50][False]) * 2,

        )
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
