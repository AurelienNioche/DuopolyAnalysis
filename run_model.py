import argparse
import model
from backup import backup


class BackupSimulation:

    def __init__(self, positions, prices, n_consumers, profits):

        self.positions = positions
        self.prices = prices
        self.profits = profits
        self.n_consumers = n_consumers

    def save(self, file_name="data/simulation.p"):

        backup.save(obj=self, file_name=file_name)


def main(*args):

    p0_strategy, p1_strategy =

    for r in (0.25, 0.5):

        m = model.simulation.Model(r=r)

        data = m.run()

        to_save = BackupSimulation(*data)

        to_save.save(file_name="data/simulation_r={}_{}_vs_{}.p".format(r, ))

def treat_args(*args):

    to_return = []

    for a in args:
        if "profit" in a:
            to_return.append("profit_strategy")
        elif "competition" in a:
            to_return.append("competition_strategy")






if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run simulations.')

    parser.add_argument('-p0', action='store',
                    dest='p0_strategy',
                    help='Strategy used by player 0')

    parser.add_argument('-p1', action='store',
                    dest='p1_strategy',
                    help='Strategy used by player 1')

    parsed_args = parser.parse_args()

    main()

