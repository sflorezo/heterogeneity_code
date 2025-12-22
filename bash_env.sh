# --- Guard: this file must be sourced, not executed ---
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "[error] bash_env.sh must be sourced, not executed."
    echo "[error] Use: source bash_env.sh"
    exit 1
fi

# ========== headers ========== #

echo "#--------------------------------------#"
echo "# STARTING HETEROGENEITY PROJECT ENV   #"
echo "#--------------------------------------#"

# ========== load master environment ========== #

source $HOME/.bashrc

# ========== activate project conda env ========== #

micromamba activate heterogeneity_code

# ========== project level globals ========== #

# DO NOT USE SCRIPTDIR. THIS FILE WILL BE RUN FROM DIFFERENT FILES,
# SO PLEASE CALL GLOBALS ALREADY DEFINED IN MASTER ENVIRONMENT

export PROJECT_ROOT="$HETEROGENEITY_CODE_PATH"
export PROJECT_SRC="$PROJECT_ROOT/src"
export SEC_API_KEY="$SEC_API_KEY"
export DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"

# ========== expand configs for python ========== #

mkdir -p configs_local
expanded_toml=$(envsubst < $PROJECT_ROOT/configs/project_params.toml)
printf "%s" "$expanded_toml" > $PROJECT_ROOT/configs_local/project_params.toml

# ========== project level aliases ========== #d

# alias cd_documents='cd $DATA_RAW/factset/documents'
# alias cd_symbology='cd $DATA_TEMP/factset/symbology'
# alias cd_ownership='cd $DATA_RAW/factset/ownership'

# CLEAN: I think this is no longer needed as the packages are included in installed packages on the conda env
# # ---- PYTHONPATH
# export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_SRC}:${PYSFO_SRC}:${PYTHONPATH}"

# ========== work variables ========== #d

export_envfile "$PROJECT_ROOT/.vscode/.env" \
    PROJECT_ROOT \
    SEC_API_KEY \
    DEEPSEEK_API_KEY

# ========== env activation assetion ========== #

echo "[heterogeneity_code] Environment heterogeneity_code activated succesfully"

