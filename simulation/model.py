# SpatialCompetition
# Copyright (C) 2018  Aurélien Nioche, Basile Garcia & Nicolas Rougier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import numpy as np
import itertools
import enum

import simulation.backup as backup


def get_heuristics():
    return [str(i).replace("Move.", "") for i in
            (Move.max_profit, Move.max_diff, Move.tacit_collusion)]


class Move(enum.Enum):

    max_profit = enum.auto()
    max_diff = enum.auto()
    tacit_collusion = enum.auto()
    # strategic = enum.auto()


class Model:

    def __init__(self, param):

        self.parameters = param

        np.random.seed(param.seed)

        self.n_positions = param.n_positions
        self.n_prices = param.n_prices
        self.t_max = param.t_max
        self.r = param.r
        self.p_min = param.p_min
        self.p_max = param.p_max

        self.strategies = np.array(
            list(itertools.product(range(self.n_positions), range(self.n_prices))),
            dtype=int
        )

        self.prices = np.linspace(self.p_min, self.p_max, self.n_prices)

        # Useful n
        self.n_strategies = len(self.strategies)
        self.idx_strategies = np.arange(self.n_strategies)

        # Prepare useful arrays
        self.n_consumers = self.compute_n_consumers()

        self.move = {

            Move.max_profit: self.move_profit_based,
            Move.max_diff: self.move_diff_based,
            Move.tacit_collusion: self.move_tacit_collusion,
            # Move.strategic: self.move_profit_strategic_based

        }[self.parameters.move]

    def compute_n_consumers(self):
        
        """
        Compute the number of captive and shared targetable consumers for each combination of positions.
        :return: For each combination of combination, number of captive consumers of firm 0, 
        number of captive consumers of firm 1,
        shared targetable consumers for both firms (choice will depend on price politics)
        (np.array of dimension n_position, n_position, 3).  
        """

        z = np.zeros((self.n_positions, self.n_positions, 3), dtype=int)
        # Last parameter is idx0: n consumers seeing only A,
        #                   idx1: n consumers seeing only B,
        #                   idx2: consumers seeing A and B,

        field_of_view = np.zeros((self.n_positions, 2))  # 2: min, max
        field_of_view[:] = [self.field_of_view(x) for x in range(self.n_positions)]

        for i, j in itertools.combinations_with_replacement(range(self.n_positions), r=2):

            for x in range(self.n_positions):

                see_firm_0 = field_of_view[x, 0] <= i <= field_of_view[x, 1]
                see_firm_1 = field_of_view[x, 0] <= j <= field_of_view[x, 1]

                if see_firm_0 and see_firm_1:
                    z[i, j, 2] += 1

                elif see_firm_0:
                    z[i, j, 0] += 1

                elif see_firm_1:
                    z[i, j, 1] += 1

            z[j, i, 0] = z[i, j, 1]
            z[j, i, 1] = z[i, j, 0]
            z[j, i, 2] = z[i, j, 2]

        return z

    def field_of_view(self, x):
        
        """
        Compute the field of view for a consumer
        :param x: Position of the consumer (int)
        :return: Min and max of the field of view (list)
        """

        r = int(self.r * self.n_positions)

        field_of_view = [
            max(x - r, 0),
            min(x + r, self.n_positions - 1)
        ]

        return field_of_view

    def profits_given_position_and_price(self, move0, move1, n_consumers=None):
        
        """
        Given moves of the two firms, compute expected profits.
        :param move0: Move of firm 0 (int)
        :param move1: Move of firm 1 (int)
        :param n_consumers: (Optional) Number of expected consumers for both firms (np.array of length 2)
        :return: Expected profits (np.array of length 2)
        """

        if n_consumers is None:
            n_consumers = self.get_n_consumers_given_moves(move0=move0, move1=move1)

        return n_consumers * self.prices[
            self.strategies[(move0, move1), 1]  # In strategies, idx of prices are stored, not prices themselves
        ]

    def get_n_consumers_given_moves(self, move0, move1):

        """
        Given moves of the two firms, compute the number of consumers for the two firms.
        NB: Could be half of consumer as it has to be interpreted more as the expected number as the actual number.
        :param move0: Move of firm 0 (int)
        :param move1: Move of firm 1 (int)
        :return: Number of expected consumers for both firms (np.array of length 2)
        """

        pos0, price0 = self.strategies[move0, :]
        pos1, price1 = self.strategies[move1, :]

        n_consumers = np.zeros(2)
        n_consumers[:] = self.n_consumers[pos0, pos1, :2]

        to_share = self.n_consumers[pos0, pos1, 2]

        if to_share > 0:

            if price0 == price1:
                n_consumers[:] += to_share / 2

            else:
                n_consumers[int(price1 < price0)] += to_share

        return n_consumers

    def move_profit_based(self, opp_move):

        """
        Select the move that give the maximum profit at t
        :param opp_move: Move of the opponent (int)
        :return: Selected move (int)
        """

        exp_profits = np.zeros(self.n_strategies)

        for i in range(self.n_strategies):
            exp_profits[i] = self.profits_given_position_and_price(i, opp_move)[0]

        max_profits = max(exp_profits)

        idx = np.flatnonzero(exp_profits == max_profits)

        i = np.random.choice(idx)

        return i

    def move_diff_based(self, opp_move):

        exp_profits = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits[i, :] = self.profits_given_position_and_price(i, opp_move)

        profits_differences = exp_profits[:, 0] - exp_profits[:, 1]
        max_profits_difference = max(profits_differences)

        # noinspection PyTypeChecker
        idx = np.flatnonzero(profits_differences == max_profits_difference)

        return np.random.choice(idx)

    # def move_profit_strategic_based(self, opp_move):
    #
    #     values = np.zeros(self.n_strategies)
    #
    #     profits_t_plus = np.zeros((self.n_strategies, 2))
    #
    #     for i in range(self.n_strategies):
    #         profits_t = self.profits_given_position_and_price(i, opp_move)[0]
    #         for j in range(self.n_strategies):
    #             profits_t_plus[j] = self.profits_given_position_and_price(i, j)
    #
    #         max_profits_opp = max(profits_t_plus[:, 1])
    #         mean_profits_t_plus = np.mean(profits_t_plus[profits_t_plus[:, 1] == max_profits_opp, 0])
    #         values[i] = profits_t + mean_profits_t_plus
    #
    #     max_value = max(values)
    #
    #     idx = np.flatnonzero(values == max_value)
    #
    #     return np.random.choice(idx)

    def move_tacit_collusion(self, opp_move):

        exp_profits = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits[i] = self.profits_given_position_and_price(i, opp_move)

        max_profits = np.max(exp_profits, axis=0)
        sum_diff = np.sum(exp_profits - max_profits, axis=1)

        max_value = max(sum_diff)

        idx = np.flatnonzero(sum_diff == max_value)

        return np.random.choice(idx)

    def run(self):
        
        """
        Run simulation of an economy.
        :return: A backup (arbitrary Python object)
        """
        
        # For recording
        positions = np.zeros((self.t_max, 2), dtype=int)
        prices = np.zeros((self.t_max, 2))
        n_consumers = np.zeros((self.t_max, 2))
        profits = np.zeros((self.t_max, 2))

        moves = np.zeros(2, dtype=int)

        active = 0
        moves[:] = -99, np.random.randint(low=0, high=self.n_prices * self.n_positions)

        for t in range(self.t_max):

            passive = (active + 1) % 2  # Get passive id

            moves[active] = self.move(moves[passive])  # Make play active firm

            move0, move1 = moves  # Useful for call of functions

            # Record for further analysis
            positions[t, :] = self.strategies[moves, 0]
            prices[t, :] = self.prices[self.strategies[moves, 1]]
            n_consumers[t, :] = self.get_n_consumers_given_moves(move0=move0, move1=move1)
            profits[t, :] = self.profits_given_position_and_price(
                move0=move0, move1=move1, n_consumers=n_consumers[t, :])

            active = passive  # Inverse role

        return backup.RunBackup(
            parameters=self.parameters, positions=positions, prices=prices, profits=profits, n_consumers=n_consumers)
