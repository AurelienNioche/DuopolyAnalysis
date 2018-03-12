import numpy as np
from scipy.stats import mannwhitneyu
import seaborn as sns


# def boxplot(backups, ax, y, content=""):
#
#     different_r = list(np.unique([b.parameters.r for b in backups]))
#
#     to_plot = tuple([[] for i in range(len(different_r))])
#
#     for i, b in enumerate(backups):
#         cond = different_r.index(b.parameters.r)
#         to_plot[cond].append(y[i])
#
#     bp = ax.boxplot(to_plot, positions=different_r)
#     for e in ['boxes', 'caps', 'whiskers']:
#         for b in bp[e]:
#             b.set_alpha(0.5)
#
#     if len(to_plot) == 2:
#         u, p = mannwhitneyu(to_plot[0], to_plot[1])
#         print("Mann-Whitney rank test for {}: \nu {}, p {}".format(content, u, p))
#
#     ax.set_xticks(np.arange(0, 1.1, 0.25))
#     ax.set_xlim(-0.01, 1.01)
#     ax.set_xticks(np.arange(0, 1.1, 0.25))
#     ax.set_xlabel("$r$")


def boxplot(backups, ax, y, attr, content=""):

    different_cond = \
        list(np.unique([getattr(b, attr) for b in backups]))  # Display opponent score can be true or false

    ticks_positions = np.arange(len(different_cond))

    to_plot = tuple([[] for i in range(len(different_cond))])

    for i, b in enumerate(backups):
        cond = different_cond.index(getattr(b, attr))
        to_plot[cond].append(y[i])

    bp = ax.boxplot(to_plot, positions=ticks_positions)
    for e in ['boxes', 'caps', 'whiskers']:
        for b in bp[e]:
            b.set_alpha(0.5)

    if len(to_plot) == 2:
        u, p = mannwhitneyu(to_plot[0], to_plot[1])
        print("[{}] Mann-Whitney rank test: u {}, p {}".format(content, u, p))

    ax.set_xticks(ticks_positions)
    ax.set_xticklabels([str(i) for i in different_cond])

    ax.set_xlabel(attr)


def violin(backups, ax, y, attr, content=""):

    different_cond = \
        list(np.unique([getattr(b, attr) for b in backups]))  # Display opponent score can be true or false

    ticks_positions = np.arange(len(different_cond))

    to_plot = [[] for i in range(len(different_cond))]

    for i, b in enumerate(backups):
        cond = different_cond.index(getattr(b, attr))
        to_plot[cond].append(y[i])

    sns.violinplot(data=to_plot, ax=ax, color="white", scale="count", cut=0)

    if len(to_plot) == 2:
        u, p = mannwhitneyu(to_plot[0], to_plot[1])
        print("[{}] Mann-Whitney rank test: u {}, p {}".format(content, u, p))

    ax.set_xticks(ticks_positions)
    ax.set_xticklabels([str(i) for i in different_cond])

    ax.set_xlabel(attr)
