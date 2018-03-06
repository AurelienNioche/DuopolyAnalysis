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


def prices_over_fov(pool_backup, pos_subplot):

    # Shortcuts
    parameters = pool_backup.parameters
    backups = pool_backup.backups

    # Look at the parameters
    t_max = parameters.t_max

    # How many time steps from the end of the simulation are included in analysis
    span_ratio = 0.33  # Take last third
    span = int(span_ratio * t_max)

    # Create figs and plot
    ax = plt.subplot(*pos_subplot)

    # Enhance aesthetics
    ax.set_xlim(-0.01, 1.01)
    ax.set_xticks([])
    ax.set_ylabel("Mean prices")

    # Do the boxplot
    n_simulations = len(backups)
    y = np.zeros(n_simulations)

    for i, b in enumerate(backups):

        data = b.prices[-span:, :]

        # Compute the mean price
        y[i] = np.mean(data)

    _boxplot(backups=backups, ax=ax, y=y)


def profits_over_fov(pool_backup, pos_subplot):

    # Shortcuts
    parameters = pool_backup.parameters
    backups = pool_backup.backups

    # Look at the parameters
    t_max = parameters.t_max

    # How many time steps from the end of the simulation are included in analysis
    span_ratio = 0.33  # Take last third
    span = int(span_ratio * t_max)

    # Do the boxplot
    n_simulations = len(backups)
    y = np.zeros(n_simulations)

    for i, b in enumerate(backups):

        data = b.profits[-span:, :]
        # Compute the mean profit
        y[i] = np.mean(data)

    # Create figs and plot
    ax = plt.subplot(*pos_subplot)

    # Enhance aesthetics
    ax.set_xlim(-0.01, 1.01)
    ax.set_xticks(np.arange(0, 1.1, 0.25))
    ax.set_xlabel("$r$")
    ax.set_ylabel("Mean profits")

    # Plot the boxplot
    _boxplot(backups=backups, ax=ax, y=y)


def prices_and_profits(pool_backup, fig_name):

    # Create directories if not already existing
    os.makedirs(os.path.dirname(fig_name), exist_ok=True)

    # Create the fig object
    plt.figure(figsize=(9, 8))

    # 2 rows, 1 column
    n_rows, n_cols = 2, 1

    # Create the two subfigures
    prices_over_fov(pool_backup, (n_rows, n_cols, 1))
    profits_over_fov(pool_backup, (n_rows, n_cols, 2))

    # Cut margins
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)

    plt.close()
