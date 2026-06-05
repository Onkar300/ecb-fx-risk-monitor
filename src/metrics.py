"""Phase 4 — Risk metrics.

Named, defensible measures (this is your Risk Analyst story):
  - rolling annualised volatility
  - Value-at-Risk: historical + parametric (variance-covariance)
  - z-score anomaly flags on daily FX returns
  - (stretch) GARCH(1,1) conditional volatility via `arch`

These are pure functions on a returns Series so they're unit-testable (Phase 7).
We FILL THESE IN in Phase 4.
"""
import numpy as np
import pandas as pd


def log_returns(prices: pd.Series) -> pd.Series:
    """Daily log returns."""
    return np.log(prices / prices.shift(1)).dropna()


def rolling_volatility(returns: pd.Series, window: int = 21, annualize: bool = True) -> pd.Series:
    """Rolling stdev of returns; annualised by sqrt(252) by default."""
    raise NotImplementedError  # Phase 4


def historical_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """Historical VaR at the given confidence (e.g. 5%)."""
    raise NotImplementedError  # Phase 4


def parametric_var(returns: pd.Series, alpha: float = 0.05) -> float:
    """Parametric (normal) VaR."""
    raise NotImplementedError  # Phase 4


def zscore_flags(returns: pd.Series, window: int = 60, threshold: float = 3.0) -> pd.Series:
    """Boolean flags where |rolling z-score| exceeds threshold."""
    raise NotImplementedError  # Phase 4
