# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import numpy as np
import argparse
import tqdm

from game.models import Room, Round, FirmPosition, FirmPrice, FirmProfit

from backup import backup
from analysis.separate import separate
from analysis.pool import distance, prices_and_profits


def load_data_from_db():

    backups = []

    rms = Room.objects.filter(state="end")

    for rm in rms:

        t_max = rm.ending_t
        r = rm.radius

        rds = Round.objects.filter(room_id=rm.id).order_by("pvp")

        for rd in rds:

            positions = np.zeros((t_max, 2), dtype=int)
            prices = np.zeros((t_max, 2), dtype=int)
            profits = np.zeros((t_max, 2), dtype=int)

            position_entries = FirmPosition.objects.filter(round_id=rd.id)
            price_entries = FirmPrice.objects.filter(round_id=rd.id)
            profits_entries = FirmProfit.objects.filter(round_id=rd.id)

            for t in range(t_max):
                positions[t, :] = \
                    [i[0] for i in position_entries.values_list("value").filter(t=t).order_by("agent_id")]
                prices[t, :] = \
                    [i[0] for i in price_entries.values_list("value").filter(t=t).order_by("agent_id")]

            for t in range(1, t_max + 1):
                profits[t - 1] = \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t).order_by("agent_id")]) - \
                    np.array([i[0] for i in profits_entries.values_list("value").filter(t=t - 1).order_by("agent_id")])

            b = backup.RunBackup(parameters=backup.Parameters(t_max=t_max, r=r),
                                 positions=positions, prices=prices, profits=profits,
                                 room_id=rm.id, round_id=rd.id, pvp=rd.pvp)

            backups.append(b)

    pool_backup = backup.PoolBackup(
        parameters=backup.Parameters(r=None, t_max=25),
        backups=backups
    )

    pool_backup.save()

    return pool_backup


def main(force):

    if not os.path.exists("data/data.p") or force:
        pool_backup = load_data_from_db()

    else:
        pool_backup = backup.PoolBackup.load()

    pool_backup.backups = [b for b in pool_backup.backups if b.pvp]

    distance.distance(pool_backup=pool_backup, fig_name="fig/pool_distance.pdf")
    prices_and_profits.prices_and_profits(pool_backup=pool_backup, fig_name="fig/prices_and_profits.pdf")

    for b in tqdm.tqdm(pool_backup.backups):
        fig_name = "fig/room{}_round{}_{}_separate.pdf".format(b.room_id, b.round_id, "pvp" if b.pvp else "pve")
        separate.separate(backup=b, fig_name=fig_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-run analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)

