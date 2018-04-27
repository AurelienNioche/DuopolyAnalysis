import numpy as np

import os
import itertools as it

from fit import compute
from fit import score

from behavior import backup


def get(force=False):

    if not os.path.exists("data/fit.p") or force:
        fit_b = compute.get_fit(force)

    else:
        fit_b = backup.load("data/fit.p")

    r_values = np.sort(np.unique(fit_b.r))
    s_values = (False, True)

    exp_conditions = list(it.product(r_values, s_values))

    data = []

    scores_to_plot = score.Score.names  # fit.Score.names
    n_dim = len(scores_to_plot)

    for r_value, s_value in exp_conditions:

        cond0 = fit_b.r == r_value
        cond1 = fit_b.display_opponent_score == int(s_value)

        cond = cond0 * cond1

        n = np.sum(cond)

        d = np.zeros((n_dim, n))

        for i, sc in enumerate(scores_to_plot):
            d[i] = fit_b.fit_scores[sc][cond]

        data.append(d)

    return data
