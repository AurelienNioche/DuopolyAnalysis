import argparse
from backup import backup
import contextlib
import numpy as np
import matplotlib.pyplot as plt

import run_simulation


# def plot_hist_scores_distribution(backups, fig_name):
#
#     bins = np.arange(0, 4000, 500)
#
#     bounds = ["{}~{}".format(i, j) for i, j in zip(bins[:-1], bins[1:])]
#
#     fig = plt.figure(figsize=(12, 8))
#     axes = fig.add_subplot(211), fig.add_subplot(212)
#
#     for r, ax in zip((0.25, 0.5), axes):
#
#         scores = {
#             0:  [],
#             1: []
#         }
#
#         for b in backups:
#
#             for player in (0, 1):
#                 if b.r == r:
#                     sum_profit = np.sum(b.profits[:, player])
#                     scores[player].append(sum_profit)
#
#         if np.max([max(i) for i in scores.values()]) > max(bins):
#             raise Exception("Max bound has been reached")
#
#         y_upper_bound = 100
#
#         ind = np.arange(len(bins)-1)
#
#         rects = [[], []]
#
#         for player, color in zip((0,  1), ("C0", "C1")):
#
#             sc = np.array(scores[player])
#
#             print("Score (r = {:.2f}, player = {}) mean: {:.2f}, std: {:.2f}, min:{}, max: {}"
#                   .format(r, player, np.mean(sc), np.std(sc), np.min(sc), np.max(sc)))
#
#             d = np.digitize(sc, bins=bins)
#
#             n = len(sc)
#
#             y = []
#             for i in ind:
#
#                 y.append(len(sc[d == i]) / n * 100)
#
#             if np.max(y) > y_upper_bound:
#                 raise Exception("Max bound has been reached ({:.2f} > {})"
#                                 .format(np.max(y), y_upper_bound))
#
#             width = 0.35  # the width of the bars
#
#             rect = ax.bar(ind - width / 2 if player == 0 else ind+width/2, y, width,
#                    label='player = '.format(player), alpha=0.8, edgecolor=color)
#
#             rects[player].append(rect)
#
#         ax.legend((rects[0][0], rects[1][0]), ('Player 0', 'Player 1'))
#
#         ax.set_xticks(ind)
#         ax.set_xticklabels(bounds, fontsize=8)
#
#         ax.set_ylim(0, y_upper_bound)
#
#         ax.set_ylabel("Proportion (%)")
#
#         ax.spines['top'].set_visible(False)
#         ax.spines['right'].set_visible(False)
#         ax.spines['bottom'].set_visible(False)
#         ax.tick_params(length=0)
#         ax.set_title('r = {}'.format(r))
#
#     plt.tight_layout()
#     plt.savefig(fig_name)
#

@contextlib.contextmanager
def backup_safe_load(file_name, args):

    try:

        b = None

        if args.force:
            run_simulation.main(
                p0_strategy=args.p0_strategy,
                p1_strategy=args.p1_strategy
            )

        b = backup.load(file_name=file_name)

    except (RuntimeError, FileNotFoundError):

        if not args.force:
            exit("File not found, use -f flag to generate new data.")
        else:
            exit("Something went wrong, new data were generated, but file loading failed.")

    finally:

        yield b


def main(args):

    p0_strategy, p1_strategy = \
        run_simulation.treat_args(args.p0_strategy, args.p1_strategy)

    file_name = "data/simulation_{}_vs_{}.p".format(p0_strategy, p1_strategy)

    with backup_safe_load(file_name=file_name, args=args) as backups:

        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")

    parser.add_argument('-p0', action='store',
                    dest='p0_strategy',
                    help='Strategy used by player 0 (competition/profit/random)')

    parser.add_argument('-p1', action='store',
                    dest='p1_strategy',
                    help='Strategy used by player 1 (competition/profit/random)')

    parsed_args = parser.parse_args()

    if parsed_args.force and \
            None in (parsed_args.p0_strategy, parsed_args.p1_strategy):
        exit("Please run the script with -h flag.")

    main(parsed_args)

