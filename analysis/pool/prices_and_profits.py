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


def prices_over_fov(backups, pos_subplot, attr="r", violin=True):

    # Format data
    n_simulations = len(backups)
    y = np.zeros(n_simulations)

    for i, b in enumerate(backups):

        data = b.prices[:, :]  # b.prices[-span:, :]

        # Compute the mean price
        y[i] = np.mean(data)

    # Create figs and plot
    ax = plt.subplot(*pos_subplot)

    # Enhance aesthetics
    ax.set_ylabel("Mean prices")
    ax.set_ylim(0.5, 11.5)

    ax.set_yticks(np.arange(1, 12, 2))

    # Plot data
    if violin:
        plot.violin(backups=backups, ax=ax, y=y, attr=attr, content="Prices")
    else:
        plot.boxplot(backups=backups, ax=ax, y=y, attr=attr, content="Prices")


def profits_over_fov(backups, pos_subplot, attr="r", violin=True):

    # Format data
    n_simulations = len(backups)
    y = np.zeros(n_simulations)

    for i, b in enumerate(backups):

        data = b.profits[:, :]
        # Compute the mean profit
        y[i] = np.mean(data)

    # Create figs and plot
    ax = plt.subplot(*pos_subplot)

    # Enhance aesthetics
    ax.set_ylabel("Mean profits")
    ax.set_ylim(0, 150)

    # Plot data
    if violin:
        plot.violin(backups=backups, ax=ax, y=y, attr=attr, content="Profits")
    else:
        plot.boxplot(backups=backups, ax=ax, y=y, attr=attr, content="Profits")


def prices_and_profits(backups, fig_name, attr="r"):

    # Create directories if not already existing
    os.makedirs(os.path.dirname(fig_name), exist_ok=True)

    # Create the fig object
    plt.figure(figsize=(9, 8))

    # 2 rows, 1 column
    n_rows, n_cols = 2, 1

    # Create the two sub-figures
    prices_over_fov(backups=backups, pos_subplot=(n_rows, n_cols, 1), attr=attr)
    profits_over_fov(backups=backups, pos_subplot=(n_rows, n_cols, 2), attr=attr)

    # Cut margins
    plt.tight_layout()

    # Save fig
    plt.savefig(fig_name)

    plt.close()
