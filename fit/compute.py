import numpy as np
from tqdm import tqdm

import os
import itertools as it


from backup import backup
from fit import score


class BackupFit:

    def __init__(self, size):

        self.display_opponent_score = np.zeros(size, dtype=bool)
        self.r = np.zeros(size)
        self.firm_id = np.zeros(size, dtype=int)
        self.user_id = np.zeros(size, dtype=int)
        self.room_id = np.zeros(size, dtype=int)
        self.round_id = np.zeros(size, dtype=int)
        self.score = np.zeros(size, dtype=int)

        self.fit_scores = {i: np.zeros(size) for i in score.Score.names}


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
                sc = getattr(self.model, self.str_method)(
                    player_position=self.positions[t, self.firm_id], player_price=self.prices[t, self.firm_id],
                    opp_position=self.positions[t, opp], opp_price=self.prices[t, opp]
                )

                scores.append(sc)

            player_active = (player_active + 1) % 2

        return np.mean(scores)


def get_fit(force):

    backups = backup.get_data(force)

    backups = [b for b in backups if b.pvp]

    m = {
        0.25: score.Score(r=0.25),
        0.50: score.Score(r=0.5)
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

                for str_method in score.Score.names:

                    rm = RunModel(**kwargs, str_method=str_method)
                    sc = rm.run()
                    fit_backup.fit_scores[str_method][i] = sc

                    tqdm.write("[id={}, r={:.2f}, s={}] [{}] score: {:.2f}".format(
                        i, b.r, int(b.display_opponent_score), str_method, sc))

                i += 1
                pbar.update(1)

                tqdm.write("\n")

    backup.save(fit_backup, "data/fit.p")

    return fit_backup
