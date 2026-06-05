-- ECB key policy rates, wide.
{{ config(materialized='view') }}

select
    obs_date,
    max(case when series_id = 'MRO' then cast(value as numeric(8, 4)) end) as mro_rate,
    max(case when series_id = 'DFR' then cast(value as numeric(8, 4)) end) as dfr_rate,
    max(case when series_id = 'MLF' then cast(value as numeric(8, 4)) end) as mlf_rate
from {{ source('raw', 'observations') }}
where series_group = 'policy_rates'
  and value is not null
group by obs_date
