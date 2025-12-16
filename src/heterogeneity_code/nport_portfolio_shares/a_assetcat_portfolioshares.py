#%% ========== headers ========== %%#

from configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet, statatab, sumstats, test_time
from pathlib import Path
import pandas as pd
from typing import cast, Dict
import matplotlib.pyplot as plt
import numpy as np
import umap
import random
from sklearn.decomposition import PCA

# from pysfo.basic import *

PROCESSED_NPORT = Path(CONFIGS["PATHS"]["PROCESSED_NPORT"])
PROJECT_TEMP = Path(CONFIGS["PATHS"]["PROJECT_TEMP"])

random_seed = CONFIGS["GENERAL"]["random_seed"]

#%% ========== helper functions ========== %%#


#%% ========== work 2025Q2 data ========== %%#

assetcat_shares = load_parquet(PROCESSED_NPORT / "NPORT_assetcat_portfolioshares.parquet")
assetcat_shares = assetcat_shares[assetcat_shares["quarterly"] == "2025Q2"]

# see distribution of fund_assets (Huge high outliers)

plt.hist(
    assetcat_shares["fund_total_assets"], 
    bins=100, 
    range = (-0.25e12, 0.5e12)
)

# drop smallest funds 

smallest_funds = (
    assetcat_shares[["fund_id", "fund_total_assets"]]
    .drop_duplicates()
    .sort_values(by = "fund_total_assets")
)
smallest_funds["total"] = smallest_funds["fund_total_assets"].sum()
smallest_funds["cumshare"] = (smallest_funds["fund_total_assets"] / smallest_funds["total"]).cumsum()

mask = smallest_funds["cumshare"] <= 0.01
smallest_funds = smallest_funds.loc[mask, "fund_id"].to_list()

keep = [fund_id not in smallest_funds for fund_id in assetcat_shares["fund_id"]]
assetcat_shares = assetcat_shares[keep].reset_index()

# save

save_parquet(assetcat_shares, PROJECT_TEMP / "assetcat_shares_2025q2.parquet")
del assetcat_shares

#%% ========== see assetcat portfolioshares ========== %%#

fundshares = load_parquet(PROJECT_TEMP / "assetcat_shares_2025q2.parquet")
fundshares = fundshares.rename(columns={"w": "s"})

#---- params ----#
# FIXME: Params
_lambda = 1e-4

#---- small histogram to see portfolio shares distribution in period ----#

sumstats(fundshares["s"])
# unw
plt.hist(fundshares["s"], bins=20, range = (0, 3))
# w
plt.hist(fundshares["s"], bins=20, range = (0, 3), weights=fundshares["currency_value"])
plt.close()

#--- compute bilateral contrasts ----#

all_funds = fundshares[["fund_id"]].drop_duplicates()
all_asset_cats = fundshares[["asset_cat"]].drop_duplicates()

bilateral = all_asset_cats.merge(all_asset_cats, how = "cross")
bilateral = all_funds.merge(bilateral, how = "cross")
bilateral = (
    bilateral.rename(
        columns = {
            "asset_cat_x" : "asset_cat_i",
            "asset_cat_y" : "asset_cat_j"
        }
    )
)

for i in ["i", "j"]:

    bilateral = (
        bilateral.merge(
            fundshares[["fund_id", "asset_cat", "s"]],
            left_on = ["fund_id", f"asset_cat_{i}"],
            right_on = ["fund_id", "asset_cat"],
            how = "left",
            validate = "m:1"
        )
        .drop(columns = "asset_cat")
    )

    bilateral["s"] = bilateral["s"].fillna(0)
    bilateral.rename(columns = {"s": f"s_{i}"}, inplace = True)
    
bilateral["c_ij"] = (bilateral["s_i"] - bilateral["s_j"]) / ( bilateral["s_i"] + bilateral["s_j"] + _lambda)

sumstats(bilateral["c_ij"])
plt.hist(bilateral["c_ij"], bins=100, range = (-1.2, 1.2))
plt.show()
plt.close()

_cij_min = bilateral["c_ij"].quantile(0.01)
_cij_max = bilateral["c_ij"].quantile(0.99)
bilateral["c_ij"] = np.where(bilateral["c_ij"] < _cij_min, _cij_min, bilateral["c_ij"])
bilateral["c_ij"] = np.where(bilateral["c_ij"] > _cij_max, _cij_max, bilateral["c_ij"])

# bilateral contrast (C_ij) matrix

C_ij = (
    bilateral[["fund_id", "asset_cat_i", "asset_cat_j", "c_ij"]]
    .pivot_table(values = "c_ij",
                 index = "fund_id",
                 columns = ["asset_cat_i", "asset_cat_j"])
)

#--- Get principal components ----#

K = 10
pca = PCA(n_components=K, random_state=cast(int, random_seed))

X_pc = pca.fit_transform(C_ij)
X_pc = pd.DataFrame(X_pc, columns = [f"pc_{i}" for i in range(1, 11)])
X_pc.index = C_ij.index
X_pc = X_pc.reset_index()

pca.explained_variance_ratio_


#--- merge with fund names and check description ----#

fund_names = fundshares[["fund_id", "series_name"]].drop_duplicates()
X_pc_ = pd.merge(fund_names, X_pc, on = "fund_id")

for k in range(1, K+1):
    print(k)
    X_pc_ = X_pc_.sort_values(by = f"pc_{k}", ascending = False)
    top = [
        item if item is not None else "None" 
        for item in X_pc_["series_name"].head(10).to_list()
    ]
    bottom = [
        item if item is not None else "None" 
        for item in X_pc_["series_name"].tail(10).to_list()
    ]

    lines = "\n".join(
        ["\n#========== TOP ==========#\n"]
        + top
        + ["\n#========== BOTTOM ==========#\n"]
        + bottom
    )

    with open(PROJECT_TEMP / f"pc_{k}.txt", "w") as f:
        f.writelines(lines)
    
#---- temp

bilateral.head(4)

