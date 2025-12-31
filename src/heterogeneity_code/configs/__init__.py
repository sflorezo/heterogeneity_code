#%% ========== packages ========== %%#

from pathlib import Path
import os
from pysfo.basic import load_tomli
from pysfo.basic import configure_pandas_display
from pathlib import Path

#%% ========= helper functions

def _expand_paths(path_dict: dict) -> dict:
    path_dict = {
        k : os.path.expandvars(v) 
        for k, v in path_dict.items()
    }

    return path_dict

#%% ========== upload configs ========== %%#

#--- Unified snapshot for logging or experiment reproducibility
config_path = (
    Path(__file__)
    .resolve()
    .parents[3] / "configs" / "project_params.toml"
)

CONFIGS = load_tomli(config_path)
CONFIGS = {k.upper(): v for k, v in CONFIGS.items()}
CONFIGS = {
    k_0 : {
        k_1 : (Path(val_1) if k_0 == "PATHS" else val_1) for k_1, val_1 in dict_1.items()
    } 
    for k_0, dict_1 in CONFIGS.items()
}

# expand paths

CONFIGS["PATHS"] = _expand_paths(CONFIGS["PATHS"])

#---- Display options for pandas

configure_pandas_display(max_cols=500, max_rows=300)
