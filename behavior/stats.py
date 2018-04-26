import scipy.stats
import statsmodels.stats.multitest


def stats(r, s, dist, prices, scores):

    to_compare = [
        {
            "measure": "distance",
            "constant": "s = 0",
            "var": "r",
            "data": [dist[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "distance",
            "constant": "s = 1",
            "var": "r",
            "data": [dist[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "price",
            "constant": "s = 0",
            "var": "r",
            "data": [prices[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "price",
            "constant": "s = 1",
            "var": "r",
            "data": [prices[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "profit",
            "constant": "s = 0",
            "var": "r",
            "data": [scores[(r == r_value) * (s == 0)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "profit",
            "constant": "s = 1",
            "var": "r",
            "data": [scores[(r == r_value) * (s == 1)] for r_value in (0.25, 0.50)]
        }, {
            "measure": "distance",
            "constant": "r = 0.25",
            "var": "s",
            "data": [dist[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "distance",
            "constant": "r = 0.50",
            "var": "s",
            "data": [dist[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "price",
            "constant": "r = 0.25",
            "var": "s",
            "data": [prices[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "price",
            "constant": "r = 0.50",
            "var": "s",
            "data": [prices[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "profit",
            "constant": "r = 0.25",
            "var": "s",
            "data": [scores[(r == 0.25) * (s == s_value)] for s_value in (0, 1)]
        }, {
            "measure": "profit",
            "constant": "r = 0.50",
            "var": "s",
            "data": [scores[(r == 0.50) * (s == s_value)] for s_value in (0, 1)]
        }
    ]

    ps = []
    us = []

    for dic in to_compare:
        u, p = scipy.stats.mannwhitneyu(dic["data"][0], dic["data"][1])
        ps.append(p)
        us.append(u)

    valid, p_corr, alpha_c_sidak, alpha_c_bonf = \
        statsmodels.stats.multitest.multipletests(pvals=ps, alpha=0.01, method="b")

    for p, u, p_c, v, dic in zip(ps, us, p_corr, valid, to_compare):
        print("[Diff in {} when {} depending on {}-value] "
              "Mann-Whitney rank test: u {}, p {:.3f}, p corr {:.3f}, significant: {}"
              .format(dic["measure"], dic["constant"], dic["var"], u, p, p_c, v))
        print()

    table = \
        r"\begin{table}[htbp]" + "\n" + \
        r"\begin{center}" + "\n" + \
        r"\begin{tabular}{llllllll}" + "\n" + \
        r"Measure & Variable & Constant & $u$ & $p$ (before corr.) " \
        r"& $p$ (after corr.) & Sign. at 1\% threshold \\" + "\n" + \
        r"\hline \\" + "\n"

    for p, u, p_c, v, dic in zip(ps, us, p_corr, valid, to_compare):
        p = "{:.3f}".format(p) if p >= 0.001 else "$<$ 0.001"
        p_c = "{:.3f}".format(p_c) if p_c >= 0.001 else "$<$ 0.001"
        v = "yes" if v else "no"
        table += r"{} & ${}$ & ${}$ & {} & {} & {} & {} \\" \
                     .format(dic["measure"], dic["var"], dic["constant"], u, p, p_c, v) \
                 + "\n"

    table += \
        r"\end{tabular}" + "\n" + \
        r"\end{center}" + "\n" + \
        r"\caption{Significance tests for comparison using Mann-Withney's u. " \
        r"Bonferroni corrections are applied.}" + "\n" + \
        r"\label{table:significance_tests}" + "\n" + \
        r"\end{table}"

    print("*** Latex-formated table ***")
    print(table)
