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
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# from pysfo.basic import *
# from pprint import pprint

#%% ========== initialize work objects and configs ========== %%#

PROJECT_TEMP = Path(CONFIGS["PATHS"]["PROJECT_TEMP"])
SEC_API_KEY = CONFIGS["GENERAL"]["SEC_API_KEY"]
DEEPSEEK_API_KEY = cast(str, CONFIGS["GENERAL"]["DEEPSEEK_API_KEY"])
random_seed = cast(int, CONFIGS["GENERAL"]["random_seed"])

rng = np.random.default_rng(random_seed)

client = OpenAI(api_key = DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

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

        save_pickle(responses, PROJECT_TEMP / "test_prospectuses.pkl")

#%% ========== get test html ========== %%#

if DO_NOT_TURN_TO_TRUE_UNLESS_SURE_ABOUT_IT:

    responses = load_pickle(PROJECT_TEMP / "test_prospectuses.pkl")
    myresp = responses[0]
    filings = myresp["filings"][0]

    headers = {
        "User-Agent": "Sergio Florez-Orrego Academic Research saf9215@stern.nyu.edu",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }

    prosp_url_1 = filings["linkToFilingDetails"]
    resp_1 = requests.get(prosp_url_1, headers = headers)

    soup = BeautifulSoup(resp_1.text, "lxml")

    save_pickle(soup, PROJECT_TEMP / "test_prosp_html.pkl")

#%% ========== get test html and process through LLM ========== %%#

if DO_NOT_TURN_TO_TRUE_UNLESS_SURE_ABOUT_IT:

    soup = load_pickle(PROJECT_TEMP / "test_prosp_html.pkl")

    _message = f"""
    Suppose I give you the following prospectus, and ask you to give me a set of N financial embeddings that describe the strategy of the following fund. How would you select which embeddings you will provide? (i.e. will you order in terms of importance? What will you try to do?)


    PROSPECTUS:
    ------------

    {soup}
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You will receive an html file from a prospectus. Ignore all non-human readable information."},
            {"role": "user", "content": f"{_message}"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)