#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt

# from pysfo.basic import *

PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

#%% ========= Upload data ========== %%#

PC_panel = load_parquet(PROJECT_TEMP / "PC_assetcat_Cij_funds.parquet")

#%% ========= analysis ========== %%#

PC_cols = (PC_panel.filter(regex = r"pc_\d").columns)

agg_dict = {
    f"{col}_mean": (col, "mean")
    for col in PC_cols
} | {
    f"{col}_std": (col, "std")
    for col in PC_cols
}

out = PC_panel.groupby("quarterly").agg(**agg_dict).reset_index()

plt.figure()
for col in PC_cols:
    mean_col = out[col + "_mean"]
    period_col = out["quarterly"].dt.to_timestamp() # pyright: ignore[reportAttributeAccessIssue]

    plt.plot(period_col, mean_col, label = col)
    plt.legend()
plt.show()
# %%
