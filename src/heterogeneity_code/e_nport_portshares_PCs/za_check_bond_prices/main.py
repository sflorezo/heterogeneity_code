#%% ========== configs ========== %%#

from heterogeneity_code.a_configs import CONFIGS
from pysfo.basic import load_parquet
from heterogeneity_code.b_prep_nport_holdings.a_sample_selectors.funds_that_hold_bonds import keep_bond_funds

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

#%% ========== go ========== %%#

yq = "2025q2"

holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")
holdings_df = keep_bond_funds(holdings_df)

holdings_df = holdings_df[holdings_df["asset_cat"] == "DBT"]

h_tmp = holdings_df[holdings_df["investment_country_iso3"] == "COL"]