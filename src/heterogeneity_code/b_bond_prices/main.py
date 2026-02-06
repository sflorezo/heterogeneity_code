#%% ========== configs ========== %%#

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

#%% ========== rest ========== %%#

_start_date = pd.to_datetime("2009-10-01").tz_localize("America/New_York") # 2019-10-01

regions = ["EM", "DM", "US"]
tickers = ["EMB", "IGOV", "AGG"]

yf_dict = {
    r : yf.Ticker(t)
    for r, t in zip(regions, tickers)
}

data_dict = {}
for _r, _t in zip(regions, tickers):
    _yf = yf_dict[_r]
    # print(_yf.info)
    data = _yf.history(period = 'max')
    data = data[data.index >= _start_date]

    data_dict[_r] = data


EM_p = (data_dict["EM"] - data_dict["EM"].mean()) / data_dict["EM"].std()
DM_p = (data_dict["DM"] - data_dict["DM"].mean()) / data_dict["DM"].std()
US_p = (data_dict["US"] - data_dict["US"].mean()) / data_dict["US"].std()

EM_p = EM_p - EM_p.iloc[0]
DM_p = DM_p - DM_p.iloc[0]
US_p = US_p - US_p.iloc[0]

plt.plot(EM_p.index, EM_p["Close"], label = "EM")
plt.plot(DM_p.index, DM_p["Close"], label = "DM")
plt.plot(US_p.index, US_p["Close"], label = "US")
plt.legend()


yf_dict["EM"].funds_data.bond_holdings


