# def dynamics_fig(force=False):
#
#     xp_examples = fit.exemplary_cases.get(force=force)
#     sim_examples = simulation.data.individual(force=force)
#
#     fig = plt.figure(figsize=(10, 8), dpi=200)
#     gs = matplotlib.gridspec.GridSpec(
#         nrows=4, ncols=5,
#         width_ratios=[0.13, 1, 1, 1, 1],
#         height_ratios=[0.12, 1, 0.2, 1])
#
#     # First row
#
#     analysis.dynamics.separate.eeg_like(
#         backup=sim_examples["max_profit"]["25"], subplot_spec=gs[1, 1], letter='A'
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=xp_examples["max_profit"]["25"], subplot_spec=gs[1, 2], letter=''
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=sim_examples["max_diff"]["25"], subplot_spec=gs[1, 3], letter='C'
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=xp_examples["max_diff"]["25"], subplot_spec=gs[1, 4], letter=''
#     )
#
#     # Second row
#
#     analysis.dynamics.separate.eeg_like(
#         backup=sim_examples["max_profit"]["50"], subplot_spec=gs[3, 1], letter='B'
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=xp_examples["max_profit"]["50"], subplot_spec=gs[3, 2], letter=''
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=sim_examples["tacit_collusion"]["50"], subplot_spec=gs[3, 3], letter='D'
#     )
#
#     analysis.dynamics.separate.eeg_like(
#         backup=xp_examples["tacit_collusion"]["50"], subplot_spec=gs[3, 4], letter=''
#     )
#
#     ax = fig.add_subplot(gs[:, :], zorder=-10)
#
#     plt.axis("off")
#
#     L, R = 0.3, 0.8
#     shift = 0.14
#
#     # Top left
#     ax.text(
#         s="Profit max.", x=L, y=1, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=15)
#     ax.text(
#         s="Sim.", x=L-shift, y=0.95, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#     ax.text(
#         s="Exp.", x=L+shift, y=0.95, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#
#     # Top right
#     ax.text(
#         s="Diff max.", x=R, y=1, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=15)
#
#     ax.text(
#         s="Sim.", x=R-shift, y=0.95, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#     ax.text(
#         s="Exp.", x=R+shift, y=0.95, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#
#     # Bottom left
#     ax.text(
#         s="Profit max.", x=L, y=0.43, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=15)
#
#     ax.text(
#         s="Sim.", x=L-shift, y=0.4, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#     ax.text(
#         s="Exp.", x=L+shift, y=0.4, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#
#     # Bottom right
#     ax.text(
#         s="Tacit collusion", x=R, y=0.43, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=15)
#
#     ax.text(
#         s="Sim.", x=R-shift, y=0.4, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#     ax.text(
#         s="Exp.", x=R+shift, y=0.4, horizontalalignment='center', verticalalignment='top', transform=ax.transAxes,
#         fontsize=13)
#
#     # Side
#
#     ax.text(
#         s="$r= 0.25$", x=0, y=0.75, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=15, rotation='vertical')
#     ax.text(
#         s="$r=0.50$", x=0, y=0.2, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
#         fontsize=15, rotation='vertical')
#
#     plt.tight_layout(pad=1)
#     plt.savefig("fig/dynamics.pdf")
#     plt.show()