data = \
    ((
        " ",
        "Male",
        "Female",
        "15-29",
        "30-44",
        "45-59",
        "60-74",),
     ("PM",
        "0.83\pm0.12",
        "0.83\pm0.17",
        "0.83\pm0.14",
        "0.89\pm0.12",
        "0.74\pm0.15",
        "0.88\pm0.10",),
     ("DM",
        "0.49\pm0.32",
        "0.46\pm0.33",
        "0.36\pm0.27",
        "0.46\pm0.32",
        "0.50\pm0.18",
        "0.55\pm0.26",),
     ("TC",
        "0.65\pm0.31",
        "0.64\pm0.34",
        "0.61\pm0.32",
        "0.68\pm0.24",
        "0.59\pm0.16",
        "0.64\pm0.28")
     )


print(data)


table = \
        r"\begin{table}[htbp]" + "\n" + \
        r"\begin{center}" + "\n" + \
        r"\begin{tabular}{llllllll}" + "\n"

for i, l in enumerate(data):
    for j, v in enumerate(l):
        if j != 0:
            table += " & "
            if i != 0:
                table += "$"

        table += r"{}".format(v)

        if i != 0 and j != 0:
            table += "$"

    table += r"\\ " + "\n"
    if i == 0:
        table += r"\hline \\" + "\n"

table += \
    r"\end{tabular}" + "\n" + \
    r"\end{center}" + "\n" + \
    r"\end{table}"

# r"\caption{Significance tests for comparison using Mann-Withney's u. Bonferroni corrections are applied.}" + "\n" + \
# r"\label{table:significance_tests}" + "\n" + \

print(table)


# output

#\begin{table}[htbp]
#\begin{center}
#\begin{tabular}{llllllll}
#  & Male & Female & 15-29 & 30-44 & 45-59 & 60-74\\
#\hline \\
#PM & $0.83\pm0.12$ & $0.83\pm0.17$ & $0.83\pm0.14$ & $0.89\pm0.12$ & $0.74\pm0.15$ & $0.88\pm0.10$\\
#DM & $0.49\pm0.32$ & $0.46\pm0.33$ & $0.36\pm0.27$ & $0.46\pm0.32$ & $0.50\pm0.18$ & $0.55\pm0.26$\\
#TC & $0.65\pm0.31$ & $0.64\pm0.34$ & $0.61\pm0.32$ & $0.68\pm0.24$ & $0.59\pm0.16$ & $0.64\pm0.28$\\
#\end{tabular}
#\end{center}
#\end{table}