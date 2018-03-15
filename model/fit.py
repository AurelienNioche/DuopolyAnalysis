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
from . import abstract


class Score(abstract.AbstractModel):

    names = "profit", "profit_strategic", "competition", "competition_strategic", "equal_sharing"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # @staticmethod
    # def _softmax(values, temp):
    #
    #     e = np.exp(values / temp)
    #     dist = e / np.sum(e)
    #     return dist

    def _get_expected_profits(self, opp_position, opp_price):

        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        exp_profits = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits[i] = self._profits_given_position_and_price(i, opp_move)

        return exp_profits

    def profit(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        exp_profits = self._get_expected_profits(opp_position=opp_position, opp_price=opp_price)[:, 0]

        max_value = max(exp_profits)
        player_value = exp_profits[player_move]

        score = player_value / max_value if max_value > 0 else 1

        return score

    def competition(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        exp_profits = self._get_expected_profits(opp_position=opp_position, opp_price=opp_price)

        profits_differences = exp_profits[:, 0] - exp_profits[:, 1]

        max_value = max(profits_differences)
        player_value = profits_differences[player_move]

        return player_value / max_value if max_value > 0 else 1

    def profit_strategic(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        exp_profits = np.zeros(self.n_strategies)

        exp_profits_t = np.zeros(self.n_strategies)
        exp_profits_t_plus = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits_t[i] = self._profits_given_position_and_price(i, opp_move)[0]
            for j in range(self.n_strategies):
                exp_profits_t_plus[j] = self._profits_given_position_and_price(i, j)

            max_profits_opp = max(exp_profits_t_plus[:, 1])
            exp_profits[i] = \
                exp_profits_t[i] + np.mean(exp_profits_t_plus[exp_profits_t_plus[:, 1] == max_profits_opp, 0])

        max_value = max(exp_profits)
        player_value = exp_profits[player_move]

        return player_value / max_value if max_value > 0 else 1

    def competition_strategic(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        profits_differences = np.zeros(self.n_strategies)

        exp_profits_t = np.zeros((self.n_strategies, 2))
        profits_differences_t = np.zeros(self.n_strategies)
        exp_profits_t_plus = np.zeros((self.n_strategies, 2))
        profits_differences_t_plus = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):

            exp_profits_t[i] = self._profits_given_position_and_price(i, opp_move)
            profits_differences_t[i] = exp_profits_t[i, 0] - exp_profits_t[i, 1]

            for j in range(self.n_strategies):
                exp_profits_t_plus[j] = self._profits_given_position_and_price(i, j)
                profits_differences_t_plus[j, 1] = exp_profits_t_plus[j, 1] - exp_profits_t_plus[j, 0]
                profits_differences_t_plus[j, 0] = exp_profits_t_plus[j, 0] - exp_profits_t_plus[j, 1]

            max_diff_opp = max(profits_differences_t_plus[:, 1])

            profits_differences[i] = \
                profits_differences[i] + \
                np.mean(profits_differences_t_plus[profits_differences_t_plus[:, 1] == max_diff_opp, 0])

        max_value = max(profits_differences)
        player_value = profits_differences[player_move]

        return player_value / max_value if max_value > 0 else 1

    def equal_sharing(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]

        exp_profits = self._get_expected_profits(opp_position, opp_price)

        max_profits_0 = max(exp_profits[:, 0])
        max_profits_1 = max(exp_profits[:, 1])

        diff_max_0 = exp_profits[:, 0] - max_profits_0
        diff_max_1 = exp_profits[:, 1] - max_profits_1

        diff = diff_max_0 + diff_max_1

        max_value = max(diff)
        player_value = diff[player_move]

        return player_value / max_value if max_value > 0 else 1
