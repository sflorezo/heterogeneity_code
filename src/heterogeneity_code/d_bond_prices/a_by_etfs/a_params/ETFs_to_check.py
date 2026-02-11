#%% ========== EM_DMexUS_US ========== %%#

EM = {
    "region" : "EM",
    "region_desc" : "Emerging Markets",
    "funds" : [
        {
            "ticker" : "EMB",
            "full_name" : "iShares J.P. Morgan USD Emerging Markets Bond ETF",
        }
    ]
}

DM_EX_US = {
    "region" : "DM_EX_US",
    "region_desc": "Developed Markets (ex-USA)",
    "funds" : [
        {
            "ticker" : "IGOV",
            "full_name" : "iShares International Treasury Bond ETF",
        }
    ]
}

USA = {
    "region" : "USA",
    "region_desc" : "United States",
    "funds" : [
        {
            "ticker" : "AGG",
            "full_name" : "iShares Core US Aggregate Bond ETF",
        }
    ]
}

region_list = [EM, DM_EX_US, USA]

EM_DMexUS_US = {
    "metadata" : (
        "Important passive funds, by major regions:\n"
        "1. Emerging Markets\n"
        "2. Developed Markets (ex-USA)\n"
        "3. USA",
    ),
    "data": region_list
}

# %%
