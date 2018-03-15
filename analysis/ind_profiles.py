import matplotlib.pyplot as plt
import matplotlib.gridspec
import numpy as np
import itertools as it


def plot(data=np.random.random(size=(60, 5)), fig_size=(12, 12),
         labels=[str(_) for _ in range(5)],
         n_dim=5, n_cols=6, title="Title",
         colors=["C{}".format(_) for _ in range(5)]):

    ratio = len(data) / n_cols

    n_rows = int(ratio) if int(ratio) == len(data)// n_cols else int(ratio) + 1

    gs = matplotlib.gridspec.GridSpec(nrows=n_rows+1, ncols=n_cols)

    positions = it.product(range(1, n_rows+1), range(n_cols))

    fig = plt.figure(figsize=fig_size)

    ax0 = fig.add_subplot(gs[0, :])
    ax0.set_title(title)
    for label, color in zip(labels, colors):
        ax0.scatter(-1, -1, marker="s", color=color, label=label)
        ax0.set_xlim(0, 1)
        ax0.set_ylim(0, 1)
        ax0.spines['top'].set_visible(False)
        ax0.spines['right'].set_visible(False)
        ax0.spines['left'].set_visible(False)
        ax0.spines['bottom'].set_visible(False)
        ax0.set_xticks([])
        ax0.set_yticks([])
    ax0.legend(ncol=n_dim, loc="upper center")

    axes = []

    for i, (pos, d) in enumerate(zip(positions, data)):

        ax = fig.add_subplot(gs[pos[0], pos[1]])
        ax.bar(np.arange(n_dim), d, width=1, color=colors)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if i not in np.arange(0, n_rows * n_cols, n_cols):
            ax.spines['left'].set_visible(False)
            ax.tick_params(length=0, axis="y")
            ax.set_yticklabels([])

        ax.spines['bottom'].set_visible(False)
        ax.tick_params(axis="x", length=0)
        ax.set_ylim(0, 1)
        ax.set_yticks((0, 1))
        ax.set_xticklabels([])
        # ax.set_aspect(4)

        axes.append(ax)

        if i == len(data) - 1:
            break

    plt.tight_layout()

    plt.savefig("fig/ind_profiles_{}.pdf".format(title.replace(" ", "_").replace(",", "")))
    plt.show()


if __name__ == "__main__":
    plot()
