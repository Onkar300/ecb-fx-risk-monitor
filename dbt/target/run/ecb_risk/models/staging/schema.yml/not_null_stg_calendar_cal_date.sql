select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select cal_date
from "ecb_risk"."analytics_staging"."stg_calendar"
where cal_date is null



      
    ) dbt_internal_test