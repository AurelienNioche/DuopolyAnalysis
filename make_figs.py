import matplotlib.gridspec
import matplotlib.pyplot as plt

import numpy as np

import fit.fig
import fit.data

import behavior.fig
import behavior.data

from fit.compute import BackupFit  # Needed by pickle


def main():

    fit_data = fit.data.get()
    behavior_data = behavior.data.get()

    # --------- Clustered figure ------------------ #

    n_rows, n_cols = 2, 1

    fig = plt.figure(figsize=(10, 8), dpi=200)
    gs = matplotlib.gridspec.GridSpec(nrows=n_rows, ncols=n_cols, height_ratios=[2, 1.])

    # ------------------ BEHAVIOR ---------------------- #

    gs_behavior = matplotlib.gridspec.GridSpecFromSubplotSpec(subplot_spec=gs[0, 0], ncols=1, nrows=1)
    behavior.fig.plot(data=behavior_data, subplot_spec=gs_behavior[0, 0])

    # ------------------- FIT ------------------------------ #

    gs_fit = matplotlib.gridspec.GridSpecFromSubplotSpec(subplot_spec=gs[1, 0], ncols=2, nrows=1, width_ratios=[1.1, 1])
    # GridSpec(nrows=n_rows, ncols=n_cols, width_ratios=[1, 0.7])

    # --------- Score distribution ---------------- #

    fit.fig.scores_distribution(fit_data, subplot_spec=gs_fit[0, 0])

    # --------- Correlations --------------- #

    corr = [np.corrcoef(d) for d in fit_data]

    fit.fig.correlations(corr, subplot_spec=gs_fit[0, 1])

    # --------- Numbering ------------------ #

    plt.tight_layout()
    # gs.tight_layout(fig)

    ax = fig.add_subplot(gs[:, :], zorder=-10)

    plt.axis("off")
    ax.text(
        s="A", x=-0.06, y=0.4, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    ax.text(
        s="B", x=-0.06, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="C", x=0.55, y=-0.1, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    plt.savefig("fig/fit.pdf")
    plt.show()


if __name__ == "__main__":
    main()
