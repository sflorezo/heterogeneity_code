#%% ========== auxiliar: see names of main funds by PCA componets ========== %%#


for k in range(1, K+1):
    print(k)
    X_pc_ = X_pc_.sort_values(by = f"pc_{k}", ascending = False)
    top = [
        item if item is not None else "None" 
        for item in X_pc_["series_name"].head(10).to_list()
    ]
    bottom = [
        item if item is not None else "None" 
        for item in X_pc_["series_name"].tail(10).to_list()
    ]

    lines = "\n".join(
        ["\n#========== TOP ==========#\n"]
        + top
        + ["\n#========== BOTTOM ==========#\n"]
        + bottom
    )

    with open(PROJECT_TEMP / f"pc_{k}.txt", "w") as f:
        f.writelines(lines)
    