"""Phase 3 — Transformations. Runs the SQL files in order to build staging + marts."""
import logging
from pathlib import Path

from src.db import run_sql_file

log = logging.getLogger(__name__)
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def run_transformations():
    for f in sorted(SQL_DIR.glob("*.sql")):
        log.info("running %s", f.name)
        run_sql_file(str(f))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_transformations()
