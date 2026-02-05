#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from heterogeneity_code.a_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import _keep_bond_funds

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

#%% ========== go ========== %%#

yq = "2025q2"

holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")
holdings_df = _keep_bond_funds(holdings_df)

holdings_df = holdings_df[holdings_df["asset_cat"] == "DBT"]

h_tmp = holdings_df[holdings_df["investment_country_iso3"] == "COL"]