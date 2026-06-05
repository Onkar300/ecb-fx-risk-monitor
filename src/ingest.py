"""Phase 1 — Ingestion.

Pulls ECB series (FX reference rates, key policy rates, HICP) and lands them in
`raw.observations` idempotently.

Design:
  * Primary fetch via the `ecbdata` library (smooths SDMX).
  * Automatic fallback to the ECB SDMX REST API if the library raises.
  * Flexible TIME_PERIOD parsing: daily ("2024-01-15") and monthly ("2024-01").
  * Idempotent upsert on (series_id, obs_date) so re-runs never duplicate.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

import pandas as pd
import requests
from psycopg2.extras import execute_values

from src.config import INGEST_START_DATE, load_series
from src.db import engine, run_sql_file

log = logging.getLogger(__name__)

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
SDMX_BASE = "https://data-api.ecb.europa.eu/service/data"


# --------------------------------------------------------------------------- #
# Fetch
# --------------------------------------------------------------------------- #
def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce an ECB result into tidy columns [obs_date, value]."""
    cols = {c.upper(): c for c in df.columns}
    tp = cols.get("TIME_PERIOD")
    ov = cols.get("OBS_VALUE")
    if tp is None or ov is None:
        raise ValueError(f"unexpected columns: {list(df.columns)}")
    out = df[[tp, ov]].rename(columns={tp: "obs_date", ov: "value"})
    # Handles both daily (YYYY-MM-DD) and monthly (YYYY-MM) periods.
    out["obs_date"] = pd.to_datetime(out["obs_date"]).dt.date
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out.dropna(subset=["value"]).reset_index(drop=True)


def _fetch_via_library(series_key: str, start: str) -> pd.DataFrame:
    from ecbdata import ecbdata
    df = ecbdata.get_series(series_key, start=start)
    return _normalise(df)


def _fetch_via_rest(series_key: str, start: str) -> pd.DataFrame:
    """Fallback: hit the SDMX REST endpoint and parse CSV.

    series_key 'EXR.D.USD.EUR.SP00.A' -> flow 'EXR', key 'D.USD.EUR.SP00.A'.
    """
    flow, _, key = series_key.partition(".")
    url = f"{SDMX_BASE}/{flow}/{key}"
    resp = requests.get(
        url,
        params={"format": "csvdata", "startPeriod": start},
        headers={"Accept": "text/csv"},
        timeout=60,
    )
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    return _normalise(df)


def fetch_series(series_key: str, start: str = INGEST_START_DATE) -> pd.DataFrame:
    """Fetch one series, library-first with REST fallback."""
    try:
        df = _fetch_via_library(series_key, start)
        log.info("fetched %s via ecbdata (%d rows)", series_key, len(df))
    except Exception as exc:  # noqa: BLE001 - we genuinely want any failure to fall back
        log.warning("ecbdata failed for %s (%s); falling back to REST", series_key, exc)
        df = _fetch_via_rest(series_key, start)
        log.info("fetched %s via REST (%d rows)", series_key, len(df))
    return df


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #
def _upsert(series_id: str, series_group: str, df: pd.DataFrame) -> int:
    """Idempotent upsert into raw.observations."""
    if df.empty:
        log.warning("no rows to load for %s", series_id)
        return 0
    rows = [(series_id, series_group, r.obs_date, float(r.value)) for r in df.itertuples()]
    sql = """
        INSERT INTO raw.observations (series_id, series_group, obs_date, value)
        VALUES %s
        ON CONFLICT (series_id, obs_date)
        DO UPDATE SET value = EXCLUDED.value, loaded_at = now();
    """
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            execute_values(cur, sql, rows)
        raw_conn.commit()
    finally:
        raw_conn.close()
    return len(rows)


def ensure_schema() -> None:
    """Create raw/staging/marts schema + raw.observations if absent."""
    run_sql_file(str(SQL_DIR / "01_schema.sql"))


def land_raw(start: str = INGEST_START_DATE) -> dict[str, int]:
    """Pull every series in config/series.yml into raw.observations."""
    ensure_schema()
    cfg = load_series()
    summary: dict[str, int] = {}
    for group, series in cfg.items():
        for series_id, series_key in series.items():
            df = fetch_series(series_key, start=start)
            n = _upsert(series_id, group, df)
            summary[series_id] = n
    log.info("ingestion summary: %s", summary)
    return summary


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )
    land_raw()
