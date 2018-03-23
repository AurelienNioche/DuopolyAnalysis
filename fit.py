import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec
import itertools as it
# from hyperopt import fmin, tpe, hp
import scipy.stats
import statsmodels.stats.multitest

from backup import backup
from model import fit
from analysis import ind_profiles
from analysis import customized_plot


class BackupFit:

    def __init__(self, size):

        self.display_opponent_score = np.zeros(size, dtype=bool)
        self.r = np.zeros(size)
        self.firm_id = np.zeros(size, dtype=int)
        self.user_id = np.zeros(size, dtype=int)
        self.room_id = np.zeros(size, dtype=int)
        self.round_id = np.zeros(size, dtype=int)
        self.score = np.zeros(size, dtype=int)

        self.fit_scores = {i: np.zeros(size) for i in fit.Score.names}


class RunModel:

    def __init__(self, dm_model, str_method, firm_id, active_player_t0, positions, prices, t_max):

        self.model = dm_model
        self.str_method = str_method
        self.firm_id = firm_id
        self.active_player_t0 = active_player_t0
        self.positions = positions
        self.prices = prices
        self.t_max = t_max

    def run(self):

        opp = (self.firm_id + 1) % 2
        player_active = self.active_player_t0

        scores = []

        for t in range(self.t_max):

            if player_active == self.firm_id:
                score = getattr(self.model, self.str_method)(
                    player_position=self.positions[t, self.firm_id], player_price=self.prices[t, self.firm_id],
                    opp_position=self.positions[t, opp], opp_price=self.prices[t, opp]
                )

                scores.append(score)

            player_active = (player_active + 1) % 2

        return np.mean(scores)


def get_fit(force):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    m = {
        0.25: fit.Score(r=0.25),
        0.50: fit.Score(r=0.5)
    }

    fit_backup = BackupFit(size=len(backups*2))

    with tqdm(total=len(backups*2)) as pbar:

        i = 0

        for b in backups:

            for player in (0, 1):

                # Register information
                fit_backup.display_opponent_score[i] = b.display_opponent_score
                fit_backup.r[i] = b.r
                fit_backup.score[i] = np.sum(b.profits[:, player])
                fit_backup.user_id[i] = b.user_id[player]
                fit_backup.room_id[i] = b.room_id
                fit_backup.round_id[i] = b.round_id
                fit_backup.firm_id[i] = player

                # Compute score
                kwargs = {
                    "dm_model": m[b.r],
                    "firm_id": player,
                    "active_player_t0": b.active_player_t0,
                    "positions": b.positions,
                    "prices": b.prices,
                    "t_max": b.t_max
                }

                for str_method in fit.Score.names:

                    rm = RunModel(**kwargs, str_method=str_method)
                    score = rm.run()
                    fit_backup.fit_scores[str_method][i] = score

                    tqdm.write("[id={}, r={:.2f}, s={}] [{}] score: {:.2f}".format(
                        i, b.r, int(b.display_opponent_score), str_method, score))

                i += 1
                pbar.update(1)

                tqdm.write("\n")

    backup.save(fit_backup, "data/fit.p")

    return fit_backup


def ind_plots(fit_b):

    scores_to_plot = ["profit", "competition"]  # fit.Score.names
    n_dim = len(scores_to_plot)
    colors = ["C{}".format(i + 2) for i in range(n_dim)]

    for r_value in (0.25, 0.50):

        for s_value in (True, False):

            cond0 = fit_b.r == r_value
            cond1 = fit_b.display_opponent_score == int(s_value)

            cond = cond0 * cond1

            n = np.sum(cond)

            data = np.zeros((n, n_dim))

            for j, score in enumerate(scores_to_plot):

                data[:, j] = fit_b.fit_scores[score][cond]

            idx = np.argsort(data[:, 1])[::-1]

            data = data[idx]

            title = "r = {:.2f} s = {}".format(r_value, int(s_value))
            ind_profiles.plot(data, labels=scores_to_plot, fig_size=(10, 3),
                              title=title, colors=colors,
                              n_dim=n_dim, n_cols=20)


def plot_scores_distribution(data, subplot_spec):

    n_rows, n_cols = 2, 2

    if not subplot_spec:

        plt.figure(figsize=(5.5, 5.5))

        gs = matplotlib.gridspec.GridSpec(nrows=n_rows, ncols=n_cols)

    else:
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=n_rows, ncols=n_cols,
                                                         subplot_spec=subplot_spec)

    positions = it.product(range(2), repeat=2)

    scores_to_plot = ["profit", "competition", "equal_sharing"]  # fit.Score.names
    n_dim = len(scores_to_plot)

    colors = ["C{}".format(i + 2) for i in range(n_dim)]

    axes = []

    for d in data:

        pos = next(positions)
        ax = plt.subplot(gs[pos[0], pos[1]])

        customized_plot.violin(data=d, ax=ax, color=colors, alpha=0.8)

        ax.set_ylim(0, 1)
        ax.set_yticks(np.arange(0, 1.1, 0.25))
        ax.tick_params(labelsize=8, axis="y")
        ax.tick_params(length=0, axis='x')
        axes.append(ax)

    for i, ax in enumerate(axes[:-2]):
        ax.set_title(["$s = 0$", "$s = 1$"][i], fontsize=14)
        ax.set_xticklabels([])

    for ax in axes[-2:]:
        ax.set_xticklabels(["Profit\nmax.", "Difference\nmax.", "Tacit\ncollusion"])

    for ax in axes[1::2]:
        ax.set_yticklabels([])
        ax.tick_params(length=0, axis="y")

    for i, ax in enumerate(axes[0::2]):
        ax.text(-0.32, 0.5, ["$r = 0.25$", "$r = 0.50$"][i], rotation="vertical", verticalalignment='center',
                horizontalalignment='center', transform=ax.transAxes, fontsize=14)
        ax.set_ylabel("\nScore")

    if not subplot_spec:

        plt.tight_layout()

        plt.savefig("fig/fit.pdf")
        plt.show()


def plot_correlations(data, subplot_spec=None):

    n_rows, n_cols = 2, 3

    width_ratios = [1, 1, 0.15]

    if not subplot_spec:

        plt.figure(figsize=(6.9, 5.5))

        gs = matplotlib.gridspec.GridSpec(nrows=n_rows, ncols=n_cols, width_ratios=width_ratios)

    else:
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=n_rows, ncols=n_cols,
                                                         subplot_spec=subplot_spec,
                                                         width_ratios=width_ratios)

    positions = it.product(range(2), repeat=2)

    scores_to_plot = ["profit", "competition", "equal_sharing"]  # fit.Score.names
    n_dim = len(scores_to_plot)

    # colors = ["C{}".format(i + 2) for i in range(n_dim)]

    axes = []

    im = None

    for d in data:

        pos = next(positions)
        ax = plt.subplot(gs[pos[0], pos[1]])

        im = ax.imshow(d, vmin=-1, vmax=1, cmap="bwr", origin='lower')

        # ax.set_ylim(0, 1)
        # ax.set_yticks(np.arange(0, 1.1, 0.25))
        # ax.tick_params(labelsize=8, axis="y")
        # ax.tick_params(length=0, axis='x')
        ax.set_aspect(1)
        axes.append(ax)

    for i, ax in enumerate(axes[:-2]):
        ax.set_title(["$s = 0$", "$s = 1$"][i], fontsize=14)
        ax.set_xticks([])

    for ax in axes[-2:]:
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Profit\nmax.", "Difference\nmax.", "Tacit\ncollusion"], rotation="vertical")

    for ax in axes[1::2]:
        ax.set_yticklabels([])
        ax.tick_params(length=0, axis="y")

    for i, ax in enumerate(axes[0::2]):
        ax.set_yticks(np.arange(3))

        ax.set_yticklabels(["Profit\nmax.", "Difference\nmax.", "Tacit\ncollusion"])
        ax.set_ylabel(["$r = 0.25$", "$r = 0.50$"][i], fontsize=14)
        #ax.text(-0.32, 0.5, ["$r = 0.25$", "$r = 0.50$"][i], rotation="vertical", verticalalignment='center',
        #        horizontalalignment='center', transform=ax.transAxes, fontsize=14)
        # ax.set_ylabel("\nScore")

    g = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=3, ncols=3, subplot_spec=gs[:, 2],
                                                    height_ratios=[0.2, 1, 0.2],
                                                    width_ratios=[0.2, 0.8, 0.1])

    cax = plt.subplot(g[1, 1])
    plt.colorbar(im, ticks=(-1, 0, 1), cax=cax),  # cax=cax)
    cax.tick_params(labelsize=10)
    cax.set_ylabel(ylabel="$R_{Pearson}$", fontsize=12)

    if not subplot_spec:

        plt.tight_layout()

        plt.savefig("fig/fit.pdf")
        plt.show()


def main(force, do_it_again, ind_profiles):

    if not os.path.exists("data/fit.p") or do_it_again or force:
        fit_b = get_fit(force)

    else:
        fit_b = backup.load("data/fit.p")

    if ind_profiles:
        ind_plots(fit_b)

    r_values = np.sort(np.unique(fit_b.r))
    s_values = (False, True)

    exp_conditions = list(it.product(r_values, s_values))

    data = []

    scores_to_plot = ["profit", "competition", "equal_sharing"]  # fit.Score.names
    n_dim = len(scores_to_plot)

    for r_value, s_value in exp_conditions:

        cond0 = fit_b.r == r_value
        cond1 = fit_b.display_opponent_score == int(s_value)

        cond = cond0 * cond1

        n = np.sum(cond)

        d = np.zeros((n_dim, n))

        for i, score in enumerate(scores_to_plot):
            d[i] = fit_b.fit_scores[score][cond]

        data.append(d)

    # ----- Clustered figure -------- #

    n_rows, n_cols = 1, 2

    fig = plt.figure(figsize=(11, 4), dpi=200)
    gs = matplotlib.gridspec.GridSpec(nrows=n_rows, ncols=n_cols, width_ratios=[1, 0.7])

    # --------- Score distribution ---------------- #

    plot_scores_distribution(data, subplot_spec=gs[0, 0])

    # --------- Correlations --------------- #

    corr = [np.corrcoef(d) for d in data]

    plot_correlations(corr, subplot_spec=gs[0, 1])

    # ----------- Fig ------------------ #

    plt.tight_layout()

    ax = fig.add_subplot(gs[:, :], zorder=-10)

    plt.axis("off")
    ax.text(
        s="A", x=-0.06, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="B", x=0.55, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    plt.savefig("fig/fit.pdf")
    plt.show()

    # ----------- Stats ----------------- #

    r = fit_b.r
    s = fit_b.display_opponent_score

    p = fit_b.fit_scores["profit"]
    d = fit_b.fit_scores["competition"]
    e = fit_b.fit_scores["equal_sharing"]

    to_compare = []

    for name, score in [("Profit maximization", p),
                        ("Difference maximization", d),
                        ("Tacit collusion", e)]:

        to_compare.append({
            "measure": name,
            "constant": "s = 0",
            "var": "r",
            "data": [score[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        })
        to_compare.append({
            "measure": name,
            "constant": "s = 1",
            "var": "r",
            "data": [score[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        })
        to_compare.append({
            "measure": name,
            "constant": "r = 0.25",
            "var": "s",
            "data": [score[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        })
        to_compare.append({
            "measure": name,
            "constant": "r = 0.50",
            "var": "s",
            "data": [score[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        })

    ps = []
    us = []

    for dic in to_compare:
        u, p = scipy.stats.mannwhitneyu(dic["data"][0], dic["data"][1])
        ps.append(p)
        us.append(u)

    valid, p_corr, alpha_c_sidak, alpha_c_bonf = \
        statsmodels.stats.multitest.multipletests(pvals=ps, alpha=0.01, method="b")

    for p, u, p_c, v, dic in zip(ps, us, p_corr, valid, to_compare):
        print("[Diff in {} when {} depending on {}-value] "
              "Mann-Whitney rank test: u {}, p {:.3f}, p corr {:.3f}, significant: {}"
              .format(dic["measure"], dic["constant"], dic["var"], u, p, p_c, v))
        print()

    table = \
        r"\begin{table}[htbp]" + "\n" + \
        r"\begin{center}" + "\n" + \
        r"\begin{tabular}{llllllll}" + "\n" + \
        r"Measure & Variable & Constant & $u$ & $p$ (before corr.) " \
        r"& $p$ (after corr.) & Sign. at 1\% threshold \\" + "\n" + \
        r"\hline \\" + "\n"

    for p, u, p_c, v, dic in zip(ps, us, p_corr, valid, to_compare):

        p = "{:.3f}".format(p) if p >= 0.001 else "$<$ 0.001"
        p_c = "{:.3f}".format(p_c) if p_c >= 0.001 else "$<$ 0.001"
        v = "yes" if v else "no"
        table += r"{} & ${}$ & ${}$ & {} & {} & {} & {} \\".format(dic["measure"], dic["var"], dic["constant"], u, p, p_c, v) \
                 + "\n"

    table += \
        r"\end{tabular}" + "\n" + \
        r"\end{center}" + "\n" + \
        r"\caption{Significance tests for comparison using Mann-Withney's u. Bonferroni corrections are applied.}" + "\n" + \
        r"\label{table:significance_tests}" + "\n" + \
        r"\end{table}"

    print("*** Latex-formated table ***")
    print(table)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do analysis")

    parser.add_argument('-i', '--ind_profiles', action="store_true", default=False,
                        help="Draw individual profiles")

    parsed_args = parser.parse_args()

    main(force=parsed_args.force, do_it_again=parsed_args.do_it_again,
         ind_profiles=parsed_args.ind_profiles)
