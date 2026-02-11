#%% ========== configs ========== %%#

import pandas as pd
import numpy as np


#%% ========== asset bucket helfuns ========== %%#

def asset_bucket_lv_0(df: pd.DataFrame):

    # df = holdings_df.copy()
    
    issuer = df["issuer_type"].astype("string").str.upper()
    act    = df["asset_cat_type"].astype("string").str.lower()

    asset_bucket_lv_0 = np.select(
        [
            issuer.isin(["USGSE", "USGA", "UST"]) & act.eq("debt"),  # 1) sovereign debt
            issuer.eq("CORP") & act.eq("debt"),                     # 2) corporate debt
            act.eq("equity"),                                       # 3) equity
            act.eq("loans"),                                        # 4) loans
        ],
        [
            "sovereign debt",
            "corporate debt",
            "equity",
            "loans",
        ],
        default="other",                                            # 5) other
    )

    return asset_bucket_lv_0

def asset_bucket_lv_1(df: pd.DataFrame):

    # df = holdings_df.copy()
   
    asset_bucket_lv_1 = df["asset_cat_type"].str.lower()

    asset_bucket_lv_1 = asset_bucket_lv_1.replace({
        "asset-backed securities": "abs",
        "cash and short-term vehicles": "stv",
        "real assets / other": "other",
        "repurchase agreements": "repos",
        "unknown category": "unknown",
    })

    return asset_bucket_lv_1

def asset_bucket_lv_99(df: pd.DataFrame):

    asset_bucket_lv_99  = df["asset_cat"]

    return asset_bucket_lv_99

