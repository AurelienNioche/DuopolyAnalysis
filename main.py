# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from game.models import Users, Players, Room, Round, RoundComposition, FirmProfits


mt_id = "A1036BH0RBAF1O"

# Application logic
user = Users.objects.get(mechanical_id=mt_id)

p = Players.objects.get(player_id=user.player_id)

rm = Room.objects.get(room_id=p.room_id)

ending_t = rm.ending_t - 1

rds = Round.objects.filter(room_id=rm.room_id)

round_id_and_agent_ids = []

for rd in rds:

    rc = RoundComposition.objects.filter(round_id=rd.round_id, player_id=p.player_id).first()
    if rc is not None:
        round_id_and_agent_ids.append((rd.round_id, rc.agent_id))

profit = 0

for round_id, agent_id in round_id_and_agent_ids:

    profit += FirmProfits.objects.get(agent_id=agent_id, t=ending_t, round_id=round_id)

print("total profit", profit)