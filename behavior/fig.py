import numpy as np

import matplotlib.gridspec
import matplotlib.pyplot as plt

from analysis.batch import customized_plot


def plot(data, subplot_spec):

    r, s, dist, prices, scores = data

    gs = matplotlib.gridspec.GridSpecFromSubplotSpec(nrows=3, ncols=1, subplot_spec=subplot_spec)

    axes = (
        plt.subplot(gs[0, 0]),
        plt.subplot(gs[1, 0]),
        plt.subplot(gs[2, 0])
    )

    y_labels = "Distance", "Price\n", "Profit\n"
    y_limits = (0, 1), (1, 11), (0, 120)

    # s_values = (0, 1, ) * 3

    arr = (dist, prices, scores)

    # axes[0].text(2, 1.3, "Display opponent score", fontsize=12)
    # axes[0].set_title("$s = 0$")
    # axes[1].set_title("$s = 1$")

    for idx in range(len(axes)):

        ax = axes[idx]

        ax.set_axisbelow(True)

        # Violin plot
        data = [arr[idx][(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        color = ['C0' if r_value == 0.25 else 'C1' for r_value in (0.25, 0.50)]

        print(data)

        customized_plot.violin(ax=ax, data=data, color=color, edgecolor="white", alpha=0.8)  # color, alpha=0.5)

    axes[0].set_yticks(np.arange(0, 1.1, 0.25))

    axes[1].set_yticks(np.arange(1, 11.1, 2))

    axes[2].set_yticks(np.arange(0, 121, 25))

    axes[2].set_xticklabels(["{:.2f}".format(i) for i in (0.25, 0.50)])
    axes[2].set_xlabel("$r$")

    for ax in axes[:2]:
        ax.tick_params(length=0, axis="x")
        ax.set_xticklabels([])

    for ax, y_label, y_lim in zip(axes, y_labels, y_limits):
        #ax.text(-0.35, 0.5, y_label, rotation="vertical", verticalalignment='center',
         #       horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        ax.set_ylabel(y_label)
        ax.tick_params(axis="y", labelsize=9)
        ax.set_ylim(y_lim)

    # for ax, y_lim in zip(axes, y_limits):
    #     ax.set_ylim(y_lim)
    #     ax.tick_params(length=0, axis="y")
    #     ax.set_yticklabels([])
