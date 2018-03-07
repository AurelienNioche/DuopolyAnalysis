import numpy as np
from scipy.stats import mannwhitneyu


def boxplot(backups, ax, y, content=""):

    different_r = list(np.unique([b.parameters.r for b in backups]))

    to_plot = tuple([[] for i in range(len(different_r))])

    for i, b in enumerate(backups):
        cond = different_r.index(b.parameters.r)
        to_plot[cond].append(y[i])

    bp = ax.boxplot(to_plot, positions=different_r)
    for e in ['boxes', 'caps', 'whiskers']:
        for b in bp[e]:
            b.set_alpha(0.5)

    if len(to_plot) == 2:
        u, p = mannwhitneyu(to_plot[0], to_plot[1])
        print("Mann-Whitney rank test for {}: \nu {}, p {}".format(content, u, p))
