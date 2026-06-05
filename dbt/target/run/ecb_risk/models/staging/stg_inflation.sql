
  create view "ecb_risk"."analytics_staging"."stg_inflation__dbt_tmp"
    
    
  as (
    -- HICP forward-filled onto the daily business-day calendar.


with hicp as (
    select
        obs_date as hicp_month,
        cast(value as numeric(8, 4)) as hicp_yoy_pct
    from "ecb_risk"."raw"."observations"
    where series_group = 'inflation'
      and series_id    = 'HICP_ALL_ANR'
      and value is not null
)
select
    c.cal_date as obs_date,
    h.hicp_month,
    h.hicp_yoy_pct
from "ecb_risk"."analytics_staging"."stg_calendar" c
left join lateral (
    select hicp_month, hicp_yoy_pct
    from hicp
    where hicp_month <= c.cal_date
    order by hicp_month desc
    limit 1
) h on true
  );