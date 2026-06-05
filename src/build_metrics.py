"""Phase 4 — Build risk metrics into the warehouse.

Reads marts.fct_fx_returns, computes per-pair risk metrics, and writes:
  * marts.fct_fx_risk_metrics  (daily, per-pair: rolling vol, z-score, anomaly
                                flag, GARCH conditional vol)
  * marts.fct_fx_var_summary   (one row per pair: historical & parametric VaR)

Idempotent: both tables are dropped and recreated each run.
"""
from __future__ import annotations

import logging

import pandas as pd
from sqlalchemy import text

from src import metrics
from src.db import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("build_metrics")

PAIRS = ["EUR_USD", "EUR_GBP", "EUR_JPY", "EUR_CHF"]
RETURNS_TABLE = "analytics_marts.fct_fx_returns"


def load_returns() -> pd.DataFrame:
    q = f"select obs_date, pair, log_return from {RETURNS_TABLE} order by obs_date"
    with engine.connect() as conn:
        df = pd.read_sql(text(q), conn, parse_dates=["obs_date"])
    log.info("loaded %d return rows across %d pairs", len(df), df['pair'].nunique())
    return df


def build_daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for pair in PAIRS:
        sub = df[df["pair"] == pair].sort_values("obs_date").set_index("obs_date")
        r = sub["log_return"]
        rv = metrics.rolling_volatility(r, window=21, annualise=True)
        z = metrics.zscore_flags(r, window=60, threshold=3.0)
        try:
            gv = metrics.garch_conditional_vol(r, annualise=True)
        except Exception as exc:  # noqa: BLE001
            log.warning("GARCH failed for %s (%s); filling NaN", pair, exc)
            gv = pd.Series(index=r.index, dtype=float)

        part = pd.DataFrame({
            "obs_date": r.index,
            "pair": pair,
            "log_return": r.values,
            "rolling_vol_21d": rv.values,
            "zscore_60d": z["zscore"].values,
            "is_anomaly": z["is_anomaly"].values,
            "garch_cond_vol": gv.reindex(r.index).values,
        })
        out.append(part)
        log.info("%s: %d rows, %d anomalies flagged", pair, len(part),
                 int(part["is_anomaly"].sum()))
    return pd.concat(out, ignore_index=True)


def build_var_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair in PAIRS:
        r = df[df["pair"] == pair]["log_return"]
        rows.append({
            "pair": pair,
            "historical_var_95": metrics.historical_var(r, 0.05),
            "parametric_var_95": metrics.parametric_var(r, 0.05),
            "historical_var_99": metrics.historical_var(r, 0.01),
            "parametric_var_99": metrics.parametric_var(r, 0.01),
            "n_observations": int(r.shape[0]),
        })
    return pd.DataFrame(rows)


def write_table(df: pd.DataFrame, name: str) -> None:
    with engine.begin() as conn:
        df.to_sql(name, conn, schema="analytics_marts",
                  if_exists="replace", index=False)
    log.info("wrote analytics_marts.%s (%d rows)", name, len(df))


def main() -> None:
    log.info("=== build_metrics start ===")
    df = load_returns()
    daily = build_daily_metrics(df)
    var = build_var_summary(df)
    write_table(daily, "fct_fx_risk_metrics")
    write_table(var, "fct_fx_var_summary")
    log.info("=== build_metrics done ===")


if __name__ == "__main__":
    main()
