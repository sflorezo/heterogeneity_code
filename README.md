# heterogeneity_code {.unnumbered}

__________
# Where we at?

2026-01-29

- Can the variation in important asset classes prices be explained by the variation in funds holdings principal components? How?

<!--========== International Bond Prices Evolution ==========-->
## International Bond Prices Evolution

**Evolution of Bond Prices in Time** <br>
<img src="_imagesdump/2026-02-06-16-44-37.png" width="650" /> <br>
The figure shows the evolution in time of 3 very important ETFs for bonds (EM, DM and USA). What drives the variation behind the prices in these? Which countries? For this, I will need to see the holdings of such ETFs.

 <br>

<!--========== International Bond Holdings Evolution ==========-->
## International Bond Holdings Evolution

<br>

**1. Evolution of Bond Dollar Holdings Across Time** <br>
<img src="_imagesdump/2026-02-05-17-18-32.png" width="650" /> <br>
For each economy type, the figure shows the ratio of bond dollar holdings in that economy type and period, as proportion to the time average bond dollar holdings for the economy type (for comparison across economies).

<br>

**2 Evolution of the Portfolio Allocation to Each Economy Across Time (size weighted)** <br>
<img src="_imagesdump/2026-02-05-17-23-55.png" width="650" /> <br>
For each economy type, the figure shows the fund size-weighted ratio of the portfolio share assigned to that economy type (holdings in economy type / total holdings) in a period, as proportion to the time average portfolio share for the economy type (for comparison across economies).

<br>

**2 Evolution of the Portfolio Allocation to Each Economy Across Time (equally weighted)** <br>
<img src="_imagesdump/2026-02-05-17-37-03.png" width="650" /> <br>
For each economy type, the figure shows the equally sized ratio of the portfolio share assigned to that economy type (holdings in economy type / total holdings) in a period, as proportion to the time average portfolio share for the economy type (for comparison across economies).

<br>

**Main Message:** We need to see bond aggregate prices and see how these might be driving those responses by these guys. Currently in script [EM_vs_DMexUSA.py](src/heterogeneity_code/a_nport_portshares/c_PCs_prelim_regressions/check_lhs/EM_vs_DMexUSA.py)