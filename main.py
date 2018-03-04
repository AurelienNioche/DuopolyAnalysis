# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from game.models import User, Room, Round, RoundComposition, FirmProfit


conversion_rate = 0.5 * 10 ** (-3)


def compute_remuneration(mt_ids=None):

    if mt_ids is None:
        mt_ids = [i[0] for i in User.objects.all().values_list("mechanical_id")]
        print(mt_ids)

    for mt_id in mt_ids:

        print("Looking for MT '{}'".format(mt_id))

        # Application logic
        u = User.objects.filter(mechanical_id=mt_id).first()

        if u:
            print("Name: {}".format(u.username))

            rm = Room.objects.filter(id=u.room_id).first()
            if rm:
                if rm.state == "end":

                    rds = Round.objects.filter(room_id=rm.id)

                    round_id_and_agent_ids = []

                    for rd in rds:

                        rc = RoundComposition.objects.filter(round_id=rd.id, user_id=u.id).first()
                        if rc is not None:
                            round_id_and_agent_ids.append((rd.id, rc.firm_id))

                    profit = 0

                    for round_id, agent_id in round_id_and_agent_ids:

                        # print("round_id", round_id, "agent_id", agent_id)

                        pr = FirmProfit.objects.get(agent_id=agent_id, t=rm.ending_t, round_id=round_id).value

                        profit += pr

                        state = "pvp" if Round.objects.get(id=round_id).pvp else "pve"
                        print("Profit round {}: {}".format(state, pr))

                    print("Total profit", profit)
                    print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit*conversion_rate))

                else:

                    if rm.state == "pvp":

                        rds = Round.objects.filter(room_id=rm.room_id, state="pve")

                        round_id_and_agent_ids = []

                        for rd in rds:

                            rc = RoundComposition.objects.filter(round_id=rd.id, user_id=u.id).first()
                            if rc is not None:
                                round_id_and_agent_ids.append((rd.round_id, rc.agent_id))

                        profit = 0

                        for round_id, agent_id in round_id_and_agent_ids:
                            # print("round_id", round_id, "agent_id", agent_id)

                            pr = FirmProfit.objects.get(agent_id=agent_id, t=rm.ending_t, round_id=round_id).value

                            profit += pr

                            state = "pvp" if Round.objects.get(id=round_id).pvp else "pve"
                            print("Profit round {}: {}".format(state, pr))

                        print("Room stopped at PVP")
                        print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit * conversion_rate))

                    elif rm.state == "pve":
                        print("Room stopped at PVE")
                        print("{} TO PAY: 1$".format(mt_id))

                    else:
                        print("Room stopped at tutorial")
                        print("{} TO PAY: 1$".format(mt_id))

                    if u.deserter:
                        print("{} DESERTER".format(mt_id))

                print()

            else:
                print("User did not enter in a room")
                print()
        else:
            print("Did not find someone that sign up with this name")
            print()



def compute_n_rooms_that_end_up():

    rm = Room.objects.filter(state="end")
    print("N rooms with final state at end: {}".format(len(rm)))


def main():

    # compute_remuneration()
    mt_ids = ("A21B78D7E5N17N", )
    compute_remuneration(mt_ids=mt_ids)
    print()
    compute_n_rooms_that_end_up()


if __name__ == "__main__":
    main()
