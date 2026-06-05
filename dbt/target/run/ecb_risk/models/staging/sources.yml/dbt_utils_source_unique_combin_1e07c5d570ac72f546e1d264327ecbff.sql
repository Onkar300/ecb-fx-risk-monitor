select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      





with validation_errors as (

    select
        series_id, obs_date
    from "ecb_risk"."raw"."observations"
    group by series_id, obs_date
    having count(*) > 1

)

select *
from validation_errors



      
    ) dbt_internal_test