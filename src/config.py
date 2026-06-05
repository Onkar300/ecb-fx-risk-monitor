"""Central config: loads .env and exposes settings + the DB URL."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PG = {
    "user": os.getenv("POSTGRES_USER", "ecb"),
    "password": os.getenv("POSTGRES_PASSWORD", "ecb_pw"),
    "db": os.getenv("POSTGRES_DB", "ecb_risk"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

DB_URL = f"postgresql+psycopg2://{PG['user']}:{PG['password']}@{PG['host']}:{PG['port']}/{PG['db']}"

INGEST_START_DATE = os.getenv("INGEST_START_DATE", "2015-01-01")


def load_series() -> dict:
    """Return the series config dict from config/series.yml."""
    with open(ROOT / "config" / "series.yml") as f:
        return yaml.safe_load(f)
