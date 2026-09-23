import os
from pathlib import Path

from sqlalchemy import text

from app.database import Base, SessionLocal, ensure_schema_compatibility, engine
from app.services.historical_import import rebuild_live_dataset


def main() -> None:
    db_path = Path(__file__).with_name("virtual_sports_ai.db")
    if db_path.exists():
        db_path.unlink()

    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()

    db = SessionLocal()
    try:
        result = rebuild_live_dataset(db, 9)
        match_rows = db.execute(text("SELECT COUNT(*) FROM matches")).scalar()
        seasons = [
            season[0]
            for season in db.execute(
                text("SELECT DISTINCT season FROM matches ORDER BY season DESC LIMIT 10")
            ).fetchall()
        ]
        print("RESULT", result)
        print("MATCH_ROWS", match_rows)
        print("SEASONS", seasons)
    finally:
        db.close()


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    main()
