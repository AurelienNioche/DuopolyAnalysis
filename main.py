# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from game.models import Users, Players, Room, Round, RoundComposition


mt_id = "A1036BH0RBAF1O"

# Application logic
user = Users.objects.get(mechanical_id=mt_id)

p = Players.objects.get(player_id=user.player_id)

rm = Room.objects.get(room_id=p.room_id)

rds = Round.objects.filter(room_id=rm.room_id)

agent_ids = []

for rd in rds:

    rc = RoundComposition.objects.filter(round_id=rd.round_id, player_id=p.player_id).first()
    if rc:
        agent_ids.append(rc.agent_id)

print(agent_ids)


