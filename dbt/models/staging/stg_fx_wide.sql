-- FX rates pivoted: one row per date, one column per pair.
{{ config(materialized='view') }}

select
    obs_date,
    max(case when series_id = 'EUR_USD' then rate end) as eur_usd,
    max(case when series_id = 'EUR_GBP' then rate end) as eur_gbp,
    max(case when series_id = 'EUR_JPY' then rate end) as eur_jpy,
    max(case when series_id = 'EUR_CHF' then rate end) as eur_chf
from {{ ref('stg_fx_long') }}
group by obs_date
