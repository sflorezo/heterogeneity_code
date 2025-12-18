# ------------------------------------------------------------
# SLURM Default Job Parameters
# ------------------------------------------------------------

# === Resource allocation ===
NODES=1
NTASKS_PER_NODE=1
CPUS_PER_TASK=4
TIME="1:00:00"
MEM="18G"
PARTITION="general"

# === Job parameters ===
PROJECT="default"
JOB_NAME="${PROJECT}_job"
JOB_OUTPUT="${PROJECT}_job.out"
JOB_SCRIPT="batch_job_simplified_default.sh"

# === Notifications ===
MAIL_USER="saf9215@stern.nyu.edu"
MAIL_TYPE="END,FAIL"