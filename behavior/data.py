import numpy as np

from behavior import backup


def get(force=False):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    # ----------------- Data ------------------- #

    # Look at the parameters
    n_simulations = len(backups)
    n_positions = backups[0].n_positions

    # Containers
    dist = np.zeros(n_simulations)
    prices = np.zeros(n_simulations)
    scores = np.zeros(n_simulations)
    r = np.zeros(n_simulations)
    s = np.zeros(n_simulations, dtype=bool)

    for i, b in enumerate(backups):
        # Compute the mean distance between the two firms
        data = np.absolute(
            b.positions[:, 0] -
            b.positions[:, 1]) / n_positions

        dist[i] = np.mean(data)

        # Compute the mean price
        prices[i] = np.mean(b.prices[:, :])

        # Compute the mean profit
        scores[i] = np.mean(b.profits[:, :])

        r[i] = b.r
        s[i] = b.display_opponent_score

    return r, s, dist, prices, scores
