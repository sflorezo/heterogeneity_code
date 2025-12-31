# ------------------------------------------------------------
# SLURM Default Job Parameters
# ------------------------------------------------------------

# === Resource allocation ===
NODES=1
NTASKS_PER_NODE=1
CPUS_PER_TASK=28
TIME="3:00:00"
MEM="160G"
PARTITION="general"
ACCOUNT="torch_pr_366_general"

# === Job parameters ===
PROJECT="build_Cij_panel"
JOB_NAME="${PROJECT}_job"
JOB_OUTPUT="${PROJECT}_job.out"
JOB_SCRIPT="build_Cij_panel.sh"

# === Notifications ===
MAIL_USER="saf9215@stern.nyu.edu"
MAIL_TYPE="END,FAIL"