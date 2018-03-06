# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from game.models import Room


def count():

    rms = Room.objects.filter(state="end")
    print("N rooms with final state at end: {}".format(len(rms)))
    rm_25 = rms.filter(radius=0.25)
    rm_50 = rms.filter(radius=0.5)
    print("N rooms with 25: {}".format(len(rm_25)))
    print("N rooms with 50: {}".format(len(rm_50)))


def main():
    count()


if __name__ == "__main__":
    main()
