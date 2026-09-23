from sqlalchemy.orm import Session

from app.models import League, MarketOdds, MarketType, Match, Team
from app.schemas import MatchDetailOut, MatchListOut, OddsOutcomeOut


def _team_name(db: Session, team_id: int) -> str:
    t = db.query(Team).filter(Team.id == team_id).first()
    return t.name if t else "Unknown"


def _odds_for_match(db: Session, match_id: int, market: MarketType) -> list[OddsOutcomeOut]:
    rows = (
        db.query(MarketOdds)
        .filter(MarketOdds.match_id == match_id, MarketOdds.market == market)
        .order_by(MarketOdds.id)
        .all()
    )
    return [
        OddsOutcomeOut(key=r.outcome_key, label=r.outcome_label, odds=r.odds_value) for r in rows
    ]


def match_to_list_out(db: Session, match: Match, market: MarketType) -> MatchListOut:
    league = db.query(League).filter(League.id == match.league_id).first()
    return MatchListOut(
        id=match.id,
        league_id=match.league_id,
        league_name=league.name if league else "",
        league_code=league.code if league else "",
        round=match.round,
        home_team=_team_name(db, match.home_team_id),
        away_team=_team_name(db, match.away_team_id),
        kickoff_at=match.kickoff_at,
        status=match.status.value,
        home_score=match.home_score,
        away_score=match.away_score,
        is_demo=match.is_demo,
        odds=_odds_for_match(db, match.id, market),
    )


def match_to_detail_out(db: Session, match: Match, market: MarketType = MarketType.X1X2) -> MatchDetailOut:
    base = match_to_list_out(db, match, market)
    return MatchDetailOut(
        **base.model_dump(),
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_score=match.home_score,
        away_score=match.away_score,
    )
