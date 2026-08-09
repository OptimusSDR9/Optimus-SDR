from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "optimus.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database():
    """Create tables and add newly introduced lead columns to older SQLite databases."""
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "leads" not in inspector.get_table_names():
        return

    lead_columns = {column["name"] for column in inspector.get_columns("leads")}
    missing_columns = {
        "linkedin": "VARCHAR(500)",
        "npi": "VARCHAR(50)",
        "insurance": "VARCHAR(255)",
        "decision_maker": "VARCHAR(255)",
        "lead_score": "FLOAT NOT NULL DEFAULT 0.0",
        "tags": "VARCHAR(1000)",
        "notes": "TEXT",
        "created_at": "DATETIME",
        "priority": "VARCHAR(50) NOT NULL DEFAULT 'Medium'",
        "updated_at": "DATETIME",
    }
    with engine.begin() as connection:
        for column_name, column_definition in missing_columns.items():
            if column_name not in lead_columns:
                connection.execute(
                    text(f"ALTER TABLE leads ADD COLUMN {column_name} {column_definition}")
                )
        if "created_at" not in lead_columns:
            connection.execute(text("UPDATE leads SET created_at = CURRENT_TIMESTAMP"))
        connection.execute(
            text("UPDATE leads SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)")
        )
