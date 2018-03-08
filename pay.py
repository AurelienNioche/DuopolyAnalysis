# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Your application specific imports
from game.models import User, Room, Round, RoundComposition, FirmProfit


conversion_rate = 0.5 * 10 ** (-3)


def compute_remuneration(mt_ids=None, supp_bonus=None):

    if mt_ids is None:
        mt_ids = [i[0] for i in User.objects.all().values_list("mechanical_id")]
        print(mt_ids)

    for mt_id in mt_ids:

        print("Looking for MT '{}'".format(mt_id))

        # Application logic
        u = User.objects.filter(mechanical_id=mt_id, registered=True).first()
        if not u:
            u = User.objects.filter(mechanical_id=mt_id).first()

        if u:
            print("Name: {}".format(u.username))
            if supp_bonus and u.username in supp_bonus:
                print("!!!!!!!!!!!!! SUP BONUS !!!!!!!!!!!!!!!!!!!")

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

                        state = "final" if Round.objects.get(id=round_id).pvp else "first"
                        print("Score {} round: {}".format(state, pr))

                    print("Total score: {}".format(profit))
                    print("Conversion rate: 1,000 points -> 0.50$")
                    print("Bonus: {:.2f}$".format(profit*conversion_rate))
                    print("Thanks for your participation! We hope you enjoyed the game!")
                    print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit*conversion_rate))

                else:

                    if rm.state in ("pvp", "pve"):

                        rds = Round.objects.filter(room_id=rm.id)

                        round_id_and_agent_ids = []

                        for rd in rds:

                            rc = RoundComposition.objects.filter(round_id=rd.id, user_id=u.id).first()
                            if rc is not None:
                                round_id_and_agent_ids.append((rd.id, rc.firm_id))

                        profit = 0

                        for round_id, agent_id in round_id_and_agent_ids:
                            # print("round_id", round_id, "agent_id", agent_id)

                            pr = \
                                FirmProfit.objects.filter(agent_id=agent_id, round_id=round_id)\
                                .order_by("-value").first().value

                            profit += pr

                            state = "final" if Round.objects.get(id=round_id).pvp else "first"
                            print("Score {} round: {}".format(state, pr) if pr > 0 else "")

                        print("Total score: {}".format(profit))
                        print("Conversion rate: 1,000 points -> 0.50$")
                        print("Bonus: {:.2f}$".format(profit * conversion_rate))
                        print("Thanks for your participation!")
                        print("Room stopped before the end.")
                        print("{} TO PAY: 1$ + {:.2f} $ BONUS".format(mt_id, profit * conversion_rate))

                    else:
                        print("Room stopped at tutorial")
                        print("{} TO PAY: 1$".format(mt_id))

                    if u.deserter:
                        print("{} quits ('deserter' status)".format(mt_id))
                        print("{} TO PAY: 1$".format(mt_id))

                print()

            else:
                print("User did not enter in a room")
                print()
        else:
            print("Did not find someone that sign up with this name")
            print()


def main():

    mt_ids = ("A2VUAAJHX6ROS9", )
    compute_remuneration(mt_ids=mt_ids, supp_bonus=(
        "xelitexk1llerx@yahoo.com", "l.turner782@gmail.com", "restinagony@gmail.com",
        "marcusdavvid@icloud.com", "amy_777_rene@hotmail.com", "kmhaines91@gmail.com"
    ))


if __name__ == "__main__":
    main()
