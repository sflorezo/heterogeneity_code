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

    return hold_bonds_df

#%% ========== Main Sample Selector ========== %%#

def funds_that_hold_bonds():

    quarters = (
            pd
            .period_range(process_quarters["start"].upper(), 
                        process_quarters["end"].upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    df_list = Parallel(n_jobs = joblib_n_workers, verbose = joblib_verbose)(
            delayed(_funds_that_hold_bonds_inquarter)(q) for q in quarters
        )

    df = pd.concat(df_list, axis = 0)

    save_parquet(df, PROJECT_TEMP / "NPORT_funds_that_hold_bonds.parquet")
    print("Saved PROJECT_TEMP/NPORT_funds_that_hold_bonds.parquet")


