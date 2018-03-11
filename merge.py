# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from game.models import Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState

import shutil
from tqdm import tqdm

from analyse import load_data_from_db


def merge():

    shutil.copy("duopolyNew.sqlite3", "duopoly.sqlite3")

    for table in Room, Round, FirmPosition, FirmPrice, FirmProfit, RoundComposition, RoundState:

        entries = table.objects.all().using('old')
        print("entries in ", table, ":", entries.count())
        i = 0
        # new_entries = []
        for e in entries:
            e_dic = {k:v for (k, v) in e.__dict__.items() if not k.startswith("_")}
            print(e_dic)
            new_e = table(**e_dic)
            new_e.save()
            i += 1
            print(i, "done")
            # new_entries.append(new_e)


        # table.objects.bulk_create(new_entries)


def stats():

    backups = load_data_from_db()

    n = {
        0.25: {True: 0, False: 0},
        0.50: {True: 0, False: 0}
    }
    for b in backups:

        if b.active_player_t0 == 1:
            cond = b.positions[0, 0] == 0 and b.prices[0, 0] == 5
        else:
            cond = b.positions[0, 1] == 20 and b.prices[0, 1] == 5

        if not cond:
            print(b.positions[0, :], b.prices[0, :], b.r, b.display_opponent_score)

        if cond and b.pvp:
            n[b.r][b.display_opponent_score] += 1

    print(n)


def main():

    merge()
    stats()


if __name__ == "__main__":

    main()

