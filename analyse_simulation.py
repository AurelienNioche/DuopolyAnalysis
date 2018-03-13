import argparse
from backup import backup
import contextlib

import run_simulation
from analysis.pool import prices_and_profits


@contextlib.contextmanager
def backup_safe_load(file_name, args):
    try:
        b = None

        if args.force:
            run_simulation.main(
                p0_strategy=args.p0_strategy,
                p1_strategy=args.p1_strategy
            )

        b = backup.load(file_name=file_name)

    except (RuntimeError, FileNotFoundError):

        if not args.force:
            exit("File not found, use -f flag to generate new data.")
        else:
            exit("Something went wrong, new data were generated, but file loading failed.")

    finally:

        if b:
            yield b


def main(args):

    p0_strategy, p1_strategy = \
        run_simulation.treat_args(args.p0_strategy, args.p1_strategy)

    file_name = "data/simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    with backup_safe_load(file_name=file_name, args=args) as b:

        fig_name = "fig/simulation/prices_and_profits_{}_vs_{}.pdf"
        prices_and_profits.prices_and_profits(backups=b, fig_name=fig_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")

    parser.add_argument('-p0', action='store',
                    dest='p0_strategy',
                    help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument('-p1', action='store',
                    dest='p1_strategy',
                    help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    if parsed_args.force and \
            None in (parsed_args.p0_strategy, parsed_args.p1_strategy):
        exit("Please run the script with -h flag.")

    main(parsed_args)

