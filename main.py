import pickle
import numpy as np

import fit.data
import behavior.data
import behavior.stats
import behavior.backup
import behavior.demographics


def load(fname):
    with open(f'data/{fname}', 'rb') as f:
        return pickle.load(f)


def save(obj, fname):
    with open(f'data/{fname}', 'wb') as f:
        return pickle.dump(obj=obj, file=f)


def print_stats():

    behavior.stats.stats()


def make_counts():

    count = behavior.backup.get_count_data()
    return count


def compute_number_of_observations_xp_fit(force=False):
    # fit data structure = [ [[r=0.25, s=0] * n_heuristic],
    #                        [[r=0.25, s=1] * n_heuristic]],
    #                       [[r=0.5, s=0] * n_heuristic]],
    #                       [[r=0.5, s=1] * n_heuristic]] ]

    fit_data = fit.data.get_customized(force)

    count = {
        "r=0.25, s=0": len(fit_data[0][0]),
        "r=0.25_s=1": len(fit_data[1][0]),
        "r=0.5_s=0": len(fit_data[2][0]),
        "r=0.5_s=1": len(fit_data[3][0]),
        "total": sum([len(x[0]) for x in fit_data])
    }

    return count


def compute_number_of_observations_xp_behavior():
    # behavior data structure:
    # each variable (r, s, dist, price, profits)
    # len(variable) == number of subjects == 222
    # we use numpy array masks in order to select values
    # depending on conditions

    r, s, dist, price, profits = behavior.data.get()

    count = {
        "r=0.25, s=0": len(dist[(r == 0.25) * (s == 0)]),
        "r=0.25_s=1": len(dist[(r == 0.25) * (s == 1)]),
        "r=0.5_s=0": len(dist[(r == 0.5) * (s == 0)]),
        "r=0.5_s=1": len(dist[(r == 0.5) * (s == 1)]),
        "total": len(dist)
    }

    return count


def compute_remuneration():

    remuneration_data = behavior.backup.get_remuneration_data()
    v = list(remuneration_data.values())
    return {'mean': np.mean(v), 'std': np.std(v), 'n': len(v)}


def main():

    print('Subjects stats regarding selection:\n', make_counts(), '\n')
    print('Count of xp fit data (unit=subject)\n', compute_number_of_observations_xp_fit(), '\n')
    print('Count of xp behavior data (unit=room)\n', compute_number_of_observations_xp_behavior(), '\n')
    print('Subjects stats regarding remuneration:\n', compute_remuneration(), '\n')


if __name__ == "__main__":
    main()
