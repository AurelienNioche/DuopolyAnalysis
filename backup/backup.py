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

import pickle
import os


class Backup:

    def __init__(self, r, t_max, display_opponent_score, positions, prices, profits,
                 pvp, room_id, round_id, active_player_t0, user_id, n_positions=21, n_prices=11,
                 p_min=0, p_max=11):

        # Backup.__init__(self)

        # Data
        self.positions = positions
        self.prices = prices
        self.profits = profits

        self.active_player_t0 = active_player_t0

        # Parameters
        self.pvp = pvp
        self.r = r
        self.display_opponent_score = display_opponent_score
        self.t_max = t_max  # Should be 25
        self.n_positions = n_positions
        self.n_prices = n_prices
        self.p_min = p_min
        self.p_max = p_max

        # Info
        self.user_id = user_id  # List of 2 users
        self.room_id = room_id
        self.round_id = round_id


def save(obj, file_name="data/data.p"):

    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Save data in pickle
    with open(file_name, "wb") as f:
        pickle.dump(obj, f)


def load(file_name="data/data.p"):

    with open(file_name, "rb") as f:
        return pickle.load(f)
