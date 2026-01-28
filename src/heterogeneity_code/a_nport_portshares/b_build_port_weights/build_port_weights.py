#%% ========== configs ========== %%#

# FIXME: These parameters should not be used in a final clean version

checks = False

#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from typing import cast, Dict
from pysfo.basic import load_parquet, save_parquet, relocate_columns
import pandas as pd
from joblib import Parallel, delayed 
import numpy as np
import matplotlib.pyplot as plt

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
process_quarters = cast(Dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]


#%% ========== helper functions ========== %%

def _keep_bond_funds(holdings_df: pd.DataFrame) -> pd.DataFrame:

    # yq = "2025q2"
    # holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")

    from heterogeneity_code.a_nport_portshares.a_select_sample.funds_that_hold_bonds import funds_that_hold_bonds_list

    bondfunds = funds_that_hold_bonds_list()
    bondfunds["bondfunds"] = 1

    holdings_df = pd.merge(holdings_df, bondfunds, on = ["accession_number", "quarterly"], how = "left", validate = "m:1")
    holdings_df = holdings_df[holdings_df["bondfunds"] == 1]

    return holdings_df

def _group_asset_cat_levels(df: pd.DataFrame, bool = True) -> pd.DataFrame:

    # df = holdings_df.copy()
    
    issuer = df["issuer_type"].astype("string").str.upper()
    act    = df["asset_cat_type"].astype("string").str.lower()

    asset_bucket = np.select(
        [
            issuer.isin(["USGSE", "USGA", "UST"]) & act.eq("debt"),  # 1) sovereign debt
            issuer.eq("CORP") & act.eq("debt"),                     # 2) corporate debt
            act.eq("equity"),                                       # 3) equity
            act.eq("loans"),                                        # 4) loans
        ],
        [
            "sovereign debt",
            "corporate debt",
            "equity",
            "loans",
        ],
        default="other",                                            # 5) other
    )

    if bool == True:

        df["asset_bucket"] = asset_bucket

    else :

        df["asset_bucket"] = df["asset_cat"]

    return df



#%% ========== buid portfolio shares ========== %%

def _build_quarterly_portfolio_shares(yq):
    
    ###
    # yq = "2020q2"
    ###

    holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")

    # group asset cat levels

    holdings_df = _group_asset_cat_levels(holdings_df, bool = True)

    # collapse at asset_cat_level

    fund_ids = ["accession_number", "fund_id", "quarterly"]
    asset_cat_ids = ["asset_bucket"] # ["asset_cat", "asset_cat_type", "asset_cat_desc"]
    fund_vars = [
        item for item in
        (
            holdings_df.filter(regex = "^fund_").columns.to_list()
            + holdings_df.filter(regex = "^series_").columns.to_list()
            + holdings_df.filter(regex = "^registrant_").columns.to_list()
        )
        if item != "fund_id"
    ]

    agg_dict_sum = {
        "currency_value": "sum",
    }
    agg_dict_first = {
        fund_var : "first" for fund_var in fund_vars
    }

    holdings_df = (
        holdings_df.groupby(fund_ids + asset_cat_ids)
        .agg({**agg_dict_sum, **agg_dict_first})
        .reset_index()
    )

    # build asset cat portfolio shares (wrt to fund_total_assets)

    holdings_df["w"] = holdings_df["currency_value"] / holdings_df["fund_total_assets"]
    holdings_df = relocate_columns(
        holdings_df,
        cols_to_move = ["w"],
        anchor_col = "currency_value",
        how = "after"
    )
    
    # return

    return holdings_df

#%% ========== build_portf_weights ========== %%#

def build_portf_weights():

    quarters = (
            pd
            .period_range(process_quarters["start"].upper(), 
                        process_quarters["end"].upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
            delayed(_build_quarterly_portfolio_shares)(q) for q in quarters
        )

    df = pd.concat(df_list, axis = 0)

    save_parquet(df, PROJECT_TEMP / "NPORT_assetcat_portfolioshares.parquet")
    print("Saved PROJECT_TEMP/NPORT_assetcat_portfolioshares.parquet")

#%% ========== import portfolio weights dataset ========== %%#

def portfolio_weights_df(type = "bond_funds"):

    df = load_parquet(PROJECT_TEMP / "NPORT_assetcat_portfolioshares.parquet")

    # select type
    
    if type == "bond_funds":
        df = _keep_bond_funds(df)
    elif type == "all" :
        pass

    df = (
        df.groupby(["fund_id", "quarterly", ""])
    )

    return df    

#%% ========== checks ========== %%#

if checks:

    df = portfolio_weights_df()

    _plot = df["w"][(df["w"] >= np.quantile(df["w"], 0.01)) & (df["w"] <= np.quantile(df["w"], 0.99))]

    plt.hist(_plot)