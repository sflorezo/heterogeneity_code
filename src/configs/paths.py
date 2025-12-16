#%%

from pathlib import Path
from dotenv import load_dotenv
import os

# system env vars

load_dotenv(Path.home() / ".env")

DATA_RAW  = Path(os.environ["DATA_RAW"])
DATA_WORK = Path(os.environ["DATA_WORK"])
DATA_TEMP = Path(os.environ["DATA_TEMP"])
DATA_LOGS = Path(os.environ["DATA_LOGS"])

PROJECT_TEMP = DATA_TEMP / "heterogeneity_temp"
PROJECT_LOGS = DATA_LOGS / "heterogeneity_logs"

HETEROGENEITY_CODE_ROOT = Path(os.path.dirname(__file__)).parents[0]

PROCESSED_NPORT = DATA_WORK / "sec_NPORT_work"
OUT_NPORT_REPORT = DATA_WORK / "sec_NPORT_work" / "sfo_report" / "out"

MACHINE_ID = os.environ.get("MACHINE_ID", "unknown")
USER_ID    = os.environ.get("USER_ID", "unknown")