# pyright: reportIndexIssue=false

#%% ========== params ========== %%#
# FIXME: Params

#%% ========== project-wide configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet, statatab, sumstats, test_time
from pysfo import paralell_utils
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from typing import cast
import numpy as np
from sklearn.decomposition import PCA
from joblib import Parallel, delayed

# from pysfo.basic import *

PROCESSED_NPORT = Path(CONFIGS["PATHS"]["PROCESSED_NPORT"])
PROJECT_TEMP = Path(CONFIGS["PATHS"]["PROJECT_TEMP"])

random_seed = CONFIGS["GENERAL"]["random_seed"]
n_workers = CONFIGS["GENERAL"]["n_workers"]
batch_job_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]
process_quarters = CONFIGS["NPORT"]["process_quarters"]
aggregation_level = CONFIGS["NPORT"]["build_PCs"]["aggregation_level"]

#%% ========== script-specific configs ========== %%#

_start_q = process_quarters["start"]
_end_q = process_quarters["end"]
funds_PC_file = PROJECT_TEMP / f"PC_assetcat_funds_{_start_q}_{_end_q}_aggLvl{aggregation_level}.parquet"

#%% ========== helper functions ========== %%#

def _drop_smallest_funds_in_quarter(quarterly_assetcat_shares_df):

    df = quarterly_assetcat_shares_df.copy()

    if df["quarterly"].nunique() != 1:

        raise ValueError("[_drop_smallest_funds_in_quarter] quarterly_assetcat_shares_df must contain only data for one quarter.")
    
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
    
def _quarterly_build_PC(quarterly_assetcat_shares_df):

    # quarterly_assetcat_shares_df = df_list[0]

    df = quarterly_assetcat_shares_df.copy()

    if df["quarterly"].nunique() != 1:

        raise ValueError("[_quarterly_build_PC] quarterly_assetcat_shares_df must contain only data for one quarter.")

    df = df.rename(columns={"w": "s"})

    #--- one-dimensional cross-sectional weights ----#

    W = df[["fund_id", "asset_bucket", "s"]].copy()
    W = (
        W
        .pivot(
            columns = ["asset_bucket"], 
            index = ["fund_id"], 
            values = ["s"]
        )
    )
    W.columns = W.columns.get_level_values(1)
    W.columns.name = None
    W.reset_index(inplace = True)
    W.iloc[:,1:] = W.iloc[:,1:].apply(lambda x : x.fillna(0))

    W = W.copy()
    W.set_index("fund_id", inplace = True)

    #--- Normalize data ----#

    W = (W - W.mean()) / W.std()

    drop_col = [True in list(~W[col].isna()) for col in W.columns]
    W = W.loc[:, drop_col]

    #--- Get principal components ----#

    K = 5
    pca = PCA(n_components=K, random_state=cast(int, random_seed))

    X_pc = pca.fit_transform(W)
    X_pc = pd.DataFrame(X_pc, columns = [f"pc_{i}" for i in range(1, K + 1)])
    X_pc.index = W.index
    X_pc = X_pc.reset_index()

    # pca.explained_variance_ratio_

    #--- merge with fund names and save working data ----#

    fund_ids = df[["quarterly", "fund_id", "fund_id_desc", "series_id", "series_lei", "series_name", "registrant_lei", "registrant_name"]].drop_duplicates()
    X_pc_ = pd.merge(fund_ids, X_pc, on = "fund_id")
    
    # X_pc_["quarterly"]

    return X_pc_


#%% ========== Call PCs dataset ========== %%#

def build_assetcat_PC_fullpanel():

    # packages

    from heterogeneity_code.a_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import portfolio_weights_df

    #check that function is not run in paralell

    if paralell_utils.is_nested_parallel():

        _message = (
            "[build_assetcat_PC_fullpanel] build_assetcat_PC_fullpanel runs in parallel, and cannot itself be called in a paralellized job."
            "Please check the code and try again."
            "(Suggestion: Run build_assetcat_PC_fullpanel() before calling the paralellized job.)"
        )
    
        raise paralell_utils.errors.NestedParallelError(_message)


    # load data
    
    df = portfolio_weights_df(keep_fund_type = "bond_funds")

    df_list = [
        df[df["quarterly"] == yq]
        for yq in df["quarterly"].unique()
    ]

    # drop smallest funds 

    print("[build_assetcat_PC_fullpanel] Dropping smallest funds...")

    df_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_drop_smallest_funds_in_quarter)(df) 
        for df in df_list
    )

    # build bilateral contrasts

    print("[build_assetcat_PC_fullpanel] Building assetcat PCs...")

    df_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_quarterly_build_PC)(df) 
        for df in df_list
    )

    # consolidate panel

    df = pd.concat(df_list, axis = 0)
    
    # save
    
    save_parquet(df, funds_PC_file)
    print(f"-> Saved {funds_PC_file}")

def fetch_PC_df():

    try :
        
        df = load_parquet(funds_PC_file)

    except FileNotFoundError:

        print(f"[fetch_PC_df] PCs dataframe ({_start_q} - {_end_q}) not found. Creating it now")
        build_assetcat_PC_fullpanel()
        df = load_parquet(funds_PC_file)

    return df
# %%
