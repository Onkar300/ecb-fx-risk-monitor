# ECB Macro & FX Risk Monitor

An end-to-end, automated data pipeline that ingests real euro-area economic data
from the **ECB Data Portal API** and turns it into a refreshable **risk-monitoring
dashboard**. FX reference rates, key ECB policy rates, and HICP inflation are pulled
on a schedule, validated, loaded into **PostgreSQL**, transformed in **analytical
SQL**, and scored with recognizable **risk measures** (rolling volatility, VaR,
z-score anomaly flags). The output is an interactive Streamlit monitor.

> Status: built as a portfolio project. Forecasting is intentionally a modest
> baseline reported with its error, not a market call — this is a *risk monitoring*
> tool, not a prediction engine.

## Stack
Python · PostgreSQL · SQL · pandas/numpy/scipy · Streamlit · Plotly · Docker

## Architecture
`ECB API → raw (Postgres) → staging (SQL) → marts (SQL) → risk metrics → dashboard`
(diagram added in Phase 7)

## Quickstart
```bash
cp .env.example .env
make db            # start postgres
pip install -r requirements.txt
make pipeline      # ingest -> quality -> transform
make dashboard     # launch the monitor
```

## Pipeline stages
| Stage | Command | What it does |
|---|---|---|
| Ingest | `make ingest` | pull ECB series → `raw.observations` |
| Quality | `make quality` | row counts, freshness, key uniqueness |
| Transform | `make transform` | build `staging` + `marts` in SQL |
| Dashboard | `make dashboard` | trends, volatility, anomaly flags |

(Screenshots + CV bullets added in Phase 7.)
