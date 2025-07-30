from mwtoolbox import smithplot
import matplotlib.pyplot as plt 
import numpy as np

# fig1 = plt.figure(figsize=(15, 7), layout="constrained")
# ax1 = smithplot.get_smith(fig1, 121, plot_impedance=True, plot_ticks=False, plot_admittance=True, plot_labels=True,)

fig2 = plt.figure(figsize=(15, 7), layout="constrained")
ax2 = smithplot.get_smith(fig2, 121, plot_impedance=True,
                          plot_ticks=False, plot_admittance=True, plot_labels=True,
                          # resticks=[0.5,1.0,1.5,2.0],
                          xlim=(-1,0.5), ylim=(-1,0.5))

# fig3 = plt.figure(figsize=(15, 7), layout="constrained")
# ax3 = smithplot.get_smith(fig3, 121, plot_impedance=False, plot_ticks=False, plot_admittance=True, plot_labels=True,)

# for ax in [ax2]:
#     ax.set_xlim([-0.5,0.5])
#     ax.set_ylim([-0.5,0.5])

# fig1.savefig("only_admittance_impedance.png")
# fig2.savefig("only_impedance.png")
# fig3.savefig("only_admittance.png")

plt.show()
