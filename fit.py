import os
import numpy as np
import argparse
from tqdm import tqdm
from pylab import plt

from backup import backup
from analyse import load_data_from_db

from model import model
from hyperopt import fmin, tpe, hp


class BackupFit:

    def __init__(self, temp_c, temp_p, prediction_accuracy_c, prediction_accuracy_p, r, display_opponent_score, score):

        self.temp_c = temp_c
        self.prediction_accuracy_c = prediction_accuracy_c

        self.temp_p = temp_p
        self.prediction_accuracy_p = prediction_accuracy_p

        self.display_opponent_score = display_opponent_score
        self.r = r
        self.score = score


class RunModel:

    def __init__(self, dm_model, str_method, firm_id, active_player_t0, positions, prices, t_max):

        self.model = dm_model
        self.str_method = str_method
        self.firm_id = firm_id
        self.active_player_t0 = active_player_t0
        self.positions = positions
        self.prices = prices
        self.t_max = t_max

    def run(self, temp):

        opp = (self.firm_id + 1) % 2
        player_active = self.active_player_t0

        ps = []

        for t in range(self.t_max):

            if player_active == self.firm_id:
                p = getattr(self.model, self.str_method)(
                    player_position=self.positions[t, self.firm_id], player_price=self.prices[t, self.firm_id],
                    opp_position=self.positions[t, opp], opp_price=self.prices[t, opp], temp=temp
                )

                ps.append(p)

            player_active = (player_active + 1) % 2

        return -np.mean(ps)


def optimize_model(**kwargs):

    run_model = RunModel(**kwargs)

    best = fmin(fn=run_model.run,
                space=hp.uniform('temp', 0.0015, 0.2),
                algo=tpe.suggest,
                max_evals=100)

    return best["temp"]


def get_fit(force):

    m = {
        0.25: model.Model(r=0.25),
        0.50: model.Model(r=0.5)
    }

    if not os.path.exists("data/data.p") or force:

        backups = load_data_from_db()

    else:
        backups = backup.load()

    temp_c = []
    prediction_accuracy_c = []

    temp_p = []
    prediction_accuracy_p = []

    display_opponent_score = []
    r = []
    score = []

    for b in tqdm(backups):
        if b.pvp:

            for player in (0, 1):

                kwargs = {
                    "dm_model": m[b.r],
                    "str_method": "p_profit",
                    "firm_id": player,
                    "active_player_t0": b.active_player_t0,
                    "positions": b.positions,
                    "prices": b.prices,
                    "t_max": b.t_max
                }

                best_temp = optimize_model(**kwargs)

                rm = RunModel(**kwargs)
                p = rm.run(temp=best_temp) * -1

                temp_p.append(best_temp)
                prediction_accuracy_p.append(p)

                kwargs["str_method"] = "p_competition"

                best_temp = optimize_model(**kwargs)
                rm = RunModel(**kwargs)
                c = rm.run(temp=best_temp) * -1

                temp_c.append(best_temp)
                prediction_accuracy_c.append(c)

                display_opponent_score.append(b.display_opponent_score)
                r.append(b.r)
                score.append(np.sum(b.profits[:, player]))

    fit_b = BackupFit(
        temp_c=temp_c,
        temp_p=temp_p,
        prediction_accuracy_p=prediction_accuracy_p,
        prediction_accuracy_c=prediction_accuracy_c,
        display_opponent_score=display_opponent_score,
        r=r,
        score=score
    )

    backup.save(fit_b, "data/fit.p")

    return fit_b


def plot_fit(force):

    if not os.path.exists("data/fit.p") or force:
        fit_b = get_fit(force)

    else:
        fit_b = backup.load("data/fit.p")

    x = fit_b.prediction_accuracy_p
    y = fit_b.prediction_accuracy_c
    colors = ["C0" if i == 0.25 else "C1" for i in fit_b.r]
    markers = ["o" if i is True else "x" for i in fit_b.display_opponent_score]

    x = np.array(x)
    y = np.array(y)
    colors = np.array(colors)
    markers = np.array(markers)
    sizes = np.ones(len(colors)) * 25  # np.square(scores / max(scores)) * 100

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    for m in np.unique(markers):
        ax.scatter(x[markers == m], y[markers == m],
                   alpha=0.5, c=colors[markers == m],
                   s=sizes[markers == m], marker=m)

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="o", label="r = .25, s = 1")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="x", label="r = .25, s = 0")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="o", label="r = .50, s = 1")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="x", label="r = .50, s = 0")
    plt.xlabel("Profit-based prediction")
    plt.ylabel("Competition-based prediction")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect(1)
    ax.legend(bbox_to_anchor=(0.7, 0.5))

    plt.tight_layout()
    plt.savefig("fig/pool_prediction.pdf")
    plt.show()
    plt.close()

    # fig = plt.figure()
    # ax = fig.add_subplot(221)
    # ax.scatter(scores, ps, alpha=0.5, c=rs)
    # ax.set_xlabel("Score")
    # ax.set_ylabel("Profit-based prediction")
    #
    # ax = fig.add_subplot(222)
    # ax.scatter(scores, cs, alpha=0.5, c=rs)
    # ax.set_xlabel("Score")
    # ax.set_ylabel("Competition-based prediction")
    # # ax.set_ylim(-0.02, 1.02)
    # # ax.set_aspect(0.5)
    #
    # plt.tight_layout()
    # plt.savefig("fig/pool_prediction_against_score.pdf")
    # plt.show()


def main(force):

    plot_fit(force)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
