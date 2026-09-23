"""Backtestable VFL Mentor heuristics for virtual-football analysis."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Match, MatchStatus, Team


BETPAWA_OVER_TEAMS = {"MCI", "LEI", "MUN", "CRY", "SOU", "AST", "WHU"}
MINIMUM_SAMPLE_SIZE = 100
MINIMUM_EDGE = 0.02


@dataclass(frozen=True)
class VFLBacktest:
    market: str
    sample_size: int
    hit_rate: float
    baseline_rate: float
    validated: bool


def _over_2_5(match: Match) -> bool:
    return (match.home_score or 0) + (match.away_score or 0) > 2


def _btts(match: Match) -> bool:
    return (match.home_score or 0) > 0 and (match.away_score or 0) > 0


def backtest_vfl_rules(db: Session, provider_name: str = "BETPAWA Uganda") -> list[VFLBacktest]:
    matches = (
        db.query(Match)
        .filter(
            Match.provider_name == provider_name,
            Match.status == MatchStatus.finished,
            Match.home_score.is_not(None),
            Match.away_score.is_not(None),
        )
        .all()
    )
    team_names = dict(db.query(Team.id, Team.name).all())
    focus_matches = [
        match
        for match in matches
        if team_names.get(match.home_team_id) in BETPAWA_OVER_TEAMS
        or team_names.get(match.away_team_id) in BETPAWA_OVER_TEAMS
    ]

    if not focus_matches:
        return [
            VFLBacktest(market, 0, 0.0, 0.0, False)
            for market in ("OU_OVER_2_5", "BTTS", "1X2")
        ]

    over_hits = sum(_over_2_5(match) for match in focus_matches)
    btts_hits = sum(_btts(match) for match in focus_matches)
    overall_over = sum(_over_2_5(match) for match in matches)
    overall_btts = sum(_btts(match) for match in matches)

    results = [
        VFLBacktest(
            "OU_OVER_2_5",
            len(focus_matches),
            over_hits / len(focus_matches),
            overall_over / len(matches) if matches else 0.0,
            len(focus_matches) >= MINIMUM_SAMPLE_SIZE
            and over_hits / len(focus_matches) >= overall_over / len(matches) + MINIMUM_EDGE,
        ),
        VFLBacktest(
            "BTTS",
            len(focus_matches),
            btts_hits / len(focus_matches),
            overall_btts / len(matches) if matches else 0.0,
            len(focus_matches) >= MINIMUM_SAMPLE_SIZE
            and btts_hits / len(focus_matches) >= overall_btts / len(matches) + MINIMUM_EDGE,
        ),
    ]
    return results


def validated_signal_for_match(
    db: Session, match: Match, market: str, provider_name: str
) -> str | None:
    results = {result.market: result for result in backtest_vfl_rules(db, provider_name)}
    market_key = "OU_OVER_2_5" if market == "OU" else "BTTS" if market == "BTTS" else None
    result = results.get(market_key or "")
    if not result or not result.validated:
        return None

    team_names = dict(db.query(Team.id, Team.name).all())
    if team_names.get(match.home_team_id) not in BETPAWA_OVER_TEAMS and team_names.get(match.away_team_id) not in BETPAWA_OVER_TEAMS:
        return None
    return (
        f"Validated VFL signal for {market}: {result.hit_rate * 100:.1f}% hit rate "
        f"across {result.sample_size} historical matches versus "
        f"{result.baseline_rate * 100:.1f}% overall baseline."
    )