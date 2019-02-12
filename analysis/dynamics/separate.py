# DuopolyAnalysis
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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import SubplotParams
import matplotlib.gridspec as gridspec
import os


def eeg_like(backup, subplot_spec, letter=None):

    gs = gridspec.GridSpecFromSubplotSpec(
        nrows=4, ncols=1, subplot_spec=subplot_spec)

    pst = backup.positions
    prc = backup.prices

    t_max = len(pst)

    t = np.arange(1, t_max)

    try:
        position_max = backup.n_positions - 1
        price_min = backup.p_min
        price_max = backup.p_max

    except AttributeError:
        position_max = backup.parameters.n_positions
        price_min = backup.parameters.p_min
        price_max = backup.parameters.p_max

    position_A = pst[1:t_max, 0] / position_max
    position_B = pst[1:t_max, 1] / position_max
    price_A = prc[1:t_max, 0]
    price_B = prc[1:t_max, 1]

    color_A = "orange"
    color_B = "blue"

    # Position firm A
    ax = plt.subplot(gs[0, 0])
    ax.plot(t, position_A, color=color_A, alpha=1, linewidth=1.1)
    ax.plot(t, np.ones(len(t)) * 0.5, color='0.5', linewidth=0.5, linestyle='dashed', zorder=-10)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.set_xticks([])
    ax.set_yticks([0, 1])
    ax.set_ylabel('Pos. A', labelpad=16)
    for tick in ax.get_xticklabels():
        tick.set_fontsize("small")
    for tick in ax.get_yticklabels():
        tick.set_fontsize("small")

    # Add title
    # plt.title("$r={}$".format(backup.parameters.r))

    # Position firm B
    ax = plt.subplot(gs[1, 0])
    ax.plot(t, position_B, color=color_B, alpha=1, linewidth=1.1)
    ax.plot(t, np.ones(len(t)) * 0.5, color='0.5', linewidth=0.5, linestyle='dashed', zorder=-10)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.set_xticks([])
    ax.set_yticks([0, 1])
    ax.set_ylabel('Pos. B', labelpad=16)
    for tick in ax.get_xticklabels():
        tick.set_fontsize("small")
    for tick in ax.get_yticklabels():
        tick.set_fontsize("small")

    # Price firm A
    ax = plt.subplot(gs[2, 0])
    ax.plot(t, price_A, color=color_A, alpha=1, linewidth=1.1, clip_on=False)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.set_xticks([])
    ax.set_yticks([price_min, price_max])
    ax.set_ylabel('Price A', labelpad=10)  # , rotation=0)
    ax.set_ylim([price_min, price_max])
    for tick in ax.get_xticklabels():
        tick.set_fontsize("small")
    for tick in ax.get_yticklabels():
        tick.set_fontsize("small")

    # Price firm B
    ax = plt.subplot(gs[3, 0])
    ax.plot(t, price_B, color=color_B, alpha=1, linewidth=1.1, clip_on=False)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.set_xticks([])
    ax.set_yticks([price_min, price_max])
    ax.set_ylabel('Price B', labelpad=10)  # , rotation=0)
    ax.set_ylim([price_min, price_max])

    ax.set_xlabel("Time", labelpad=10)
    for tick in ax.get_xticklabels():
        tick.set_fontsize("small")
    for tick in ax.get_yticklabels():
        tick.set_fontsize("small")

    if letter:
        ax.text(
            s=letter, x=-0.3, y=-0.4, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
            fontsize=20)
