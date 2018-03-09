from pylab import np, plt
import os
import argparse

from analyse import load_data_from_db
from backup import backup


def main(force):

    if not os.path.exists("data/data.p") or force:
        backups = load_data_from_db()

    else:
        backups = backup.load()

    bins = np.arange(0, 3001, 300)

    bounds = ["{}~{}".format(i, j) for i, j in zip(bins[:-1], bins[1:])]

    fig = plt.figure(figsize=(12, 8))
    axes = fig.add_subplot(211), fig.add_subplot(212)

    for s, ax in zip((1, 0), axes):

        scores = {
            0.25: [],
            0.5: []
        }

        for b in backups:

            if b.pvp and b.display_opponent_score is bool(s):
                for player in (0, 1):
                    sum_profit = np.sum(b.profits[:, player])
                    scores[b.r].append(sum_profit)

        ind = np.arange(len(bins)-1)

        for r in (0.25, 0.50):

            sc = np.array(scores[r])

            d = np.digitize(sc, bins=bins)

            n = []

            for i in ind:

                n.append(len(sc[d == i]))

            width = 0.35  # the width of the bars

            print(len(n))
            print(len(ind))

            ax.bar(ind - width / 2 if r == 0.25 else ind+width/2, n, width, label='r = {:.2f}'.format(r))

        ax.set_xticks(ind)
        ax.set_xticklabels(bounds, fontsize=8)

        ax.set_ylim(0, 10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(length=0)
        ax.set_title('s = {}'.format(s))

    plt.tight_layout()
    plt.legend()
    plt.savefig("fig/pool_score_distribution.pdf")
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)