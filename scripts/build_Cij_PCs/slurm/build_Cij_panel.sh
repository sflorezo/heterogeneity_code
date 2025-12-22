#!/bin/bash
# ============================================================
# Simplified batch job default example
# ============================================================

source "$HOME/.env_machine"

PROJECT_ROOT_PATH="$DEV_PATH/heterogeneity_code"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# bash env should be the project bash_env, with project-specific uploads for pythonenv

source "$PROJECT_ROOT_PATH/bash_env.sh"
# python -u "${SCRIPT_DIR}/../build.py" 2>&1 | tee "${SCRIPT_DIR}/../build.log"