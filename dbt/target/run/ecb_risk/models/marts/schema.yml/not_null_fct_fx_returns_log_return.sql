select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select log_return
from "ecb_risk"."analytics_marts"."fct_fx_returns"
where log_return is null



      
    ) dbt_internal_test