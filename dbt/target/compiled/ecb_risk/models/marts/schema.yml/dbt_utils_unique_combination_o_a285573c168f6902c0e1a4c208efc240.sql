





with validation_errors as (

    select
        obs_date, pair
    from "ecb_risk"."analytics_marts"."fct_fx_volatility"
    group by obs_date, pair
    having count(*) > 1

)

select *
from validation_errors


