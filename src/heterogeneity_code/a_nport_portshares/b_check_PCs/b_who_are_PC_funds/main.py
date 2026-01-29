# pyright: reportAttributeAccessIssue=false

#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd
from heterogeneity_code.a_nport_portshares.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

#%% ========= Upload data ========== %%#

df = fetch_PCs_with_fund_info()

#%% ========= quarterly mean of PCs ========== %%#

PC_cols = (df.filter(regex = r"pc_\d").columns)

agg_dict = {
    f"{col}_mean": (col, "mean")
    for col in PC_cols
} | {
    f"{col}_std": (col, "std")
    for col in PC_cols
}

out = df.groupby("quarterly").agg(**agg_dict).reset_index()

plt.figure()
for col in PC_cols:
    mean_col = out[col + "_mean"]
    period_col = out["quarterly"].dt.to_timestamp() # pyright: ignore[reportAttributeAccessIssue]

    plt.plot(period_col, mean_col, label = col)
    plt.legend()
plt.show()

#%% ========= See who are the main funds identified by components ========== %%#


pc = "pc_1"


fund_ids = (
    df[["fund_id", "series_name", "quarterly", "fund_total_assets"]]
    .sort_values(by = ["fund_id", "series_name", "quarterly"])
    .groupby(["fund_id"])
    .last()
    .reset_index()
)

mask0 = fund_ids["series_name"].isna()
fund_ids = fund_ids[~mask0]




#%% ========== See some important funds ========== %%#

# FIXME: Old, deprecated. See if this can be eliminated.

fund_ids = (
    df[["fund_id", "series_name", "quarterly", "fund_total_assets"]]
    .sort_values(by = ["fund_id", "series_name", "quarterly"])
    .groupby(["fund_id"])
    .last()
    .reset_index()
)

mask0 = fund_ids["series_name"].isna()
fund_ids = fund_ids[~mask0]

# Bonds, active: Pimco tot ret

mask = fund_ids["series_name"].str.contains("^pimco total return", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
pimco_totret = "GCOBPT5OHTVIN37L8N43"
pimco_totret_ = df[df["fund_id"] == pimco_totret].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(pimco_totret_["quarterly"].dt.to_timestamp(), pimco_totret_[pc], label = pc)
plt.legend()

# Bonds, passive: Vanguard Total Bond Market Index Fund

mask = fund_ids["series_name"].str.contains("^vanguard total bond market", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
vanguard_totbond = "CIJB0QNLPT2SSWMJ5W92"
vanguard_totbond_ = df[df["fund_id"] == vanguard_totbond].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(vanguard_totbond_["quarterly"].dt.to_timestamp(), vanguard_totbond_[pc], label = pc)
plt.legend()

# Equity, active: Fidelity Magellan Fund

mask = fund_ids["series_name"].str.contains("^fidelity magellan", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
fidelity_magellan = "YHT3QK75G1JTE4XRDE89"
fidelity_magellan_ = df[df["fund_id"] == fidelity_magellan].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(fidelity_magellan_["quarterly"].dt.to_timestamp(), fidelity_magellan_[pc], label = pc)
plt.legend()

# Equity, active: Vanguard 500 Index Fund

mask = fund_ids["series_name"].str.contains("^vanguard 500", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
vanguard_500 = "12WZ1W76P8QD4VJ6OB47"
vanguard_500_ = df[df["fund_id"] == vanguard_500].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(vanguard_500_["quarterly"].dt.to_timestamp(), vanguard_500_[pc], label = pc)
plt.legend()

