#%% ========== temp params ========== %%#

# FIXME: temp params

DO_NOT_TURN_TO_TRUE_UNLESS_SURE_ABOUT_IT = False

#%% ========== libraries ========== %%#

from heterogeneity_code.configs import CONFIGS
from sec_api import QueryApi
from pathlib import Path
import random
from pysfo.basic import load_parquet, load_pickle, save_pickle, save_parquet, statatab, sumstats, test_time
import numpy as np
from typing import cast

# from pysfo.basic import *


#%% ========== initialize work objects and configs ========== %%#

PROJECT_TEMP = Path(CONFIGS["PATHS"]["PROJECT_TEMP"])
SEC_API_KEY = CONFIGS["GENERAL"]["SEC_API_KEY"]
random_seed = cast(int, CONFIGS["GENERAL"]["random_seed"])

rng = np.random.default_rng(random_seed)

queryApi = QueryApi(api_key = SEC_API_KEY)

#%% ========== get test prospectuses ========== %%#

def get_test_prospectuses():

    '''
    search_params = {
        "query": "seriesAndClassesContractsInformation.series:S000011051 AND formType:497K",
        "from": "0",
        "size": "10",
        "sort": [{ "filedAt": { "order": "desc" } }]
    }

    response = queryApi.get_filings(search_params)
    '''

    funds_pca = load_parquet(PROJECT_TEMP / "PC_funds.parquet")

    test_series_ids = rng.choice(funds_pca["series_id"].dropna(), size = 10, replace=False)

    queries = [
        {
            "query": f"seriesAndClassesContractsInformation.series:{series} AND formType:497K",
            "from": "0",
            "size": "10",
            "sort": [{ "filedAt": { "order": "desc" } }]
        } for series in test_series_ids
    ]

    if DO_NOT_TURN_TO_TRUE_UNLESS_SURE_ABOUT_IT:
        responses = [
            queryApi.get_filings(query)
            for query in queries
        ]

        save_pickle(responses, PROJECT_TEMP / "test_prospectuses.parquet")

#%% ========== operate test ========== %%#


# Here. I am here.

responses = load_pickle(PROJECT_TEMP / "test_prospectuses.parquet")
myresp = responses[0]
filings = myresp["filings"][0]

