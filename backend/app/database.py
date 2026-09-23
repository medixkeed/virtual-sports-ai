from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema_compatibility() -> None:
    """Apply only additive SQLite changes; existing rows are never replaced."""
    inspector = inspect(engine)
    additions = {
        "matches": {
            "provider_name": "VARCHAR(64)",
            "last_fetched_at": "DATETIME",
        },
        "refresh_state": {
            "last_successful_provider": "VARCHAR(64)",
            "last_fetched_at": "DATETIME",
        },
    }
    with engine.begin() as connection:
        for table, columns in additions.items():
            existing = {column["name"] for column in inspector.get_columns(table)} if table in inspector.get_table_names() else set()
            for column, sql_type in columns.items():
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
