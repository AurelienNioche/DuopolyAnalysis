# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from game.models import Users, Players, Room, Round, RoundComposition, FirmProfits


conversion_rate = 0.5 * 10 **(-3)


mt_ids = ["A2KOXR5OXIFUIW"]


for mt_id in mt_ids:

    # Application logic
    user = Users.objects.get(mechanical_id=mt_id)

    print("Looking for MT {} ({})".format(user.mechanical_id, user.username))

    p = Players.objects.get(player_id=user.player_id)

    rm = Room.objects.get(room_id=p.room_id)

    if rm.state == "end":
        ending_t = rm.ending_t - 1

        rds = Round.objects.filter(room_id=rm.room_id)

        round_id_and_agent_ids = []

        for rd in rds:

            rc = RoundComposition.objects.filter(round_id=rd.round_id, player_id=p.player_id).first()
            if rc is not None:
                round_id_and_agent_ids.append((rd.round_id, rc.agent_id))

        profit = 0

        for round_id, agent_id in round_id_and_agent_ids:

            # print("round_id", round_id, "agent_id", agent_id)

            pr = FirmProfits.objects.get(agent_id=agent_id, t=ending_t, round_id=round_id).value

            profit += pr

            state = Round.objects.get(round_id=round_id).state  # pve, pvp
            print("Profit round {}: {}".format(state, pr))

        print("Total profit", profit)
        print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit*conversion_rate))

    else:

        if rm.state == "pvp":

            ending_t = rm.ending_t - 1

            rds = Round.objects.filter(room_id=rm.room_id, state="pve")

            round_id_and_agent_ids = []

            for rd in rds:

                rc = RoundComposition.objects.filter(round_id=rd.round_id, player_id=p.player_id).first()
                if rc is not None:
                    round_id_and_agent_ids.append((rd.round_id, rc.agent_id))

            profit = 0

            for round_id, agent_id in round_id_and_agent_ids:
                # print("round_id", round_id, "agent_id", agent_id)

                pr = FirmProfits.objects.get(agent_id=agent_id, t=ending_t, round_id=round_id).value

                profit += pr

                state = Round.objects.get(round_id=round_id).state  # pve, pvp
                print("Profit round {}: {}".format(state, pr))

            print("Room stopped at PVP")
            print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit * conversion_rate))

        elif rm.state == "pve":
            print("Room stopped at PVE")
            print("{} TO PAY: 1$".format(mt_id))

        else:
            print("Room stopped at tutorial")
            print("{} TO PAY: 1$".format(mt_id))

        if user.deserter:
            print("{} DESERTER".format(mt_id))

    print()
