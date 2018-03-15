import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec
from hyperopt import fmin, tpe, hp

from backup import backup
from model import fit
import run_simulation

from analysis import ind_profiles
from analysis import customized_plot


class RoundProfiler:

    def __init__(self, strategies, const):

        self.const = const
        self.strategies = strategies

        self.means = {
            s: {
                0.25: {"price": 0, "score": 0, "distance": 0},
                0.5: {"price": 0, "score": 0, "distance": 0}
            } for s in strategies.values()
        }

        self.n_positions = 21

        self.compute_means()

    def compute_means(self):

        for s in self.strategies.values():

            file_name = "data/simulation_{}_vs_{}.p".format(*s)
            backups = backup.load(file_name)

            mean_score = np.zeros(len(backups))
            mean_distance = np.zeros(len(backups))
            mean_price = np.zeros(len(backups))
            r = np.zeros(len(backups))

            for i, b in enumerate(backups):

                mean_score[i] = np.mean(b.profits[:, :])

                d = np.absolute(
                    b.positions[:, 0] -
                    b.positions[:, 1]) / self.n_positions

                mean_distance[i] = np.mean(d)

                mean_price[i] = np.mean(b.prices[:, :])

                r[i] = b.r

            for radius in (0.25, 0.5):
                self.means[s][radius]["price"] = np.mean(mean_price[r == radius])
                self.means[s][radius]["distance"] = np.mean(mean_distance[r == radius])
                self.means[s][radius]["score"] = np.mean(mean_score[r == radius])

    def score(self, r, means, strategy):

        d = {}

        for k, v in means.items():

            d[k] = abs(self.means[strategy][r][k] - v)

        return (self.const - d["distance"] - d["price"] - d["score"]) / self.const


class BackupRoundProfiler:

    def __init__(self, size, strategies):

        self.display_opponent_score = np.zeros(size, dtype=bool)
        self.r = np.zeros(int(size/2))
        self.firm_id = np.zeros(size, dtype=int)
        self.user_id = np.zeros(size, dtype=int)
        self.room_id = np.zeros(size, dtype=int)
        self.round_id = np.zeros(size, dtype=int)
        self.score = np.zeros(size, dtype=int)

        self.fit_scores = np.zeros((int(size/2), len(strategies)), dtype=float)


def get_all_backup_round_profiler(force, strategies):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    profiler = RoundProfiler(strategies=strategies, const=100)

    profiler_backup = BackupRoundProfiler(size=len(backups*2), strategies=strategies)

    tqdm.write("Profiling rounds...")
    with tqdm(total=len(backups*2)) as pbar:

        i = 0

        for rd_idx, b in enumerate(backups):

            for player in (0, 1):

                # Register information
                profiler_backup.display_opponent_score[i] = b.display_opponent_score
                profiler_backup.score[i] = np.sum(b.profits[:, player])
                profiler_backup.user_id[i] = b.user_id[player]
                profiler_backup.room_id[i] = b.room_id
                profiler_backup.round_id[i] = b.round_id
                profiler_backup.firm_id[i] = player

                i += 1

                pbar.update()

            # save round's radius
            profiler_backup.r[rd_idx] = b.r

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

    # get all strategies
    s = list(run_simulation.treat_args("all"))
    # store strategies
    strategies = {k: v for k, v in zip(range(len(s)), s) if v in [("profit", "profit"), ("profit", "competition")]}

    file_name = "data/round_profiler_all.p"

    if not os.path.exists(file_name) or args.do_it_again:

        backups = get_all_backup_round_profiler(args.force, strategies)
        backup.save(obj=backups, file_name=file_name)

    else:
        backups = backup.load(file_name=file_name)

    return backups, strategies


def main(args):

    bkup, strategies = get_profile_all(args)
    individual_plot(bkup, strategies)

    # general_plot(bkup, strategies)


def individual_plot(bkup, strategies):

    labels = [v for k, v in sorted(strategies.items())]

    data = bkup.fit_scores[bkup.r == 0.25]

    n_cols = 10
    n_rows = len(data) / n_cols

    assert n_cols * n_rows == len(data)

    n_rows = int(n_rows)

    ind_profiles.plot(
        data=data,
        labels=labels,
        n_dim=len(labels),
        n_cols=n_cols,
        n_rows=n_rows,
        title="0.25",
        colors=["C{}".format(i) for i in range(len(labels))]
    )

    ind_profiles.save("fig/rounds_over_strategies.pdf")


# def general_plot(bkup, strategies):







if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")

    parsed_args = parser.parse_args()

    main(parsed_args)
