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


class FitModel(abstract.AbstractModel):

    def __int__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _softmax(values, temp):

        e = np.exp(values / temp)
        dist = e / np.sum(e)
        return dist

    def p_profit(self, player_position, player_price, opp_position, opp_price, temp):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        exp_profits = np.zeros(self.n_strategies)

        for i in range(self.n_strategies):
            exp_profits[i] = self._profits_given_position_and_price(i, opp_move)[0]

        return self._softmax(exp_profits/self.max_profit, temp)[player_move]

    def p_competition(self, player_position, player_price, opp_position, opp_price, temp):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        exp_profits = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits[i, :] = self._profits_given_position_and_price(i, opp_move)

        profits_differences = np.array(exp_profits[:, 0] - exp_profits[:, 1])

        max_profits_difference = max(profits_differences)

        idx_max_diff = np.flatnonzero(profits_differences == max_profits_difference)

        # If more than one value
        if len(idx_max_diff) > 1:

            # Get max profit
            max_profits_value = max(exp_profits[idx_max_diff][:, 0])

            # Get matching idx
            idx_max_profit = np.flatnonzero(exp_profits[:, 0] == max_profits_value)

            # Get idx that are True in both condition: max profit and max difference
            idx_max_profit_in_max_diff = np.intersect1d(idx_max_profit, idx_max_diff)

            return np.random.choice(idx_max_profit_in_max_diff)

        else:
            return self._softmax(profits_differences/self.max_profit, temp)[player_move]

