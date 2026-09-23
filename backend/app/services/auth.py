from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, UserRole
from app.services.refresh import get_setting_int

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_user_id(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        return int(sub) if sub else None
    except (JWTError, ValueError):
        return None


def reset_daily_usage_if_needed(user: User) -> None:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.predictions_day != today:
        user.predictions_day = today
        user.predictions_used_today = 0


def user_to_public(user: User, db: Session) -> dict:
    reset_daily_usage_if_needed(user)
    limit = get_setting_int(db, "free_prediction_limit", settings.free_prediction_limit)
    role = user.role.value if isinstance(user.role, UserRole) else user.role
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": role,
        "is_premium": user.is_premium or role == "admin",
        "predictions_used_today": user.predictions_used_today,
        "free_prediction_limit": limit,
    }


def can_create_prediction(user: User, db: Session) -> tuple[bool, str | None]:
    reset_daily_usage_if_needed(user)
    role = user.role.value if isinstance(user.role, UserRole) else user.role
    if role == "admin" or user.is_premium or role == "premium":
        return True, None
    limit = get_setting_int(db, "free_prediction_limit", settings.free_prediction_limit)
    if user.predictions_used_today >= limit:
        return False, f"Free tier limit reached ({limit}/day). Upgrade or ask an admin for premium."
    return True, None
