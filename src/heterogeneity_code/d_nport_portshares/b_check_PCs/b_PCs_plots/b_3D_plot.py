# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false
# pyright: reportIndexIssue=false

#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd
from heterogeneity_code.d_nport_portshares.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info
from heterogeneity_code.d_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import portfolio_weights_df
import numpy as np
from matplotlib.ticker import MultipleLocator
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
OUT_PATH = CONFIGS["PATHS"]["OUT_PATH"]

aggregation_level = CONFIGS["NPORT"]["build_PCs"]["aggregation_level"]

#%% ========== See funds in 2-dimensional space of components ========== %%#

df = fetch_PCs_with_fund_info()

_plot = {}

for q in df["quarterly"].unique():

    _q = df[df["quarterly"] == q]

    drop = (
        (_q["pc_1"] <= _q["pc_1"].quantile(0.015)) 
        | (_q["pc_1"] >= _q["pc_1"].quantile(0.985))
        | (_q["pc_2"] <= _q["pc_2"].quantile(0.015)) 
        | (_q["pc_2"] >= _q["pc_2"].quantile(0.985))
    )

    _q = _q[~drop]

    _plot[str(q)] = {
        "pc_1" : _q["pc_1"],
        "pc_2" : _q["pc_2"],
        "w" : (_q["fund_total_assets"]  / _q["fund_total_assets"].max()) * 50
    }
    
    _q[["pc_1", "pc_2"]]

#---- Figure creation

quarters = ["2019Q4", "2020Q1", "2020Q2", "2020Q3", "2020Q4", "2021Q1", "2021Q2", "2021Q3"]
q_to_i = {q: i for i, q in enumerate(quarters)}  # quarter -> numeric axis

fig = plt.figure(figsize=(30, 6))
ax = fig.add_subplot(111, projection="3d")

for q in quarters:
    x = _plot[q]["pc_1"].to_numpy()
    z = _plot[q]["pc_2"].to_numpy()
    y = np.full_like(x, fill_value=q_to_i[q], dtype=float)  # quarter axis (horizontal)
    s = _plot[q]["w"].to_numpy()

    ax.scatter(x, y, z, s=s, alpha=0.6, depthshade=False, label=q)

# Axis labels (note: quarter is Y here)
ax.set_xlabel("PC 1")
ax.set_ylabel("")
ax.set_zlabel("PC 2")

# Put quarter labels on the quarter axis
ax.set_yticks(list(q_to_i.values()))  # quarter axis (horizontal
ax.set_yticklabels(quarters)

for label in ax.get_yticklabels():
    label.set_rotation(45)
    label.set_ha("right")

# Make the quarter axis look like a horizontal sweep across the screen
ax.view_init(elev=15, azim=-15)

ax.xaxis.set_major_locator(MultipleLocator(1.0))
ax.xaxis.set_minor_locator(MultipleLocator(0.5))  # faint intermediate grid
ax.tick_params(axis="x", which="major", length=6)
ax.tick_params(axis="x", which="minor", length=3)

# ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))

fig.subplots_adjust(
    left=0.00,
    right=0.88,
    bottom=0.22,
    top=1.00
)

plt.savefig(OUT_PATH / "3D_plot.pdf", 
            bbox_inches="tight",
            pad_inches=0.45
            )
plt.show()
# %%
