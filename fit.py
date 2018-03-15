import os
import numpy as np
import argparse
from tqdm import tqdm
# import matplotlib.pyplot as plt
# import matplotlib.gridspec
# from hyperopt import fmin, tpe, hp
from scipy.stats import mannwhitneyu

from backup import backup
from model import fit
# from analysis import customized_plot


class BackupFit:

    def __init__(self, size):

        self.display_opponent_score = np.zeros(size, dtype=bool)
        self.r = np.zeros(size)
        self.firm_id = np.zeros(size, dtype=int)
        self.user_id = np.zeros(size, dtype=int)
        self.room_id = np.zeros(size, dtype=int)
        self.round_id = np.zeros(size, dtype=int)
        self.score = np.zeros(size, dtype=int)

        self.fit_scores = {i: np.zeros(size) for i in fit.Score.names}


class RunModel:

    def __init__(self, dm_model, str_method, firm_id, active_player_t0, positions, prices, t_max):

        self.model = dm_model
        self.str_method = str_method
        self.firm_id = firm_id
        self.active_player_t0 = active_player_t0
        self.positions = positions
        self.prices = prices
        self.t_max = t_max

    def run(self):

        opp = (self.firm_id + 1) % 2
        player_active = self.active_player_t0

        scores = []

        for t in range(self.t_max):

            if player_active == self.firm_id:
                score = getattr(self.model, self.str_method)(
                    player_position=self.positions[t, self.firm_id], player_price=self.prices[t, self.firm_id],
                    opp_position=self.positions[t, opp], opp_price=self.prices[t, opp]
                )

                scores.append(score)

            player_active = (player_active + 1) % 2

        return np.mean(scores)


def get_fit(force):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    m = {
        0.25: fit.Score(r=0.25),
        0.50: fit.Score(r=0.5)
    }

    fit_backup = BackupFit(size=len(backups*2))

    with tqdm(total=len(backups*2)) as pbar:

        i = 0

        for b in backups:

            for player in (0, 1):

                # Register information
                fit_backup.display_opponent_score[i] = b.display_opponent_score
                fit_backup.r[i] = b.r
                fit_backup.score[i] = np.sum(b.profits[:, player])
                fit_backup.user_id[i] = b.user_id[player]
                fit_backup.room_id[i] = b.room_id
                fit_backup.round_id[i] = b.round_id
                fit_backup.firm_id[i] = player

                # Compute score
                kwargs = {
                    "dm_model": m[b.r],
                    "firm_id": player,
                    "active_player_t0": b.active_player_t0,
                    "positions": b.positions,
                    "prices": b.prices,
                    "t_max": b.t_max
                }

                for str_method in fit.Score.names:

                    rm = RunModel(**kwargs, str_method=str_method)
                    score = rm.run()
                    fit_backup.fit_scores[str_method][i] = score

                    tqdm.write("[id={}, r={:.2f}, s={}] [{}] score: {:.2f}".format(
                        i, b.r, int(b.display_opponent_score), str_method, score))

                i += 1
                pbar.update(1)

                tqdm.write("\n")

    backup.save(fit_backup, "data/fit.p")

    return fit_backup


def main(force, do_it_again):

    if not os.path.exists("data/fit.p") or do_it_again or force:
        fit_b = get_fit(force)

    else:
        fit_b = backup.load("data/fit.p")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do fit")
    # parser.add_argument('-s', '--softmax', action="store_true", default=False,
    #                     help="Optmize using a softmax function")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force, do_it_again=parsed_args.do_it_again)
