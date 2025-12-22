#!/bin/bash
# ============================================================
# Simplified batch job default example
# ============================================================

# manually define paths to bash_env and job to run

PROJECT_ROOT_PATH="/storage/Dropbox/01_main/dev/heterogeneity_code"
SCRIPT_DIR="$PROJECT_ROOT_PATH/scripts/build_Cij_PCs/build.py"

# bash env should be the project bash_env, with project-specific uploads for pythonenv

source "$PROJECT_ROOT_PATH/bash_env.sh"
# python -u "${SCRIPT_DIR}/build.py" 2>&1 | tee "${SCRIPT_DIR}/build.log"