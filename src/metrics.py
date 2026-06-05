"""Phase 4 — Risk metrics.

Named, defensible measures computed on a daily FX log-return Series:
  - rolling annualised volatility
  - Value-at-Risk: historical + parametric (variance-covariance)
  - z-score anomaly flags on returns
  - GARCH(1,1) conditional volatility (volatility clustering)

Design note: every function is a PURE function of its inputs (no DB calls, no
globals), which makes them unit-testable. The DB read/write lives in
src/build_metrics.py so this module stays cleanly testable.

These are RISK-MONITORING measures (detect / quantify / flag), not forecasts.
GARCH yields a conditional volatility *estimate*, not a market prediction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


# --------------------------------------------------------------------------- #
# Returns
# --------------------------------------------------------------------------- #
def log_returns(prices: pd.Series) -> pd.Series:
    """Daily log returns from a price Series. Drops the first (NaN) row."""
    return np.log(prices / prices.shift(1)).dropna()


# --------------------------------------------------------------------------- #
# Volatility
# --------------------------------------------------------------------------- #
def rolling_volatility(returns: pd.Series, window: int = 21,
                       annualise: bool = True) -> pd.Series:
    """Rolling sample stdev of returns. Annualised by sqrt(252) by default.

    A 21-day window approximates one trading month.
    """
    vol = returns.rolling(window=window).std(ddof=1)
    if annualise:
        vol = vol * np.sqrt(TRADING_DAYS)
    return vol


# --------------------------------------------------------------------------- #
# Value-at-Risk  (reported as a positive loss magnitude)
# --------------------------------------------------------------------------- #
def historical_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """Historical (empirical) VaR at confidence 1-alpha.

    Returns the loss magnitude: the alpha-quantile of returns, sign-flipped so
    a 5% VaR of 0.012 reads as 'a 1.2% daily loss is exceeded 5% of the time'.
    """
    if returns.empty:
        return float("nan")
    return float(-np.quantile(returns, alpha))


def parametric_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """Parametric (normal / variance-covariance) VaR as a positive loss.

    Assumes returns ~ Normal(mu, sigma). Underestimates tail risk when returns
    have fat tails (they usually do) — which is exactly the historical-vs-
    parametric tradeoff worth discussing.
    """
    from scipy.stats import norm
    if returns.empty:
        return float("nan")
    mu, sigma = returns.mean(), returns.std(ddof=1)
    z = norm.ppf(alpha)            # negative for small alpha
    return float(-(mu + sigma * z))


# --------------------------------------------------------------------------- #
# Anomaly detection
# --------------------------------------------------------------------------- #
def zscore_flags(returns: pd.Series, window: int = 60,
                 threshold: float = 3.0) -> pd.DataFrame:
    """Flag returns whose rolling z-score exceeds +/- threshold.

    Returns a DataFrame [return, zscore, is_anomaly] aligned to `returns`.
    """
    roll_mean = returns.rolling(window).mean()
    roll_std = returns.rolling(window).std(ddof=1)
    z = (returns - roll_mean) / roll_std
    return pd.DataFrame({
        "log_return": returns,
        "zscore": z,
        "is_anomaly": z.abs() > threshold,
    })


# --------------------------------------------------------------------------- #
# GARCH(1,1) — volatility clustering
# --------------------------------------------------------------------------- #
def garch_conditional_vol(returns: pd.Series, annualise: bool = True) -> pd.Series:
    """Fit GARCH(1,1) and return the in-sample conditional volatility.

    Uses the `arch` library. Returns are scaled to % (×100) for the optimiser's
    numerical stability, then conditional vol is scaled back.
    """
    from arch import arch_model
    r = returns.dropna() * 100.0
    model = arch_model(r, mean="constant", vol="GARCH", p=1, q=1, dist="normal")
    res = model.fit(disp="off")
    cond_vol = res.conditional_volatility / 100.0      # back to return units
    cond_vol = pd.Series(cond_vol, index=r.index)
    if annualise:
        cond_vol = cond_vol * np.sqrt(TRADING_DAYS)
    return cond_vol
