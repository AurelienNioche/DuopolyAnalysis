# SpatialCompetition
# Copyright (C) 2018  Aurélien Nioche, Basile Garcia & Nicolas Rougier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pylab import plt, np
import os
from . import plot

# plt.style.use("seaborn")


def distance(backups, fig_name, attr="r", violin=True):

    # Create directories if not already existing
    os.makedirs(os.path.dirname(fig_name), exist_ok=True)

    # Look at the parameters
    n_simulations = len(backups)
    n_positions = backups[0].n_positions

    # Containers
    y = np.zeros(n_simulations)

    for i, b in enumerate(backups):

        # Compute the mean distance between the two firms
        data = np.absolute(
            b.positions[:, 0] -
            b.positions[:, 1]) / n_positions

        y[i] = np.mean(data)

    # Create figure and ax
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Enhance aesthetics
    # ax.set_xlim(-0.01, 1.01)
    y_upper_bound = 0.9
    if max(y) < y_upper_bound:
        ax.set_ylim(0, y_upper_bound)
    else:
        raise Exception('Y upper bound has been reached')
    # if max(y) < 0.5:
    #     ax.set_ylim(-0.01, 0.51)

    # ax.set_yticks(np.arange(0, 0.51, 0.1))

    ax.set_ylabel("Mean distance")

    # Display line for indicating 'random' level
    seed = 123
    np.random.seed(seed)
    random_pos = np.random.random(size=(2, 10 ** 6))
    random_dist = np.mean(np.absolute(random_pos[0] - random_pos[1]))
    # noinspection PyTypeChecker
    ax.axhline(random_dist, color='0.5', linewidth=0.5, linestyle="--", zorder=1)

    # Plot data
    if violin:
        plot.violin(backups=backups, ax=ax, y=y, attr=attr, content="Localisation")
    else:
        plot.boxplot(backups=backups, ax=ax, y=y, attr=attr, content="Localisation")

    # Cut the margins
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)

    plt.close()
