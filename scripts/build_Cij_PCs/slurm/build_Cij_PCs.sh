#!/bin/bash
# ============================================================
# Simplified batch job default example
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# bash env should be the project bash_env, with project-specific uploads for pythonenv

source "$PROJECT_ROOT_PATH/bash_env.sh"
python -u "${SCRIPT_DIR}/master.py" 2>&1 | tee "${SCRIPT_DIR}/0_master_py.log"