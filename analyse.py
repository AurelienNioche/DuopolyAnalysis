import numpy as np
import argparse
import matplotlib.gridspec
import matplotlib.pyplot as plt
import scipy.stats
import statsmodels.stats.multitest

from backup import backup
from analysis import customized_plot


def main(force):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    # ----------------- Data ------------------- #

    # Look at the parameters
    n_simulations = len(backups)
    n_positions = backups[0].n_positions

    # Containers
    d = np.zeros(n_simulations)
    prices = np.zeros(n_simulations)
    scores = np.zeros(n_simulations)
    r = np.zeros(n_simulations)
    s = np.zeros(n_simulations, dtype=bool)

    for i, b in enumerate(backups):

        # Compute the mean distance between the two firms
        data = np.absolute(
            b.positions[:, 0] -
            b.positions[:, 1]) / n_positions

        d[i] = np.mean(data)

        # Compute the mean price
        prices[i] = np.mean(b.prices[:, :])

        # Compute the mean profit
        scores[i] = np.mean(b.profits[:, :])

        r[i] = b.r
        s[i] = b.display_opponent_score

    # ---------- Plot ----------------------------- #

    fig = plt.figure(figsize=(10, 7))

    sub_gs = matplotlib.gridspec.GridSpec(nrows=3, ncols=2)

    axes = (
        fig.add_subplot(sub_gs[0, 0]),
        fig.add_subplot(sub_gs[0, 1]),
        fig.add_subplot(sub_gs[1, 0]),
        fig.add_subplot(sub_gs[1, 1]),
        fig.add_subplot(sub_gs[2, 0]),
        fig.add_subplot(sub_gs[2, 1])
    )

    y_labels = "Distance", "Price", "Score"
    y_limits = (0, 1), (0.9, 11.1), (0, 120)

    s_values = (0, 1, ) * 3

    arr = (d, d, prices, prices, scores, scores)

    axes[0].text(2, 1.3, "Display opponent score", fontsize=12)
    axes[0].set_title("\n\nFalse")
    axes[1].set_title("True")

    for idx in range(len(axes)):

        ax = axes[idx]

        ax.set_axisbelow(True)

        # Violin plot
        data = [arr[idx][(r == r_value) * (s == s_values[idx])] for r_value in (0.25, 0.50)]
        color = ['C0' if r_value == 0.25 else 'C1' for r_value in (0.25, 0.50)]

        customized_plot.violin(ax=ax, data=data, color=color, edgecolor=color, alpha=0.5)

    for ax in (axes[-2:]):
        ax.set_xticklabels(["{:.2f}".format(i) for i in (0.25, 0.50)])
        ax.set_xlabel("r")

    for ax in axes[:4]:
        ax.tick_params(length=0)
        ax.set_xticklabels([])

    for ax, y_label, y_lim in zip(axes[0::2], y_labels, y_limits):
        ax.set_ylabel(y_label)
        ax.set_ylim(y_lim)

    for ax, y_lim in zip(axes[1::2], y_limits):
        ax.set_ylim(y_lim)
        ax.tick_params(length=0)
        ax.set_yticklabels([])

    plt.tight_layout()

    plt.savefig("fig/main_exp.pdf")
    plt.show()

    # ----------- Stats ----------------- #

    to_compare = [
        {
            "measure": "distance",
            "constant": "s = 0",
            "var": "r",
            "data": [d[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "distance",
            "constant": "s = 1",
            "var": "r",
            "data": [d[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "prices",
            "constant": "s = 0",
            "var": "r",
            "data": [prices[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "prices",
            "constant": "s = 1",
            "var": "r",
            "data": [prices[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "scores",
            "constant": "s = 0",
            "var": "r",
            "data": [scores[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "scores",
            "constant": "s = 1",
            "var": "r",
            "data": [scores[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "distance",
            "constant": "r = 0.25",
            "var": "s",
            "data": [d[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "distance",
            "constant": "r = 0.50",
            "var": "s",
            "data": [d[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "prices",
            "constant": "r = 0.25",
            "var": "s",
            "data": [prices[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "prices",
            "constant": "r = 0.50",
            "var": "s",
            "data": [prices[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "price",
            "constant": "r = 0.25",
            "var": "s",
            "data": [scores[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "scores",
            "constant": "r = 0.50",
            "var": "s",
            "data": [scores[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }
    ]

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
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)

