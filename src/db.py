"""Postgres connection helpers (SQLAlchemy engine)."""
from sqlalchemy import create_engine, text

from src.config import DB_URL

engine = create_engine(DB_URL, pool_pre_ping=True)


def run_sql_file(path: str) -> None:
    """Execute a .sql file (one or many statements)."""
    with open(path) as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))


def fetch_df(query: str):
    """Run a SELECT and return a DataFrame."""
    import pandas as pd
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)
