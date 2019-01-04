from pylab import plt
import numpy as np
import matplotlib.gridspec

import operator
import itertools
# import argparse
import scipy.stats
import statsmodels.stats

import behavior.backup
import fit.data

from analysis.batch import customized_plot


def old_plot(data):

    gs = matplotlib.gridspec.GridSpec(2, 2, width_ratios=[1, 1.5])
    plt.figure(figsize=(9, 4))

    # -------------------------- Nationalities hist ---------------------------------- #
    ax = plt.subplot(gs[:, 0])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(length=0)
    plt.title("Nationality")

    # data
    dic_nationality = {}
    for n in np.unique(data.nationality):
        dic_nationality[n] = np.sum(data.nationality == n)
    nationalities = sorted(dic_nationality.items(), key=operator.itemgetter(1))
    labels = [i[0].capitalize() for i in nationalities]
    labels_pos = np.arange(len(labels))
    values = [round((i[1] / len(data.age)) * 100, 2) for i in nationalities]

    # text
    ax.set_yticks(labels_pos)
    ax.set_yticklabels(labels)
    ax.set_xticks([])
    for i, v in enumerate(values):
        ax.text(v + 1, i - 0.05, "{:.2f}%".format(v))

    # create
    ax.barh(labels_pos, values, edgecolor="white", align="center", alpha=0.5)

    # -------------------------- Gender pie ---------------------------------- #

    ax = plt.subplot(gs[0, 1])
    ax.axis('equal')
    plt.title("Gender")

    # get data
    genders = np.unique(data.gender)
    labels = [i.capitalize() for i in genders]
    values = [np.sum(data.gender == i) for i in genders]

    # create
    ax.pie(values,
           labels=labels, explode=(0.01, 0.05), autopct='%1.1f%%',
           startangle=90, shadow=False)
    # -------------------------- Age hist ---------------------------------- #
    ax = plt.subplot(gs[1, 1])
    plt.title("Age", y=1.05)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(length=0)

    # get data
    n_ages = len(data.age)
    ages = [list(i[1]) for i in itertools.groupby(sorted(data.age), lambda x: x // 10)]
    decades = ["{}0-{}9".format(int(i[0] / 10), int(i[0] / 10)) if i[0] >= 20 else "18-19" for i in ages]
    decades_pos = np.arange(len(decades))
    values = np.array([round((len(i) / n_ages) * 100) for i in ages])

    # text
    ax.set_xticks(decades_pos)
    ax.set_xticklabels(decades)
    ax.set_yticks([])
    for i, v in enumerate(values):
        ax.text(i - 0.1, v + 1, "{}%".format(v))
    ax.text(3.5, 20, "Mean: {:.2f} $\pm$ {:.2f} (SD)".format(np.mean(data.age), np.std(data.age)))

    # create
    ax.bar(decades_pos, values, edgecolor="white", align="center", alpha=0.5)

    plt.tight_layout()

    plt.savefig("fig/demographics.pdf")
    plt.show()


def old_run(force):

    data = behavior.backup.get_user_data(force)

    print("\nThere is a total of {} users.".format(len(data.age)))

    print("******* Age ********")
    print("Average age: {:.2f} ".format(np.mean(data.age)))
    print("Std age: {:.2f}".format(np.std(data.age)))
    print("Min age: {}".format(np.min(data.age)))
    print("Max age: {}".format(np.max(data.age)))
    print("******* Nationalities ********")
    for n in np.unique(data.nationality):
        print(n, np.sum(data.nationality == n))
    print("******* Gender ********")
    for g in np.unique(data.gender):
        print("{}: {}".format(g, np.sum(data.gender == g)))

    old_plot(data)


def run(force):

    fit_bkup = fit.data.get(force)
    user_bkup = behavior.backup.get_user_data(force)

    # nationalities = np.unique(user_bkup.nationality)

    user_bkup.gender[user_bkup.gender == "male"] = 0
    user_bkup.gender[user_bkup.gender == "female"] = 1

    # for i, n in enumerate(nationalities):
    #     user_bkup.nationality[user_bkup.nationality == n] = i

    n_ind = 222
    n_var = 2  # Gender, age   ## , nationality
    n_hr = 3  # Max profit, max diff, equal sharing

    hr = ('max_profit', 'max_diff', 'tacit_collusion')

    x = np.zeros((n_var, n_ind))
    y = np.zeros((n_hr, n_ind))

    for i in range(n_ind):
        x[0, i] = user_bkup.gender[i]  # np.random.choice([0, 1])
        x[1, i] = user_bkup.age[i]  # np.random.random()
        # x[2, i] = user_bkup.nationality[i]  # np.random.random()

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

    ps = []

    for i_h, heuristic in enumerate(hr):

        male_data[i_h] = y[i_h, x[0, :] == 0]
        female_data[i_h] = y[i_h, x[0, :] == 1]

        for s_data, s_name in zip((male_data[i_h], female_data[i_h]), ('male', 'female')):
            m = np.mean(s_data)
            s = np.std(s_data)
            print("{}: mean={:.02f} std={:.02f}".format(s_name, m, s))

        u, p = scipy.stats.mannwhitneyu(male_data[i_h], female_data[i_h])
        print(f'Mann-Whitney rank test for sex-score: u {u}, p {p:.3f}, n {n}')
        print()
        ps.append(p)

    valid, p_corr, alpha_c_sidak, alpha_c_bonf = \
        statsmodels.stats.multitest.multipletests(pvals=ps, alpha=0.01, method="b")

    print("p_corrected = ", [f"{i:.3f}" for i in p_corr])
    print()

    # Plot

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

    ps = []

    for i_h, heuristic in enumerate(hr):

        cor, p = scipy.stats.pearsonr(x[1, :], y[i_h])
        print(f'Pearson corr age-score {cor:.2f}, p {p:.3f}, n {len(x[0])}')

        print()
        ps.append(p)

    valid, p_corr, alpha_c_sidak, alpha_c_bonf = \
        statsmodels.stats.multitest.multipletests(pvals=ps, alpha=0.01, method="b")

    print("p_corrected = ", [f"{i:.3f}" for i in p_corr])
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

