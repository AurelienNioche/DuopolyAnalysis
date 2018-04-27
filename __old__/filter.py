import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import numpy as np
import argparse
import matplotlib.gridspec
import matplotlib.pyplot as plt
from analysis.batch import customized_plot

from behavior import backup


def save_filtered_data():

    backups = backup.load_data_from_db()

    means = {
        k: v for k, v in zip((0.25, 0.5), _get_bot_mean_profits("random", "profit"))
    }

    filtered_backups = []

    for b in backups:
        for player_id in (0, 1):
            cond = np.mean(b.profits[:, player_id]) > means[b.r]
            if cond:
                filtered_backups.append(b)

    backup.save(obj=filtered_backups, file_name="data/filtered_data.p")


def _get_bot_mean_profits(strategy0, strategy1):

    backups = backup.load(
        file_name="data/simulation_{}_strategy_vs_{}_strategy.p".format(strategy0, strategy1)
    )

    means = []

    for r in (0.25, 0.5):
        profits = []
        for b in backups:
            if b.r == r:
                profits.append(np.mean(b.profits[:, 0]))
        means.append(np.mean(profits))

    return means


def main(force):

    plot_violin_with_dashed_mean(force)


def plot_violin_with_dashed_mean(force):

    backups = backup.get_data(force)

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

    fig = plt.figure(figsize=(8, 4))

    sub_gs = matplotlib.gridspec.GridSpec(nrows=1, ncols=2)

    axes = (
        fig.add_subplot(sub_gs[0, 0]),
        fig.add_subplot(sub_gs[0, 1]),
    )

    s_values = (0, 1)
    r_values = (0.25, 0.5)

    arr = (scores, scores)

    mean_025_profit, mean_05_profit = _get_bot_mean_profits("profit", "profit")
    mean_025_comp, mean_05_comp = _get_bot_mean_profits("competition", "competition")
    arr_mean_profit = ((mean_025_profit, mean_05_profit), ) * 2
    arr_mean_comp = ((mean_025_comp, mean_05_comp), ) * 2
    xmins = (0.02, 0.6)
    xmaxs = (0.4, 0.98)

    plt.text(0.01, 140, "Display opponent score", fontsize=12)
    axes[0].set_title("\n\nFalse")
    axes[1].set_title("True")

    for idx in range(len(axes)):

        ax = axes[idx]

        ax.set_axisbelow(True)
        ax.set_ylim(0, 120)
        ax.set_ylabel("Score")
        ax.set_xticklabels(r_values)

        for i in range(2):
            ax.axhline(arr_mean_profit[idx][i], color='green', linewidth=1.2, linestyle="--",
                       label="Profit-based" if i == 0 else None,
                       zorder=1, xmin=xmins[i], xmax=xmaxs[i])

        for i in range(2):
            ax.axhline(arr_mean_comp[idx][i], color='red', linewidth=1.2, linestyle="--",
                       label="Competition-based" if i == 0 else None,
                       zorder=1, xmin=xmins[i], xmax=xmaxs[i])

        ax.legend()

        data = [arr[idx][(r == r_value) * (s == s_values[idx])] for r_value in (0.25, 0.50)]
        color = ['C0' if r_value == 0.25 else 'C1' for r_value in (0.25, 0.50)]

        customized_plot.violin(ax=ax, data=data, color=color, edgecolor=color, alpha=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
