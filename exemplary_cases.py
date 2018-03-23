import os
import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib.gridspec

from backup import backup
from analysis import separate

from fit import get_fit, BackupFit  # Important for pickle loading


def d(positions):
    return np.mean(np.absolute(
        positions[:, 0] -
        positions[:, 1]) / 21)


def info_room(b):
    return "b: room_id {} round_id {} r {}, d {:.2f}, price {:.2f}, profit {:.2f}".format(
        b.room_id, b.round_id, b.r, d(b.positions), np.mean(b.prices), np.mean(b.profits))


def main(force, do_it_again):

    backups = [i for i in backup.get_data(force) if i.pvp]

    if not os.path.exists("data/fit.p") or do_it_again or force:
        fit_b = get_fit(force=False)

    else:
        fit_b = backup.load("data/fit.p")

    r_values = np.sort(np.unique(fit_b.r))

    it = (j for j in range(100))

    # --------------- #

    user_id = np.zeros(len(backups), dtype=int)
    firm_id = np.zeros(len(backups), dtype=int)
    room_id = np.zeros(len(backups), dtype=int)
    round_id = np.zeros(len(backups), dtype=int)
    profit = np.zeros(len(backups))
    compet = np.zeros(len(backups))
    equal_sharing = np.zeros(len(backups))
    r = np.zeros(len(backups))

    for i, idx in enumerate(range(0, len(backups) * 2, 2)):

        assert fit_b.round_id[idx] == fit_b.round_id[idx+1]
        user_id[i] = fit_b.user_id[idx]
        firm_id[i] = fit_b.firm_id[idx]
        room_id[i] = fit_b.room_id[idx]
        round_id[i] = fit_b.round_id[idx]
        r[i] = fit_b.r[idx]
        profit[i] = np.min(fit_b.fit_scores["profit"][idx:idx+2])
        # compet[i] = np.min(fit_b.fit_scores["competition"][idx:idx+2] /
        #                    fit_b.fit_scores["profit"][idx:idx+2])
        compet[i] = np.min(fit_b.fit_scores["competition"][idx:idx+2])
        equal_sharing[i] = np.min(fit_b.fit_scores["equal_sharing"][idx:idx+2])

    # ------------------------------------------------------ #
    #
    # for r_value in r_values:
    #
    #     print("PROFIT")
    #
    #     idx = np.argmax(profit[r == r_value])
    #     rd_id = round_id[r == r_value][idx]
    #     b = [b for b in backups if b.round_id == rd_id][0]
    #     print(next(it))
    #     print(info_room(b))
    #     separate.plot(b, fig_name="fig/best_max_profit_r{}.pdf".format(int(r_value*100)))
    #
    #     print("*****************************************************************************************")
    #
    # for r_value in r_values:
    #
    #     print("COMPET")
    #
    #     idx = np.argmax(compet[r == r_value])
    #     rd_id = round_id[r == r_value][idx]
    #     b = [b for b in backups if b.round_id == rd_id][0]
    #     print(next(it))
    #     print(info_room(b))
    #     separate.plot(b, fig_name="fig/best_max_diff_r{}.pdf".format(int(r_value*100)))
    #
    #     print("*****************************************************************************************")
    #
    # for r_value in r_values:
    #     print("EQUAL SHARING")
    #
    #     idx = np.argmax(equal_sharing[r == r_value])
    #     rd_id = round_id[r == r_value][idx]
    #     b = [b for b in backups if b.round_id == rd_id][0]
    #     print(next(it))
    #     print(info_room(b))
    #     separate.plot(b, fig_name="fig/best_equal_sharing_r{}.pdf".format(int(r_value*100)))
    #
    #     print("*****************************************************************************************")

    fig = plt.figure(figsize=(10, 6), dpi=200)
    gs = matplotlib.gridspec.GridSpec(nrows=2, ncols=2)

    # Profit maximizator r = 0.25 and r = 0.50
    idx = np.argmax(profit[r == 0.25])
    rd_id = round_id[r == 0.25][idx]
    b = [b for b in backups if b.round_id == rd_id][0]
    separate.plot(b, subplot_spec=gs[0, 0])

    idx = np.argmax(profit[r == 0.50])
    rd_id = round_id[r == 0.50][idx]
    b = [b for b in backups if b.round_id == rd_id][0]
    separate.plot(b, subplot_spec=gs[0, 1])

    #  Diff maximizator r = 0.25
    idx = np.argmax(compet[r == 0.25])
    rd_id = round_id[r == 0.25][idx]
    b = [b for b in backups if b.round_id == rd_id][0]
    separate.plot(b, subplot_spec=gs[1, 0])

    # Equal sharing r = 0.5
    idx = np.argmax(equal_sharing[r == 0.50])
    rd_id = round_id[r == 0.50][idx]
    b = [b for b in backups if b.round_id == rd_id][0]
    separate.plot(b, subplot_spec=gs[1, 1])

    ax = fig.add_subplot(gs[:, :], zorder=-10)

    plt.axis("off")
    ax.text(
        s="A", x=-0.05, y=0.55, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="B", x=0.5, y=0.55, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="C", x=-0.05, y=0, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)
    ax.text(
        s="D", x=0.5, y=0, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
        fontsize=20)

    plt.tight_layout()
    plt.savefig("fig/exemplary_cases.pdf")
    plt.show()

    # ------------------------------------------------------------------------------------------------------- #

    # for score in ("profit", "equal_sharing"):
    #     for r in r_values:
    #
    #         idx = np.argmax(fit_b.fit_scores[score][fit_b.r == r])
    #         value = fit_b.fit_scores[score][fit_b.r == r][idx]
    #         user_id = fit_b.user_id[fit_b.r == r][idx]
    #         firm_id = fit_b.firm_id[fit_b.r == r][idx]
    #         room_id = fit_b.room_id[fit_b.r == r][idx]
    #         round_id = fit_b.round_id[fit_b.r == r][idx]
    #
    #         print(next(it))
    #         print(score.upper(), r)
    #         print("user: r = {}, score = {}, value = {}, "
    #               "idx = {}, user_id = {}, firm_id = {}, room_id = {},"
    #               "round_id = {}".format(r, score, value, idx, user_id, firm_id, room_id, round_id))
    #
    #         b = [b for b in backups if b.round_id == round_id][0]
    #
    #         print(info_room(b))
    #         separate.plot(b)
    #         print()
    #
    #         print("********************************************************************************")
    #
    # comp_score = fit_b.fit_scores["competition"] - fit_b.fit_scores["profit"]  # + fit_b.fit_scores["competition"]
    #
    # for r in r_values:
    #
    #     for min_or_max in (np.argmax, ):
    #
    #         print("MAX COMPET", r)
    #
    #         idx = min_or_max(comp_score[fit_b.r == r])
    #         value_profit = fit_b.fit_scores["profit"][fit_b.r == r][idx]
    #         value_compet = fit_b.fit_scores["competition"][fit_b.r == r][idx]
    #         user_id = fit_b.user_id[fit_b.r == r][idx]
    #         firm_id = fit_b.firm_id[fit_b.r == r][idx]
    #         room_id = fit_b.room_id[fit_b.r == r][idx]
    #         round_id = fit_b.round_id[fit_b.r == r][idx]
    #
    #         print(next(it))
    #
    #         print("user: r = {}, min_or_max = {}, value profit = {}, value compet {},"
    #               "idx = {}, user_id = {}, firm_id = {}, room_id = {},"
    #               "round_id = {}".format(r, min_or_max, value_profit,
    #                                      value_compet, idx, user_id, firm_id, room_id, round_id))
    #
    #         b = [b for b in backups if b.round_id == round_id][0]
    #
    #         print(info_room(b))
    #         separate.plot(b)
    #
    #         print()
    #         print("********************************************************************************")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Produce figures.')
    parser.add_argument('-f', '--force', action="store_true", default=False,
                        help="Re-import data")
    parser.add_argument('-d', '--do_it_again', action="store_true", default=False,
                        help="Re-do analysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force, do_it_again=parsed_args.do_it_again)
