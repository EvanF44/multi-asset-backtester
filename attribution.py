"""Brinson-Fachler attribution by asset class, computed monthly and summed.

Allocation:  (w_p - w_b) * (R_b,class - R_b,total)   -> did we overweight the right classes?
Selection:   w_b * (R_p,class - R_b,class)            -> did we pick better ETFs within a class?
Interaction: (w_p - w_b) * (R_p,class - R_b,class)
The three effects add up exactly to (portfolio gross return - benchmark return) each month.
"""
import pandas as pd
from data import ASSETS

# What the benchmark holds in each class (Alternatives uses GLD as its reference return)
BENCH_CLASS_ETF = {"Equity": "SPY", "Fixed Income": "AGG", "Alternatives": "GLD"}


def brinson(port_w, bench_w, returns):
    classes = sorted(set(ASSETS.values()))
    rows = []
    for date in port_w.index:
        r = returns.loc[date]
        rb_total = float((bench_w.loc[date] * r).sum())
        effects = {"Allocation": 0.0, "Selection": 0.0, "Interaction": 0.0}
        for c in classes:
            members = [a for a in ASSETS if ASSETS[a] == c]
            wp = port_w.loc[date, members].sum()
            wb = bench_w.loc[date, members].sum()
            rb_c = r[BENCH_CLASS_ETF[c]]
            rp_c = (port_w.loc[date, members] * r[members]).sum() / wp if wp > 0 else rb_c
            effects["Allocation"] += (wp - wb) * (rb_c - rb_total)
            effects["Selection"] += wb * (rp_c - rb_c)
            effects["Interaction"] += (wp - wb) * (rp_c - rb_c)
        rows.append(pd.Series(effects, name=date))
    return pd.DataFrame(rows)
