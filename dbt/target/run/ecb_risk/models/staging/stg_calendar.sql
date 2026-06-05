
  
    

  create  table "ecb_risk"."analytics_staging"."stg_calendar__dbt_tmp"
  
  
    as
  
  (
    -- Business-day calendar from 2015-01-01 to today. Used to forward-fill HICP.


select d::date as cal_date
from generate_series(date '2015-01-01', current_date, interval '1 day') as d
where extract(isodow from d) < 6
  );
  