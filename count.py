# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from game.models import Room, RoomComposition, User


def count():

    rms = Room.objects.filter(state="end")
    print("N rooms with final state at end: {}".format(len(rms)))
    rm_25 = rms.filter(radius=0.25)
    rm_50 = rms.filter(radius=0.5)
    print("N rooms with 25: {}".format(len(rm_25)))
    print("N rooms with 50: {}".format(len(rm_50)))


def count2():

    n = 0
    rms = Room.objects.all()

    for rm in rms:

        end = True
        rcs = RoomComposition.objects.filter(room_id=rm.id)
        for rc in rcs:

            u = User.objects.filter(id=rc.user_id).first()
            if u and u.state == "end":
                pass
            else:
                end = False
        n += int(end)

    print("N room (version 2 for computing):", n)


def main():
    count()
    count2()


if __name__ == "__main__":
    main()
