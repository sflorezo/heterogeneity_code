#%% ========== scratch check portfolio shares ========== %%

from pysfo.basic import *
from portf_shares.build_security_port_shares import build_portfolio_shares
import numpy as np


#%% ========== preliminary: check potential asset_type_vars ========== %%

#---- upload data

holdings, _ = build_portfolio_shares("2025q2")

#---- select base asset cat to define 
 
# See possible asset cats to define base asset for holdings share

statatab(holdings["asset_cat_desc"])

h_sum = (
    holdings.groupby(["asset_cat", "asset_cat_type", "asset_cat_desc"])
    .agg(
        n_funds = ("series_id", "count")
    )
)


#%% ========== check asset_cat as asset_type var ========== %%

#---- get data

holdings, _ = build_portfolio_shares("2025q2")
mask1, mask2 = (
    holdings[["series_id", "asset_cat"]].duplicated(),
    holdings["fund_id"].isna()
)
holdings = holdings.loc[~(mask1 | mask2), :]

# params

asset_type_vars = ["asset_cat", "asset_cat_type", "asset_cat_desc"]
base_asset_cat = "STIV"
fund_ids = ["series_name", "fund_id", "fund_id_desc"]

# collapse dataset at the asset_type level

holdings = (
    holdings.groupby(asset_type_vars + fund_ids)
    .agg(
        currency_value = ("currency_value", "sum")
    )
    .reset_index()
)

#--- create df to compute fund distance

all_fund_ids = pd.DataFrame(holdings["fund_id"].drop_duplicates())
all_asset_cats = pd.DataFrame(holdings["asset_cat"].drop_duplicates())

bilateral = all_asset_cats.merge(all_asset_cats, how = "cross")
bilateral = all_fund_ids.merge(bilateral, how = "cross")

for i in ["x", "y"]:

    bilateral = (
        bilateral.merge(
            holdings[["fund_id", "asset_cat", "currency_value"]],
            left_on = ["fund_id", f"asset_cat_{i}"],
            right_on = ["fund_id", "asset_cat"],
            how = "left",
            validate = "m:1"
        )
        .drop(columns = "asset_cat")
    )

    bilateral["currency_value"] = bilateral["currency_value"].fillna(0)
    bilateral.rename(columns = {"currency_value": f"currency_value_{i}"}, inplace = True)
    


#--- create all combinations of assets_cat and funds

# # len(holdings["series_id"].unique())*len(holdings["asset_cat"].unique())

# df1 = holdings[fund_ids].drop_duplicates()
# df2 = holdings[asset_type_vars].drop_duplicates()

# skeleton = df1.merge(df2, how="cross")

# skeleton = skeleton.merge(
#     holdings,
#     how = "left", 
#     on = asset_type_vars + fund_ids,
#     indicator = True
# )

# skeleton["currency_value"] = np.where(
#     skeleton["_merge"] == "left_only",
#     0,
#     skeleton["currency_value"]
# )

# skeleton.drop(columns = "_merge", inplace = True)

# #--- create flattened bilateral ratios of assets




# %%
