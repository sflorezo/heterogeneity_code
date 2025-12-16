#%%

from pathlib import Path
import os
from pysfo.basic import load_tomli
from pysfo.basic import configure_pandas_display

#--- Unified snapshot for logging or experiment reproducibility
config_path = (
    Path(os.environ["PROJECT_ROOT"]) / "configs_local" / "project_params.toml"
)

CONFIGS = load_tomli(config_path)
CONFIGS = {k.upper(): v for k, v in CONFIGS.items()}
CONFIGS = {
    k_0 : {
        k_1 : (Path(val_1) if k_0 == "PATHS" else val_1) for k_1, val_1 in dict_1.items()
    } 
    for k_0, dict_1 in CONFIGS.items()
}

#---- Display options for pandas
configure_pandas_display(max_cols=500, max_rows=300)
