#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from heterogeneity_code.a_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import _keep_bond_funds
from heterogeneity_code.a_nport_portshares.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

#%% ========== go ========== %%#

fund_info = load_parquet(PROCESSED_NPORT / "NPORT_funds_allQuarters.parquet")