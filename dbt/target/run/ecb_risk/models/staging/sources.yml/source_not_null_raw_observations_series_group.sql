select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select series_group
from "ecb_risk"."raw"."observations"
where series_group is null



      
    ) dbt_internal_test