-- FX rates in long form, typed and validated.
{{ config(materialized='view') }}

select
    obs_date,
    series_id,
    cast(value as numeric(18, 6)) as rate
from {{ source('raw', 'observations') }}
where series_group = 'fx_rates'
  and value is not null
  and value > 0
