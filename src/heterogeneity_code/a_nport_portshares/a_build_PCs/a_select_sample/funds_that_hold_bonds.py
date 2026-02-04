#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from typing import cast, Dict
from pysfo.basic import load_parquet, save_parquet, relocate_columns
import pandas as pd
from joblib import Parallel, delayed 
import numpy as np

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
process_quarters = cast(Dict, CONFIGS["NPORT"]["process_quarters"])
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]

#%% ========== Helper Functions ========== %%#

def _funds_that_hold_bonds_inquarter(yq : str) -> pd.DataFrame:

    ####
    # yq = "2024q4"
    ####

    # holdings data (to see who holds bonds)

    holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")

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

    fund_info_df = load_parquet(PROCESSED_NPORT / f"NPORT_funds_allQuarters.parquet")
    fund_info_df = fund_info_df[["accession_number", "quarterly", "fund_id"]]

    hold_bonds_df = hold_bonds_df.merge(fund_info_df, on = ["accession_number", "quarterly"], how = "left")
    hold_bonds_df = hold_bonds_df[["fund_id", "quarterly"]].drop_duplicates()

    return hold_bonds_df

def _create_funds_that_hold_bonds_list():

    '''
    Fundtion that creates list of funds that hold bonds, in paralell
    '''

    _start_q = process_quarters["start"]
    _end_q = process_quarters["end"]

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

    save_parquet(df, PROJECT_TEMP / f"NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet")
    print(f"Saved PROJECT_TEMP/NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet")


#%% ========== call list of funds that hold bonds ========== %%#

def funds_that_hold_bonds_list():

    _start_q = process_quarters["start"]
    _end_q = process_quarters["end"]

    try :
        
        bondfunds = load_parquet(PROJECT_TEMP / f"NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet")
    
    except FileNotFoundError:

        print(f"File with NPORT funds that hold bonds ({_start_q} - {_end_q}) not found. Creating it now")
        _create_funds_that_hold_bonds_list()
        bondfunds = load_parquet(PROJECT_TEMP / f"NPORT_funds_that_hold_bonds_{_start_q}_{_end_q}.parquet")

    return bondfunds
# %%
