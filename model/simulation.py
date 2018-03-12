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


class SimulationModel(abstract.AbstractModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def optimal_profit_move(self, opp_move):

        """
        Select the move that give the maximum profit at t
        :param opp_move: Move of the opponent (int)
        :return: Selected move (int)
        """

        exp_profits = np.zeros(self.n_strategies)

        for i in range(self.n_strategies):
            exp_profits[i] = self._profits_given_position_and_price(i, opp_move)[0]

        max_profits = max(exp_profits)

        idx = np.flatnonzero(exp_profits == max_profits)

        return np.random.choice(idx)

    def optimal_move_to_beat_the_opponent(self, opp_move):

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
            return np.random.choice(idx_max_diff)

    def random_move(self):
        return np.random.randint(self.n_positions), np.random.randint(self.p_min, self.p_max + 1)

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

            moves[active] = self.random_move()

            move0, move1 = moves  # Useful for call of functions

            # Record for further analysis
            positions[t, :] = self.strategies[moves, 0]
            prices[t, :] = self.prices[self.strategies[moves, 1]]
            n_consumers[t, :] = self._get_n_consumers_given_moves(move0=move0, move1=move1)
            profits[t, :] = self._profits_given_position_and_price(
                move0=move0, move1=move1, n_consumers=n_consumers[t, :])

            active = passive  # Inverse role

        # return backup.backup.save(
        #     obj={"profits": profits},
        #     file_name="data/random_player_{}.p".format(data         ))
