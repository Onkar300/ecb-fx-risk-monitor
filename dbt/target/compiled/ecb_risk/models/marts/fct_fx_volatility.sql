-- 21-day rolling realised volatility per pair, annualised (sqrt(252)).
-- A 21-day window approximates one trading month.


with r as (
    select obs_date, pair, log_return
    from "ecb_risk"."analytics_marts"."fct_fx_returns"
),
rolled as (
    select
        obs_date,
        pair,
        log_return,
        stddev_samp(log_return) over (
            partition by pair
            order by obs_date
            rows between 20 preceding and current row
        ) as rolling_sd_21d,
        count(*) over (
            partition by pair
            order by obs_date
            rows between 20 preceding and current row
        ) as window_n
    from r
)
select
    obs_date,
    pair,
    log_return,
    rolling_sd_21d,
    rolling_sd_21d * sqrt(252) as annualised_vol_21d
from rolled
where window_n = 21          -- only emit fully-formed windows