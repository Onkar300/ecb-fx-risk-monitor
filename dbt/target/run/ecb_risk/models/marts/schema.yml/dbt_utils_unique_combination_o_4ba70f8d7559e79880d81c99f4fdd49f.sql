select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      





with validation_errors as (

    select
        obs_date, pair
    from "ecb_risk"."analytics_marts"."fct_fx_returns"
    group by obs_date, pair
    having count(*) > 1

)

select *
from validation_errors



      
    ) dbt_internal_test