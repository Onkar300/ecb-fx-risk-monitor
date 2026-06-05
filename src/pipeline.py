"""Phase 6 — Orchestration entrypoint.

Runs the whole pipeline as one idempotent, logged command:
    ingest -> quality -> transform -> (metrics materialised in marts)

This single CLI is what makes the project a 'pipeline' not a notebook.
Stretch: wrap each step as an Airflow task in the same order.
"""
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("logs/pipeline.log")],
)
log = logging.getLogger("pipeline")


def main():
    from src import ingest, quality, transform
    log.info("=== pipeline start ===")
    ingest.land_raw()
    quality.run_all()
    transform.run_transformations()
    log.info("=== pipeline done ===")


if __name__ == "__main__":
    main()
