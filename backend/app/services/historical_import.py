import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    League,
    MarketOdds,
    MarketType,
    Match,
    MatchStatus,
    OddsSnapshot,
    Prediction,
    PredictionResult,
    RefreshState,
    ScraperLog,
    Team,
    UserSelection,
)
from app.providers.base import ProviderMatch
from app.providers.betpawa import BetPawaProvider
from app.services.refresh import _validate_matches, run_data_refresh


def clear_sports_data(db: Session) -> None:
    db.query(PredictionResult).delete(synchronize_session=False)
    db.query(Prediction).delete(synchronize_session=False)
    db.query(UserSelection).delete(synchronize_session=False)
    db.query(OddsSnapshot).delete(synchronize_session=False)
    db.query(MarketOdds).delete(synchronize_session=False)
    db.query(Match).delete(synchronize_session=False)
    db.query(Team).delete(synchronize_session=False)
    db.query(League).delete(synchronize_session=False)
    db.query(ScraperLog).delete(synchronize_session=False)
    db.commit()


def import_historical_seasons(db: Session, season_ids: list[str]) -> dict[str, int]:
    provider = BetPawaProvider()
    matches = provider.fetch_historical_seasons(season_ids)
    _validate_matches(matches)
    clear_sports_data(db)

    leagues: dict[str, League] = {}
    teams: dict[tuple[int, str], Team] = {}
    now = datetime.utcnow()
    for provider_match in matches:
        league = leagues.get(provider_match.league_code)
        if not league:
            league = League(
                name=provider_match.league_name or provider_match.league_code,
                code=provider_match.league_code,
                country=provider_match.league_country or "",
                is_demo=False,
                external_id=provider_match.league_code.removeprefix("BP-"),
            )
            db.add(league)
            db.flush()
            leagues[provider_match.league_code] = league

        home_key = (league.id, provider_match.home_team)
        away_key = (league.id, provider_match.away_team)
        home = teams.get(home_key)
        if not home:
            home = Team(
                league_id=league.id,
                name=provider_match.home_team,
                short_name=provider_match.home_team[:3].upper(),
                is_demo=False,
            )
            db.add(home)
            db.flush()
            teams[home_key] = home
        away = teams.get(away_key)
        if not away:
            away = Team(
                league_id=league.id,
                name=provider_match.away_team,
                short_name=provider_match.away_team[:3].upper(),
                is_demo=False,
            )
            db.add(away)
            db.flush()
            teams[away_key] = away

        match = Match(
            external_key=provider_match.external_key,
            league_id=league.id,
            home_team_id=home.id,
            away_team_id=away.id,
            round=provider_match.round,
            season=provider_match.season,
            kickoff_at=provider_match.kickoff_at,
            status=MatchStatus(provider_match.status),
            home_score=provider_match.home_score,
            away_score=provider_match.away_score,
            is_demo=False,
            provider_name=provider.name,
            last_fetched_at=now,
        )
        db.add(match)
        db.flush()

        for market_key, outcomes in provider_match.odds_by_market.items():
            market = MarketType(market_key)
            for outcome in outcomes:
                db.add(
                    MarketOdds(
                        match_id=match.id,
                        market=market,
                        outcome_key=outcome.key,
                        outcome_label=outcome.label,
                        odds_value=outcome.odds,
                        updated_at=now,
                    )
                )
            db.add(
                OddsSnapshot(
                    match_id=match.id,
                    market=market,
                    payload_json=json.dumps(
                        [{"key": x.key, "label": x.label, "odds": x.odds} for x in outcomes]
                    ),
                    captured_at=now,
                )
            )

    state = db.query(RefreshState).first()
    if not state:
        state = RefreshState()
        db.add(state)
    state.data_source = provider.name
    state.refresh_status = "ok"
    state.last_successful_refresh = now
    state.last_successful_provider = provider.name
    state.last_fetched_at = now
    state.last_error = None
    db.commit()
    return {
        "matches": len(matches),
        "leagues": len(leagues),
        "teams": len(teams),
        "seasons": len(season_ids),
    }


def rebuild_live_dataset(db: Session, season_count: int) -> dict[str, int]:
    provider = BetPawaProvider()
    season_ids = provider.discover_historical_season_ids(season_count)
    result = import_historical_seasons(db, season_ids)
    run_data_refresh(db)
    return result
