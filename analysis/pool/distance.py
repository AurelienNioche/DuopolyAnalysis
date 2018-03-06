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


def _boxplot(backups, ax, y):

    different_r = list(np.unique([b.parameters.r for b in backups]))

    to_plot = tuple([[] for i in range(len(different_r))])

    for i, b in enumerate(backups):
        cond = different_r.index(b.parameters.r)
        to_plot[cond].append(y[i])

    bp = ax.boxplot(to_plot, positions=different_r)
    for e in ['boxes', 'caps', 'whiskers']:
        for b in bp[e]:
            b.set_alpha(0.5)


def distance(pool_backup, fig_name):

    # Create directories if not already existing
    os.makedirs(os.path.dirname(fig_name), exist_ok=True)

    # Shortcuts
    parameters = pool_backup.parameters
    backups = pool_backup.backups

    # Look at the parameters
    n_simulations = len(backups)
    n_positions = parameters.n_positions
    t_max = parameters.t_max

    # Containers
    y = np.zeros(n_simulations)

    # How many time steps from the end of the simulation are included in analysis
    span_ratio = 0.33  # Take last third
    span = int(span_ratio * t_max)

    for i, b in enumerate(backups):

        # Compute the mean distance between the two firms
        data = np.absolute(
            b.positions[-span:, 0] -
            b.positions[-span:, 1]) / n_positions

        y[i] = np.mean(data)

    # Create figure and ax
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Enhance aesthetics
    ax.set_xlim(-0.01, 1.01)
    if max(y) < 0.5:
        ax.set_ylim(-0.01, 0.51)

    ax.set_xticks(np.arange(0, 1.1, 0.25))
    ax.set_yticks(np.arange(0, 0.51, 0.1))

    ax.set_xlabel("$r$")
    ax.set_ylabel("Mean distance")

    # Display line for indicating 'random' level
    seed = 123
    np.random.seed(seed)
    random_pos = np.random.random(size=(2, 10 ** 6))
    random_dist = np.mean(np.absolute(random_pos[0] - random_pos[1]))
    # noinspection PyTypeChecker
    ax.axhline(random_dist, color='0.5', linewidth=0.5, linestyle="--", zorder=1)

    # Plot the boxplot
    _boxplot(backups=backups, ax=ax, y=y)

    # Cut the margins
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)

    plt.close()
