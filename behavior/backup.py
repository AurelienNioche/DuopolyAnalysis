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
# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from game.models import Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState, User

import pickle
from tqdm import tqdm
import numpy as np
import collections


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


class UserBackup:

    def __init__(self, user_id, nationality, age, gender):

        self.nationality = nationality
        self.age = age
        self.gender = gender
        self.user_id = user_id


def save(obj, file_name="data/data.p"):

    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # Save data in pickle
    with open(file_name, "wb") as f:
        pickle.dump(obj, f)


def load(file_name="data/data.p"):

    with open(file_name, "rb") as f:
        return pickle.load(f)


def load_data_from_db():

    backups = []

    rms = Room.objects.filter(state="end")

    for rm in tqdm(rms):

        t_max = rm.ending_t
        r = rm.radius
        display_opponent_score = rm.display_opponent_score

        rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

        for rd in rds:

            positions = np.zeros((t_max, 2), dtype=int)
            prices = np.zeros((t_max, 2), dtype=int)
            profits = np.zeros((t_max, 2), dtype=int)

            position_entries = FirmPosition.objects.filter(round_id=rd.id)
            price_entries = FirmPrice.objects.filter(round_id=rd.id)
            profits_entries = FirmProfit.objects.filter(round_id=rd.id)

            for t in range(t_max):
                positions[t, :] = \
                    [i[0] for i in position_entries.values_list("value").filter(t=t).order_by("agent_id")]
                prices[t, :] = \
                    [i[0] for i in price_entries.values_list("value").filter(t=t).order_by("agent_id")]

            for t in range(1, t_max + 1):
                profits[t - 1] = \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t).order_by("agent_id")]) - \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t - 1).order_by("agent_id")])

            round_composition = RoundComposition.objects.filter(round_id=rd.id).order_by("firm_id")
            user_id = ["bot" if rc.bot else rc.user_id for rc in round_composition]

            active_player_t0 = RoundState.objects.filter(round_id=rd.id, t=0).first().firm_active

            if active_player_t0 == 1:
                cond = positions[0, 0] == 0 and prices[0, 0] == 5
            else:
                cond = positions[0, 1] == 20 and prices[0, 1] == 5

            if cond:
                b = Backup(
                    t_max=t_max, r=r, display_opponent_score=display_opponent_score,
                    positions=positions, prices=prices, profits=profits,
                    room_id=rm.id, round_id=rd.id, pvp=rd.pvp, user_id=user_id,
                    active_player_t0=active_player_t0)

                backups.append(b)

    save(backups)

    return backups


def load_filtered_data_from_db():

    backups = []

    rms = Room.objects.filter(state="end")

    for rm in tqdm(rms):

        t_max = rm.ending_t
        r = rm.radius
        display_opponent_score = rm.display_opponent_score

        rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

        for rd in rds:

            positions = np.zeros((t_max, 2), dtype=int)
            prices = np.zeros((t_max, 2), dtype=int)
            profits = np.zeros((t_max, 2), dtype=int)

            position_entries = FirmPosition.objects.filter(round_id=rd.id)
            price_entries = FirmPrice.objects.filter(round_id=rd.id)
            profits_entries = FirmProfit.objects.filter(round_id=rd.id)

            for t in range(t_max):
                positions[t, :] = \
                    [i[0] for i in position_entries.values_list("value").filter(t=t).order_by("agent_id")]
                prices[t, :] = \
                    [i[0] for i in price_entries.values_list("value").filter(t=t).order_by("agent_id")]

            for t in range(1, t_max + 1):
                profits[t - 1] = \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t).order_by("agent_id")]) - \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t - 1).order_by("agent_id")])

            round_composition = RoundComposition.objects.filter(round_id=rd.id).order_by("firm_id")
            user_id = ["bot" if rc.bot else rc.user_id for rc in round_composition]

            active_player_t0 = RoundState.objects.filter(round_id=rd.id, t=0).first().firm_active

            if active_player_t0 == 1:
                cond = positions[0, 0] == 0 and prices[0, 0] == 5
            else:
                cond = positions[0, 1] == 20 and prices[0, 1] == 5

            if cond:

                b = Backup(
                    t_max=t_max, r=r, display_opponent_score=display_opponent_score,
                    positions=positions, prices=prices, profits=profits,
                    room_id=rm.id, round_id=rd.id, pvp=rd.pvp, user_id=user_id,
                    active_player_t0=active_player_t0)

                backups.append(b)

    save(backups)

    return backups


def load_user_data_from_db():

    print("reimport data")

    users = User.objects.filter(state="end")

    gender = []
    age = []
    nationality = []
    user_id = []

    for u in users:

        rm = Room.objects.get(id=u.room_id)
        if rm.state != "end":
            print('room not ended')
            continue
        else:
            initial_placement_correct = True

            rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

            for rd in rds:
                active_player_t0 = RoundState.objects.filter(round_id=rd.id, t=0).first().firm_active

                if active_player_t0 == 1:
                    cond = FirmPosition.objects.get(round_id=rd.id, t=0, agent_id=0).value == 0 and \
                           FirmPrice.objects.get(round_id=rd.id, t=0, agent_id=0).value == 5
                else:
                    cond = FirmPosition.objects.get(round_id=rd.id, t=0, agent_id=1).value == 20 and \
                           FirmPrice.objects.get(round_id=rd.id, t=0, agent_id=1).value == 5

                if not cond:
                    initial_placement_correct = False

            if not initial_placement_correct:
                continue

        gender.append(u.gender.lower())
        age.append(u.age)
        user_id.append(u.id)

        raw_nationality = u.nationality.lower()

        if "india" in raw_nationality:
            nationality.append("indian")

        elif "america" in raw_nationality or raw_nationality in (
                "us", "americian", "usa", "english/united states",
                "uniyed states", "united states"):
            nationality.append("american")

        elif "dominican republic" in raw_nationality:
            nationality.append("dominican")

        elif "canada" in raw_nationality:
            nationality.append("canadian")

        elif raw_nationality in ("black", "european", "white"):
            nationality.append("undefined")

        else:
            nationality.append(raw_nationality)

    user_data = UserBackup(
        age=np.array(age),
        gender=np.array(gender),
        nationality=np.array(nationality),
        user_id=np.array(user_id)
    )

    save(user_data, "data/user.p")
    return user_data


def load_remuneration_data_from_db(force=False, conversion_rate=0.5 * 10 ** (-3)):

    data_filtered = get_data(force=force)

    remuneration_data = {}
    treated_users = set()

    for d in data_filtered:

        for user_id in d.user_id:
            if user_id == 'bot' or user_id in treated_users:
                continue

            treated_users.add(user_id)

            # Application logic
            u = User.objects.filter(id=user_id).first()
            if not u:
                raise Exception

            if u:
                rm = Room.objects.filter(id=u.room_id).first()
                if rm:
                    if rm.state == "end":

                        rds = Round.objects.filter(room_id=rm.id)

                        round_id_and_agent_ids = []

                        for rd in rds:

                            rc = RoundComposition.objects.filter(round_id=rd.id, user_id=u.id).first()
                            if rc is not None:
                                round_id_and_agent_ids.append((rd.id, rc.firm_id))

                        profit = 0

                        for round_id, agent_id in round_id_and_agent_ids:
                            # print("round_id", round_id, "agent_id", agent_id)

                            pr = FirmProfit.objects.get(agent_id=agent_id, t=rm.ending_t, round_id=round_id).value

                            profit += pr

                        comp = 1 + profit * conversion_rate
                        remuneration_data[user_id] = comp

    save(remuneration_data, 'data/remuneration_data.p')
    return remuneration_data


def load_count_data_from_db():

    count= dict(
        all=0,
        total_excluded=0,
        not_entered=0,
        stopped=0,
        tutorial=0,
        pve=0,
        pvp=0,
        end=0,
    )

    for u in User.objects.all():

        count['all'] += 1
        rm = Room.objects.filter(id=u.room_id).first()

        if rm:
            if rm.state not in count:
                count[rm.state] = 1
            else:
                count[rm.state] += 1
            if rm.state not in ('end',):
                count['stopped'] += 1
        else:
            count['not_entered'] += 1

    # 10 sessions were not valid
    #  (bad positions and prices at the beginning)
    # were part of pretests
    count['end'] -= 10
    count['all'] -= 10

    # total excluded
    count['total_excluded'] = count['stopped'] + count['not_entered']

    save(count, 'data/count_data.p')
    return count


def get_user_data(force=False):

    if not os.path.exists("data/user.p") or force:
        user_data = load_user_data_from_db()
    else:
        user_data = load("data/user.p")

    return user_data


def get_remuneration_data(force=False):

    if not os.path.exists("data/remuneration_data.p") or force:
        remuneration_data = load_remuneration_data_from_db(force=force)
    else:
        remuneration_data = load("data/remuneration_data.p")

    return remuneration_data


def get_count_data(force=False):

    if not os.path.exists("data/count_data.p") or force:
        count_data = load_count_data_from_db()
    else:
        count_data = load("data/count_data.p")

    return count_data


def get_data(force=False):

    if not os.path.exists("data/data.p") or force:
        backups = load_data_from_db()
    else:
        backups = load()

    return backups
