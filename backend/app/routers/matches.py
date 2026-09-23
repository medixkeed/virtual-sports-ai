from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MarketType, Match
from app.providers.factory import get_provider
from app.schemas import MatchDetailOut, MatchListOut
from app.services.matches import match_to_detail_out, match_to_list_out

router = APIRouter(prefix="/matches", tags=["matches"])


def _parse_market(market: str) -> MarketType:
    try:
        return MarketType(market)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid market") from exc


@router.get("/results", response_model=list[MatchListOut])
def list_results(
    market: str = Query("1X2"),
    db: Session = Depends(get_db),
):
    mkt = _parse_market(market)
    active_demo = get_provider().is_demo
    latest_finished = (
        db.query(Match)
        .filter(
            Match.is_demo == active_demo,
            Match.status == "finished",
        )
        .order_by(Match.kickoff_at.desc())
        .first()
    )
    if latest_finished is None:
        return []
    matches = (
        db.query(Match)
        .filter(
            Match.is_demo == active_demo,
            Match.status == "finished",
            Match.season == latest_finished.season,
            Match.round == latest_finished.round,
        )
        .order_by(Match.kickoff_at.desc())
        .all()
    )
    return [match_to_list_out(db, match, mkt) for match in matches]


@router.get("", response_model=list[MatchListOut])
def list_matches(
    league_id: int | None = None,
    round: int | None = None,
    provider: str | None = None,
    search: str | None = None,
    market: str = Query("1X2"),
    db: Session = Depends(get_db),
):
    mkt = _parse_market(market)
    q = db.query(Match).order_by(Match.kickoff_at)
    active_demo = get_provider().is_demo
    q = q.filter(Match.is_demo == active_demo)
    latest_match = (
        db.query(Match)
        .filter(Match.is_demo == active_demo)
        .order_by(Match.kickoff_at.desc())
        .first()
    )
    if latest_match is not None:
        q = q.filter(Match.season == latest_match.season, Match.round == latest_match.round)
    if league_id:
        q = q.filter(Match.league_id == league_id)
    if round:
        q = q.filter(Match.round == round)
    if provider:
        q = q.filter(Match.provider_name == provider)
    matches = q.all()
    results: list[MatchListOut] = []
    for m in matches:
        item = match_to_list_out(db, m, mkt)
        if search:
            s = search.lower()
            if s not in item.home_team.lower() and s not in item.away_team.lower() and s not in item.league_name.lower():
                continue
        results.append(item)
    return results


@router.get("/{match_id}", response_model=MatchDetailOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match_to_detail_out(db, match)


@router.get("/{match_id}/odds")
def get_match_odds(
    match_id: int,
    market: str = Query("1X2"),
    db: Session = Depends(get_db),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    mkt = _parse_market(market)
    detail = match_to_detail_out(db, match, mkt)
    return {"market": market, "outcomes": detail.odds}
