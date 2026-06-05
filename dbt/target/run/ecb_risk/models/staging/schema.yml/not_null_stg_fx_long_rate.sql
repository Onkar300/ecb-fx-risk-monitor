select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select rate
from "ecb_risk"."analytics_staging"."stg_fx_long"
where rate is null



      
    ) dbt_internal_test