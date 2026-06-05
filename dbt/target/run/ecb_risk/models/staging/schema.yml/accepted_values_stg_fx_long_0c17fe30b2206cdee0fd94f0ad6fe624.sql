select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        series_id as value_field,
        count(*) as n_records

    from "ecb_risk"."analytics_staging"."stg_fx_long"
    group by series_id

)

select *
from all_values
where value_field not in (
    'EUR_USD','EUR_GBP','EUR_JPY','EUR_CHF'
)



      
    ) dbt_internal_test