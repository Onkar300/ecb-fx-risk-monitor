"""Unit tests for the pure risk-metric functions (src/metrics.py)."""
import numpy as np
import pandas as pd

from src import metrics


def _sample_returns(seed: int = 0, n: int = 500, vol: float = 0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n, freq="B")
    return pd.Series(rng.normal(0.0, vol, n), index=idx)


def test_log_returns_length_and_value():
    prices = pd.Series([100.0, 110.0, 99.0])
    r = metrics.log_returns(prices)
    assert len(r) == 2
    assert np.isclose(r.iloc[0], np.log(110 / 100))


def test_rolling_volatility_is_annualised():
    r = _sample_returns(vol=0.01)
    rv = metrics.rolling_volatility(r, window=21, annualise=True).dropna()
    # ~1% daily vol annualises to roughly 0.16; allow a wide band.
    assert 0.05 < rv.mean() < 0.30
    # Annualised must exceed the non-annualised version.
    raw = metrics.rolling_volatility(r, window=21, annualise=False).dropna()
    assert rv.mean() > raw.mean()


def test_var_positive_and_99_exceeds_95():
    r = _sample_returns()
    h95 = metrics.historical_var(r, 0.05)
    h99 = metrics.historical_var(r, 0.01)
    p95 = metrics.parametric_var(r, 0.05)
    assert h95 > 0 and p95 > 0
    # Deeper-tail VaR must be at least as large.
    assert h99 >= h95


def test_zscore_flags_shape_and_extreme_detection():
    r = _sample_returns(n=200).copy()
    r.iloc[150] = 0.20  # inject an obvious outlier
    out = metrics.zscore_flags(r, window=60, threshold=3.0)
    assert set(["log_return", "zscore", "is_anomaly"]).issubset(out.columns)
    assert bool(out["is_anomaly"].iloc[150]) is True


def test_empty_returns_handled():
    empty = pd.Series(dtype=float)
    assert np.isnan(metrics.historical_var(empty))
    assert np.isnan(metrics.parametric_var(empty))
