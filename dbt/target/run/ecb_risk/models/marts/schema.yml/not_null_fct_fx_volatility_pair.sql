select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select pair
from "ecb_risk"."analytics_marts"."fct_fx_volatility"
where pair is null



      
    ) dbt_internal_test