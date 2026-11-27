"""Performance and risk metrics for monthly return series."""
import numpy as np
import pandas as pd


def max_drawdown(r):
    wealth = (1 + r).cumprod()
    return (wealth / wealth.cummax() - 1).min()


def summary(r, bench, rf):
    rf = rf.reindex(r.index)
    excess = r - rf
    active = r - bench
    downside = excess[excess < 0]
    years = len(r) / 12
    return pd.Series({
        "Ann. return": (1 + r).prod() ** (1 / years) - 1,
        "Ann. volatility": r.std() * np.sqrt(12),
        "Sharpe": excess.mean() / r.std() * np.sqrt(12),
        "Sortino": excess.mean() / np.sqrt((downside ** 2).sum() / len(r)) * np.sqrt(12),
        "Max drawdown": max_drawdown(r),
        "Beta vs 60/40": np.cov(r, bench)[0, 1] / bench.var(),
        "Tracking error": active.std() * np.sqrt(12),
        "Information ratio": active.mean() / active.std() * np.sqrt(12) if active.std() > 0 else np.nan,
    })
