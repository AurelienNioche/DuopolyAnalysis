import os
import numpy as np
import argparse

from backup import backup
from analyse import load_data_from_db

from model import model


def fit(pool_backup):

    parameters = pool_backup.parameters
    backups = pool_backup.backups

    t_max = parameters.t_max

    summary = []

    ps = []
    cs = []
    rs = []
    scores = []

    m = {
        0.25: model.Model(r=0.25),
        0.50: model.Model(r=0.5)
    }

    temp = 0.01

    for b in backups:
        if b.pvp:
            param = b.parameters

            positions = b.positions
            prices = b.prices
            r = param.r

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

                ps.append(p)
                cs.append(c)
                rs.append("C0" if r == 0.25 else "C1")

                scores.append(np.sum(b.profits[:, player]))

                print("profit: {:.2f}".format(p))
                print("best: {:.2f}".format(c))
                best_fit = "BEST" if c > p else "PROFIT"
                summary.append(best_fit)
                print(best_fit)
                print()

    print(summary.count("BEST"), "vs", summary.count("PROFIT"))
    from pylab import plt

    scores = np.array(scores)
    rel_scores = scores / max(scores)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(ps, cs, alpha=0.5, c=rs, s=np.square(rel_scores)*100)
    plt.xlabel("Profit-based prediction")
    plt.ylabel("Competition-based prediction")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect(1)
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

    if not os.path.exists("data/data.p") or force:
        pool_backup = load_data_from_db()

    else:
        pool_backup = backup.PoolBackup.load()

    fit(pool_backup)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)

