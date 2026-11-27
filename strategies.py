"""Portfolio strategies. Each takes the trailing window of monthly returns
(only data available at the time) and returns target weights that sum to 1."""
import numpy as np
import pandas as pd


def equal_weight(window, rf_window=None):
    n = window.shape[1]
    return pd.Series(1 / n, index=window.columns)


def risk_parity(window, rf_window=None):
    """Naive risk parity: weight each asset by 1 / volatility."""
    inv_vol = 1 / window.std()
    return inv_vol / inv_vol.sum()


def max_sharpe_mc(window, rf_window, n_portfolios=10_000, seed=0):
    """Monte Carlo: try 10,000 random long-only portfolios, keep the highest Sharpe."""
    rng = np.random.default_rng(seed)
    mu = window.mean().values * 12                    # annualized expected returns
    cov = window.cov().values * 12                    # annualized covariance matrix
    rf = rf_window.mean() * 12
    w = rng.dirichlet(np.ones(len(mu)), n_portfolios) # random weights, each row sums to 1
    port_ret = w @ mu
    port_vol = np.sqrt(np.einsum("ij,jk,ik->i", w, cov, w))
    sharpe = (port_ret - rf) / port_vol
    return pd.Series(w[np.argmax(sharpe)], index=window.columns)


def benchmark_60_40(window, rf_window=None):
    w = pd.Series(0.0, index=window.columns)
    w["SPY"], w["AGG"] = 0.6, 0.4
    return w
