import os
import numpy as np

import behavior.backup

from fit import score, compute


def distance(positions):
    return np.mean(np.absolute(
        positions[:, 0] -
        positions[:, 1]) / 21)


def info_room(b):
    return "b: room_id {} round_id {} r {}, d {:.2f}, price {:.2f}, profit {:.2f}".format(
        b.room_id, b.round_id, b.r, distance(b.positions), np.mean(b.prices), np.mean(b.profits))


def get(force=False):

    backups = [b for b in behavior.backup.get_data(force) if b.pvp]

    if not os.path.exists("data/fit.p") or force:
        fit_b = compute.get_fit(force)

    else:
        fit_b = behavior.backup.load("data/fit.p")

    n = len(backups)

    # --------------- #

    user_id = np.zeros(n, dtype=int)
    firm_id = np.zeros(n, dtype=int)
    room_id = np.zeros(n, dtype=int)
    round_id = np.zeros(n, dtype=int)
    
    d = {i: np.zeros(n) for i in score.Score.names}

    r = np.zeros(n)

    for i, idx in enumerate(range(0, n * 2, 2)):

        assert fit_b.round_id[idx] == fit_b.round_id[idx+1]
        user_id[i] = fit_b.user_id[idx]
        firm_id[i] = fit_b.firm_id[idx]
        room_id[i] = fit_b.room_id[idx]
        round_id[i] = fit_b.round_id[idx]
        r[i] = fit_b.r[idx]

        for sc in d.keys():
            d[sc][i] = np.min(fit_b.fit_scores[sc][idx:idx+2])

    ex_cases = {sc: {} for sc in d.keys()}

    for sc in d.keys():
        for rv in 0.25, 0.50:
            # Profit maximizator r = 0.25 and r = 0.50
            idx = np.argmax(d[sc][r == rv])
            rd_id = round_id[r == rv][idx]
            b = [b for b in backups if b.round_id == rd_id][0]
            ex_cases[sc][str(int(rv*100))] = b

    return ex_cases
