select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        pair as value_field,
        count(*) as n_records

    from "ecb_risk"."analytics_marts"."fct_fx_returns"
    group by pair

)

select *
from all_values
where value_field not in (
    'EUR_USD','EUR_GBP','EUR_JPY','EUR_CHF'
)



      
    ) dbt_internal_test