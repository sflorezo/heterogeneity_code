#%% =========== project wide configs ==========#%%

from heterogeneity_code.a_configs import CONFIGS
import pysfo.pulldata as pysfo_pull
from pysfo.basic import save_parquet, load_parquet, dupli_report
from pysfo.geo_utils.country_groups import get_country_list_in_category
import country_converter as coco
from heterogeneity_code.c_compare_w_bis_ids.a_consolidate_eme_debt import get_bis_ids_eme_debt_panel
from heterogeneity_code.b_prep_nport_holdings.a_sample_selectors.funds_that_hold_bonds import keep_bond_funds
import pandas as pd
from matplotlib import pyplot as plt
from typing import cast
import pysfo.paralell_utils as paralell_utils
from joblib import Parallel, delayed
import time

# from pysfo.basic import *

DATA_RAW_PATH = CONFIGS["PATHS"]["DATA_RAW_PATH"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

process_quarters = cast(dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = cast(dict, CONFIGS["GENERAL"]["n_workers"])
joblib_verbose  = cast(dict, CONFIGS["GENERAL"]["batch_job_verbose"])


#%% =========== script specific configs ==========#%%

_start_q = process_quarters["start"]
_end_q = process_quarters["end"]

fund_holdings_by_country_file_name = PROJECT_TEMP / f"fund_holdings_by_country_{_start_q}_{_end_q}.parquet"

# %% =========== helper functions ==========#%%


    
# %% =========== caller ==========#%%

def build_fund_investments_by_investment_country_panel():

    #---- helper functions

    def _fund_investments_by_investment_country_in_quarter(yq):

        # yq = "2020q4"

        _hdgs_file_path = PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet"

        # get needed data

        holdings_df = load_parquet(_hdgs_file_path)

        # collapse holdings_df at the investment country level

        holdings_df = (
            holdings_df
            .groupby(["fund_id", "quarterly", "investment_country_iso2", "asset_cat", "asset_cat_type", "asset_cat_desc"])
            .agg({"currency_value" : "sum"})
            .reset_index()
        )

        return holdings_df

    #---- checker for exiting if function is run as a batch job

    if paralell_utils.is_nested_parallel():

        _message = (
            "[build_fund_investments_by_investment_country_panel] build_fund_investments_by_investment_country_panel runs in parallel, and cannot itself be called in a paralellized job."
            "Please check the code and try again."
            "(Suggestion: Run build_fund_investments_by_investment_country_panel() before calling the paralellized job.)"
        )
    
        raise paralell_utils.errors.NestedParallelError(_message)

    #---- rest of function

    # paralellize build

    print("Building fund investments by country...")

    _start_q = process_quarters["start"]
    _end_q = process_quarters["end"]

    quarters = (
            pd
            .period_range(_start_q.upper(), 
                          _end_q.upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )
    
    df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
            delayed(_fund_investments_by_investment_country_in_quarter)(q) for q in quarters
        )

    df = pd.concat(df_list, axis = 0)

    save_parquet(df, fund_holdings_by_country_file_name)
    print(f"-> Saved {fund_holdings_by_country_file_name}")
    
    time.sleep(2)

def get_fund_investments_by_country():

    try :
        df = load_parquet(fund_holdings_by_country_file_name)
    except FileNotFoundError:

        print("File not found. Building fund investments by country...")
        build_fund_investments_by_investment_country_panel()
        df = load_parquet(fund_holdings_by_country_file_name)

    return df