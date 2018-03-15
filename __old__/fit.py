import os
import numpy as np
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec
from hyperopt import fmin, tpe, hp
from scipy.stats import mannwhitneyu

from backup import backup
from model import fit
from analysis import customized_plot


class BackupFit:

    def __init__(self, temp_c, temp_p, prediction_accuracy_c,
                 prediction_accuracy_p, r, display_opponent_score, score,
                 firm_id, user_id, room_id, round_id):

        self.temp_c = temp_c
        self.prediction_accuracy_c = prediction_accuracy_c

        self.temp_p = temp_p
        self.prediction_accuracy_p = prediction_accuracy_p

        self.display_opponent_score = display_opponent_score
        self.r = r
        self.score = score
        self.firm_id = firm_id
        self.user_id = user_id
        self.room_id = room_id
        self.round_id = round_id


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


def get_fit(force, softmax):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    m = {
        0.25: fit.Model(r=0.25),
        0.50: fit.Model(r=0.5)
    }

    temp_c = []
    prediction_accuracy_c = []

    temp_p = []
    prediction_accuracy_p = []

    display_opponent_score = []
    r = []
    score = []
    firm_id = []
    room_id = []
    round_id = []
    user_id = []

    with tqdm(total=len(backups*2)) as pbar:
        for b in backups:

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

                if not softmax:

                    # --- Profit based ---- #

                    rm = RunModel(**kwargs)
                    p = rm.run(temp=None) * -1

                    temp_p.append(-1)
                    prediction_accuracy_p.append(p)

                    tqdm.write("[Profit-based] p: {}".format(p))

                    # --- Competition based --- #

                    kwargs["str_method"] = "p_competition"

                    rm = RunModel(**kwargs)
                    c = rm.run(temp=None) * -1

                    tqdm.write("[Competition-based] c: {}".format(c))

                    temp_c.append(-1)
                    prediction_accuracy_c.append(c)

                    # ---- Profit strategic -------- #

                    kwargs["str_method"] = "p_profit_strategic"

                    rm = RunModel(**kwargs)
                    p = rm.run(temp=None) * -1

                    tqdm.write("[Profit strategic-based] p: {}".format(p))
                    tqdm.write("***\n")

                else:

                    # --- Profit based ---- #

                    best_temp = optimize_model(**kwargs)

                    rm = RunModel(**kwargs)
                    p = rm.run(temp=best_temp) * -1

                    temp_p.append(best_temp)
                    prediction_accuracy_p.append(p)

                    tqdm.write("[Profit-based] temp: {}, p: {}".format(best_temp, p))

                    # --- Competition based --- #

                    kwargs["str_method"] = "p_competition"

                    best_temp = optimize_model(**kwargs)
                    rm = RunModel(**kwargs)
                    c = rm.run(temp=best_temp) * -1

                    temp_c.append(best_temp)
                    prediction_accuracy_c.append(c)

                    tqdm.write("[Competition-based] temp: {}, c: {}".format(best_temp, c))

                display_opponent_score.append(b.display_opponent_score)
                r.append(b.r)
                score.append(np.sum(b.profits[:, player]))
                firm_id.append(player)
                room_id.append(b.room_id)
                round_id.append(b.round_id)
                user_id.append(b.user_id[player])

                pbar.update(1)

    fit_b = BackupFit(
        temp_c=np.array(temp_c),
        temp_p=np.array(temp_p),
        prediction_accuracy_p=np.array(prediction_accuracy_p),
        prediction_accuracy_c=np.array(prediction_accuracy_c),
        display_opponent_score=np.array(display_opponent_score),
        r=np.array(r),
        score=np.array(score),
        firm_id=np.array(firm_id),
        user_id=np.array(user_id),
        room_id=np.array(room_id),
        round_id=np.array(round_id)
    )

    backup.save(fit_b, "data/fit.p")

    return fit_b


def main(force, do_it_again, softmax):

    if not os.path.exists("data/fit.p") or do_it_again or force:
        fit_b = get_fit(force, softmax)

    else:
        fit_b = backup.load("data/fit.p")

    x = fit_b.prediction_accuracy_p
    y = fit_b.prediction_accuracy_c

    colors = np.array(["C0" if i == 0.25 else "C1" for i in fit_b.r])
    markers = np.array(["o" if i else "x" for i in fit_b.display_opponent_score])

    sizes = np.ones(len(colors)) * 25  # np.square(scores / max(scores)) * 100

    fig = plt.figure(figsize=(11, 4.5))

    gs = matplotlib.gridspec.GridSpec(1, 2, width_ratios=(1, 1.35))

    ax = fig.add_subplot(gs[0, 0])

    for m in np.unique(markers):
        ax.scatter(x[markers == m], y[markers == m],
                   alpha=0.5, c=colors[markers == m],
                   s=sizes[markers == m], marker=m)

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="o", label="r = .25, s = 1")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="x", label="r = .25, s = 0")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="o", label="r = .50, s = 1")
    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="x", label="r = .50, s = 0")
    plt.xlabel("Profit-based fit accuracy")
    plt.ylabel("Competition-based fit accuracy")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect(1)
    ax.legend(bbox_to_anchor=(0.65, 0.6))

    # --------------------------------------------- #

    sub_gs = matplotlib.gridspec.GridSpecFromSubplotSpec(
        subplot_spec=gs[0, 1], nrows=2, ncols=2, hspace=0, wspace=0.1)

    ax1 = fig.add_subplot(sub_gs[0, 0])
    ax2 = fig.add_subplot(sub_gs[0, 1])
    ax3 = fig.add_subplot(sub_gs[1, 0])
    ax4 = fig.add_subplot(sub_gs[1, 1])

    # Number 'sub-figures'
    ax.text(-0.2, -0.15, "A", fontsize=20)
    ax3.text(0.2, -0.35,  "B", fontsize=20)

    for prediction_accuracy, y_label, ax, r, in zip(
            (fit_b.prediction_accuracy_c,  fit_b.prediction_accuracy_c,
             fit_b.prediction_accuracy_p, fit_b.prediction_accuracy_p),
            ("Competition", "Competition", "Profit", "Profit"),
            (ax1, ax2, ax3, ax4),
            (0.25, 0.50, 0.25, 0.50)):

        # Violin plot
        s1_25 = (fit_b.r == r) * (fit_b.display_opponent_score == 1)
        s0_25 = (fit_b.r == r) * (fit_b.display_opponent_score == 0)

        to_plot = [
            prediction_accuracy[s0_25],
            prediction_accuracy[s1_25]
        ]

        color = "C0" if r == 0.25 else "C1"
        customized_plot.violin(data=to_plot, ax=ax, color=color, edgecolor=color, alpha=0.5)

        ax.set_ylim(-0.025, 1.025)

        ax.set_yticks(np.arange(0, 1.1, 0.25))
        ax.set_aspect(1)

        if len(to_plot) == 2:
            u, p = mannwhitneyu(to_plot[0], to_plot[1])
            print("[{}] Mann-Whitney rank test: u {}, p {}".format("Prediction {}-based r={}".format(y_label, r), u, p))

        if ax in (ax3, ax4):
            ax.set_xticklabels(["False", "True"])
            ax.set_xlabel("Display opponent score")
        else:
            ax.tick_params(length=0, axis="x")
            ax.set_xticklabels([])

        if ax in (ax1, ax3):
            ax.set_ylabel("{}-based\nfit accuracy".format(y_label))

        else:
            ax.tick_params(length=0, axis="y")
            ax.set_yticklabels([])

        if ax in (ax1, ax2):
            ax.set_title("r = {}\n".format(r))

    plt.tight_layout()

    plt.savefig("fig/fit.pdf")
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")
    parser.add_argument('-s', '--softmax', action="store_true", default=False,
                        help="Optmize using a softmax function")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force, do_it_again=parsed_args.do_it_again, softmax=parsed_args.softmax)