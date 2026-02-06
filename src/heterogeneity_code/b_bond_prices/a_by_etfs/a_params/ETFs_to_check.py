#%% ========== EM_DMexUS_US ========== %%#

EM = {
    "region" : "EM",
    "region_desc" : "Emerging Markets",
    "funds" : [
        {
            "ticker" : "EMB"
        }
    ]
}

DM_EX_US = {
    "region" : "DM_EX_US",
    "region_desc": "Developed Markets (ex-USA)",
    "funds" : [
        {
            "ticker" : "IGOV"
        }
    ]
}

USA = {
    "region" : "USA",
    "region_desc" : "United States",
    "funds" : [
        {
            "ticker" : "AGG"
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
