
  
    

  create  table "ecb_risk"."analytics_marts"."fct_macro_snapshot__dbt_tmp"
  
  
    as
  
  (
    -- One row per business day with the full macro context: FX, policy rates, HICP.
-- This is the table the dashboard's overview tab reads from.


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
from "ecb_risk"."analytics_staging"."stg_calendar" c
left join "ecb_risk"."analytics_staging"."stg_fx_wide"            fx  on fx.obs_date  = c.cal_date
left join "ecb_risk"."analytics_staging"."stg_policy_rates_wide"  pr  on pr.obs_date  = c.cal_date
left join "ecb_risk"."analytics_staging"."stg_inflation"          inf on inf.obs_date = c.cal_date
  );
  