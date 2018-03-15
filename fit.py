import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec
import itertools as it
# from hyperopt import fmin, tpe, hp
from scipy.stats import mannwhitneyu

from backup import backup
from model import fit
from analysis import ind_profiles
from analysis import customized_plot


class BackupFit:

    def __init__(self, size):

        self.display_opponent_score = np.zeros(size, dtype=bool)
        self.r = np.zeros(size)
        self.firm_id = np.zeros(size, dtype=int)
        self.user_id = np.zeros(size, dtype=int)
        self.room_id = np.zeros(size, dtype=int)
        self.round_id = np.zeros(size, dtype=int)
        self.score = np.zeros(size, dtype=int)

        self.fit_scores = {i: np.zeros(size) for i in fit.Score.names}


class RunModel:

    def __init__(self, dm_model, str_method, firm_id, active_player_t0, positions, prices, t_max):

        self.model = dm_model
        self.str_method = str_method
        self.firm_id = firm_id
        self.active_player_t0 = active_player_t0
        self.positions = positions
        self.prices = prices
        self.t_max = t_max

    def run(self):

        opp = (self.firm_id + 1) % 2
        player_active = self.active_player_t0

        scores = []

        for t in range(self.t_max):

            if player_active == self.firm_id:
                score = getattr(self.model, self.str_method)(
                    player_position=self.positions[t, self.firm_id], player_price=self.prices[t, self.firm_id],
                    opp_position=self.positions[t, opp], opp_price=self.prices[t, opp]
                )

                scores.append(score)

            player_active = (player_active + 1) % 2

        return np.mean(scores)


def get_fit(force):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    m = {
        0.25: fit.Score(r=0.25),
        0.50: fit.Score(r=0.5)
    }

    fit_backup = BackupFit(size=len(backups*2))

    with tqdm(total=len(backups*2)) as pbar:

        i = 0

        for b in backups:

            for player in (0, 1):

                # Register information
                fit_backup.display_opponent_score[i] = b.display_opponent_score
                fit_backup.r[i] = b.r
                fit_backup.score[i] = np.sum(b.profits[:, player])
                fit_backup.user_id[i] = b.user_id[player]
                fit_backup.room_id[i] = b.room_id
                fit_backup.round_id[i] = b.round_id
                fit_backup.firm_id[i] = player

                # Compute score
                kwargs = {
                    "dm_model": m[b.r],
                    "firm_id": player,
                    "active_player_t0": b.active_player_t0,
                    "positions": b.positions,
                    "prices": b.prices,
                    "t_max": b.t_max
                }

                for str_method in fit.Score.names:

                    rm = RunModel(**kwargs, str_method=str_method)
                    score = rm.run()
                    fit_backup.fit_scores[str_method][i] = score

                    tqdm.write("[id={}, r={:.2f}, s={}] [{}] score: {:.2f}".format(
                        i, b.r, int(b.display_opponent_score), str_method, score))

                i += 1
                pbar.update(1)

                tqdm.write("\n")

    backup.save(fit_backup, "data/fit.p")

    return fit_backup


def main(force, do_it_again):

    if not os.path.exists("data/fit.p") or do_it_again or force:
        fit_b = get_fit(force)

    else:
        fit_b = backup.load("data/fit.p")

    # --------- ind plot

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

    # ------------------------------------ #

    # colors = np.array(["C0" if i == 0.25 else "C1" for i in fit_b.r])
    # markers = np.array(["o" if i else "x" for i in fit_b.display_opponent_score])
    #
    # x = fit_b.fit_scores["profit"]
    # y = fit_b.fit_scores["competition"]
    #
    # sizes = np.ones(len(colors)) * 25  # np.square(scores / max(scores)) * 100
    #
    # fig = plt.figure(figsize=(4.5, 4.5))
    #
    # #gs = matplotlib.gridspec.GridSpec(1, 2, width_ratios=(1, 1.35))
    #
    # ax = fig.add_subplot(111)
    #
    # for m in np.unique(markers):
    #     ax.scatter(x[markers == m], y[markers == m],
    #                alpha=0.5, c=colors[markers == m],
    #                s=sizes[markers == m], marker=m)
    #
    # ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="o", label="r = .25, s = 1")
    # ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="x", label="r = .25, s = 0")
    # ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="o", label="r = .50, s = 1")
    # ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="x", label="r = .50, s = 0")
    # plt.xlabel("Profit-based fit accuracy")
    # plt.ylabel("Competition-based fit accuracy")
    # ax.set_xlim(-0.02, 1.02)
    # ax.set_ylim(-0.02, 1.02)
    # ax.set_aspect(1)
    # ax.legend(bbox_to_anchor=(0.65, 0.6))
    #
    # plt.show()

    # ------------------------------------ #
    plt.close()

    fig = plt.figure(figsize=(11, 5))

    gs = matplotlib.gridspec.GridSpec(2, 2)

    positions = it.product(range(2), repeat=2)

    scores_to_plot = ["profit", "competition"]  # fit.Score.names
    n_dim = len(scores_to_plot)

    colors = ["C{}".format(i+2) for i in range(n_dim)]

    axes = []

    for r_value in (0.25, 0.50):

        for s_value in (True, False):

            pos = next(positions)
            ax = fig.add_subplot(gs[pos[0], pos[1]])

            cond0 = fit_b.r == r_value
            cond1 = fit_b.display_opponent_score == int(s_value)

            cond = cond0 * cond1

            n = np.sum(cond)

            data = np.zeros((n_dim, n))

            for i, score in enumerate(scores_to_plot):
                data[i] = fit_b.fit_scores[score][cond]

            ax.set_title("r = {:.2f}, s = {}".format(r_value, int(s_value)))
            customized_plot.violin(data=data, ax=ax, color=colors,
                                   edgecolor="black")
            ax.set_ylim(0, 1)
            ax.set_yticks(np.arange(0, 1.1, 0.25))

            ax.tick_params(length=0, axis='x')
            axes.append(ax)

    for ax in axes[:-2]:
        ax.set_xticklabels([])

    for ax in axes[-2:]:
        ax.set_xticklabels(["Profit-maximization", "Difference-maximization"])

    for ax in axes[1::2]:
        ax.set_yticklabels([])
        ax.tick_params(length=0, axis="y")

    for ax in axes[0::2]:
        ax.set_ylabel("Score")

    plt.tight_layout()

    plt.savefig("fig/fit.pdf")
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")
    # parser.add_argument('-s', '--softmax', action="store_true", default=False,
    #                     help="Optmize using a softmax function")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force, do_it_again=parsed_args.do_it_again)
