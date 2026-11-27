"""Download ETF prices with yfinance and turn them into monthly returns."""
import os
import pandas as pd

# Each ETF and the asset class it belongs to (used for attribution)
ASSETS = {
    "SPY": "Equity",        # US large-cap stocks
    "EFA": "Equity",        # International developed stocks
    "VNQ": "Equity",        # US real estate (REITs)
    "AGG": "Fixed Income",  # US aggregate bonds
    "TLT": "Fixed Income",  # 20+ year US Treasuries
    "GLD": "Alternatives",  # Gold
}
RISK_FREE = "BIL"           # 1-3 month T-bill ETF, used as the risk-free rate
PRICE_FILE = "data/prices.csv"


def download(start="2007-06-01", end=None):
    """Download adjusted closing prices once and save them, so later runs work offline."""
    import yfinance as yf
    tickers = list(ASSETS) + [RISK_FREE]
    px = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    os.makedirs("data", exist_ok=True)
    px.to_csv(PRICE_FILE)
    print(f"Saved {px.shape[0]} days x {px.shape[1]} tickers to {PRICE_FILE}")


def load_monthly_returns():
    """Return (asset returns, risk-free returns) as monthly DataFrames/Series."""
    if not os.path.exists(PRICE_FILE):
        download()
    px = pd.read_csv(PRICE_FILE, index_col=0, parse_dates=True)
    monthly = px.resample("ME").last()           # last price of each month
    rets = monthly.pct_change().dropna()          # monthly % change
    return rets[list(ASSETS)], rets[RISK_FREE]
