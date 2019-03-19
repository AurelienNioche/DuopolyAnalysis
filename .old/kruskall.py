import numpy as np
import scipy.stats


def kruskal(user_bkup, fit_bkup):

    x = np.asarray(fit_bkup.fit_scores)[user_bkup.gender == 'female']
    y = np.asarray(fit_bkup.fit_scores)[user_bkup.gender == 'male']

    print(scipy.stats.kruskal(x, y))
