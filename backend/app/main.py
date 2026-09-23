from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine, ensure_schema_compatibility
from app.seed import ensure_seeded
from app.providers.factory import get_provider
from app.services.refresh import run_data_refresh
from app.routers import (
    admin,
    analytics,
    auth,
    dashboard,
    data,
    health,
    leagues,
    matches,
    predictions,
    pricing,
    selections,
)

scheduler = BackgroundScheduler()


def _scheduled_refresh():
    db = SessionLocal()
    try:
        run_data_refresh(db)
    except Exception:  # noqa: BLE001 — scheduler must not crash
        pass
    finally:
        db.close()
    _schedule_next_round_refresh()


def _schedule_next_round_refresh():
    provider = get_provider()
    next_refresh_at = provider.get_next_refresh_at()
    if next_refresh_at is None:
        return
    scheduler.add_job(
        _scheduled_refresh,
        DateTrigger(run_date=next_refresh_at),
        id="next_round_refresh",
        replace_existing=True,
        max_instances=1,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()
    db = SessionLocal()
    try:
        ensure_seeded(db)
    finally:
        db.close()

    scheduler.add_job(
        _scheduled_refresh,
        "interval",
        minutes=settings.refresh_interval_minutes,
        id="demo_refresh",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _schedule_next_round_refresh()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.app_name,
    description="Virtual football analytics API (DEMO data by default)",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    health,
    dashboard,
    leagues,
    matches,
    predictions,
    analytics,
    auth,
    data,
    pricing,
    admin,
    selections,
]
for r in routers:
    app.include_router(r.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
        "data_source": settings.data_provider,
    }
