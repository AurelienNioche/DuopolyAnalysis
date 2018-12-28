# Django specific settings
import os
import pickle
import numpy as np
import linearmodels as lm
import scipy.stats

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# Ensure settings are read
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
# Your application specific imports
from game.models import User, Room
import fit.data
import behavior.data
import behavior.demographics
from make_figs import simulation_fig


def load(fname):
    with open(f'data/{fname}', 'rb') as f:
        return pickle.load(f)


def save(obj, fname):
    with open(f'data/{fname}', 'wb') as f:
        return pickle.dump(obj=obj, file=f)


def kruskal():

    fit_bkup = load('fit.p')
    user_bkup = load('user.p')

    # ----- age ----------------------------------------------------------- #

    bnds = [(i, i+14) for i in range(15, 61, 15)]

    for h in ('max_profit', 'max_diff', 'equal_sharing'):

        samples = []

        for b in bnds:
            samples += [
                fit_bkup.fit_scores[h][
                np.array(user_bkup.age >= b[0]) * np.array(user_bkup.age <= b[1])
            ], ]

        print(scipy.stats.kruskal(*samples))


if __name__ == '__main__':
    kruskal()