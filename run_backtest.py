"""Run every strategy, print metrics and attribution, and save charts to results/."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from data import load_monthly_returns
import strategies as s
import backtest
import metrics
import attribution

os.makedirs("results", exist_ok=True)
returns, rf = load_monthly_returns()

STRATS = {
    "60/40 benchmark": s.benchmark_60_40,
    "Equal weight": s.equal_weight,
    "Risk parity": s.risk_parity,
    "Max Sharpe (MC)": s.max_sharpe_mc,
}
results = {name: backtest.run(returns, rf, fn) for name, fn in STRATS.items()}
bench_net, _, bench_w = results["60/40 benchmark"]
start, end = bench_net.index[0], bench_net.index[-1]
print(f"Out-of-sample period: {start:%b %Y} to {end:%b %Y} ({len(bench_net)} months)\n")

# 1) Metrics table
table = pd.DataFrame({n: metrics.summary(net, bench_net, rf) for n, (net, _, _) in results.items()})
fmt = table.copy().astype(object)
for row in fmt.index:
    pct = row not in ("Sharpe", "Sortino", "Beta vs 60/40", "Information ratio")
    fmt.loc[row] = ["n/a" if pd.isna(v) else f"{v:.1%}" if pct else f"{v:.2f}" for v in table.loc[row]]
print(fmt.to_string(), "\n")
table.to_csv("results/metrics.csv")
with open("results/metrics.md", "w", encoding="utf-8") as f:
    f.write(fmt.to_markdown())

# 2) Brinson attribution vs 60/40, in basis points per year (average)
bench_gross = results["60/40 benchmark"][1]
years = len(bench_net) / 12
attr_rows = {}
for name, (net, gross, w) in results.items():
    if name == "60/40 benchmark":
        continue
    a = attribution.brinson(w, bench_w, returns)
    total = a.sum()
    total["Costs (vs benchmark)"] = ((net - gross) - (bench_net - bench_gross)).sum()
    total["Total excess return"] = (net - bench_net).sum()
    # check: the effects must add up exactly to the total
    assert abs(total.iloc[:4].sum() - total["Total excess return"]) < 1e-9
    attr_rows[name] = (total / years * 10_000).round(0)
attr = pd.DataFrame(attr_rows)
print("Brinson attribution vs 60/40 (average bps per year):")
print(attr.to_string(), "\n")
attr.to_csv("results/attribution.csv")
with open("results/attribution.md", "w", encoding="utf-8") as f:
    f.write(attr.to_markdown())

# 3) Charts
fig, ax = plt.subplots(figsize=(10, 4.5))
for name, (net, _, _) in results.items():
    ax.plot((1 + net).cumprod(), label=name, lw=1.8 if name == "60/40 benchmark" else 1.3)
ax.set_yscale("log"); ax.set_title("Growth of $1 (out-of-sample, after costs)")
ax.legend(frameon=False); [ax.spines[x].set_visible(False) for x in ("top", "right")]
plt.tight_layout(); plt.savefig("results/growth.png", dpi=150)

fig, ax = plt.subplots(figsize=(10, 3.5))
for name, (net, _, _) in results.items():
    w = (1 + net).cumprod(); ax.plot(w / w.cummax() - 1, label=name, lw=1.2)
ax.set_title("Drawdowns"); ax.legend(frameon=False)
[ax.spines[x].set_visible(False) for x in ("top", "right")]
plt.tight_layout(); plt.savefig("results/drawdowns.png", dpi=150)

w = results["Max Sharpe (MC)"][2]
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.stackplot(w.index, w.T.values, labels=w.columns)
ax.set_ylim(0, 1); ax.set_title("Max Sharpe (MC) weights over time")
ax.legend(loc="upper left", bbox_to_anchor=(1, 1), frameon=False)
plt.tight_layout(); plt.savefig("results/weights_max_sharpe.png", dpi=150)
print("Charts saved to results/")
