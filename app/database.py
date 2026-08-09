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
        "contact_person": "VARCHAR(255)",
        "designation": "VARCHAR(255)",
        "city": "VARCHAR(100)",
        "country": "VARCHAR(100)",
        "linkedin_url": "VARCHAR(500)",
        "npi": "VARCHAR(50)",
        "practice_type": "VARCHAR(100)",
        "independent_practice": "BOOLEAN NOT NULL DEFAULT 0",
        "insurance_status": "VARCHAR(255)",
        "lead_source": "VARCHAR(100)",
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
        if "insurance" in lead_columns:
            connection.execute(
                text(
                    "UPDATE leads SET insurance_status = insurance "
                    "WHERE insurance_status IS NULL AND insurance IS NOT NULL"
                )
            )
        if "linkedin" in lead_columns:
            connection.execute(
                text(
                    "UPDATE leads SET linkedin_url = linkedin "
                    "WHERE linkedin_url IS NULL AND linkedin IS NOT NULL"
                )
            )
        if "decision_maker" in lead_columns:
            connection.execute(
                text(
                    "UPDATE leads SET contact_person = decision_maker "
                    "WHERE contact_person IS NULL AND decision_maker IS NOT NULL"
                )
            )
        connection.execute(
            text("UPDATE leads SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)")
        )
