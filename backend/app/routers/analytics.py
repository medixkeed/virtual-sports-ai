from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.ai.vfl import backtest_vfl_rules
from app.models import Match, MatchStatus
from app.providers.factory import get_provider
from app.schemas import AnalyticsOverviewOut, VFLBacktestOut

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverviewOut)
def analytics_overview(db: Session = Depends(get_db)):
    matches = db.query(Match).all()
    finished = [m for m in matches if m.status == MatchStatus.finished]
    total_goals = sum((m.home_score or 0) + (m.away_score or 0) for m in finished)
    home_w = draw = away_w = 0
    for m in finished:
        if m.home_score is None or m.away_score is None:
            continue
        if m.home_score > m.away_score:
            home_w += 1
        elif m.home_score < m.away_score:
            away_w += 1
        else:
            draw += 1
    n = len(finished) or 1
    return AnalyticsOverviewOut(
        total_matches=len(matches),
        finished_matches=len(finished),
        avg_goals_per_match=total_goals / n,
        home_win_rate=home_w / n,
        draw_rate=draw / n,
        away_win_rate=away_w / n,
        data_source=get_provider().name,
    )


@router.get("/vfl-backtest", response_model=list[VFLBacktestOut])
def vfl_backtest(db: Session = Depends(get_db)):
    return [
        VFLBacktestOut(
            market=result.market,
            sample_size=result.sample_size,
            hit_rate=result.hit_rate,
            baseline_rate=result.baseline_rate,
            validated=result.validated,
        )
        for result in backtest_vfl_rules(db, get_provider().name)
    ]
