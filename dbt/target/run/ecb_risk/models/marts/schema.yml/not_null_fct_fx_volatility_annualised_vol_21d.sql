select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select annualised_vol_21d
from "ecb_risk"."analytics_marts"."fct_fx_volatility"
where annualised_vol_21d is null



      
    ) dbt_internal_test