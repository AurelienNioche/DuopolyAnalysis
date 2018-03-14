import argparse
import os

from tqdm import tqdm
import itertools

from backup import backup
import model


class BackupSimulation:

    def __init__(self, positions, prices, profits, n_consumers,
                 active_player_t0, p_strategy, t_max, r):

        self.positions = positions
        self.prices = prices
        self.profits = profits
        self.n_consumers = n_consumers
        self.active_player_t0 = active_player_t0
        self.r = r
        self.p_strategy = p_strategy
        self.t_max = t_max


def treat_args(*args):

    s = "profit", "competition", "random"

    for a in args:
        if a in ("all", ):
            return itertools.combinations_with_replacement(s, r=2)
        elif a in s:
            pass
        else:
            exit("Please use a valid strategy (not '{}'): random, profit, competition.".format(a))


def backup_simulation(file_name, args):

    if not os.path.exists(file_name) or args.force:
        main(p0_strategy=args.p0_strategy, p1_strategy=args.p1_strategy)

    return backup.load(file_name=file_name)


def main(p0_strategy, p1_strategy):

    n_simulation = 30

    data = []

    tqdm.write("\n********* {} VS {} *************".format(p0_strategy, p1_strategy))

    for r in (0.25, 0.5):

        tqdm.write("Computing {} radius simulations.".format(r))

        for _ in tqdm(range(n_simulation)):

            m = model.simulation.Model(r=r, p0_strategy=p0_strategy, p1_strategy=p1_strategy)
            results = m.run()
            b = BackupSimulation(*results, r)
            data.append(b)

    tqdm.write("*********************************")

    file_name = "data/simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    backup.save(
        obj=data,
        file_name=file_name
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run simulations.')

    parser.add_argument(
        '-p0', action='store',
        dest='p0_strategy',
        help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument(
        '-p1', action='store',
        dest='p1_strategy',
        help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    if None in (parsed_args.p0_strategy, parsed_args.p1_strategy):
        exit("You don't know what you're doing. Run the script with -h flag.")

    treat_args(parsed_args.p0_strategy, parsed_args.p1_strategy)

    main(
        p0_strategy=parsed_args.p0_strategy,
        p1_strategy=parsed_args.p1_strategy
    )

