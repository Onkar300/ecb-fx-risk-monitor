"""Phase 7 — unit tests for the pure metric functions."""
import numpy as np
import pandas as pd

from src.metrics import log_returns


def test_log_returns_length():
    prices = pd.Series([1.0, 1.1, 1.05, 1.2])
    assert len(log_returns(prices)) == len(prices) - 1
