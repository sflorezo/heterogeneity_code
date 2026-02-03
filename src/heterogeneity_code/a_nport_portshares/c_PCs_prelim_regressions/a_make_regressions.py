# pyright: reportArgumentType=false
# pyright: reportIndexIssue=false
# pyright: reportOptionalMemberAccess=false

#%% ========== params ========== %%#
# FIXME: temporal params

do_check_figs = False

#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet
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

random_seed = CONFIGS["GENERAL"]["random_seed"]
n_workers = CONFIGS["GENERAL"]["n_workers"]
batch_job_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]

process_quarters = CONFIGS["NPORT"]["process_quarters"]

#%% ========== quarterly regression results ========== %%#

def _quarterly_regression_results(yq):

    #####
    # yq = "2025q2"
    #####

    # collapse fund bond holdings at the EM/DM level

    holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")
    holdings_df = _keep_bond_funds(holdings_df)
    holdings_df = holdings_df[holdings_df["asset_cat"] == "DBT"]

    keep = (
        (
            holdings_df["investment_country_EME"] == 1
        )
        | (
            (holdings_df["investment_country_DM"] == 1) & (holdings_df["investment_country_iso3"] != "USA")
        )
    )

    holdings_df = holdings_df[keep]

    holdings_df = (
        holdings_df
        .groupby(["fund_id", "quarterly", "investment_country_EME"])
        .agg({
            "currency_value" : "sum",
            "fund_total_assets" : "first"
        })
        .reset_index()
        .pivot_table(
            index = ["fund_id", "quarterly", "fund_total_assets"],
            columns = "investment_country_EME",
            values = "currency_value"
        )
        .reset_index()
    )

    holdings_df.iloc[:,3:] = holdings_df.iloc[:,3:].apply(lambda x : x.fillna(0))
    holdings_df.rename(columns = {0 : "DM", 1 : "EM"}, inplace = True)
    holdings_df.columns.name = None

    holdings_df["s_EM"] = holdings_df["EM"] / holdings_df["fund_total_assets"]
    holdings_df["s_DM"] = holdings_df["DM"] / holdings_df["fund_total_assets"]
    holdings_df = holdings_df.drop(columns = ["DM", "EM"])

    # merge with PC data

    df_PC = fetch_PCs_with_fund_info(aggregation_level = 1)
    df_PC = df_PC[df_PC["quarterly"] ==  yq][["fund_id", "quarterly", "pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]]
    mask = df_PC[["fund_id", "quarterly"]].duplicated()
    df_PC = df_PC[~mask]

    df_ = holdings_df.merge(df_PC, on = ["fund_id", "quarterly"], how = "left", validate = "m:1")
    df_["w_"] = (df_["fund_total_assets"] / df_["fund_total_assets"].max()) * 50

    # keep only emerging markets and developed markets outside the US

    if do_check_figs:
        plt.scatter(df_["s_EM"], df_["pc_1"] , s = df_["w_"].to_numpy()) # 
        plt.scatter(df_["s_DM"], df_["pc_1"] , s = df_["w_"].to_numpy())

    # add constant
    X = sm.add_constant(df_[["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]])

    # run OLS
    w_ = df_["w_"].to_numpy()
    model_dm = sm.WLS(df_["s_DM"], X, weights = w_, missing="drop").fit()
    model_em = sm.WLS(df_["s_EM"], X, weights = w_, missing="drop").fit()


    results = {
        "DM" : {
            "params" : model_dm.params,
            "bse" : model_dm.bse
        },
        "EM" : {
            "params" : model_em.params,
            "bse" : model_em.bse
        }
    }
    print(f". {yq} results finished")

    return results

def _generate_regression_results():

    results = {}

    quarters = (
            pd
            .period_range(process_quarters["start"].upper(), 
                        process_quarters["end"].upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    result_list = Parallel(
        n_jobs = n_workers,
        verbose = batch_job_verbose
    )(
        delayed(_quarterly_regression_results)(yq) 
        for yq in quarters
    )

    results = pd.concat(
        [
            pd.concat([
                pd.DataFrame(df).assign(regtype = type) 
                for type, df in q_df.items()
            ], axis = 0).assign(quarter = quarter)
            for quarter, q_df in zip(quarters, result_list)
        ], axis = 0
    )

    results = (
        results
        .reset_index(names = "parameter")
        .pivot(index = ["quarter", "parameter"],
               columns = "regtype",
               values = ["params", "bse"])
    )

    results.columns = [
        "_".join(col).strip() if isinstance(col, tuple) else col
        for col in results.columns
    ]

    results.reset_index(inplace = True)

    save_parquet(results, PROJECT_TEMP / "regression_results.parquet")
    print(f"Regression results saved to $PROJECT_TEMP/regression_results.parquet")


# %% ========== generate regression results for all quarters




