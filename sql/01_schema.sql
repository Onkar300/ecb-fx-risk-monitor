-- Phase 2 — schema. Raw landing + staging. Marts come in 03_marts.sql.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Raw landing: long/tidy, one row per (series, date).
CREATE TABLE IF NOT EXISTS raw.observations (
    series_id   TEXT        NOT NULL,   -- e.g. EUR_USD, DFR, HICP_ALL_ANR
    series_group TEXT       NOT NULL,   -- fx_rates | policy_rates | inflation
    obs_date    DATE        NOT NULL,
    value       DOUBLE PRECISION,
    loaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (series_id, obs_date)   -- enables idempotent upserts
);

CREATE INDEX IF NOT EXISTS idx_obs_group_date
    ON raw.observations (series_group, obs_date);
