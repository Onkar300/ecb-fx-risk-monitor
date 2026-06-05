.PHONY: db ingest transform metrics quality pipeline dashboard test fmt

db:                 ## start postgres
	docker compose up -d db

ingest:             ## Phase 1: pull ECB data -> raw tables
	python -m src.ingest

transform:          ## Phase 3: run sql/ transformations
	python -m src.transform

metrics:            ## Phase 4: compute risk metrics
	python -m src.metrics

quality:            ## Phase 6: data-quality checks
	python -m src.quality

pipeline:           ## Phase 6: run the whole thing end to end
	python -m src.pipeline

dashboard:          ## Phase 5: launch the monitor
	streamlit run dashboard/app.py

test:
	pytest -q
