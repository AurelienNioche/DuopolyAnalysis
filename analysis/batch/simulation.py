import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec

from . import customized_plot


def plot(batch_backup, subplot_spec):

    # ----------------- Data ------------------- #

    # Look at the parameters
    n_simulations = len(batch_backup.backups)
    n_positions = batch_backup.parameters["n_positions"]

    # Containers
    d = np.zeros(n_simulations)
    prices = np.zeros(n_simulations)
    scores = np.zeros(n_simulations)
    r = np.zeros(n_simulations)

    for i, b in enumerate(batch_backup.backups):

        # Compute the mean distance between the two firms
        data = np.absolute(
            b.positions[:, 0] -
            b.positions[:, 1]) / n_positions

        d[i] = np.mean(data)

        # Compute the mean price
        prices[i] = np.mean(b.prices[:, :])

        # Compute the mean profit
        scores[i] = np.mean(b.profits[:, :])

        r[i] = b.parameters.r

    # ---------- Plot ----------------------------- #

    n_rows, n_cols = 3, 1

    gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
        nrows=n_rows, ncols=n_cols, subplot_spec=subplot_spec, wspace=0.5)

    ax_distance = plt.subplot(gs[0, 0])
    ax_price = plt.subplot(gs[1, 0])
    ax_profit = plt.subplot(gs[2, 0])

    # y_labels = "Distance", "Price", "Profit"
    y_limits = (0, 1), (1, 11), (0, 120)
    arr = (d, prices, scores)
    axes = [ax_distance, ax_price, ax_profit]

    for i, ax in enumerate(axes):
        ax.set_axisbelow(True)

        # Violin plot
        data = [arr[i][r == r_value] for r_value in (0.25, 0.50)]
        color = ['C0' if r_value == 0.25 else 'C1' for r_value in (0.25, 0.50)]

        customized_plot.violin(ax=ax, data=data, color=color, edgecolor="white", alpha=0.8)  # color, alpha=0.5)

        # ax.text(-0.35, 0.5, y_labels[i], rotation="vertical", verticalalignment='center',
        #         horizontalalignment='center', transform=ax.transAxes, fontsize=12)

        # ax.set_ylabel(y_labels[i])

        # ax.set
        # ax.tick_params(axis="y", labelsize=9)
        ax.set_ylim(*y_limits[i])

        ax.set_xticklabels(["{:.2f}".format(i) for i in (0.25, 0.50)])
        # ax.set_xlabel("$r$")

    axes[0].set_yticks(np.arange(0, 1.1, 0.25))
    axes[1].set_yticks(np.arange(1, 11.1, 2))

    for ax in axes[:2]:
        ax.tick_params(length=0, axis="x")
        ax.set_xticklabels([])

    for ax in axes:
        ax.tick_params(length=0, axis='y')
        ax.set_yticklabels([])

    axes[2].set_xlabel("$r$")

