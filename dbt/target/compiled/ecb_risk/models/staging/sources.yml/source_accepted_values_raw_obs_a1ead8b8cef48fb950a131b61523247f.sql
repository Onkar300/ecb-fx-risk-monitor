
    
    

with all_values as (

    select
        series_group as value_field,
        count(*) as n_records

    from "ecb_risk"."raw"."observations"
    group by series_group

)

select *
from all_values
where value_field not in (
    'fx_rates','policy_rates','inflation'
)


