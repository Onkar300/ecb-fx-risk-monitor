
    
    

select
    obs_date as unique_field,
    count(*) as n_records

from "ecb_risk"."analytics_staging"."stg_inflation"
where obs_date is not null
group by obs_date
having count(*) > 1


