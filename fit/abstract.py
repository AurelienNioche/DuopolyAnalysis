# DuopolyAnalysis
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


class AbstractModel:

    n_positions = 21
    n_prices = 11
    p_min = 1
    p_max = 11
    t_max = 25

    def __init__(self, r, **kwargs):

        self.r = r

        self.strategies, self.convert_to_strategies = self.get_strategies()

        self.prices = np.arange(self.p_min, self.p_max+1)

        assert len(self.prices) == self.n_prices, "General case is not handled!"

        # Useful n
        self.n_strategies = len(self.strategies)
        self.idx_strategies = np.arange(self.n_strategies)

        # Prepare useful arrays
        self.n_consumers, self.max_n = self.compute_n_consumers()

        self.max_profit = self.p_max * self.max_n

    def get_strategies(self):

        strategies = []
        convert_to_strategies = dict()
        for i, (pos, i_price) in enumerate(itertools.product(range(self.n_positions), range(self.n_prices))):
            strategies.append([pos, i_price])
            price = i_price + 1
            convert_to_strategies[(pos, price)] = i

        return np.asarray(strategies, dtype=int), convert_to_strategies

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
        field_of_view[:] = [self._field_of_view(x) for x in range(self.n_positions)]

        max_n = 0

        for i, j in itertools.combinations_with_replacement(range(self.n_positions), r=2):

            n0, n1 = 0, 0
            for x in range(self.n_positions):

                see_firm_0 = field_of_view[x, 0] <= i <= field_of_view[x, 1]
                see_firm_1 = field_of_view[x, 0] <= j <= field_of_view[x, 1]

                if see_firm_0 and see_firm_1:
                    z[i, j, 2] += 1
                    n0 += 1
                    n1 += 1

                elif see_firm_0:
                    z[i, j, 0] += 1
                    n0 += 1

                elif see_firm_1:
                    z[i, j, 1] += 1
                    n1 += 1

            max_n = max(max_n, n0, n1)

            z[j, i, 0] = z[i, j, 1]
            z[j, i, 1] = z[i, j, 0]
            z[j, i, 2] = z[i, j, 2]

        return z, max_n

    def _field_of_view(self, x):

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

    def _profits_given_position_and_price(self, move0, move1, n_consumers=None):

        """
        Given moves of the two firms, compute expected profits.
        :param move0: Move of firm 0 (int)
        :param move1: Move of firm 1 (int)
        :param n_consumers: (Optional) Number of expected consumers for both firms (np.array of length 2)
        :return: Expected profits (np.array of length 2)
        """

        if n_consumers is None:
            n_consumers = self._get_n_consumers_given_moves(move0=move0, move1=move1)

        return n_consumers * self.prices[
            self.strategies[(move0, move1), 1]  # In strategies, idx of prices are stored, not prices themselves
        ]

    def _get_n_consumers_given_moves(self, move0, move1):

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
