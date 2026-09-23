from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.engine import get_active_model
from app.database import get_db
from app.deps import require_admin
from app.models import Match, Prediction, ScraperLog, User, UserRole
from app.schemas import (
    AdminStatsOut,
    AdminUserOut,
    DataStatusOut,
    PremiumUpdateIn,
    RoleUpdateIn,
    ScraperLogOut,
    SettingsUpdateIn,
)
from app.services.refresh import get_data_status, run_data_refresh, set_setting
from app.config import settings
from app.routers.data import _status_out

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsOut)
def admin_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    state = get_data_status(db)
    model = get_active_model(db)
    return AdminStatsOut(
        users_count=db.query(func.count(User.id)).scalar() or 0,
        matches_count=db.query(func.count(Match.id)).scalar() or 0,
        predictions_count=db.query(func.count(Prediction.id)).scalar() or 0,
        model_version=model.name,
        refresh_status=state.refresh_status,
    )


@router.get("/users", response_model=list[AdminUserOut])
def admin_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        AdminUserOut(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            role=u.role.value,
            is_premium=u.is_premium,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.patch("/users/{user_id}/role", response_model=AdminUserOut)
def set_role(
    user_id: int,
    body: RoleUpdateIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = UserRole(body.role)
    if body.role == "premium":
        user.is_premium = True
    db.commit()
    db.refresh(user)
    return AdminUserOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role.value,
        is_premium=user.is_premium,
        created_at=user.created_at,
    )


@router.patch("/users/{user_id}/premium", response_model=AdminUserOut)
def set_premium(
    user_id: int,
    body: PremiumUpdateIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_premium = body.is_premium
    db.commit()
    db.refresh(user)
    return AdminUserOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role.value,
        is_premium=user.is_premium,
        created_at=user.created_at,
    )


@router.get("/scraper-logs", response_model=list[ScraperLogOut])
def scraper_logs(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return (
        db.query(ScraperLog)
        .order_by(ScraperLog.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/settings")
def get_settings(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from app.services.refresh import get_setting_int

    return {
        "free_prediction_limit": get_setting_int(
            db, "free_prediction_limit", settings.free_prediction_limit
        )
    }


@router.patch("/settings")
def update_settings(
    body: SettingsUpdateIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    set_setting(db, "free_prediction_limit", str(body.free_prediction_limit))
    return {"free_prediction_limit": body.free_prediction_limit}


@router.post("/refresh", response_model=DataStatusOut)
def admin_refresh(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    state = run_data_refresh(db)
    return _status_out(state)
