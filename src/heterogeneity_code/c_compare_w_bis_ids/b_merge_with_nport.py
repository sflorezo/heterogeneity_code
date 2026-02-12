#%% =========== project wide configs ==========#%%

from heterogeneity_code.a_configs import CONFIGS
import pysfo.pulldata as pysfo_pull
from pysfo.basic import save_parquet, load_parquet, dupli_report
from pysfo.geo_utils.country_groups import assign_country_category
import country_converter as coco
from heterogeneity_code.c_compare_w_bis_ids.a_consolidate_eme_debt import get_bis_ids_eme_debt_panel
from heterogeneity_code.b_prep_nport_holdings.b_holdings_aggregators.fund_investments_by_country import get_fund_investments_by_country
from heterogeneity_code.b_prep_nport_holdings.a_sample_selectors.funds_that_hold_bonds import keep_bond_funds
import pandas as pd
from matplotlib import pyplot as plt

# from pysfo.basic import *

DATA_RAW_PATH = CONFIGS["PATHS"]["DATA_RAW_PATH"]
PROJECT_TEMP = CONFIGS["PATHS"]["PROJECT_TEMP"]
PROCESSED_NPORT = CONFIGS["PATHS"]["PROCESSED_NPORT"]

# %% =========== helper functions ==========#%%



# %% =========== rest ===========

fund_hdgs = keep_bond_funds(get_fund_investments_by_country())
fund_hdgs["EME_issuer"] = assign_country_category(
    countries = fund_hdgs["investment_country_iso2"],
    src = "iso2",
    category = "EME"
)
keep = (
    (fund_hdgs["asset_cat_type"] == "Debt")
    & (fund_hdgs["EME_issuer"] == 1)
)
fund_hdgs = fund_hdgs[keep]
fund_hdgs = (
    fund_hdgs
    .groupby(["quarterly", "investment_country_iso2", "asset_cat"])
    .agg({"currency_value" : "sum"})
    .reset_index()
    .rename(columns = {"investment_country_iso2" : "iso2"})
)

bis_ids_eme = get_bis_ids_eme_debt_panel()
bis_ids_eme = (
    bis_ids_eme
    .groupby(["quarterly", "issuer_res", "issuer_res_label"])
    .agg({"value" : "sum"})
    .reset_index()
    .rename(columns = {"issuer_res" : "iso2"})
)

merged = fund_hdgs.merge(bis_ids_eme, on = ["quarterly", "iso2"], how = "left", validate = "1:1")
merged["s"] = merged["currency_value"] / merged["value"]
merged = merged.dropna()

biggest_lastq = (
    merged[merged["quarterly"] == merged["quarterly"].max()]
    .sort_values(by = "s", ascending = False)
)

biggest_lastq = {
    i : {
        "issuer_res" : issuer_res,
        "label" : label,
    }
    for i, (issuer_res, label) in enumerate(zip(biggest_lastq["iso2"], biggest_lastq["issuer_res_label"]))
}

plot = [val["issuer_res"] for key, val in biggest_lastq.items() if key <= 20]
labels = [val["label"] for key, val in biggest_lastq.items() if key <= 20]

for cty, lab in zip(plot, labels):

    _df = merged[merged["iso2"] == cty].copy()
    plt.plot(_df["quarterly"].astype("datetime64[ns]"), _df["s"], label = lab)
plt.legend(loc = "lower center", ncols = 10, bbox_to_anchor=(0.5, -0.3))


