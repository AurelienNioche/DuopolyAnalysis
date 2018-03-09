import os
import numpy as np
import argparse

from backup import backup
from analyse import load_data_from_db

from model import model


def fit(backups):

    t_max = backups[0].t_max

    summary = []

    x = []
    y = []
    colors = []
    markers = []

    scores = []

    m = {
        0.25: model.Model(r=0.25),
        0.50: model.Model(r=0.5)
    }

    temp = 0.005

    for b in backups:
        if b.pvp:

            positions = b.positions
            prices = b.prices
            r = b.r

            for player in (0, 1):

                delta_profit = []
                delta_competition = []

                opp = (player + 1) % 2
                player_active = b.active_player_t0

                for t in range(t_max):

                    if player_active == player:

                        p_compet = m[r].p_competition(
                            player_position=positions[t, player], player_price=prices[t, player],
                            opp_position=positions[t, opp], opp_price=prices[t, opp], temp=temp
                        )
                        p_profit = m[r].p_profit(
                            player_position=positions[t, player], player_price=prices[t, player],
                            opp_position=positions[t, opp], opp_price=prices[t, opp], temp=temp
                        )

                        delta_profit.append(p_profit)
                        delta_competition.append(p_compet)

                    player_active = (player_active + 1) % 2

                p = np.mean(delta_profit)
                c = np.mean(delta_competition)

                x.append(p)
                y.append(c)

                colors.append("C0" if r == 0.25 else "C1")

                scores.append(np.sum(b.profits[:, player]))

                markers.append("o" if b.display_opponent_score else "x")

                print("profit: {:.2f}".format(p))
                print("best: {:.2f}".format(c))
                best_fit = "BEST" if c > p else "PROFIT"
                summary.append(best_fit)
                print(best_fit)
                print()

    print(summary.count("BEST"), "vs", summary.count("PROFIT"))
    from pylab import plt

    x = np.array(x)
    y = np.array(y)
    colors = np.array(colors)
    markers = np.array(markers)
    sizes = np.ones(len(colors)) * 25  # np.square(scores / max(scores)) * 100

    fig = plt.figure()
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
    plt.tight_layout()
    ax.legend()
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

    if not os.path.exists("data/data.p") or force:

        backups = load_data_from_db()

    else:
        backups = backup.load()

    fit(backups)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)

