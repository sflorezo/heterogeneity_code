# pyright: reportAttributeAccessIssue=false
# pyright: reportArgumentType=false
# pyright: reportIndexIssue=false

#%% ========= imports ========== %%#

from heterogeneity_code.configs import CONFIGS
from pysfo.basic import load_parquet
from matplotlib import pyplot as plt
import pandas as pd
from heterogeneity_code.d_nport_portshares.b_check_PCs.a_preliminary.a_merge_PCs_and_funds import fetch_PCs_with_fund_info
from heterogeneity_code.d_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import portfolio_weights_df
import numpy as np
from matplotlib.ticker import MultipleLocator

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
OUT_PATH = CONFIGS["PATHS"]["OUT_PATH"]

aggregation_level = CONFIGS["NPORT"]["build_PCs"]["aggregation_level"]

#%% ========= Upload data ========== %%#

df = fetch_PCs_with_fund_info()

#%% ========= quarterly mean of PCs ========== %%#

PC_cols = (df.filter(regex = r"pc_\d").columns)

agg_dict = {
    f"{col}_mean": (col, "mean")
    for col in PC_cols
} | {
    f"{col}_std": (col, "std")
    for col in PC_cols
}

out = df.groupby("quarterly").agg(**agg_dict).reset_index()

plt.figure()
for col in PC_cols:
    mean_col = out[col + "_mean"]
    period_col = out["quarterly"].dt.to_timestamp() # pyright: ignore[reportAttributeAccessIssue]

    plt.plot(period_col, mean_col, label = col)
    plt.legend()
plt.show()

#%% ========= See who are the main funds identified by components ========== %%#

'''
For each quarter, find funds with
1. greater weight of each PC
2. smallest weight of each PC

For each of those funds, find their holdings and plot them in the time series.
'''

df = fetch_PCs_with_fund_info()

pc = "pc_1"

df_pc_high = (
    df
    .assign(
        q90=df.groupby("quarterly")[pc].transform("quantile", 0.9)
    )
    .loc[lambda x: x[pc] >= x["q90"]]
    .drop(columns="q90")
)

df_pc_low = (
    df
    .assign(
        q10=df.groupby("quarterly")[pc].transform("quantile", 0.1)
    )
    .loc[lambda x: x[pc] <= x["q10"]]
    .drop(columns="q10")
)

df_w = portfolio_weights_df(keep_fund_type = "bond_funds")[["fund_id", "quarterly", "w", "asset_bucket"]]
df_w = (
    df_w.pivot(
    columns = "asset_bucket", 
    index = ["fund_id", "quarterly"],
    values = "w")
    .reset_index()
)
df_w.columns.name = None

#---- pc_high

df_pc_high = df_pc_high[["fund_id", "quarterly", "series_name"]].merge(df_w, on = ["fund_id", "quarterly"], validate = "m:1", how = "left")
df_pc_high.iloc[:,3:] = df_pc_high.iloc[:,3:].apply(lambda x : x.fillna(0))
cols = df_pc_high.iloc[:,3:].columns
df_pc_high = (
    df_pc_high
    .groupby("quarterly")[cols]
    .mean()
)

for col in df_pc_high.columns:
    plt.plot(df_pc_high.index.to_timestamp(), df_pc_high[col], label = col)
plt.legend()


#---- pc_low


df_pc_low = df_pc_low[["fund_id", "quarterly", "series_name"]].merge(df_w, on = ["fund_id", "quarterly"], validate = "m:1", how = "left")
df_pc_low.iloc[:,3:] = df_pc_low.iloc[:,3:].apply(lambda x : x.fillna(0))
cols = df_pc_low.iloc[:,3:].columns
df_pc_low = (
    df_pc_low
    .groupby("quarterly")[cols]
    .mean()
)

for col in df_pc_low.columns:
    plt.plot(df_pc_low.index.to_timestamp(), df_pc_low[col], label = col)
plt.legend()

