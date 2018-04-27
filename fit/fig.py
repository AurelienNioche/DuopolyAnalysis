import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec
import itertools as it

from analysis.profiling import ind_profiles
from analysis.batch import customized_plot


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


def scores_distribution(data, subplot_spec):

    n_rows, n_cols = 2, 2

    gs = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=n_rows, ncols=n_cols, subplot_spec=subplot_spec)

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


def correlations(data, subplot_spec):

    data = [np.corrcoef(d) for d in data]

    tick_fontsize = 8

    n_rows, n_cols = 1, 2

    width_ratios = [1, 0.1]
    root_gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
        nrows=n_rows, ncols=n_cols, subplot_spec=subplot_spec, width_ratios=width_ratios, wspace=0.001)

    n_rows, n_cols = 2, 2
    width_ratios = [1, 1]
    gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
        nrows=n_rows, ncols=n_cols, subplot_spec=root_gs[0, 0], width_ratios=width_ratios, wspace=0.001)

    positions = it.product(range(2), repeat=2)

    axes = []

    im = None

    for d in data:

        pos = next(positions)
        ax = plt.subplot(gs[pos[0], pos[1]])

        im = ax.imshow(d, vmin=-1, vmax=1, cmap="bwr", origin='lower')

        ax.set_aspect(1)
        axes.append(ax)

    for i, ax in enumerate(axes[:-2]):
        ax.set_title(["$s = 0$", "$s = 1$"][i], fontsize=14)
        ax.set_xticks([])

    for ax in axes[-2:]:
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Profit\nmax.", "Difference\nmax.", "Tacit\ncollusion"],
                           rotation="vertical", fontsize=tick_fontsize)

    for ax in axes[1::2]:
        ax.set_yticklabels([])
        ax.tick_params(length=0, axis="y")

    for i, ax in enumerate(axes[0::2]):
        ax.set_yticks(np.arange(3))

        ax.set_yticklabels(["Profit\nmax.", "Difference\nmax.", "Tacit\ncollusion"],
                           fontsize=tick_fontsize)
        ax.set_ylabel(["$r = 0.25$", "$r = 0.50$"][i], fontsize=14)

    # For colorbar
    g = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=3, ncols=3, subplot_spec=root_gs[0, 1],
                                                    height_ratios=[0.2, 1, 0.2],
                                                    width_ratios=[0.2, 0.8, 0.1])

    cax = plt.subplot(g[1, 1])
    plt.colorbar(im, ticks=(-1, 0, 1), cax=cax),  # cax=cax)
    cax.tick_params(labelsize=10)
    cax.set_ylabel(ylabel="$R_{Pearson}$", fontsize=12)


# def main(force, do_it_again, ind_profiles):
#
#     # ----- Clustered figure -------- #
#
#     n_rows, n_cols = 1, 2
#
#     fig = plt.figure(figsize=(11, 4), dpi=200)
#     gs = matplotlib.gridspec.GridSpec(nrows=n_rows, ncols=n_cols, width_ratios=[1, 0.7])
#
#     # --------- Score distribution ---------------- #
#
#     plot_scores_distribution(data, subplot_spec=gs[0, 0])
#
#     # --------- Correlations --------------- #
#
#     corr = [np.corrcoef(d) for d in data]
#
#     plot_correlations(corr, subplot_spec=gs[0, 1])
#
#     # ----------- Fig ------------------ #
#
#     plt.tight_layout()
#
#     ax = fig.add_subplot(gs[:, :], zorder=-10)
#
#     plt.axis("off")
#     ax.text(
#         s="A", x=-0.06, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=20)
#     ax.text(
#         s="B", x=0.55, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=20)
#
#     plt.savefig("fig/fit.pdf")
#     plt.show()
#
#     # ----------- Stats ----------------- #
#
#     stats_and_table(fit_b)
#
#
# if __name__ == "__main__":
#
#     parser = argparse.ArgumentParser(description='Produce figures.')
#     parser.add_argument('-f', '--force', action="store_true", default=False,
#                         help="Re-import data")
#     parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
#                         help="Re-do analysis")
#
#     parser.add_argument('-i', '--ind_profiles', action="store_true", default=False,
#                         help="Draw individual profiles")
#
#     parsed_args = parser.parse_args()
#
#     main(force=parsed_args.force, do_it_again=parsed_args.do_it_again,
#          ind_profiles=parsed_args.ind_profiles)
