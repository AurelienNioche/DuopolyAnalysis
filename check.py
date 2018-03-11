from pylab import np, plt
import os
import argparse

from analyse import load_data_from_db
from backup import backup


def main(force):

    if not os.path.exists("data/data.p") or force:
        backups = load_data_from_db()

    else:
        backups = backup.load()

    n = {
        0.25: {True: 0, False: 0},
        0.50: {True: 0, False: 0}
    }
    for b in backups:

        if b.active_player_t0 == 1:
            cond = b.positions[0, 0] == 0 and b.prices[0, 0] == 5
        else:
            cond = b.positions[0, 1] == 20 and b.prices[0, 1] == 5

        if not cond:
            print(b.positions[0, :], b.prices[0, :], b.r, b.display_opponent_score)

        if cond and b.pvp:
            n[b.r][b.display_opponent_score] += 1

    print(n)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
