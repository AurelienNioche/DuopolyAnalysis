# Django specific settings
import os
import pickle
import numpy as np
import linearmodels as lm
import scipy.stats

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

import matplotlib
import matplotlib.pyplot as plt

# Your application specific imports
from game.models import User, Room, Round, RoundComposition, RoundState, FirmProfit
import fit.data
import fit.stats
import behavior.data
import behavior.stats
import behavior.backup
import behavior.demographics
from make_figs import simulation_fig

from analysis.batch import customized_plot


def load(fname):
    with open(f'data/{fname}', 'rb') as f:
        return pickle.load(f)


def save(obj, fname):
    with open(f'data/{fname}', 'wb') as f:
        return pickle.dump(obj=obj, file=f)


def print_stats():

    behavior.stats.stats()
    fit.stats.stats()


def run_simulations():
    simulation_fig(
        force=False,
        # pool simulations are simulations where
        # where vary r
        span_pool=1,
        t_max_pool=100,
        t_max_xp=25,
        random_params=True,
        force_params=False,
    )


def demographics():

    behavior.demographics.run(force=False)


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


def compute_number_of_observations_xp_fit():
    # fit data structure = [ [[r=0.25, s=0] * n_heuristic],
    #                        [[r=0.25, s=1] * n_heuristic]],
    #                       [[r=0.5, s=0] * n_heuristic]],
    #                       [[r=0.5, s=1] * n_heuristic]] ]

    fit_data = fit.data.get()

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


def compute_demographics_analysis():

    fit_bkup = load('fit.p')
    user_bkup = behavior.backup.get_user_data()

    nationalities = np.unique(user_bkup.nationality)

    user_bkup.gender[user_bkup.gender == "male"] = 0
    user_bkup.gender[user_bkup.gender == "female"] = 1

    for i, n in enumerate(nationalities):
        user_bkup.nationality[user_bkup.nationality == n] = i

    n_ind = 222
    n_var = 3  # Gender, age, nationality
    n_hr = 3  # Max profit, max diff, equal sharing

    hr = ('max_profit', 'max_diff', 'equal_sharing')

    x = np.zeros((n_var, n_ind))
    y = np.zeros((n_hr, n_ind))

    for i in range(n_ind):
        x[0, i] = user_bkup.gender[i]  # np.random.choice([0, 1])
        x[1, i] = user_bkup.age[i]  # np.random.random()
        x[2, i] = user_bkup.nationality[i]  # np.random.random()

    for i_h, heuristic in enumerate(hr):

        for i, y_i in enumerate(fit_bkup.t_fit_scores[heuristic]):
            y[i_h, i] = np.mean(y_i)
            assert y[i_h, i] == fit_bkup.fit_scores[heuristic][i]

        print("\n{}: {}".format('Heuristic', heuristic))

        print("{}: {:.02f}". format("General mean", np.mean(y[i_h]), "General std", np.std(y[i_h])))

    # Sex
    n_male = np.sum(x[0, :] == 0)
    n_female = np.sum(x[0, :] == 1)

    n = n_male + n_female

    male_data = np.zeros((n_hr, n_male))
    female_data = np.zeros((n_hr, n_female))

    for i_h, heuristic in enumerate(hr):

        male_data[i_h] = y[i_h, x[0, :] == 0]
        female_data[i_h] = y[i_h, x[0, :] == 1]

        for s_data, s_name in zip((male_data[i_h], female_data[i_h]), ('male', 'female')):
            m = np.mean(s_data)
            s = np.std(s_data)
            print("{}: mean={:.02f} std={:.02f}".format(s_name, m, s))

        u, p = scipy.stats.mannwhitneyu(male_data[i_h], female_data[i_h])
        print(f'Mann-Whitney rank test for sex-score: u {u}, p {p:.3f}, n {n}')

    fig = plt.figure(figsize=(5, 8), dpi=200)

    gs = matplotlib.gridspec.GridSpec(nrows=3, ncols=1)

    axes = (
        fig.add_subplot(gs[0, 0]),
        # plt.subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        # plt.subplot(gs[1, 1]),
        fig.add_subplot(gs[2, 0]),
        # plt.subplot(gs[2, 1])
    )

    color = ("C0", "C9")

    for i_h, heuristic in enumerate(hr):
        customized_plot.violin(ax=axes[i_h], data=[male_data[i_h], female_data[i_h]],
                               color=color, edgecolor="white", alpha=0.8)
        axes[i_h].set_ylabel("Score")
        axes[i_h].set_ylim((-0.01, 1.01))

    axes[0].set_xticks([])
    axes[1].set_xticks([])
    axes[2].set_xticklabels(['Male', 'Female'])

    # axes[0].set_ylabel("Score")

    plt.tight_layout()

    ax = fig.add_subplot(gs[:, :], zorder=-10)

    plt.axis("off")
    ax.text(
        s="A", x=-0.13, y=0.69, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="B", x=-0.13, y=0.35, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="C", x=-0.13, y=0, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    plt.savefig('fig/supplementary_sex.pdf')

    # plt.show()
    plt.close()
    #
    # Age

    for i_h, heuristic in enumerate(hr):

        cor, p = scipy.stats.pearsonr(x[1, :], y[i_h])
        print(f'Pearson corr age-score {cor:.2f}, p {p:.3f}, n {len(x[0])}')

        print()

    # Figure for age

    fig = plt.figure(figsize=(5, 8), dpi=200)

    gs = matplotlib.gridspec.GridSpec(nrows=3, ncols=1)

    axes = (
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[2, 0])
    )

    for i_h, heuristic in enumerate(hr):

        # Do the scatter plot
        axes[i_h].scatter(x[1, :], y[i_h], facecolor="black", edgecolor='white', s=15, alpha=1)

        axes[i_h].set_ylabel("Score")
        axes[i_h].set_ylim((-0.01, 1.01))

    axes[0].set_xticks([])
    axes[1].set_xticks([])
    axes[2].set_xlabel("Age")

    # axes[0].set_ylabel("Score")

    plt.tight_layout()

    ax = fig.add_subplot(gs[:, :], zorder=-10)

    plt.axis("off")
    ax.text(
        s="A", x=-0.13, y=0.69, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="B", x=-0.13, y=0.35, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="C", x=-0.13, y=0, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    plt.savefig('fig/supplementary_age.pdf')

    plt.show()

        # for age in range(15, 61, 15):
        #     d = [y[i] for i in range(len(y)) if x[1, i] in (age, age+14)]
        #     print("{}-{}: mean={:.02f} std={:.02f}".format(age, age+14, np.mean(d), np.std(d)))

        # Nationality
        # for i, n in enumerate(nationalities):
        #     m = np.mean(y[x[2, :] == i])
        #     s = np.std(y[x[2, :] == i])
        #     print("{}: mean={:.02f} std={:.02f}".format(n, m, s))


# def kruskal():
#
#     fit_bkup = load('fit.p')
#     user_bkup = load('user.p')
#
#     x = np.asarray(fit_bkup.fit_scores)[user_bkup.gender == 'female']
#     y = np.asarray(fit_bkup.fit_scores)[user_bkup.gender == 'male']
#
#     print(scipy.stats.kruskal(x, y))


def main():
    # print('Subjects stats according to remuneration: ', compute_remuneration())
    # print('Subjects stats: ', compute_conditions())
    # print('Count of xp fit data')
    # print(compute_number_of_observations_xp_fit())
    # print('Count of xp behavior data')
    # print(compute_number_of_observations_xp_behavior())
    # run_simulations()
    # demographics()
    compute_demographics_analysis()
    # kruskal()
    # compute_remuneration()
    # print_stats()


if __name__ == "__main__":
    main()
