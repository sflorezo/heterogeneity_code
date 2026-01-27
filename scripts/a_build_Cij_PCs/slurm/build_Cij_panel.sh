#!/bin/bash
# ============================================================
# Simplified batch job default example
# ============================================================

# source env_machine without output to get master paths

source "$HOME/.env_machine" >/dev/null 2>&1

# manually define paths to bash_env and job to run

BASH_ENV_PATH="$HETEROGENEITY_CODE_PATH/bash_env.sh"
RUN_SCRIPT_DIR="$HETEROGENEITY_CODE_PATH/scripts/a_build_Cij_PCs"

# bash env should be the project bash_env, with project-specific uploads for pythonenv

source "$BASH_ENV_PATH"
# python -u "${RUN_SCRIPT_DIR}/1_build_portf_weights.py" 2>&1 | tee "${RUN_SCRIPT_DIR}/1_build_portf_weights.log"
python -u "${RUN_SCRIPT_DIR}/2_build_Cij_PCs.py" 2>&1 | tee "${RUN_SCRIPT_DIR}/2_build_Cij_PCs.log"