# Django specific settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

<<<<<<< HEAD
import numpy as np
from collections import Counter
import matplotlib.gridspec as gridspec
=======

import numpy as np
from collections import Counter
>>>>>>> origin/master
from pylab import plt
import operator
import itertools

from game.models import User


def main():

    # Mean age + sd
    # gender parity
    # nationalities

    users = User.objects.filter(state="end")

    print("\nThere is a total of {} users.".format(users.count()))

    data = get_data(users)
<<<<<<< HEAD
    data["n_users"] = users.count()
=======
>>>>>>> origin/master

    print("******* Age ********")
    print("Average age: {:.2f} ".format(np.mean(data["age"])))
    print("Std age: {:.2f}".format(np.std(data["age"])))
    print("******* Nationalities ********")
    for n in data["nationality"].items():
        print(n)
    print("******* Gender ********")
    for g, n in data["gender"].items():
        print("{}: {:.2f}".format(g, n))

    plot(data)


def plot(data):

<<<<<<< HEAD
    plt.style.use("seaborn-deep")

    gs = gridspec.GridSpec(2, 2)

    plt.figure(figsize=(13, 7))

    ax = plt.subplot(gs[:, 0])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.tick_params(length=0)
    # ax.axis("off")
    plt.title("Nationalities repartition (%)")
    # ax.grid(False)

    nationalities = sorted(data["nationality"].items(), key=operator.itemgetter(1))

    labels = [i[0].capitalize() for i in nationalities]
    labels_pos = np.arange(len(labels))

    values = [round((i[1] / data["n_users"]) * 100) for i in nationalities]
=======
    plt.style.use("ggplot")
    plt.axis("off")

    ax = plt.subplot(1, 2, 1)
    ax.grid(False)

    nationalities = sorted(data["nationality"].items(), key=operator.itemgetter(1))

    labels = [i[0] for i in nationalities]
    labels_pos = np.arange(len(labels))

    values = [i[1] for i in nationalities]
>>>>>>> origin/master

    ax.barh(labels_pos, values, edgecolor="white", align="center")
    ax.set_yticks(labels_pos)
    ax.set_yticklabels(labels)
<<<<<<< HEAD

    ax = plt.subplot(gs[0, 1])
    plt.title("Genders repartition")

    genders = data["gender"].items()

    labels = [i[0].capitalize() for i in genders]
    values = [i[1] for i in genders]

    ax.pie(values, labels=labels, explode=(0.1, 0.1), autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')

    ax = plt.subplot(gs[1, 1])
    plt.title("Age group repartition")
=======
    ax.set_xlim(0, 30)
    ax.set_xticks([])

    ax = plt.subplot(1, 2, 2)

    genders = data["gender"].items()

    labels = [i[0] for i in genders]
    values = [i[1] for i in genders]

    ax.pie(values, labels=labels, explode=(0, 0.1), autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')

    ax = plt.subplot(1, 2, 3)
>>>>>>> origin/master

    ages = [list(i[1]) for i in itertools.groupby(sorted(data["age"]), lambda x: x // 10)]

    n_ages = np.sum(np.flatnonzero(np.array(ages)))

<<<<<<< HEAD
    decades = [str(i[0])[0] + "0 y.o." for i in ages]
    values = [len(i) / n_ages for i in ages]

    ax.pie(values, labels=decades, explode=(0.1, ) * len(decades), autopct='%1.1f%%', startangle=90, shadow=True)

    ax.text(2, 0.01, "Age std: {:.2f}".format(np.std(data["age"])))
    ax.text(2, 0.4, "Age mean: {:.2f}".format(np.mean(data["age"])))
=======
    decades = [str(i[0])[0] + "0" for i in ages]
    values = [len(i) / n_ages for i in ages]

    ax.pie(values,  labels=decades, shadow=True, autopct='%1.1f%%', startangle=90)
    # ax.legend("Age std: {}".format(np.std(data["age"])))
    # ax.legend("Age mean: {}".format(np.mean(data["age"])))
>>>>>>> origin/master
    ax.axis('equal')

    plt.show()


<<<<<<< HEAD
=======
    # ax.pie


>>>>>>> origin/master
def get_data(users):

    data = {
        "gender": {"male": 0, "female": 0},
        "age": [],
        "nationality": [],
    }

    for u in users:

        data["gender"][u.gender.lower()] += 1
        data["age"].append(u.age)

        nationality = u.nationality.lower()

        if "india" in nationality:
            data["nationality"].append("indian")

<<<<<<< HEAD
        elif "america" in nationality or nationality == "us"\
                or nationality == "united states" or nationality == "usa":
            data["nationality"].append("american")

        elif "dominican" in nationality:

            data["nationality"].append("dominican republic")

        elif nationality == "black":

            data["nationality"].append("undefined")

=======
        elif "america" in nationality or nationality == "us" or nationality == "united states":
            data["nationality"].append("american")

>>>>>>> origin/master
        else:
            data["nationality"].append(u.nationality.lower())

    data["nationality"] = Counter(data["nationality"])
    # data["age"] = {"mean": np.mean(data["age"]), "std": np.std(data["age"])}

    for k, v in data["gender"].items():
        data["gender"][k] = (v / users.count()) * 100

    return data


<<<<<<< HEAD
main()






=======
main()
>>>>>>> origin/master
