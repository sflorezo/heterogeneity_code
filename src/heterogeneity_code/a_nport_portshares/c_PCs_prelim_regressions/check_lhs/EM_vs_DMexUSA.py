# pyright: reportArgumentType=false
# pyright: reportIndexIssue=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportAttributeAccessIssue=false

#%% ========== params ========== %%#
# FIXME: temporal params

do_check_figs = False
generate_regressions = False

#%% ========== project-wide configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet
from pysfo import paralell_utils
from heterogeneity_code.a_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import _keep_bond_funds
from heterogeneity_code.a_nport_portshares.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import pandas as pd

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
OUT_PATH = CONFIGS["PATHS"]["OUT_PATH"]

random_seed = CONFIGS["GENERAL"]["random_seed"]
n_workers = CONFIGS["GENERAL"]["n_workers"]
batch_job_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]

process_quarters = CONFIGS["NPORT"]["process_quarters"]

#%% ========== script-specific configs ========== %%#

_start_quarter = process_quarters["start"]
_end_quarter = process_quarters["end"]
fund_collapsed_hdgs_file = PROJECT_TEMP / f"fund_collapsed_hdgs_file_{_start_quarter}_{_end_quarter}.parquet"

#%% ========== helper functions ========== %%#

def _build_fund_panel_collapsed_by_EM_DM_holdings():

    from pysfo import paralell_utils
    from heterogeneity_code.a_nport_portshares.c_PCs_prelim_regressions.b_make_regressions import _collapse_debt_holdings_EM_DM_USA
    from pysfo.basic import groupby_apply_various

    #check that function is not run in paralell

    if paralell_utils.is_nested_parallel():

        _message = (
            "[build_regression_results_df] build_regression_results_df runs in parallel, and cannot itself be called in a paralellized job."
            "Please check the code and try again."
            "(Suggestion: Run build_regression_results_df() before calling the paralellized job.)"
        )
    
        raise paralell_utils.errors.NestedParallelError(_message)
    
    # Define collapse function (to be run in paralell)
    
    def _quarterly_collase(yq):

        ###
        # yq = "2025q3"
        ###

        # function params

        df = _collapse_debt_holdings_EM_DM_USA(yq)
        
        # stats

        # df[_currencyval_cols + "_mill"] = df[_currencyval_cols] / 1e6
        # df[_currencyval_cols + "_assetshare"] = df[_currencyval_cols].div(df["fund_total_assets"], axis=0)

        # collapse

        issuers = ["EM", "DM", "USA"]

        operations = {
            f"{iss}_mill" : {"fn" : lambda x : np.mean(x) / 1e6, 
                                       "df_argnames" : f"currency_value_{iss}"}
            for iss in issuers
        } | {
            f"{iss}_assetshare" : {"fn" : lambda x, y : np.mean(x / y), 
                                   "df_argnames" : [f"currency_value_{iss}", "fund_total_assets"]}
            for iss in issuers
        }

        collapsed = (
            df
            .groupby("quarterly")
            .apply(lambda g: groupby_apply_various(g, operations))
            .reset_index()
        )
        
        return collapsed
    
    # build collapsed fund panel

    quarters = (
            pd
            .period_range(_start_quarter.upper(), 
                          _end_quarter.upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    print("[_build_fund_panel_collapsed_by_EM_DM_holdings] Building collapsed fund panel...")

    result_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_quarterly_collase)(yq) 
        for yq in quarters
    )

    df = pd.concat(result_list, axis = 0)

    save_parquet(df, fund_collapsed_hdgs_file)
    print(f"-> Saved {fund_collapsed_hdgs_file}")

def fetch_fund_collapsed_by_EM_DM_holdings():

    try :

        df = load_parquet(fund_collapsed_hdgs_file)

    except FileNotFoundError:   

        _msg = (
            "[fetch_fund_collapsed_by_EM_DM_holdings] fund_collapsed_hdgs_file not found. Please check.\n",
            "(Note: This should eventually be replaced with a function that builds the file.)"
        )

        raise FileNotFoundError(_msg)
    
    return df

#%% ========== check file ========== %%#

df = fetch_fund_collapsed_by_EM_DM_holdings()

plt.plot(df["quarterly"].dt.to_timestamp(), df["EM_mill"].diff() / df["EM_mill"].shift(1), label = "EM")
plt.plot(df["quarterly"].dt.to_timestamp(), df["DM_mill"].diff() / df["DM_mill"].shift(1), label = "DM (ex-USA)")
plt.legend()


#%% ========== not importable module safeguard ========== %%#

raise ValueError("This script is a check script, not meant to be imported.")