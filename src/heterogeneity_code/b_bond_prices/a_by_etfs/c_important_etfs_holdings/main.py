#%% ========== project-wide configs ========== %%#

from heterogeneity_code.a_configs import CONFIGS
from pysfo.basic import load_parquet
from itertools import chain
import pandas as pd
from joblib import Parallel, delayed
from typing import cast, Dict
from pysfo.basic import save_parquet, load_parquet, relocate_columns
from heterogeneity_code.b_bond_prices.a_by_etfs.a_params.ETFs_to_check import EM_DMexUS_US as funds_dict

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

process_quarters = cast(Dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]


#%% ========== script-specific configs ========== %%#

_start_q = process_quarters["start"]
_end_q = process_quarters["end"]

individual_fund_holdings_filename = f"individualholdings_panel_{_start_q}_{_end_q}_" + "{fund_ticker}.parquet"


#%% ========== helper function ========== %%#

def _build_holdings_panel_for_fund_ticker(fund_ticker):

    ####
    # fund_id = "54930070R8WH6MNUJG74"
    # fund_ticker = "EMB"
    ####

    from heterogeneity_code.b_bond_prices.a_by_etfs.a_params.ETFs_to_check import EM_DMexUS_US as funds_dict

    #---- helper functions

    def _find_closest(target_n, funds_df):

        from rapidfuzz import process, fuzz

        match, score, idx = process.extractOne(
            target_n,
            funds_df["series_name"].str.lower(),
            scorer=fuzz.WRatio
        )

        return {
            "match" : match,
            "score" : score,
            "idx" : idx
        }

    def _quarterly_fund_holdings(yq, fund_id):
    
        ####
        # yq = "2025q3"
        ####
        
        holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")
        keep = holdings_df["fund_id"] == fund_id
        holdings_df = holdings_df[keep]

        return holdings_df

    #---- interest funds nport identifiers

    all_tickers = [
        el["funds"][0]["ticker"]
        for el in funds_dict["data"]
    ]
    all_fund_names = [
        el["funds"][0]["full_name"]
        for el in funds_dict["data"]
    ]

    idx = next((i for i, x in enumerate(all_tickers) if x == fund_ticker), None)

    if idx is None:
        raise ValueError(f"Fund ticker {fund_ticker} not found in funds_dict.")
    
    myticker = all_tickers[idx]
    myfundname = all_fund_names[idx]

    #---- find closest fund by name

    funds_df = load_parquet(PROCESSED_NPORT / f"NPORT_funds_allQuarters.parquet")

    match = _find_closest(myfundname, funds_df)
    fund_id = funds_df.loc[match["idx"], "fund_id"]

    #---- get all holdings for all quarters
    
    quarters = (
            pd
            .period_range(_start_q.upper(), 
                          _end_q.upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )
    
    df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
            delayed(_quarterly_fund_holdings)(q, fund_id = fund_id) for q in quarters
        )

    df = pd.concat(df_list, axis = 0)
    df["fund_ticker"] = fund_ticker
    df = relocate_columns(df, cols_to_move = ["fund_ticker"], anchor_col = "fund_id")

    _save_filename = f"{individual_fund_holdings_filename.format(fund_ticker = fund_ticker)}"
    save_parquet(df, PROCESSED_NPORT / _save_filename)
    print(f"-> Saved {_save_filename}")

def _generate_fund_hdgs_for_interest_funds():

    ticker_list = [
        el["funds"][0]["ticker"]
        for el in funds_dict["data"]
    ]

    for ticker in ticker_list:
        print(f"\nGenerating full panel of holdings for fund ticker: {ticker}")

        _build_holdings_panel_for_fund_ticker(ticker)

    print("Finished creating individual fund holdings for interest funds.")




#%% ========== rest ========== %%#

# yq = "2025q3"
# holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")


# regions = [
#     el["region"]
#     for el in funds_dict["data"]
# ]
# target_names = [
#     el["funds"][0]["full_name"].lower()
#     for el in funds_dict["data"]
# ]

# matches = [
#     _find_closest(el, funds_df)
#     for el in target_names
# ]

# indices = [el["idx"] for el in matches]


# myfunds = funds_df.loc[indices, "fund_id"]

#---- get holdings of those

