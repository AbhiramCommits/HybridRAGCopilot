import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from hybridrag.config import settings

# Fallback to sqlite if postgres is not available
sqlite_url = "sqlite:///artifacts/hybridrag.db"
os.makedirs("artifacts", exist_ok=True)

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        pass
    DB_URL = settings.DATABASE_URL
    print("Using PostgreSQL database.")
except Exception as e:
    print(f"PostgreSQL not reachable ({e}), falling back to SQLite: {sqlite_url}")
    DB_URL = sqlite_url

Base = declarative_base()

def get_engine():
    return create_engine(DB_URL)
