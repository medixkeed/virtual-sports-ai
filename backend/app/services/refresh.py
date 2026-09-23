import json
import math
from datetime import datetime
from threading import Lock

from sqlalchemy.orm import Session

from app.models import (
    AppSetting,
    League,
    MarketOdds,
    MarketType,
    Match,
    MatchStatus,
    OddsSnapshot,
    RefreshState,
    ScraperLog,
    Team,
)
from app.providers.demo import LEAGUES
from app.providers.base import ProviderError
from app.providers.base import ProviderMatch
from app.providers.factory import get_provider

_refresh_lock = Lock()


def _get_or_create_refresh_state(db: Session) -> RefreshState:
    state = db.query(RefreshState).first()
    if not state:
        state = RefreshState(refresh_status="idle", data_source=get_provider().name)
        db.add(state)
        db.commit()
        db.refresh(state)
    else:
        state.data_source = get_provider().name
    return state


def _ensure_leagues(db: Session, provider_matches: list[ProviderMatch], is_demo: bool) -> dict[str, League]:
    mapping: dict[str, League] = {}
    league_values = (
        [(code, name, country) for code, name, country in LEAGUES]
        if is_demo
        else [
            (match.league_code, match.league_name or match.league_code, match.league_country or "")
            for match in provider_matches
        ]
    )
    for code, name, country in dict.fromkeys(league_values):
        league = db.query(League).filter(League.code == code).first()
        if not league:
            league = League(name=name, code=code, country=country, is_demo=is_demo)
            db.add(league)
            db.flush()
        else:
            league.name = name
            league.country = country
            league.is_demo = is_demo
        mapping[code] = league
    db.commit()
    return mapping


def _get_or_create_team(db: Session, league_id: int, name: str, is_demo: bool) -> Team:
    team = (
        db.query(Team)
        .filter(Team.league_id == league_id, Team.name == name)
        .first()
    )
    if not team:
        team = Team(
            league_id=league_id,
            name=name,
            short_name=name[:3].upper(),
            is_demo=is_demo,
        )
        db.add(team)
        db.flush()
    return team


def _validate_matches(matches: list[ProviderMatch]) -> None:
    if not matches:
        raise ProviderError("Provider returned no validated matches")
    valid_statuses = {status.value for status in MatchStatus}
    valid_markets = {market.value for market in MarketType}
    for match in matches:
        if not match.external_key or not match.league_code or not match.home_team or not match.away_team:
            raise ProviderError("Provider returned a match with missing identity fields")
        if match.status not in valid_statuses:
            raise ProviderError("Provider returned an invalid match status")
        for market_key, outcomes in match.odds_by_market.items():
            if market_key not in valid_markets:
                raise ProviderError("Provider returned an invalid market")
            for outcome in outcomes:
                if not outcome.key or not outcome.label or not math.isfinite(outcome.odds) or outcome.odds <= 1:
                    raise ProviderError("Provider returned invalid odds")


def run_data_refresh(db: Session) -> RefreshState:
    if not _refresh_lock.acquire(blocking=False):
        return _get_or_create_refresh_state(db)

    provider = get_provider()
    state = _get_or_create_refresh_state(db)
    state.refresh_status = "running"
    state.data_source = provider.name
    state.last_fetched_at = datetime.utcnow()
    db.commit()

    log = ScraperLog(provider=provider.name, status="started", message="Refresh started")
    db.add(log)
    db.commit()

    try:
        matches = provider.fetch_matches()
        _validate_matches(matches)

        leagues = _ensure_leagues(db, matches, provider.is_demo)

        for pm in matches:
            league = leagues[pm.league_code]
            home = _get_or_create_team(db, league.id, pm.home_team, provider.is_demo)
            away = _get_or_create_team(db, league.id, pm.away_team, provider.is_demo)

            match = db.query(Match).filter(Match.external_key == pm.external_key).first()
            if not match:
                match = Match(
                    external_key=pm.external_key,
                    league_id=league.id,
                    home_team_id=home.id,
                    away_team_id=away.id,
                    round=pm.round,
                    season=pm.season,
                    kickoff_at=pm.kickoff_at,
                    status=MatchStatus(pm.status),
                    home_score=pm.home_score,
                    away_score=pm.away_score,
                    is_demo=provider.is_demo,
                    provider_name=provider.name,
                    last_fetched_at=datetime.utcnow(),
                )
                db.add(match)
                db.flush()
            match.round = pm.round
            match.kickoff_at = pm.kickoff_at
            match.status = MatchStatus(pm.status)
            match.home_score = pm.home_score
            match.away_score = pm.away_score
            match.season = pm.season
            match.provider_name = provider.name
            match.is_demo = provider.is_demo
            match.home_team_id = home.id
            match.away_team_id = away.id

            for market_key, outcomes in pm.odds_by_market.items():
                market = MarketType(market_key)
                if not outcomes:
                    continue
                for o in outcomes:
                    row = (
                        db.query(MarketOdds)
                        .filter(
                            MarketOdds.match_id == match.id,
                            MarketOdds.market == market,
                            MarketOdds.outcome_key == o.key,
                        )
                        .first()
                    )
                    if not row:
                        row = MarketOdds(
                            match_id=match.id,
                            market=market,
                            outcome_key=o.key,
                            outcome_label=o.label,
                            odds_value=o.odds,
                        )
                        db.add(row)
                    else:
                        row.odds_value = o.odds
                        row.outcome_label = o.label
                        row.updated_at = datetime.utcnow()

                snapshot = OddsSnapshot(
                    match_id=match.id,
                    market=market,
                    payload_json=json.dumps(
                        [{"key": x.key, "label": x.label, "odds": x.odds} for x in outcomes]
                    ),
                )
                db.add(snapshot)

        state.last_successful_refresh = datetime.utcnow()
        state.last_successful_provider = provider.name
        state.refresh_status = "ok"
        state.last_error = None
        db.add(
            ScraperLog(
                provider=provider.name,
                status="success",
                message=f"Synced {len(matches)} matches from {provider.name}",
            )
        )
        db.commit()
    except ProviderError as exc:
        db.rollback()
        state.refresh_status = "stale"
        state.last_error = str(exc)
        db.add(
            ScraperLog(
                provider=provider.name,
                status="error",
                message=state.last_error,
            )
        )
        db.commit()
    except Exception:  # noqa: BLE001 — log refresh failures without leaking internals
        db.rollback()
        state.refresh_status = "stale"
        state.last_error = "Refresh failed; the last successful dataset was retained"
        db.add(
            ScraperLog(
                provider=provider.name,
                status="error",
                message=state.last_error,
            )
        )
        db.commit()
    finally:
        _refresh_lock.release()

    db.refresh(state)
    return state


def get_data_status(db: Session) -> RefreshState:
    return _get_or_create_refresh_state(db)


def get_setting_int(db: Session, key: str, default: int) -> int:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not row:
        return default
    try:
        return int(row.value)
    except ValueError:
        return default


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not row:
        row = AppSetting(key=key, value=value)
        db.add(row)
    else:
        row.value = value
    db.commit()
