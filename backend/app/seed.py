from sqlalchemy.orm import Session

from app.models import AppSetting, ModelVersion, User, UserRole
from app.services.auth import hash_password
from app.services.refresh import run_data_refresh, set_setting
from app.config import settings


def seed_initial_data(db: Session) -> None:
    if not db.query(ModelVersion).first():
        db.add(
            ModelVersion(
                name="baseline-v1",
                description="Implied odds statistical baseline (demo-aware)",
                is_active=True,
            )
        )
        db.commit()

    set_setting(db, "free_prediction_limit", str(settings.free_prediction_limit))
    set_setting(db, "seed_complete", "true")

    admin = db.query(User).filter(User.email == "admin@virtualsports.ai").first()
    if not admin:
        admin = User(
            email="admin@virtualsports.ai",
            hashed_password=hash_password("Admin123!"),
            display_name="Demo Admin",
            role=UserRole.admin,
            is_premium=True,
        )
        db.add(admin)
        db.commit()

    # Idempotent demo sync
    run_data_refresh(db)


def ensure_seeded(db: Session) -> None:
    flag = db.query(AppSetting).filter(AppSetting.key == "seed_complete").first()
    if not flag:
        seed_initial_data(db)
    else:
        run_data_refresh(db)
