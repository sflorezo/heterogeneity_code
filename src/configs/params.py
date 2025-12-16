from pathlib import Path
import tomli
from pysfo.basic import load_tomli

config_path = (
    Path(__file__)
    .resolve()
    .parents[3] / "config" / "project_params.toml"
)

configs = load_tomli(config_path)

#---- setting configs

# configs.general

RANDOM_SEED = configs.get("general", {}).get("random_seed", None)

# configs.clean_holdings

process_quarters = configs.get("clean_holdings", {}).get("process_quarters", None)
holdings_data_name = configs.get("clean_holdings", {}).get("holdings_data_name", None)
sample_data = configs.get("clean_holdings", {}).get("sample_data", None)
fetch_data =  configs.get("clean_holdings", {}).get("fetch_data", None)
fetch_data_n_workers = configs.get("clean_holdings", {}).get("fetch_data_n_workers", None)
fetch_data_verbose = configs.get("clean_holdings", {}).get("fetch_data_verbose", None)
sample_flag = 'SAMPLE' if sample_data else 'FULLDATA'

CLEAN_HOLDINGS_CONFIGS = {
    "process_quarters" : process_quarters,
    "holdings_data_name" : holdings_data_name,
    "sample_data": sample_data,
    "fetch_data": fetch_data,
    "fetch_data_n_workers": fetch_data_n_workers,
    "fetch_data_verbose": fetch_data_verbose,
    "sample_flag": sample_flag
}
