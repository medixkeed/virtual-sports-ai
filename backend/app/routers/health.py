from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.providers.factory import get_provider
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    _ = db  # ensure DB reachable on startup path
    provider = get_provider()
    return HealthOut(status="ok", data_source=provider.name)
