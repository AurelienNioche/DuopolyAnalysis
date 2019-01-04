import behavior.stats
import fit.stats
import simulation.model
from collections import namedtuple


def stats_tables(force):

    behavior.stats.stats(force)
    fit.stats.stats(force)


# def expected_profits_table():
#
#     expected_profits = np.zeros
#
#     expected_profits = expected_profits.astype(int)
#     expected_profits = expected_profits.reshape((21, 11))
#     strategies = strategies.astype(int)
#
#     n_prices = 11
#     n_positions = 21
#
#     table = \
#         r"\begin{table}[htbp]" + "\n" + \
#         r"\begin{center}" + "\n" + \
#         r"\begin{tabular}{lllllllllll}" + "\n" + \
#         r"Position & " + \
#         r" & ".join(["\$" + str(strategies[i, 1] + 1) for i in range(n_prices)]) + r"\\" + "\n"\
#         r"\hline \\" + "\n"
#
#     for i in range(n_positions):
#         table += \
#             r" {} & ".format(i + 1) + " & ".join([str(expected_profits[i, j]) for j in range(n_prices)]) + \
#             "\\\ \n"
#
#     table += r"\end{tabular}" + "\n" + \
#         r"\end{center}" + "\n" + \
#         r"\end{table}"
#
#     print()
#     print("opp move", strategies[opp_move, :])
#
#     print(table)
#     quit()
#
#

