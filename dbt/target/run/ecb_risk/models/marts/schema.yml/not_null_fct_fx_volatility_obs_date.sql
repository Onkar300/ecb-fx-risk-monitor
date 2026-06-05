select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select obs_date
from "ecb_risk"."analytics_marts"."fct_fx_volatility"
where obs_date is null



      
    ) dbt_internal_test