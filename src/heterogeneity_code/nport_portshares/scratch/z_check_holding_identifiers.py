#%% ========== configs ========== %%#

from configs import CONFIGS
from pysfo.basic import load_parquet

from pysfo.basic import na_report

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

holdings = load_parquet(PROCESSED_NPORT / "NPORT_holdings_2024q1_FULLDATA.parquet")

#%% ========== pre-preps ========== %%

# FIXME: All these are pre-preps to implement

# FIXME:
# 1. Add a check that sees how many holding_ids are there, and then drop all missing holding_ids
#    - there might be various holding_id that are valid to 

_na_holding = {}
_id_holding_vars = [
    "holding_id",
    "identifier_isin",
    "identifier_ticker",
    "other_identifier"
]

# this checks missings by market value

for var in _id_holding_vars:
    _na_holding[var] = na_report(
        holdings[[var, "currency_value"]], 
        var = var,
        weight_col = "currency_value"
    )
