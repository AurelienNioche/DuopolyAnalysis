import argparse
import os
import contextlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec

from backup import backup
import run_simulation
from analysis import customized_plot


@contextlib.contextmanager
def backup_safe_load(file_name, args):

    if not os.path.exists(file_name) or args.force:
        run_simulation.main(
            p0_strategy=args.p0_strategy,
            p1_strategy=args.p1_strategy
        )

    b = backup.load(file_name=file_name)
    yield b


def plot(backups, p0_strategy, p1_strategy):

    # ----------------- Data ------------------- #

    # Look at the parameters
    n_simulations = len(backups)
    n_positions = 21

    # Containers
    d = np.zeros(n_simulations)
    prices = np.zeros(n_simulations)
    scores = np.zeros(n_simulations)
    r = np.zeros(n_simulations)

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

    # ---------- Plot ----------------------------- #

    fig = plt.figure(figsize=(4, 7))

    sub_gs = matplotlib.gridspec.GridSpec(nrows=3, ncols=1)

    axes = (
        fig.add_subplot(sub_gs[0, 0]),
        fig.add_subplot(sub_gs[1, 0]),
        fig.add_subplot(sub_gs[2, 0]),
    )

    y_labels = "Distance", "Price", "Score"
    y_limits = (0, 1), (0.9, 11.1), (0, 120)

    arr = (d, prices, scores)

    for idx in range(len(axes)):

        ax = axes[idx]

        ax.set_axisbelow(True)

        # Violin plot
        data = [arr[idx][r == r_value] for r_value in (0.25, 0.50)]
        color = ['C0' if r_value == 0.25 else 'C1' for r_value in (0.25, 0.50)]

        customized_plot.violin(ax=ax, data=data, color=color, edgecolor=color, alpha=0.5)

    axes[-1].set_xticklabels(["{:.2f}".format(i) for i in (0.25, 0.50)])
    axes[-1].set_xlabel("r")

    for ax in (axes[:-1]):
        ax.set_xticklabels([])
        ax.tick_params(axis="x", length=0)

    for ax, y_label, y_lim in zip(axes[:], y_labels, y_limits):
        ax.set_ylabel(y_label)
        ax.set_ylim(y_lim)

    plt.tight_layout()

    plt.savefig("fig/main_simulation_{}_{}.pdf".format(p0_strategy, p1_strategy))
    plt.show()


def main(args):

    p0_strategy, p1_strategy = \
        run_simulation.treat_args(args.p0_strategy, args.p1_strategy)

    file_name = "data/simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    with backup_safe_load(file_name=file_name, args=args) as backups:
        plot(backups, p0_strategy, p1_strategy)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")

    parser.add_argument(
        '-p0', action='store',
        dest='p0_strategy',
        help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument(
        '-p1', action='store',
        dest='p1_strategy',
        help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    if parsed_args.force and \
            None in (parsed_args.p0_strategy, parsed_args.p1_strategy):
        exit("Please run the script with -h flag.")

    main(parsed_args)
