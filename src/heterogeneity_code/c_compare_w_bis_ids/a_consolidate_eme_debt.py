# pyright: reportArgumentType=false

#%% =========== project wide configs ==========#%%

from heterogeneity_code.a_configs import CONFIGS
import pysfo.pulldata as pysfo_pull
from pysfo.basic import save_parquet, load_parquet, dupli_report
from pysfo.geo_utils.country_groups import get_country_list_in_category
import country_converter as coco
import pandas as pd
from matplotlib import pyplot as plt

# from pysfo.basic import *

DATA_RAW_PATH = CONFIGS["PATHS"]["DATA_RAW_PATH"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

pysfo_pull.set_data_path(DATA_RAW_PATH)

#%% =========== script-specific configs ==========#%%

tmp_0_ids_consolidated_eme_debt_file_name = PROJECT_TEMP / "BIS_IDS_EMEs.parquet"

# %% =========== helper functions ==========#%%

#---- get list of EME countries and store their residence-issued debt

def _build_bis_ids_eme_debt_panel():

    eme_list = get_country_list_in_category(category = "EME")["members"]
    iso2_list = [x["iso2"] for x in eme_list]

    eme_df_list = [
        pysfo_pull.bisIDS.get(ISSUER_RES = iso2, FREQ = "Q")
        for iso2 in iso2_list
    ]

    reference_cols = eme_df_list[0].columns
    if not all(df.columns.equals(reference_cols) for df in eme_df_list):
        raise ValueError("Not all DataFrames have identical columns.")
    else : 
        df = pd.concat(eme_df_list, axis=0)

    # leave quarterly variable

    df["quarterly"] = pd.PeriodIndex(df["period"], freq="Q")

    save_parquet(df, tmp_0_ids_consolidated_eme_debt_file_name)
    print("bis_ids_eme_debt_panel finished.")


# %% =========== merge with NPORT and see how much is intermediated by the U.S. ==========#%%

def get_bis_ids_eme_debt_panel():

    try :
        df = load_parquet(tmp_0_ids_consolidated_eme_debt_file_name)
    except FileNotFoundError:
        print("bis_ids_eme_debt_panel not found, creating it...")
        _build_bis_ids_eme_debt_panel()
        df = load_parquet(tmp_0_ids_consolidated_eme_debt_file_name)
    
    
    keep = (
        (df["freq"] == "Q") # Quarterly frequency
        & (df["issuer_bus_imm"] == "1") # All issuers
        & (df["market"] == "C") # International Market (cross-border)
        & (df["issue_cur_group"] == "A") # All currencies
        & (df["issue_cur"] == "TO1") # Total all currencies
        & (df["issue_or_mat"] == "A") # All maturities
        & (df["issue_re_mat"] == "A") # All remaining maturities
        & (df["issue_rate"] == "A") # All interest rates
        & (df["measure"] == "I") # Amounts Outstanding
    )
    df = df[keep]

    dupli_test = dupli_report(df[["issuer_res", "period"]])
    if True in dupli_test["Duplicated"]:
        raise ValueError("Check this. I did something wrong.")

    df = df[["quarterly", "issuer_res", "issuer_res_label", "value"]]

    return df

__all__ = [
    "get_bis_ids_eme_debt_panel"
]