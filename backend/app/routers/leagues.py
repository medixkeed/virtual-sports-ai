from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import League
from app.providers.factory import get_provider
from app.schemas import LeagueOut

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("", response_model=list[LeagueOut])
def list_leagues(db: Session = Depends(get_db)):
    return (
        db.query(League)
        .filter(League.is_demo == get_provider().is_demo)
        .order_by(League.code)
        .all()
    )
