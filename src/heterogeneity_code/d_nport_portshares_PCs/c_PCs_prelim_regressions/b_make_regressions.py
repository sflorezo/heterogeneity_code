# pyright: reportArgumentType=false
# pyright: reportIndexIssue=false
# pyright: reportOptionalMemberAccess=false

#%% ========== params ========== %%#
# FIXME: temporal params

do_check_figs = False
generate_regressions = False

#%% ========== project-wide configs ========== %%#

from heterogeneity_code.a_configs import CONFIGS
from pysfo.basic import load_parquet, save_parquet
from pysfo import paralell_utils
from heterogeneity_code.d_nport_portshares_PCs.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info
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

_start_q = process_quarters["start"]
_end_q = process_quarters["end"]
regression_results_df_file = PROJECT_TEMP / f"regression_results_{_start_q}_{_end_q}.parquet"


#%% ========== quarterly regression results ========== %%#

def _collapse_debt_holdings_EM_DM_USA(yq):

    #####
    # yq = "2025q2"
    #####

    # function params

    holdings_yq_file = PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet"

    # needed files check

    if not holdings_yq_file.exists():
        _message = (
            f"File not found {holdings_yq_file}.\n"
            "Please run clean_nport before running this function"
        )
        raise FileNotFoundError(_message)

    # collapse fund bond holdings at the EM/DM level

    holdings_df = load_parquet(holdings_yq_file)
    holdings_df = holdings_df[holdings_df["asset_cat"] == "DBT"]

    eme_issuer = holdings_df["investment_country_EME"] == 1
    dm_ex_usa_issuer = (holdings_df["investment_country_DM"] == 1) & (holdings_df["investment_country_iso3"] != "USA")
    usa_issuer = holdings_df["investment_country_iso3"] == "USA"

    holdings_df["issuer_cty_group"] = np.nan

    for selector, label in zip(
        [eme_issuer, dm_ex_usa_issuer, usa_issuer],
        ["eme", "dm_ex_usa", "usa"]
        
    ):
        holdings_df["issuer_cty_group"] = np.where(selector, label, holdings_df["issuer_cty_group"])

    keep = (
        eme_issuer
        | dm_ex_usa_issuer
        | usa_issuer
    )

    holdings_df = holdings_df[keep]

    # collapse

    holdings_df = (
        holdings_df
        .groupby(["fund_id", "quarterly", "issuer_cty_group"])
        .agg({
            "currency_value" : "sum",
            "fund_total_assets" : "first"
        })
        .reset_index()
        .pivot_table(
            index = ["fund_id", "quarterly", "fund_total_assets"],
            columns = "issuer_cty_group",
            values = "currency_value",
        )
        .reset_index()
    )

    holdings_df.rename(
        columns = {
            "dm_ex_usa": "currency_value_DM", 
            "eme" : "currency_value_EM",
            "usa" : "currency_value_USA",
        }, inplace = True
    )
    holdings_df.iloc[:,3:] = holdings_df.iloc[:,3:].apply(lambda x : x.fillna(0))
    holdings_df.columns.name = None

    return holdings_df

def _quarterly_regression_results(yq):

    #####
    # yq = "2025q2"
    #####

    holdings_df = _collapse_debt_holdings_EM_DM_USA(yq)

    holdings_df.columns = holdings_df.columns.str.replace("currency_value_", "")
    holdings_df.drop(columns = "USA", inplace = True)

    holdings_df["s_EM"] = holdings_df["EM"] / holdings_df["fund_total_assets"]
    holdings_df["s_DM"] = holdings_df["DM"] / holdings_df["fund_total_assets"]
    holdings_df = holdings_df.drop(columns = ["DM", "EM"])

    # merge with PC data

    df_PC = fetch_PCs_with_fund_info()
    df_PC = df_PC[df_PC["quarterly"] ==  yq][["fund_id", "quarterly", "pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]]
    mask = df_PC[["fund_id", "quarterly"]].duplicated()
    df_PC = df_PC[~mask]

    df_ = holdings_df.merge(df_PC, on = ["fund_id", "quarterly"], how = "right", validate = "m:1")
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


# %% ========== callable functions ========== %% #

def build_regression_results_df():

    #check that function is not run in paralell

    if paralell_utils.is_nested_parallel():

        _message = (
            "[build_regression_results_df] build_regression_results_df runs in parallel, and cannot itself be called in a paralellized job."
            "Please check the code and try again."
            "(Suggestion: Run build_regression_results_df() before calling the paralellized job.)"
        )
    
        raise paralell_utils.errors.NestedParallelError(_message)
    
    # rest of function

    results = {}

    _start_quarter = process_quarters["start"]
    _end_quarter = process_quarters["end"]

    quarters = (
            pd
            .period_range(_start_quarter.upper(), 
                          _end_quarter.upper(), freq="Q")
            .astype(str).str.lower().tolist()
        )

    print("[build_regression_results_df] Building regression results by quarter...")

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

    save_parquet(results, regression_results_df_file)
    print(f"Regression results saved to {regression_results_df_file}")

def fetch_regression_results_df():

    from heterogeneity_code.d_nport_portshares_PCs.a_build_PCs.a_select_sample.funds_that_hold_bonds import create_funds_that_hold_bonds_list
    from heterogeneity_code.d_nport_portshares_PCs.a_build_PCs.d_build_PCs.a_simple_one_dimensional import build_assetcat_PC_fullpanel

    try :

        df = load_parquet(regression_results_df_file)

    except FileNotFoundError:

        print(f"[fetch_regression_results_df] regression_results_df not found. Creating it now")

        try :

            build_regression_results_df()

        except paralell_utils.errors.NestedParallelError:

            create_funds_that_hold_bonds_list()
            build_assetcat_PC_fullpanel()
            build_regression_results_df()

        df = load_parquet(regression_results_df_file)

    return df

# %% ========== generate figures ========== %% #

if generate_regressions:

    df = fetch_regression_results_df()

    for _pc in ["pc_1", "pc_2", "pc_3", "pc_4", "pc_5"]:

        _pc_label = _pc.upper().replace("_", " ")

        pc = df.loc[df["parameter"].eq(_pc),
                    ["quarter", "params_DM", "params_EM", "bse_DM", "bse_EM"]].copy()


        # Ensure correct quarter ordering (expects strings like "2019q4")
        q = pc["quarter"].astype(str).str.lower().str.replace("q", "Q")
        pc["_period"] = pd.PeriodIndex(q, freq="Q")
        pc = pc.sort_values("_period")
        periods = pc["_period"]

        x = np.arange(len(pc))
        dx = 0.14  # horizontal offset: EM left, DM right

        y_em = pc["params_EM"].to_numpy()
        y_dm = pc["params_DM"].to_numpy()
        err_em = (1.9 * pc["bse_EM"]).to_numpy()
        err_dm = (1.9 * pc["bse_DM"]).to_numpy()

        fig, ax = plt.subplots(figsize=(11, 4.8))

        ax.errorbar(x - dx, y_em, yerr=err_em, fmt="o", capsize=3, label="EM")
        ax.errorbar(x + dx, y_dm, yerr=err_dm, fmt="o", capsize=3, label="DM")

        ax.axhline(0, linewidth=1, color = "gray", alpha = 0.3)

        ax.set_xticks(x)
        ax.set_xticklabels(
            pc["_period"].astype(str).str.replace("Q", "q"),
            rotation=45, ha="right"
        )
        ax.tick_params(axis="both", labelsize=12)

        ax.set_xlabel("")
        ax.set_ylabel(f"Coef. on {_pc_label}", fontsize = 15)
        ax.set_title(f"{_pc_label} coefficients by quarter (± 1.96 × SE)", fontsize = 15)
        ax.legend()

        ax.set_axisbelow(True)
        ax.grid(
            True,
            which="both",
            axis="both",
            linestyle="--",
            linewidth=0.6,
            alpha=0.35,
        )

        ax.set_xticks(x)
        ax.set_xticklabels([
            str(p).replace("Q", "q") if p.quarter == 1 else ""
            for p in periods
        ])

        fig.tight_layout()
        plt.savefig(OUT_PATH / f"EM_DM_regs_{_pc}.pdf")
        print(f"Saved OUT_PATH/EM_DM_regs_{_pc}.pdf")
        plt.close(fig)
        # plt.show()



# %%
