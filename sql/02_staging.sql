-- =============================================================================
-- Phase 2 — Staging layer.
-- Sits between raw.observations (long, mixed-frequency) and marts.
-- Goal: clean shapes that analytics & risk metrics can consume directly.
-- =============================================================================

-- Calendar of business days. We use it to forward-fill the monthly HICP series
-- onto a daily timeline so joins to FX/policy data don't produce nulls.
DROP TABLE IF EXISTS staging.calendar CASCADE;
CREATE TABLE staging.calendar AS
SELECT d::date AS cal_date
FROM generate_series(DATE '2015-01-01', CURRENT_DATE, INTERVAL '1 day') AS d
WHERE EXTRACT(ISODOW FROM d) < 6;   -- 1..5 = Mon..Fri (drops weekends)

ALTER TABLE staging.calendar ADD PRIMARY KEY (cal_date);

-- -----------------------------------------------------------------------------
-- FX (daily) — long view: typed, validated. Filters obvious nulls.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW staging.stg_fx_long AS
SELECT
    obs_date,
    series_id,
    value::numeric(18, 6) AS rate    -- EUR per 1 unit of foreign currency
FROM raw.observations
WHERE series_group = 'fx_rates'
  AND value IS NOT NULL
  AND value > 0;

-- -----------------------------------------------------------------------------
-- FX wide: one column per pair. This is the shape the risk module consumes.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW staging.stg_fx_wide AS
SELECT
    obs_date,
    MAX(CASE WHEN series_id = 'EUR_USD' THEN rate END) AS eur_usd,
    MAX(CASE WHEN series_id = 'EUR_GBP' THEN rate END) AS eur_gbp,
    MAX(CASE WHEN series_id = 'EUR_JPY' THEN rate END) AS eur_jpy,
    MAX(CASE WHEN series_id = 'EUR_CHF' THEN rate END) AS eur_chf
FROM staging.stg_fx_long
GROUP BY obs_date;

-- -----------------------------------------------------------------------------
-- Policy rates wide: ECB Main Refi, Deposit Facility, Marginal Lending.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW staging.stg_policy_rates_wide AS
SELECT
    obs_date,
    MAX(CASE WHEN series_id = 'MRO' THEN value::numeric(8, 4) END) AS mro_rate,
    MAX(CASE WHEN series_id = 'DFR' THEN value::numeric(8, 4) END) AS dfr_rate,
    MAX(CASE WHEN series_id = 'MLF' THEN value::numeric(8, 4) END) AS mlf_rate
FROM raw.observations
WHERE series_group = 'policy_rates'
  AND value IS NOT NULL
GROUP BY obs_date;

-- -----------------------------------------------------------------------------
-- HICP inflation: monthly, stamped to month-start, lags by a few weeks.
-- Forward-fill onto the daily calendar so any join "just works".
-- LATERAL pulls the most recent HICP observation on-or-before each calendar day.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW staging.stg_inflation AS
WITH hicp_raw AS (
    SELECT
        obs_date    AS hicp_month,
        value::numeric(8, 4) AS hicp_yoy_pct
    FROM raw.observations
    WHERE series_group = 'inflation'
      AND series_id    = 'HICP_ALL_ANR'
      AND value IS NOT NULL
)
SELECT
    c.cal_date            AS obs_date,
    h.hicp_month,
    h.hicp_yoy_pct
FROM staging.calendar c
LEFT JOIN LATERAL (
    SELECT hicp_month, hicp_yoy_pct
    FROM hicp_raw
    WHERE hicp_month <= c.cal_date
    ORDER BY hicp_month DESC
    LIMIT 1
) h ON TRUE;
