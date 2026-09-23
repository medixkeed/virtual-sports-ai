from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.engine import calculate_market_outcomes, calculate_prediction
from app.database import get_db
from app.models import League, MarketType, Match, Prediction, Team
from app.providers.factory import get_provider
from app.schemas import DashboardPredictionOut, DashboardStatsOut
from app.services.refresh import get_data_status

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsOut)
def dashboard_stats(db: Session = Depends(get_db)):
    state = get_data_status(db)
    provider = get_provider()
    latest_match = (
        db.query(Match)
        .filter(Match.is_demo == provider.is_demo)
        .order_by(Match.kickoff_at.desc())
        .first()
    )
    match_query = db.query(Match).filter(Match.is_demo == provider.is_demo)
    if latest_match is not None:
        match_query = match_query.filter(
            Match.season == latest_match.season,
            Match.round == latest_match.round,
        )
    total = match_query.count()
    preds = (
        db.query(func.count(Prediction.id))
        .join(Match, Prediction.match_id == Match.id)
        .filter(Match.is_demo == provider.is_demo)
        .filter(Match.season == latest_match.season if latest_match else True)
        .filter(Match.round == latest_match.round if latest_match else True)
        .scalar()
        or 0
    )
    round_val = match_query.with_entities(func.max(Match.round)).scalar() or 1
    season = match_query.with_entities(Match.season).order_by(Match.kickoff_at.desc()).limit(1).scalar() or provider.name
    last = state.last_successful_refresh or datetime.utcnow()
    return DashboardStatsOut(
        season=season,
        round=int(round_val),
        last_updated=last,
        total_events=int(total),
        available_predictions=int(preds),
        refresh_status=state.refresh_status,
        data_source=state.data_source or provider.name,
    )


@router.get("/predictions", response_model=list[DashboardPredictionOut])
def dashboard_predictions(
    market: str = "1X2",
    db: Session = Depends(get_db),
):
    if market not in {item.value for item in MarketType}:
        raise HTTPException(status_code=400, detail="Invalid market")
    provider = get_provider()
    latest_match = (
        db.query(Match)
        .filter(Match.is_demo == provider.is_demo)
        .order_by(Match.kickoff_at.desc())
        .first()
    )
    if latest_match is None:
        return []

    matches = (
        db.query(Match)
        .filter(
            Match.is_demo == provider.is_demo,
            Match.season == latest_match.season,
            Match.round == latest_match.round,
        )
        .order_by(Match.kickoff_at)
        .all()
    )
    output = []
    for match in matches:
        home = db.query(Team).filter(Team.id == match.home_team_id).first()
        away = db.query(Team).filter(Team.id == match.away_team_id).first()
        league = db.query(League).filter(League.id == match.league_id).first()
        prediction = calculate_prediction(db, match, market)
        outcomes = calculate_market_outcomes(db, match, market)
        output.append(
            DashboardPredictionOut(
                match_id=match.id,
                league_name=league.name if league else "",
                home_team=home.name if home else "Unknown",
                away_team=away.name if away else "Unknown",
                kickoff_at=match.kickoff_at,
                market=market,
                outcomes=outcomes,
                home_prob=prediction.home_prob,
                draw_prob=prediction.draw_prob,
                away_prob=prediction.away_prob,
                message=prediction.message,
                status="available" if prediction.home_prob is not None else "unavailable",
            )
        )
    return output
