#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from typing import cast, Dict
from pysfo.basic import load_parquet, save_parquet, relocate_columns
import pandas as pd
from joblib import Parallel, delayed 

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
process_quarters = cast(Dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]


#%% ========== buid portfolio shares ========== %%

def build_quarterly_portfolio_shares(yq):

    ###
    # yq = "2025q2"
    ###

    holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")

    # collapse at asset_cat_level

    fund_ids = ["fund_id", "quarterly"]
    asset_cat_ids = ["asset_cat", "asset_cat_type", "asset_cat_desc"]
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

#%% ========== headers ========== %%#

quarters = (
        pd
        .period_range(process_quarters["start"].upper(), 
                      process_quarters["end"].upper(), freq="Q")
        .astype(str).str.lower().tolist()
    )

df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
        delayed(build_quarterly_portfolio_shares)(q) for q in quarters
    )

df = pd.concat(df_list, axis = 0)

save_parquet(df, PROJECT_TEMP / "NPORT_assetcat_portfolioshares.parquet")