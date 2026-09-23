from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import DataStatusOut
from app.services.refresh import get_data_status, run_data_refresh

router = APIRouter(prefix="/data", tags=["data"])


def _status_out(state) -> DataStatusOut:
    return DataStatusOut(
        last_fetched_at=state.last_fetched_at,
        last_successful_refresh=state.last_successful_refresh,
        last_successful_provider=state.last_successful_provider,
        refresh_status=state.refresh_status,
        refresh_interval_minutes=settings.refresh_interval_minutes,
        data_source=state.data_source,
        last_error=state.last_error,
    )


@router.get("/status", response_model=DataStatusOut)
def data_status(db: Session = Depends(get_db)):
    return _status_out(get_data_status(db))


@router.post("/refresh", response_model=DataStatusOut)
def refresh_data(db: Session = Depends(get_db)):
    state = run_data_refresh(db)
    return _status_out(state)
