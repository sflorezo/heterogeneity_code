#%% ========== configs ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from pysfo.basic import na_report
from typing import Tuple, Hashable, cast

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
master_holding_id_var = CONFIGS["BUILD_PORTF_SHARES"]["master_holding_id_var"]


#%% ========== helper functions ========== %%

def _drop_and_validate_missing_identifiers(holdings_df):

    _missing_identifiers_mktval_percen = [
        item["Percentage"] 
        for idx, item in na_report(
            holdings_df, 
            var = master_holding_id_var, 
            weight_col = "currency_value"
        ).iterrows()
        if (
            (cast(Tuple[Hashable, ...], idx)[0] == master_holding_id_var)
            & (cast(Tuple[Hashable, ...], idx)[1] == "Missing")
        )
    ]

    holdings_df.dropna(subset = [master_holding_id_var], inplace = True)

    return (
        holdings_df, 
        _missing_identifiers_mktval_percen
    )


#%% ========== buid portfolio shares ========== %%

def build_portfolio_shares(yq):

    ###
    # yq = "2025q2"
    ###

    holdings_df = load_parquet(PROCESSED_NPORT / f"NPORT_holdings_{yq}_FULLDATA.parquet")

    (
        holdings_df, 
        _missing_identifiers_mktval_percen
    ) = _drop_and_validate_missing_identifiers(holdings_df)

    return (
        holdings_df, 
        _missing_identifiers_mktval_percen
    )