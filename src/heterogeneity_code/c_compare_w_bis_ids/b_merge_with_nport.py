#%% =========== project wide configs ==========#%%

from heterogeneity_code.a_configs import CONFIGS
import pysfo.pulldata as pysfo_pull
from pysfo.basic import save_parquet, load_parquet, dupli_report
from pysfo.geo_utils.country_groups import get_country_list_in_category
import country_converter as coco
from heterogeneity_code.c_compare_w_bis_ids.a_consolidate_eme_debt import get_bis_ids_eme_debt_panel
from heterogeneity_code.b_prep_nport_holdings.a_select_sample.funds_that_hold_bonds import fetch_funds_that_hold_bonds_list
import pandas as pd
from matplotlib import pyplot as plt

# from pysfo.basic import *

DATA_RAW_PATH = CONFIGS["PATHS"]["DATA_RAW_PATH"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]


# %% =========== helper functions ==========#%%

yq = "2020q4"

_hdgs_file_path = PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet"

# get needed data

holdings_df = load_parquet(_hdgs_file_path)
bis_ids_eme = get_bis_ids_eme_debt_panel()

