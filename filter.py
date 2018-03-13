import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import numpy as np
from tqdm import tqdm
import argparse
import matplotlib.gridspec
import matplotlib.pyplot as plt
from analysis import customized_plot

from game.models import Room, FirmProfit, RoundComposition, Round

from backup import backup


def get_filtered_data():

    backups = backup.load_data_from_db()

    means = {}
    means[0.25], means[0.5] = _get_random_bot_mean_profits()

    filtered_backups = []

    for b in backups:

        for player_id in (0, 1):

            cond = np.mean(b.profits[:, player_id]) > means[b.r]

            if cond:
                filtered_backups.append(b)

    return filtered_backups


def _get_random_bot_mean_profits():

    backups = backup.load(
        file_name="data/simulation_random_strategy_vs_profit_strategy.p")

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
    # excluded_rd = exclude()
    #
    # backups = backup.get_data(force)
    #
    # filtered_backups = []
    #
    # for b in backups:
    #     if b.round_id in excluded_rd:
    #         filtered_backups.append(b)
    #
    # # plots(filtered_backups)
    # # prices_and_profits.prices_and_profits(backups=filtered_backups, fig_name="fig/excluded/prices_and_profits.pdf")
    # print("N excluded players in 0.25 radius condition: ", len([b for b in filtered_backups if b.r == 0.25]))
    # print("N excluded players in 0.5 radius condition: ", len([b for b in filtered_backups if b.r == 0.5]))


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

    mean_05, mean_025 = _get_random_bot_mean_profits()
    arr_mean = ((mean_025, mean_05), ) * 2
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
            ax.axhline(arr_mean[idx][i], color='0.01', linewidth=0.7, linestyle="--",
                       zorder=1, xmin=xmins[i], xmax=xmaxs[i])

        # Violin plot
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
