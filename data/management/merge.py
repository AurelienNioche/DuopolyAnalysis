import os
from django.core.wsgi import get_wsgi_application
from tqdm import tqdm
import shutil

from game.models import Room, Round, FirmPosition, FirmPrice, \
    FirmProfit, RoundComposition, RoundState


application = get_wsgi_application()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


def merge():

    shutil.copy("duopolyNew.sqlite3", "duopoly.sqlite3")

    tables = (
        Room,
        Round,
        FirmPosition,
        FirmPrice,
        FirmProfit,
        RoundComposition,
        RoundState
    )

    n_entries = sum([table.objects.using("old").count() for table in tables])
    to_print = []

    with tqdm(total=n_entries) as pbar:

        for table in tables:

            entries = table.objects.all().using('old')
            new_entries = []

            for e in entries:
                if not table.objects.filter(id=e.id).first():
                    new_entries.append(e)
                pbar.update()

            if new_entries:
                to_print.append("Created {} new entries in table {}.".format(len(new_entries), table.__name__))
                table.objects.bulk_create(new_entries)
            else:
                to_print.append("No new entries for table {}.".format(table.__name__))

    print("\n*****************************************")
    print("\n".join(to_print))
    print("*******************************************")


def main():

    merge()


if __name__ == "__main__":

    main()
