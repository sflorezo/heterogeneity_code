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

def one_way_distance(C_ij):

    """
    Compute pairwise squared Euclidean distances between funds using a
    fund-by-block strategy.

    This function computes the distance between each fund f and all other
    funds by looping over f in Python and vectorizing over the contrast
    dimension and a block of comparison funds. It avoids materializing
    any (fund × fund × contrast) tensor and is therefore memory-safe for
    large N.

    Distance definition:
        D[f, g] = sum_k (C_ij[f, k] - C_ij[g, k])^2

    Parameters
    ----------
    C_ij : ndarray of shape (N, K)
        Matrix of bilateral contrasts, where rows correspond to funds and
        columns correspond to contrast dimensions.

    Returns
    -------
    D : ndarray of shape (N, N)
        Pairwise squared distance matrix. All entries are filled.

    Notes
    -----
    - Computation is O(N^2 · K) but memory usage is O(B · K), where B is
      the block size over funds.
    - Progress is printed every 500 funds.
    - This implementation is currently preferred in practice because it
      is faster and incurs less overhead than the two-way block version
      for typical values of N and K.

    """

    N, _ = C_ij.shape
    D = np.full((N, N), np.nan)

    B = 256
    for f in range(N):
        if f % 500 == 0:
            print(f"Iteration = {f} of {N}")
        for b in range(0, N, B):
            diff = C_ij[f] - C_ij[b:b+B]
            D[f, b:b+B] = np.sum(diff * diff, axis=1)

    return D


def twoway_distance(C_ij):

    """
    Compute pairwise squared Euclidean distances between funds using a
    block–block (two-way) vectorized strategy.

    This function computes distances between blocks of funds at once by
    broadcasting over two fund dimensions and the contrast dimension.
    Compared to the one-way version, this reduces Python loop overhead
    but increases temporary memory usage.

    Distance definition:
        D[f, g] = sum_k (C_ij[f, k] - C_ij[g, k])^2

    Parameters
    ----------
    C_ij : ndarray of shape (N, K)
        Matrix of bilateral contrasts, where rows correspond to funds and
        columns correspond to contrast dimensions.

    Returns
    -------
    D : ndarray of shape (N, N)
        Pairwise squared distance matrix. All entries are filled.

    Notes
    -----
    - Temporary working arrays have shape (Bf, Bg, K).
    - Memory usage scales with Bf · Bg · K and must be chosen carefully.
    - Progress is printed every 10 f-blocks.
    - Although more vectorized, this implementation is currently slower
      than `one_way_distance` in practice due to higher memory pressure
      and broadcasting overhead.

    """

    Bf = 2   # block size for f (4)
    Bg = 256  # block size for g

    N, _ = C_ij.shape
    D = np.full((N, N), np.nan)

    for f0 in range(0, N, Bf):
        f1 = min(f0 + Bf, N)
        C_f = C_ij[f0:f1]                  # (Bf, K)

        if f0 % 10 == 0:
            print(f"f block starting at {f0} (of {N} total funds)")

        for g0 in range(0, N, Bg):
            g1 = min(g0 + Bg, N)
            C_g = C_ij[g0:g1]              # (Bg, K)

            diff = C_f[:, None, :] - C_g[None, :, :]   # (Bf, Bg, K)
            D[f0:f1, g0:g1] = np.sum(diff * diff, axis=2)

    return D

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

#--- create df to compute fund distance ----#

all_funds = (fundshares[["fund_id"]].drop_duplicates()).reset_index(drop = True)
all_asset_cats = (fundshares["asset_cat"].drop_duplicates()).reset_index(drop = True)

bilateral = all_asset_cats[["asset_cat"]].merge(all_asset_cats, how = "cross")
bilateral = all_funds[["fund_id"]].merge(bilateral, how = "cross")
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
bilateral["w_ij"] = 1

plt.hist(bilateral["c_ij"], bins=100, range = (-1.2, 1.2))
plt.show()
plt.close()

# bilateral contrast (C_ij) and weights (W_ij) matrices

W_ij = (
    bilateral[["fund_id", "asset_cat_i", "asset_cat_j", "w_ij"]]
    .pivot_table(values = "w_ij",
                 index = "fund_id",
                 columns = ["asset_cat_i", "asset_cat_j"])
)

C_ij = np.array(
    bilateral[["fund_id", "asset_cat_i", "asset_cat_j", "c_ij"]]
    .pivot_table(values = "c_ij",
                 index = "fund_id",
                 columns = ["asset_cat_i", "asset_cat_j"])
)

#--- compute distance between pair of funds ----#

D = one_way_distance(C_ij)
D = 1 / (D + 1)
