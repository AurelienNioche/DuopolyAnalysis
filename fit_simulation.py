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


class BackupFit:

    def __init__(self, temp_c, temp_p, prediction_accuracy_c,
                 prediction_accuracy_p, r, score, strategy, idx_strategy):

        self.temp_c = temp_c
        self.prediction_accuracy_c = prediction_accuracy_c

        self.temp_p = temp_p
        self.prediction_accuracy_p = prediction_accuracy_p

        self.r = r
        self.score = score
        self.strategy = strategy
        self.idx_strategy = idx_strategy


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


def get_fit(force, p0_strategy, p1_strategy, reversed_strategies=None, optimize_temp=False):

    file_name = "data/simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    if not os.path.exists(file_name) or force:

        run_simulation.main(
            p0_strategy=p0_strategy,
            p1_strategy=p1_strategy
        )

    backups = backup.load(file_name)

    m = {
        0.25: fit.Model(r=0.25),
        0.50: fit.Model(r=0.5)
    }

    temp_c = []
    prediction_accuracy_c = []

    temp_p = []
    prediction_accuracy_p = []

    r = []
    score = []
    strategy = []
    idx_strategy = []

    tqdm.write("Creating fit backup file...")

    for b in tqdm(backups):

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

            if not optimize_temp:

                # --- Profit based ---- #

                rm = RunModel(**kwargs)
                p = rm.run(temp=None) * -1

                temp_p.append(-1)
                prediction_accuracy_p.append(p)

                # --- Competition based --- #

                kwargs["str_method"] = "p_competition"

                rm = RunModel(**kwargs)
                c = rm.run(temp=None) * -1

                temp_c.append(-1)
                prediction_accuracy_c.append(c)

            else:

                # --- Profit based ---- #

                best_temp = optimize_model(**kwargs)

                rm = RunModel(**kwargs)
                p = rm.run(temp=best_temp) * -1

                temp_p.append(best_temp)
                prediction_accuracy_p.append(p)

                # --- Competition based --- #

                kwargs["str_method"] = "p_competition"

                best_temp = optimize_model(**kwargs)
                rm = RunModel(**kwargs)
                c = rm.run(temp=best_temp) * -1

                temp_c.append(best_temp)
                prediction_accuracy_c.append(c)

            r.append(b.r)
            score.append(np.sum(b.profits[:, player]))
            strategy.append(p0_strategy if not player else p1_strategy)
            if reversed_strategies:
                idx_strategy.append(reversed_strategies[(p0_strategy, p1_strategy)])

    fit_b = BackupFit(
        temp_c=np.array(temp_c),
        temp_p=np.array(temp_p),
        prediction_accuracy_p=np.array(prediction_accuracy_p),
        prediction_accuracy_c=np.array(prediction_accuracy_c),
        r=np.array(r),
        score=np.array(score),
        strategy=np.array(strategy),
        idx_strategy=np.array(idx_strategy)
    )

    file_name = "data/fit_simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    backup.save(fit_b, file_name)

    return fit_b


def get_fit_b_all(args):

    # get all strategies
    s = list(run_simulation.treat_args("all"))
    # store strategies
    strategies = {k: v for k, v in zip(range(len(s)), s)}
    reversed_strategies = {k: v for v, k in strategies.items()}

    file_name = "data/fit_simulation_all.p"

    if not os.path.exists(file_name) or args.force:

        backups = []

        for strategy in strategies.values():

            args.p0_strategy, args.p1_strategy = strategy
            backups.append(
                get_fit(args.force, args.p0_strategy, args.p1_strategy, reversed_strategies)
            )

        backup.save(obj=backups, file_name=file_name)

    else:
        backups = backup.load(file_name=file_name)

    return backups, strategies


def plot_all(backups, strategies):

    iter_backups = iter(backups)

    plt.figure(figsize=(6, 10))

    nrows = 3
    ncols = 2

    gs = matplotlib.gridspec.GridSpec(nrows=nrows, ncols=ncols)

    for x in range(nrows):

        for y in range(ncols):

            fit_b = next(iter_backups)
            p0_strategy, p1_strategy = strategies[fit_b.idx_strategy[0]]

            xlabel = x == nrows - 1
            ylabel = not y

            plot(fit_b, p0_strategy, p1_strategy, xlabel=xlabel, ylabel=ylabel, plot_position=gs[x, y])

    plt.tight_layout()
    plt.savefig("fig/simulation_fit_all.pdf")
    plt.show()


def get_fit_b_ind(args):

    file_name = "data/fit_simulation_{}_vs_{}.p".format(args.p0_strategy, args.p1_strategy)
    if not os.path.exists(file_name) or args.force:
        fit_b = get_fit(args.force, args.p0_strategy, args.p1_strategy)
    else:
        fit_b = backup.load(file_name)

    return fit_b


def plot_individual(fit_b, args):

    plot(fit_b, args.p0_strategy, args.p1_strategy, xlabel=True, ylabel=True)
    plt.tight_layout()
    plt.savefig("fig/simulation_fit_{}_vs_{}.pdf".format(args.p0_strategy, args.p1_strategy))
    plt.show()


def plot(fit_b, p0_strategy, p1_strategy, xlabel, ylabel, plot_position=None):

    x = fit_b.prediction_accuracy_p
    y = fit_b.prediction_accuracy_c

    colors = np.array(["C0" if i == 0.25 else "C1" for i in fit_b.r])
    markers = np.array(["${}$".format(i[0]) for i in fit_b.strategy])

    sizes = np.ones(len(colors)) * 25

    if plot_position:
        ax = plt.subplot(plot_position)
    else:
        ax = plt.gca()

    for m in np.unique(markers):
        ax.scatter(x[markers == m], y[markers == m],
                   alpha=0.5, c=colors[markers == m],
                   s=sizes[markers == m], marker=m)

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="${}$".format(p0_strategy[0]),
               label="r = .25, player = {}".format(p0_strategy))

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C0", marker="${}$".format(p1_strategy[0]),
               label="r = .25, player = {}".format(p1_strategy))

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="${}$".format(p0_strategy[0]),
               label="r = .50, player = {}".format(p0_strategy))

    ax.scatter((-1, ), (-1, ), alpha=0.5, c="C1", marker="${}$".format(p1_strategy[0]),
               label="r = .50, player = {}".format(p1_strategy))

    if xlabel:
        ax.set_xlabel("Profit-based fit accuracy")
    else:
        ax.set_xticks([])

    if ylabel:
        ax.set_ylabel("Competition-based fit accuracy")
    else:
        ax.set_yticks([])

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect(1)
    ax.legend(loc="upper right", fontsize=5)


def main(args):

    if args.all:
        backups, strategies = get_fit_b_all(args)
        plot_all(backups, strategies)
    else:
        run_simulation.treat_args(args.p0_strategy, args.p1_strategy)
        fit_b = get_fit_b_ind(args)
        plot_individual(fit_b, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")

    parser.add_argument('-a', '--all', action="store_true", default=False,
                        help="Fit all combined strategies.")

    parser.add_argument(
        '-p0', action='store',
        dest='p0_strategy',
        help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument(
        '-p1', action='store',
        dest='p1_strategy',
        help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    main(parsed_args)