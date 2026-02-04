#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]

#%% ========= Upload data ========== %%#

def fetch_PCs_with_fund_info(aggregation_level):

    from heterogeneity_code.a_nport_portshares.a_build_PCs.d_build_PCs.a_simple_one_dimensional import fetch_PC_df

    PC_panel = fetch_PC_df(aggregation_level)
    fund_level_data = load_parquet(PROCESSED_NPORT / f"NPORT_funds_allQuarters.parquet")

    fund_level_data = fund_level_data[["fund_id", "quarterly", "fund_total_assets"]]

    PC_panel = pd.merge(fund_level_data, PC_panel, on = ["fund_id", "quarterly"], how = "right")

    return PC_panel
# %%
