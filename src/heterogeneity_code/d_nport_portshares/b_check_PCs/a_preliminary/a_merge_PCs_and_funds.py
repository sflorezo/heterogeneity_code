#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

#%% ========= Upload data ========== %%#

def fetch_PCs_with_fund_info():

    from heterogeneity_code.d_nport_portshares.a_build_PCs.d_build_PCs.a_simple_one_dimensional import fetch_PC_df

    # function params

    fund_info_df_file = PROCESSED_NPORT / f"NPORT_funds_allQuarters.parquet"

    # needed files check

    if not fund_info_df_file.exists():
        _message = (
            f"[fetch_PCs_with_fund_info] File not found {fund_info_df_file}.\n"
            "Please run clean_nport before running this function"
        )
        raise FileNotFoundError(_message)

    # call data

    PC_panel = fetch_PC_df()
    fund_level_data = load_parquet(fund_info_df_file)

    fund_level_data = fund_level_data[["fund_id", "quarterly", "fund_total_assets"]]

    PC_panel = pd.merge(fund_level_data, PC_panel, on = ["fund_id", "quarterly"], how = "right")

    return PC_panel
# %%
