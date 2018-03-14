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


class Model(abstract.AbstractModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _softmax(values, temp):

        e = np.exp(values / temp)
        dist = e / np.sum(e)
        return dist

    def get_expected_profits(self, opp_position, opp_price):

        opp_move = self.convert_to_strategies[(opp_position, opp_price)]

        exp_profits = np.zeros((self.n_strategies, 2))

        for i in range(self.n_strategies):
            exp_profits[i] = self._profits_given_position_and_price(i, opp_move)

        return exp_profits

    def p_profit(self, player_position, player_price, opp_position, opp_price, temp=None):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        exp_profits = self.get_expected_profits(opp_position=opp_position, opp_price=opp_price)

        if temp:
            return self._softmax(exp_profits[:, 0] / self.max_profit, temp)[player_move]
        else:
            return 1 if exp_profits[player_move, 0] == max(exp_profits[:, 0]) else 0

    def p_competition(self, player_position, player_price, opp_position, opp_price, temp=None):

        player_move = self.convert_to_strategies[(player_position, player_price)]
        exp_profits = self.get_expected_profits(opp_position=opp_position, opp_price=opp_price)

        profits_differences = np.array(exp_profits[:, 0] - exp_profits[:, 1])

        if temp:
            return self._softmax(profits_differences / self.max_profit, temp)[player_move]
        else:
            return 1 if profits_differences[player_move] == max(profits_differences) else 0
