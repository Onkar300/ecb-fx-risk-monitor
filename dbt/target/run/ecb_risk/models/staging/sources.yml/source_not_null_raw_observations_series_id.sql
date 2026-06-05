select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select series_id
from "ecb_risk"."raw"."observations"
where series_id is null



      
    ) dbt_internal_test