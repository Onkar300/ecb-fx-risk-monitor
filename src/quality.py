"""Phase 6 — Data-quality checks on the raw landing table.

Cheap, named, fail-fast checks that read like a contract. Run as a pipeline
step (manually, or between ingest and transform).
"""
from __future__ import annotations

import logging

from sqlalchemy import text

from src.db import engine

log = logging.getLogger(__name__)

EXPECTED_SERIES = 8          # 4 FX + 3 policy rates + 1 HICP
MAX_FX_LAG_DAYS = 10         # FX should be fresh within ~10 calendar days


class DataQualityError(Exception):
    pass


def _scalar(sql: str):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def check_row_counts() -> None:
    n = _scalar("select count(*) from raw.observations")
    if not n or n <= 0:
        raise DataQualityError("raw.observations is empty")
    log.info("row-count check passed: %s rows", n)


def check_series_present() -> None:
    n = _scalar("select count(distinct series_id) from raw.observations")
    if n < EXPECTED_SERIES:
        raise DataQualityError(f"expected >= {EXPECTED_SERIES} series, found {n}")
    log.info("series-presence check passed: %s distinct series", n)


def check_freshness() -> None:
    lag = _scalar("""
        select current_date - max(obs_date)
        from raw.observations
        where series_group = 'fx_rates'
    """)
    if lag is None or lag > MAX_FX_LAG_DAYS:
        raise DataQualityError(f"FX data is stale: {lag} days behind")
    log.info("freshness check passed: FX is %s day(s) behind", lag)


def check_no_duplicate_keys() -> None:
    dupes = _scalar("""
        select count(*) from (
            select series_id, obs_date
            from raw.observations
            group by series_id, obs_date
            having count(*) > 1
        ) d
    """)
    if dupes and dupes > 0:
        raise DataQualityError(f"{dupes} duplicate (series_id, obs_date) keys")
    log.info("uniqueness check passed: no duplicate keys")


def run_all() -> None:
    check_row_counts()
    check_series_present()
    check_freshness()
    check_no_duplicate_keys()
    log.info("all data-quality checks passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
    run_all()
