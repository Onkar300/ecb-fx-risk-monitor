
    
    

select
    cal_date as unique_field,
    count(*) as n_records

from "ecb_risk"."analytics_staging"."stg_calendar"
where cal_date is not null
group by cal_date
having count(*) > 1


