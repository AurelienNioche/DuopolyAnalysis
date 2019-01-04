# Django specific settings
import os
import pickle
import numpy as np

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Your application specific imports
from game.models import User, Room, Round, RoundComposition, RoundState, FirmProfit
import fit.data
import behavior.data
import behavior.stats
import behavior.backup
import behavior.demographics


def load(fname):
    with open(f'data/{fname}', 'rb') as f:
        return pickle.load(f)


def save(obj, fname):
    with open(f'data/{fname}', 'wb') as f:
        return pickle.dump(obj=obj, file=f)


def print_stats():
    behavior.stats.stats()


def old_demographics():

    behavior.demographics.old_run(force=False)


def compute_conditions():
    count = dict(
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

    return count


def compute_number_of_observations_xp_fit(force=False):
    # fit data structure = [ [[r=0.25, s=0] * n_heuristic],
    #                        [[r=0.25, s=1] * n_heuristic]],
    #                       [[r=0.5, s=0] * n_heuristic]],
    #                       [[r=0.5, s=1] * n_heuristic]] ]

    fit_data = fit.data.get_customized(force)

    count = {
        "r=0.25, s=0": len(fit_data[0][0]),
        "r=0.25_s=1": len(fit_data[1][0]),
        "r=0.5_s=0": len(fit_data[2][0]),
        "r=0.5_s=1": len(fit_data[3][0]),
        "total": sum([len(x[0]) for x in fit_data])
    }

    return count


def compute_number_of_observations_xp_behavior():
    # behavior data structure:
    # each variable (r, s, dist, price, profits)
    # len(variable) == number of subjects == 222
    # we use numpy array masks in order to select values
    # depending on conditions

    r, s, dist, price, profits = behavior.data.get()

    count = {
        "r=0.25, s=0": len(dist[(r == 0.25) * (s == 0)]),
        "r=0.25_s=1": len(dist[(r == 0.25) * (s == 1)]),
        "r=0.5_s=0": len(dist[(r == 0.5) * (s == 0)]),
        "r=0.5_s=1": len(dist[(r == 0.5) * (s == 1)]),
        "total": len(dist)
    }

    return count


def compute_remuneration():

    compensation = []
    conversion_rate = 0.5 * 10 ** (-3)

    data_filtered = behavior.backup.get_data(force=False)
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

                        compensation.append(1 + profit*conversion_rate)

    # Assert that we treat only subjects that did the experiment
    assert len(treated_users) == 222
    print("mean =", np.mean(compensation))
    print("std =", np.std(compensation))


def main():

    # print('Subjects stats according to remuneration: ', compute_remuneration())
    # print('Subjects stats: ', compute_conditions())
    # print('Count of xp fit data')
    # print(compute_number_of_observations_xp_fit())
    # print('Count of xp behavior data')
    print(compute_number_of_observations_xp_behavior())
    # run_simulations()
    # demographics()
    # kruskal()
    # compute_remuneration()
    # print_stats()


if __name__ == "__main__":
    main()
