# pyright: reportAttributeAccessIssue=false

#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

#%% ========= Upload data ========== %%#

PC_panel = load_parquet(PROJECT_TEMP / "PC_assetcat_Cij_funds.parquet")
fund_level_data = load_parquet(PROCESSED_NPORT / "NPORT_funds_allQuarters.parquet")

fund_level_data = fund_level_data[["fund_id", "quarterly", "fund_total_assets"]]

PC_panel = pd.merge(fund_level_data, PC_panel, on = ["fund_id", "quarterly"], how = "right")

#%% ========= quarterly mean of PCs ========== %%#

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

#%% ========== See some important funds ========== %%#

fund_ids = (
    PC_panel[["fund_id", "series_name", "quarterly", "fund_total_assets"]]
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
pimco_totret_ = PC_panel[PC_panel["fund_id"] == pimco_totret].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(pimco_totret_["quarterly"].dt.to_timestamp(), pimco_totret_[pc], label = pc)
plt.legend()

# Bonds, passive: Vanguard Total Bond Market Index Fund

mask = fund_ids["series_name"].str.contains("^vanguard total bond market", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
vanguard_totbond = "CIJB0QNLPT2SSWMJ5W92"
vanguard_totbond_ = PC_panel[PC_panel["fund_id"] == vanguard_totbond].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(vanguard_totbond_["quarterly"].dt.to_timestamp(), vanguard_totbond_[pc], label = pc)
plt.legend()

# Equity, active: Fidelity Magellan Fund

mask = fund_ids["series_name"].str.contains("^fidelity magellan", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
fidelity_magellan = "YHT3QK75G1JTE4XRDE89"
fidelity_magellan_ = PC_panel[PC_panel["fund_id"] == fidelity_magellan].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(fidelity_magellan_["quarterly"].dt.to_timestamp(), fidelity_magellan_[pc], label = pc)
plt.legend()

# Equity, active: Vanguard 500 Index Fund

mask = fund_ids["series_name"].str.contains("^vanguard 500", case = False)
fund_ids[mask].sort_values(by = "fund_total_assets", ascending = False)
vanguard_500 = "12WZ1W76P8QD4VJ6OB47"
vanguard_500_ = PC_panel[PC_panel["fund_id"] == vanguard_500].filter(regex = "pc_|quarterly")

for pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:
    plt.plot(vanguard_500_["quarterly"].dt.to_timestamp(), vanguard_500_[pc], label = pc)
plt.legend()

