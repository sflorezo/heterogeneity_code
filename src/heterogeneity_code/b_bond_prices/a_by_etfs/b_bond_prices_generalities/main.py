# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalSubscript=false


#%% ========== configs ========== %%#

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from heterogeneity_code.b_bond_prices.a_by_etfs.a_params.ETFs_to_check import EM_DMexUS_US as funds_dict

# from pprint import pprint

#%% ========== rest ========== %%#

# select analysis date and upload data

_start_date = pd.to_datetime("2009-10-01").tz_localize("America/New_York") # 2019-10-01

regions  = [el["region"] for el in funds_dict["data"]]
tickers  = [el["funds"][0]["ticker"] for el in funds_dict["data"]]

# create empty datadict for prices

data_dict = {}
data_dict = {
    _region : {
        "prices_raw" : None,
        "prices_normalized" : None
    }
    for _region in regions
}

# call yf and extract data

for _r, _t in zip(regions, tickers):
    _yf = yf.Ticker(_t)
    # print(_yf.info)
    data = _yf.history(period = 'max')
    data = data[data.index >= _start_date]
    data_dict[_r]["prices_raw"] = data
    data_dict[_r]["prices_normalized"] = (
        (data_dict[_r]["prices_raw"] - data_dict[_r]["prices_raw"].mean()) / data_dict["EM"]["prices_raw"].std()
    )
    data_dict[_r]["prices_normalized"] = data_dict[_r]["prices_normalized"] - data_dict[_r]["prices_normalized"].iloc[0]

# generate plots

for _r, _t in zip(regions, tickers):
    z_data = data_dict[_r]["prices_normalized"]
    plt.plot(z_data.index, z_data["Close"], label = f"{_r} ({_t})")
plt.legend()
