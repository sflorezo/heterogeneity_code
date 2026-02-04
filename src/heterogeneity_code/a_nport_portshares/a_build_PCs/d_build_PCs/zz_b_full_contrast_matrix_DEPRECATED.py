#%% ========== params ========== %%#
# FIXME: Params

_lambda = 1e-4

#%% ========== uplload libraries ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet, statatab, sumstats, test_time
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from typing import cast
import numpy as np
from sklearn.decomposition import PCA
from joblib import Parallel, delayed

# from pysfo.basic import *

#%% ========== initialize work objects and configs ========== %%#

PROCESSED_NPORT = Path(CONFIGS["PATHS"]["PROCESSED_NPORT"])
PROJECT_TEMP = Path(CONFIGS["PATHS"]["PROJECT_TEMP"])

random_seed = CONFIGS["GENERAL"]["random_seed"]
n_workers = CONFIGS["GENERAL"]["n_workers"]
batch_job_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]

#%% ========== helper functions ========== %%#

def _drop_smallest_funds_in_quarter(quarterly_assetcat_shares_df):

    df = quarterly_assetcat_shares_df.copy()

    if df["quarterly"].nunique() != 1:

        raise ValueError("quarterly_assetcat_shares_df must contain only data for one quarter.")
    
    # drop smallest funds 

    smallest_funds = (
        df[["fund_id", "fund_total_assets"]]
        .drop_duplicates()
        .sort_values(by = "fund_total_assets")
    )
    smallest_funds["total"] = smallest_funds["fund_total_assets"].sum()
    smallest_funds["cumshare"] = (smallest_funds["fund_total_assets"] / smallest_funds["total"]).cumsum()

    mask = smallest_funds["cumshare"] <= 0.01
    smallest_funds = smallest_funds.loc[mask, "fund_id"].to_list()

    keep = [fund_id not in smallest_funds for fund_id in df["fund_id"]]
    df = df[keep].reset_index()

    return df
    
def _quarterly_build_Cij_PC(quarterly_assetcat_shares_df):

    # quarterly_assetcat_shares_df = df_list[0]

    df = quarterly_assetcat_shares_df.copy()

    if df["quarterly"].nunique() != 1:

        raise ValueError("quarterly_assetcat_shares_df must contain only data for one quarter.")

    df = df.rename(columns={"w": "s"})

    #--- compute bilateral contrasts ----#

    mask = df["fund_id"].duplicated()

    all_funds = df[~mask][["fund_id", "fund_total_assets"]]
    all_funds["fund_weight"] = all_funds["fund_total_assets"] / all_funds["fund_total_assets"].max()
    all_asset_buckets = df[["asset_bucket"]].drop_duplicates()

    bilateral = all_asset_buckets.merge(all_asset_buckets, how = "cross")
    bilateral = all_funds.merge(bilateral, how = "cross")
    
    bilateral = (
        bilateral.rename(
            columns = {
                "asset_bucket_x" : "asset_bucket_i",
                "asset_bucket_y" : "asset_bucket_j"
            }
        )
    )

    for i in ["i", "j"]:

        bilateral = (
            bilateral.merge(
                df[["fund_id", "asset_bucket", "s", "currency_value"]],
                left_on = ["fund_id", f"asset_bucket_{i}"],
                right_on = ["fund_id", "asset_bucket"],
                how = "left",
                validate = "m:1"
            )
            .drop(columns = "asset_bucket")
        )

        bilateral["s"] = bilateral["s"].fillna(0)
        bilateral["currency_value"] = bilateral["currency_value"].fillna(0)
        bilateral.rename(columns = {
            "s": f"s_{i}",
            "currency_value" : f"currency_value_{i}"
        }, inplace = True)

    # drop non-informative positons (decide not to do for now)

    # mask = (bilateral["s_i"] == 0) & (bilateral["s_j"] == 0)
    # bilateral = bilateral[~mask].copy()

    # compute bilateral contrasts

    bilateral["_c_ij_pre_w"] = bilateral["currency_value_i"].abs() + bilateral["currency_value_j"].abs()
    bilateral["_c_ij_w_denom"] = bilateral.groupby("fund_id")["_c_ij_pre_w"].transform("sum")
    bilateral["_c_ij_w"] = bilateral["_c_ij_pre_w"] / bilateral["_c_ij_w_denom"]
    
    bilateral["c_ij"] = (
        (bilateral["_c_ij_w"]) * 
        (bilateral["s_i"] - bilateral["s_j"]) / ( bilateral["s_i"] + bilateral["s_j"] + _lambda)
    )

    _cij_min = bilateral["c_ij"].quantile(0.01)
    _cij_max = bilateral["c_ij"].quantile(0.99)
    bilateral["c_ij"] = np.where(bilateral["c_ij"] < _cij_min, _cij_min, bilateral["c_ij"])
    bilateral["c_ij"] = np.where(bilateral["c_ij"] > _cij_max, _cij_max, bilateral["c_ij"])

    # bilateral contrast (C_ij) matrix

    bilateral.drop(columns = bilateral.filter(regex = r"^_c_ij").columns, inplace = True)
    bilateral.drop(columns = bilateral.filter(regex = r"^currency_value").columns, inplace = True)
    bilateral.drop(columns = bilateral.filter(regex = r"^s_").columns, inplace = True)

    C_ij = (
        bilateral[["fund_id", "asset_bucket_i", "asset_bucket_j", "c_ij"]]
        .pivot_table(values = "c_ij",
                    index = "fund_id",
                    columns = ["asset_bucket_i", "asset_bucket_j"])
    )

    #--- Get principal components ----#

    K = 10
    pca = PCA(n_components=K, random_state=cast(int, random_seed))

    X_pc = pca.fit_transform(C_ij)
    X_pc = pd.DataFrame(X_pc, columns = [f"pc_{i}" for i in range(1, 11)])
    X_pc.index = C_ij.index
    X_pc = X_pc.reset_index()

    # pca.explained_variance_ratio_

    #--- merge with fund names and save working data ----#

    fund_ids = df[["quarterly", "fund_id", "fund_id_desc", "series_id", "series_lei", "series_name", "registrant_lei", "registrant_name"]].drop_duplicates()
    X_pc_ = pd.merge(fund_ids, X_pc, on = "fund_id")

    # X_pc_["quarterly"]

    return X_pc_

#%% ========== fullpanel_build_Cij_PC ========== %%#

def fullpanel_build_Cij_PC():

    df = load_parquet(PROJECT_TEMP / "NPORT_assetcat_portfolioshares.parquet")

    df_list = [
        df[df["quarterly"] == yq]
        for yq in df["quarterly"].unique()
    ]

    # drop smallest funds 

    df_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_drop_smallest_funds_in_quarter)(df) 
        for df in df_list
    )

    # build bilateral contrasts

    df_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_quarterly_build_Cij_PC)(df) 
        for df in df_list
    )

    # consolidate panel

    df = pd.concat(df_list, axis = 0)
    
    # save
    
    save_parquet(df, PROJECT_TEMP / "PC_assetcat_Cij_funds.parquet")
    print("Saved PROJECT_TEMP/PC_assetcat_Cij_funds.parquet")
