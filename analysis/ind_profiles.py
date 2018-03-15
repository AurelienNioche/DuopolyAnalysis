import matplotlib.pyplot as plt
import matplotlib.gridspec
import numpy as np
import itertools as it


def plot(data=np.random.random(size=(60, 5)),
         labels=[str(_) for _ in range(5)],
         n_dim=5, n_cols=6, n_rows=10, title="Title",
         colors=["C{}".format(_) for _ in range(5)]):

    gs = matplotlib.gridspec.GridSpec(nrows=n_rows+1, ncols=n_cols)

    positions = it.product(range(1, n_rows+1), range(n_cols))

    fig = plt.figure(figsize=(12, 12))

    ax0 = fig.add_subplot(gs[0, :])
    ax0.set_title(title)
    for label, color in zip(labels, colors):
        ax0.scatter(-1, -1, marker="s", label=label)
        ax0.set_xlim(0, 1)
        ax0.set_ylim(0, 1)
        ax0.spines['top'].set_visible(False)
        ax0.spines['right'].set_visible(False)
        ax0.spines['left'].set_visible(False)
        ax0.spines['bottom'].set_visible(False)
        ax0.set_xticks([])
        ax0.set_yticks([])
    ax0.legend(ncol=5, loc="upper center")

    for i, (pos, d) in enumerate(zip(positions, data)):

        ax = fig.add_subplot(gs[pos[0], pos[1]])
        ax.bar(np.arange(n_dim), d, width=1, color=colors)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(axis="x", length=0)
        ax.set_ylim(0, 1)
        ax.set_yticks((0, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        # ax.set_aspect(4)

        if i == len(data) - 1:
            break

    plt.tight_layout()


def show():
    plt.show()


def save(file_name):
    plt.savefig(file_name)


if __name__ == "__main__":
    plot()
