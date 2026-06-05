"""Phase 6 — Data quality checks. Cheap, named checks that read like a contract."""
import logging

from src.db import fetch_df

log = logging.getLogger(__name__)


class DataQualityError(Exception):
    pass


def check_row_counts():
    """Each raw table has > 0 rows. TODO Phase 6."""
    raise NotImplementedError


def check_freshness(max_lag_days: int = 7):
    """Latest FX observation is recent enough. TODO Phase 6."""
    raise NotImplementedError


def check_no_duplicate_keys():
    """(series_id, date) is unique. TODO Phase 6."""
    raise NotImplementedError


def run_all():
    check_row_counts()
    check_freshness()
    check_no_duplicate_keys()
    log.info("all data-quality checks passed")
