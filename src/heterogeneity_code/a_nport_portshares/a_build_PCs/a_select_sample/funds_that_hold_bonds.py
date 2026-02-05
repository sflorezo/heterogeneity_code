#%% ========== project-wide configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from typing import cast, Dict
from pysfo.basic import load_parquet, save_parquet, relocate_columns
from pysfo import paralell_utils
import pandas as pd
from joblib import Parallel, delayed
from joblib.parallel import get_active_backend
import numpy as np
import time

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
process_quarters = cast(Dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]

#%% ========== script-specific configs ========== %%#

_start_q = process_quarters["start"]
_end_q = process_quarters["end"]
funds_that_hold_bonds_file = PROJECT_TEMP / f"NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet"

#%% ========== Helper Functions ========== %%#

def _funds_that_hold_bonds_inquarter(yq : str) -> pd.DataFrame:

    ####
    # yq = "2024q4"
    ####
    
    # function params

    holdings_yq_file = PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet"
    fund_info_df_file = PROCESSED_NPORT / f"NPORT_funds_allQuarters.parquet"

    # needed files check

    for file in [holdings_yq_file, fund_info_df_file]:
        if not file.exists():
            _message = (
                f"[_funds_that_hold_bonds_inquarter] File not found {file}.\n"
                "Please run clean_nport before running this function"
            )
            raise FileNotFoundError(_message)

    # holdings data (to see who holds bonds)

    holdings_df = load_parquet(holdings_yq_file)

    holdings_df["hold_bonds"] = holdings_df["asset_cat"] == "DBT"
    holdings_df["hold_bonds"] = (
        holdings_df.groupby("accession_number")["hold_bonds"]
        .transform(lambda x : int(x.max()))
    )
    hold_bonds_df = (
        holdings_df[holdings_df["hold_bonds"] == 1][["accession_number", "quarterly"]]
        .drop_duplicates()
        .reset_index(drop = True)
    )

    # merge with fund_id

    fund_info_df = load_parquet(fund_info_df_file)
    fund_info_df = fund_info_df[["accession_number", "quarterly", "fund_id"]]

    hold_bonds_df = hold_bonds_df.merge(fund_info_df, on = ["accession_number", "quarterly"], how = "left")
    hold_bonds_df = hold_bonds_df[["fund_id", "quarterly"]].drop_duplicates()

    return hold_bonds_df


#%% ========== callable work functions ========== %%#

def create_funds_that_hold_bonds_list():

    '''
    Function that creates list of funds that hold bonds, in paralell
    '''

    # check that function is not run in paralell

    if paralell_utils.is_nested_parallel():
        
        _message = (
            "[create_funds_that_hold_bonds_list] create_funds_that_hold_bonds_list() runs in parallel, and cannot itself be called in a paralellized job.\n",
            "Please check the code and try again.\n",
            "(Suggestion: Run create_funds_that_hold_bonds_list() before calling the paralellized job.)"
        )
        
        raise paralell_utils.errors.NestedParallelError(_message)
    
    
    # and if it is not, then run...

    print("[create_funds_that_hold_bonds_list] Creating funds that hold bonds list...")

    quarters = (
            pd
            .period_range(_start_q.upper(), 
                        _end_q.upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
            delayed(_funds_that_hold_bonds_inquarter)(q) for q in quarters
        )

    df = pd.concat(df_list, axis = 0)

    time.sleep(2)

    save_parquet(df, funds_that_hold_bonds_file)
    print(f"-> Saved {funds_that_hold_bonds_file}")

def fetch_funds_that_hold_bonds_list():

    '''
    Requirements:
    - PROJECT_TEMP/f"NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet"
    '''
    
    # run rest of code

    try :
        
        bondfunds = load_parquet(funds_that_hold_bonds_file)

    except FileNotFoundError :

        _message = (
            f"[fetch_funds_that_hold_bonds_list] File with NPORT funds that hold bonds ({_start_q} - {_end_q}) not found.\n"
            "Proceeding to build it..."
        )
        print(_message)

        create_funds_that_hold_bonds_list()
        
        bondfunds = load_parquet(funds_that_hold_bonds_file)
        
    return bondfunds
