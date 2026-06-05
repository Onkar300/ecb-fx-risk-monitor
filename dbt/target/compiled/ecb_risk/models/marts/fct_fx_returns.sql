-- Daily FX log returns per pair, long form for downstream metric work.


with pivoted as (
    select * from "ecb_risk"."analytics_staging"."stg_fx_wide"
),
returns as (
    select
        obs_date,
        ln(eur_usd / nullif(lag(eur_usd) over (order by obs_date), 0)) as ret_eur_usd,
        ln(eur_gbp / nullif(lag(eur_gbp) over (order by obs_date), 0)) as ret_eur_gbp,
        ln(eur_jpy / nullif(lag(eur_jpy) over (order by obs_date), 0)) as ret_eur_jpy,
        ln(eur_chf / nullif(lag(eur_chf) over (order by obs_date), 0)) as ret_eur_chf
    from pivoted
)
-- Unpivot to long: easier for the dashboard + metrics module to filter by pair.
select obs_date, 'EUR_USD'::text as pair, ret_eur_usd as log_return from returns where ret_eur_usd is not null
union all
select obs_date, 'EUR_GBP', ret_eur_gbp from returns where ret_eur_gbp is not null
union all
select obs_date, 'EUR_JPY', ret_eur_jpy from returns where ret_eur_jpy is not null
union all
select obs_date, 'EUR_CHF', ret_eur_chf from returns where ret_eur_chf is not null