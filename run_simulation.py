import argparse
import model
from backup import backup
from tqdm import tqdm
import numpy as np


class BackupSimulation:

    def __init__(self, positions, prices, profits, n_consumers):

        self.positions = positions
        self.prices = prices
        self.profits = profits
        self.n_consumers = n_consumers


def main(*args):

    p0_strategy, p1_strategy = _treat_args(*args)

    n_simulation = 100

    for r in (0.25, 0.5):

        tqdm.write("Computing {} radius simulations.".format(r))

        data = []

        for _ in tqdm(range(n_simulation)):

            m = model.simulation.Model(r=r, p0_strategy=p0_strategy, p1_strategy=p1_strategy)

            results = m.run()

            game = BackupSimulation(*results)

            data.append(game)

        backup.save(
            obj=data,
            file_name="data/simulation_r_{}_{}_vs_{}.p".format(r, p0_strategy, p1_strategy)
        )


def _treat_args(*args):

    to_return = []

    for a in args:
        if a in ("profit", ):
            to_return.append("profit_strategy")
        elif a in ("competition", ):
            to_return.append("competition_strategy")
        elif a in ("random", ):
            to_return.append("random_strategy")
        else:
            exit("Please use a valid strategy: random, profit, competition.")

    return to_return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run simulations.')

    parser.add_argument('-p0', action='store',
                    dest='p0_strategy',
                    help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument('-p1', action='store',
                    dest='p1_strategy',
                    help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    if None in (parsed_args.p0_strategy, parsed_args.p1_strategy):
        exit("You don't know what you're doing. Run the script with -h flag.")

    main(parsed_args.p0_strategy, parsed_args.p1_strategy)

