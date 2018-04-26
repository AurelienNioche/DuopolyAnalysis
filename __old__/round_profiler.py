import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec

from backup import backup

from analysis import customized_plot

from __old__ import run_simulation


class RoundProfiler:

    def __init__(self, strategies, const, force):

        self.const = const
        self.strategies = strategies

        self.means = {
            s: {
                0.25: {"price": 0, "score": 0, "distance": 0},
                0.5: {"price": 0, "score": 0, "distance": 0}
            } for s in strategies.values()
        }

        self.n_positions = 21

        if force:
            self.run_simulations()

        self.compute_means()

    def run_simulations(self):

        for p0_strategy, p1_strategy in self.strategies.values():
            run_simulation.run(p0_strategy=p0_strategy, p1_strategy=p1_strategy)

    def compute_means(self):

        """
        computes means for all simulations

        """

        for s in self.strategies.values():

            file_name = "data/simulation_{}_vs_{}.p".format(*s)
            backups = backup.load(file_name)

            mean_score = np.zeros(len(backups))
            mean_distance = np.zeros(len(backups))
            mean_price = np.zeros(len(backups))
            radius = np.zeros(len(backups))

            for i, b in enumerate(backups):

                mean_score[i] = np.mean(b.profits[:, :])

                d = np.absolute(
                    b.positions[:, 0] -
                    b.positions[:, 1]) / self.n_positions

                mean_distance[i] = np.mean(d)

                mean_price[i] = np.mean(b.prices[:, :])

                radius[i] = b.r

            for r in (0.25, 0.5):
                self.means[s][r]["price"] = np.mean(mean_price[radius == r])
                self.means[s][r]["distance"] = np.mean(mean_distance[radius == r])
                self.means[s][r]["score"] = np.mean(mean_score[radius == r])

    def score(self, r, means, strategy):

        """
        Returns a score representing how much
        a round fits a couple of strategies.

        """

        d = {}

        for k, v in means.items():
            d[k] = abs(self.means[strategy][r][k] - v)

        return (self.const - d["distance"] - d["price"] - d["score"]) / self.const


class BackupRoundProfiler:

    def __init__(self, size_player, size_round, strategies):

        self.display_opponent_score = np.zeros(size_round, dtype=bool)
        self.r = np.zeros(size_round)
        self.fit_scores = np.zeros((size_round, len(strategies)), dtype=float)

        self.firm_id = np.zeros(size_player, dtype=int)
        self.user_id = np.zeros(size_player, dtype=int)
        self.room_id = np.zeros(size_player, dtype=int)
        self.round_id = np.zeros(size_round, dtype=int)
        self.score = np.zeros(size_player, dtype=int)


def get_all_backup_round_profiler(force, strategies):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    profiler = RoundProfiler(strategies=strategies, const=200, force=force)

    profiler_backup = BackupRoundProfiler(
        size_player=len(backups*2),
        size_round=len(backups),
        strategies=strategies
    )

    tqdm.write("Profiling rounds...")

    with tqdm(total=len(backups*2)) as pbar:

        i = 0

        for rd_idx, b in enumerate(backups):

            for player in (0, 1):

                # Register information
                profiler_backup.score[i] = np.sum(b.profits[:, player])
                profiler_backup.user_id[i] = b.user_id[player]
                profiler_backup.room_id[i] = b.room_id
                profiler_backup.firm_id[i] = player

                i += 1

                pbar.update()

            # Save round's radius
            profiler_backup.round_id[rd_idx] = b.round_id
            profiler_backup.r[rd_idx] = b.r
            profiler_backup.display_opponent_score[rd_idx] = b.display_opponent_score

            # Prepare means to compare
            means = {
                "price": np.mean(b.prices[:, :]),
                "score": np.mean(b.profits[:, :]),
                "distance": np.mean(
                    np.absolute(
                        b.positions[:, 0] -
                        b.positions[:, 1]) / 21
                )
            }

            # Compare means with each strategies means
            for k, v in strategies.items():
                profiler_backup.fit_scores[rd_idx, k] = profiler.score(r=b.r, means=means, strategy=v)

    backup.save(profiler_backup, "data/round_profiler_all.p")

    return profiler_backup


def get_profile_all(args):

    strategies = {
        0: ("profit", "profit"),
        1: ("competition", "competition"),
    }

    file_name = "data/round_profiler_all.p"

    if not os.path.exists(file_name) or args.do_it_again:
        backups = get_all_backup_round_profiler(args.force, strategies)
        backup.save(obj=backups, file_name=file_name)

    else:
        backups = backup.load(file_name=file_name)

    return backups, strategies


# def individual_plot(bkup, strategies):
#
#     labels = [v for k, v in sorted(strategies.items())]
#
#     data = bkup.fit_scores[bkup.r == 0.25]
#     n_cols = 1
#
#     ind_profiles.plot(
#         data=data,
#         labels=labels,
#         n_dim=len(labels),
#         n_cols=n_cols,
#         title="0.25",
#         colors=["C{}".format(i) for i in range(len(labels))]
#     )


def individual_bar(bkup):

    plt.figure(figsize=(15, 10))

    gs = matplotlib.gridspec.GridSpec(1, 2)

    pos = iter([
        gs[0, 0],
        gs[0, 1]
    ])

    # ---------------------- 0.25 --------------------- #

    for r in (0.25, 0.5):

        ax = plt.subplot(next(pos))

        ids = bkup.round_id[bkup.r == r]
        fit_scores = bkup.fit_scores[bkup.r == r]

        values = (fit_scores[:, 0] / (fit_scores[:, 0] + fit_scores[:, 1])) - 0.5

        # Set ticks
        idx = np.argsort(values)
        values = values[idx]
        rd_id = ids[idx]
        labels_pos = np.arange(len(idx))
        ax.set_yticks(labels_pos)
        ax.set_yticklabels(rd_id)

        # Params
        ax.tick_params(length=0, axis="y")
        ax.set_xlim(-0.25, 0.25)

        # Hide frame
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Color for each profile
        color = ("C0", "C1")
        colors = np.zeros(len(values), dtype=(str, 2))
        colors[:] = color[0]
        colors[values > 0] = color[1]

        # Add text (player's profiles)
        ax.text(
            0.25,
            1,
            'Difference maximizer',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            color=color[0],
            fontweight="bold"
        )

        ax.text(
            0.75,
            1,
            'Profit maximizer',
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            color=color[1],
            fontweight="bold"
        )

        # Set round id color depending of player's profile
        for l, color in zip(ax.get_yticklabels(), colors):
            l.set_color(color)

        ax.set_title("r = {}".format(r), y=1.05)
        ax.barh(labels_pos, values, color=colors, edgecolor="white", alpha=0.8)

    plt.tight_layout()
    plt.show()


def general_plot(bkup, strategies):

    fig = plt.figure(figsize=(8, 5))

    nrows = 2
    ncols = 2

    gs = matplotlib.gridspec.GridSpec(nrows, ncols)

    axes = [fig.add_subplot(gs[x, y]) for x in range(nrows) for y in range(ncols)]

    display_score = (False, True, ) * ncols
    radius = (0.25, ) * ncols + (0.5, ) * ncols

    for ax, r, s in zip(axes, radius, display_score):

        data = [
            bkup.fit_scores[(bkup.r == r) * (bkup.display_opponent_score == s)][:, strategy]
            for strategy in sorted(strategies.keys())
        ]

        color = ["C{}".format(strategy + 1) for strategy in sorted(strategies.keys())]

        ax.set_ylim(0, 1)
        ax.set_title("r = {:.2f}, s = {}".format(r, int(s)))
        customized_plot.violin(ax=ax, data=data, color=color, alpha=0.8)

    for ax in axes[2:]:

        labels = []
        for k in sorted(strategies.keys()):
            if "competition" in strategies[k]:
                labels.append(
                    "{}\nvs\n{}".format(*strategies[k]).replace("competition", "distance")
                )
            else:
                labels.append("{}\nvs\n{}".format(*strategies[k]))
        ax.set_xticklabels(labels)
        ax.tick_params(length=0)

    for ax in axes[:2]:
        ax.set_xticks([])

    for ax in axes[::2]:
        ax.set_ylabel("Score")

    plt.tight_layout()
    plt.show()


def main(args):

    bkup, strategies = get_profile_all(args)
    individual_bar(bkup)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")

    # parser.add_argument('-id', action="store", default=None, help="Select round ids", nargs="+", type=int)

    parsed_args = parser.parse_args()

    main(parsed_args)
