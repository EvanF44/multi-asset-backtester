"""Walk-forward backtest with monthly rebalancing and transaction costs."""
import pandas as pd


def run(returns, rf, strategy, lookback=36, cost_bps=5):
    """At each month-end, set target weights using only the previous `lookback` months,
    pay costs on the trades needed to get there, then earn next month's return."""
    weights, gross, net = {}, {}, {}
    drifted = None
    for t in range(lookback, len(returns)):
        date = returns.index[t]
        target = strategy(returns.iloc[t - lookback:t], rf.iloc[t - lookback:t])
        turnover = target.abs().sum() if drifted is None else (target - drifted).abs().sum()
        r = returns.iloc[t]
        g = float((target * r).sum())
        weights[date], gross[date] = target, g
        net[date] = g - turnover * cost_bps / 10_000
        drifted = target * (1 + r) / (1 + g)          # weights after the month's price moves
    return pd.Series(net, name="net"), pd.Series(gross, name="gross"), pd.DataFrame(weights).T
