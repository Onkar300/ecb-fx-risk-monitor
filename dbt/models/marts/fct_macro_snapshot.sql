-- One row per business day with the full macro context: FX, policy rates, HICP.
-- This is the table the dashboard's overview tab reads from.
{{ config(materialized='table') }}

select
    c.cal_date              as obs_date,
    fx.eur_usd,
    fx.eur_gbp,
    fx.eur_jpy,
    fx.eur_chf,
    pr.mro_rate,
    pr.dfr_rate,
    pr.mlf_rate,
    inf.hicp_yoy_pct
from {{ ref('stg_calendar') }} c
left join {{ ref('stg_fx_wide') }}            fx  on fx.obs_date  = c.cal_date
left join {{ ref('stg_policy_rates_wide') }}  pr  on pr.obs_date  = c.cal_date
left join {{ ref('stg_inflation') }}          inf on inf.obs_date = c.cal_date
