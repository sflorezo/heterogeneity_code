#%%

from .paths import (
    MACHINE_ID, USER_ID,
    DATA_RAW, DATA_WORK, DATA_TEMP, DATA_LOGS, 
    CLEAN_NPORT_ROOT, PROJECT_TEMP, PROJECT_LOGS, 
    RAW_NPORT, PROCESSED_NPORT, OUT_NPORT_REPORT,
)
from .params import RANDOM_SEED, CLEAN_HOLDINGS_CONFIGS
from pysfo.basic import configure_pandas_display

#--- Importing all settings in debugging or interactive sessions

# from paths import RAW, WORK, TEMP, LOGS, MACHINE_ID, USER_ID
# from params import N_WORKERS, VERBOSE

#--- Unified snapshot for logging or experiment reproducibility

CONFIG = {
    "MACHINE_ID": MACHINE_ID,
    "USER_ID": USER_ID,
    "PATHS": {
        "RAW": DATA_RAW,
        "WORK": DATA_WORK,
        "TEMP": DATA_TEMP,
        "LOGS": DATA_LOGS,
        "CLEAN_NPORT_ROOT": CLEAN_NPORT_ROOT,
        "PROJECT_TEMP" : PROJECT_TEMP,
        "PROJECT_LOGS" : PROJECT_LOGS,
        "RAW_NPORT": RAW_NPORT,
        "PROCESSED_NPORT": PROCESSED_NPORT,
        "OUT_NPORT_REPORT": OUT_NPORT_REPORT,
    },
    "PROJECT": {
        "RANDOM_SEED" : RANDOM_SEED,
    },
    "CLEAN_HOLDINGS_CONFIGS" : CLEAN_HOLDINGS_CONFIGS,
}

#---- set ideal parameters for work

# show up to 500 columns when printing dataframes
configure_pandas_display(max_cols = 500, max_rows = 300)
