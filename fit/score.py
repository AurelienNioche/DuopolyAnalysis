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
from fit import abstract


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
        player_value = max(0, profits_differences[player_move])

        return player_value / max_value if max_value > 0 else 1

    def profit_strategic(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        values = np.zeros(self.n_strategies)

        profits_t_plus = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            profits_t = self._profits_given_position_and_price(i, opp_move)[0]
            for j in range(self.n_strategies):
                profits_t_plus[j] = self._profits_given_position_and_price(i, j)

            max_profits_opp = max(profits_t_plus[:, 1])
            mean_profits_t_plus = np.mean(profits_t_plus[profits_t_plus[:, 1] == max_profits_opp, 0])
            values[i] = profits_t + mean_profits_t_plus

        max_value = max(values)
        player_value = values[player_move]

        return player_value / max_value if max_value > 0 else 1

    def competition_strategic(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        values = np.zeros(self.n_strategies)

        profits_t_plus = np.zeros((self.n_strategies, 2))
        delta_t_plus = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):

            profits_t = self._profits_given_position_and_price(i, opp_move)
            delta_t = profits_t[0] - profits_t[1]

            # print("delta t", delta_t)

            for j in range(self.n_strategies):
                profits_t_plus[j] = self._profits_given_position_and_price(i, j)
                delta_t_plus[j, 1] = profits_t_plus[j, 1] - profits_t_plus[j, 0]
                delta_t_plus[j, 0] = profits_t_plus[j, 0] - profits_t_plus[j, 1]

            max_delta_opp = max(delta_t_plus[:, 1])
            mean_delta_t_plus = np.mean(delta_t_plus[delta_t_plus[:, 1] == max_delta_opp, 0])

            #  print("mean delta t plus", mean_delta_t_plus)

            values[i] = delta_t + mean_delta_t_plus

        max_value = max(values)  # Why always 21?
        player_value = max(0, values[player_move])

        return player_value / max_value if max_value > 0 else 1

    def equal_sharing(self, player_position, player_price, opp_position, opp_price):

        player_move = self.convert_to_strategies[(player_position, player_price)]

        exp_profits = self._get_expected_profits(opp_position, opp_price)

        max_profits_0 = max(exp_profits[:, 0])
        max_profits_1 = max(exp_profits[:, 1])

        diff_max_0 = max_profits_0 - exp_profits[:, 0]
        diff_max_1 = max_profits_1 - exp_profits[:, 1]

        diff = diff_max_0 + diff_max_1

        max_value = max(diff)
        player_value = max_value - diff[player_move]

        return player_value / max_value if max_value > 0 else 1
