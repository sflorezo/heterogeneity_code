# pyright: reportIndexIssue=false

#%% ========== project-wide configs ========== %%#

from heterogeneity_code.d_nport_portshares.a_build_PCs.b_build_port_weights.b_build_port_weights import portfolio_weights_df
from heterogeneity_code.configs import CONFIGS
from pysfo.basic import relocate_columns, export_txt
import pandas as pd

OUT_PATH = CONFIGS["PATHS"]["OUT_PATH"]

# from pysfo.basic import *

PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
process_quarters = CONFIGS["NPORT"]["process_quarters"]
joblib_n_workers = CONFIGS["GENERAL"]["n_workers"]
joblib_verbose = CONFIGS["GENERAL"]["batch_job_verbose"]
aggregation_level = CONFIGS["NPORT"]["build_PCs"]["aggregation_level"]


#%% ========== running sumstats ========== %%#

df = portfolio_weights_df(keep_fund_type = "bond_funds")

#---- clean and do sumstats

df = df[df["quarterly"] == df["quarterly"].max()]

_sumstats = (
    df
    .groupby(["quarterly", "asset_bucket"])
    .agg(
        fund_count = ("w", lambda x : x.count()),
        mean = ("w", lambda x : x.mean()),
        std = ("w", lambda x : x.std()),
        pc_25 = ("w", lambda x : x.quantile(0.25)),
        pc_75 = ("w", lambda x : x.quantile(0.75)),
    )
    .reset_index()
)

asset_bucket_map = {
    "abs": "ABS",
    "debt": "Debt",
    "derivatives": "Derivatives",
    "equity": "Equity (Preferred)",
    "loans": "Loans",
    "repos": "Repos",
    "stv": "Short-Term Vehicles",
    "other": "Other",
    "unknown": "Unknown",
}
drop = (_sumstats["asset_bucket"] == "unknown")
_sumstats = _sumstats[~drop]
_sumstats["asset_bucket_label"] = _sumstats["asset_bucket"].map(asset_bucket_map)
_sumstats = relocate_columns(_sumstats, cols_to_move = ["asset_bucket_label"], anchor_col = "quarterly", how = "before")
_sumstats = _sumstats.drop(columns = ["asset_bucket", "quarterly"])
_sumstats.sort_values(by = "mean", ascending = False, inplace = True)
_sumstats = _sumstats.reset_index(drop = True)

#---- export

tex_str = "\\begin{tabular}{lccccc} \n"
tex_str += "\\hline \n"
tex_str += "Asset Class & Fund Count & Mean & Std. Dev. & 25th Percentile & 75th Percentile \\\\ \n"
tex_str += "\\hline \n"
for _, row in _sumstats.iterrows():
    tex_str += f"{row["asset_bucket_label"]} & {row["fund_count"]} & {row["mean"]:.2f} & {row["std"]:.2f} & {row["pc_25"]:.2f} & {row["pc_75"]:.2f} \\\\ \n"
tex_str += "\\hline \n"
tex_str += "\\end{tabular}"

export_txt(tex_str, path = OUT_PATH / "major_asset_classes.tex")


# %%
