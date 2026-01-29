#!/bin/bash
# ============================================================
# SLURM Batch Job Template
# ============================================================
# This file is not submitted directly — it is used by
# `run_batch_job` to generate a complete, filled-in sbatch file.
# Placeholders like 3:00:00 and 160G are replaced dynamically.
# ============================================================

# ---------------------------------------------
# SLURM Job Configuration
# ---------------------------------------------
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=3:00:00
#SBATCH --mem=160G
#SBATCH --job-name=build_Cij_panel_job
#SBATCH --output=build_Cij_panel_job.out
#SBATCH --mail-user=saf9215@stern.nyu.edu
#SBATCH --mail-type=END,FAIL

# ---------------------------------------------
# Shell Safety Settings
# ---------------------------------------------
set -euo pipefail

# ---------------------------------------------
# Environment setup
# ---------------------------------------------

#---- For reproducibility
echo "==================== SLURM JOB INFO"
echo "[slurm] Job started on $(hostname)"
echo "[slurm] Job ID: ${SLURM_JOB_ID}"
echo "[slurm] Job name: ${SLURM_JOB_NAME}"
echo "[slurm] Nodes: ${SLURM_JOB_NODELIST}"
echo "[slurm] Started at: $(date)"

#---- load master environment

source "$HOME/.env_machine"

# ----------------------------------------------------
# Thread control
# ----------------------------------------------------
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# ----------------------------------------------------
# Run project master script
# ----------------------------------------------------
echo "==================== RUNNING PROJECT SCRIPT"
echo

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
# bash "build_Cij_panel.sh" 2>&1 | tee "${SLURM_JOB_NAME}_${TIMESTAMP}.log"
bash "build_Cij_panel.sh"
exit_code=${PIPESTATUS[0]}

if [ "$exit_code" -ne 0 ]; then
    echo "-> ERROR: Project script failed with exit code $exit_code"
    exit "$exit_code"
fi

echo
echo "==================== JOB COMPLETED at $(date)"