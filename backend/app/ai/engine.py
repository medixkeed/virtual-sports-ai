from sqlalchemy.orm import Session

from app.ai.baseline import predict_from_odds, predict_non_1x2
from app.ai.vfl import validated_signal_for_match
from app.models import MarketOdds, MarketType, Match, MatchStatus, ModelVersion, Prediction


def get_active_model(db: Session) -> ModelVersion:
    model = db.query(ModelVersion).filter(ModelVersion.is_active.is_(True)).first()
    if not model:
        model = ModelVersion(
            name="baseline-v1",
            description="Implied odds baseline (demo-aware). LightGBM hook reserved for future.",
            is_active=True,
        )
        db.add(model)
        db.commit()
        db.refresh(model)
    return model


def _team_form(db: Session, team_id: int, current_match_id: int) -> tuple[float, float]:
    matches = (
        db.query(Match)
        .filter(
            Match.id != current_match_id,
            Match.status == MatchStatus.finished,
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
        )
        .order_by(Match.kickoff_at.desc())
        .limit(5)
        .all()
    )
    if not matches:
        return 0.0, 0.0

    points = 0.0
    goal_difference = 0.0
    for item in matches:
        if item.home_score is None or item.away_score is None:
            continue
        is_home = item.home_team_id == team_id
        scored = item.home_score if is_home else item.away_score
        conceded = item.away_score if is_home else item.home_score
        goal_difference += scored - conceded
        points += 3 if scored > conceded else 1 if scored == conceded else 0
    return points / len(matches), goal_difference / len(matches)


def _form_signal(db: Session, match: Match) -> tuple[float, float, float] | None:
    home_points, home_goal_difference = _team_form(db, match.home_team_id, match.id)
    away_points, away_goal_difference = _team_form(db, match.away_team_id, match.id)
    if home_points == 0 and away_points == 0 and home_goal_difference == 0 and away_goal_difference == 0:
        return None

    edge = (home_points - away_points) * 3 + (home_goal_difference - away_goal_difference) * 2
    home = max(5.0, 33.33 + edge)
    away = max(5.0, 33.33 - edge)
    draw = max(5.0, 100.0 - home - away)
    return home, draw, away


def _odds_by_key(rows: list[MarketOdds]) -> dict[str, float]:
    values = {row.outcome_key.lower(): row.odds_value for row in rows}
    return {
        "home": values.get("home", values.get("1")),
        "draw": values.get("draw", values.get("x")),
        "away": values.get("away", values.get("2")),
    }


def calculate_prediction(db: Session, match: Match, market: str):
    if market != "1X2":
        dto = predict_non_1x2(market, match.is_demo, match.id)
        signal = validated_signal_for_match(db, match, market, match.provider_name or "")
        if signal:
            dto.message = f"{signal} {dto.message or ''}".strip()
        return dto

    odds = (
        db.query(MarketOdds)
        .filter(MarketOdds.match_id == match.id, MarketOdds.market == MarketType.X1X2)
        .all()
    )
    by_key = _odds_by_key(odds)
    dto = predict_from_odds(
        by_key.get("home"),
        by_key.get("draw"),
        by_key.get("away"),
        is_demo=match.is_demo,
        match_id=match.id,
        form_signal=_form_signal(db, match),
    )
    return dto


def calculate_market_outcomes(db: Session, match: Match, market: str) -> list[dict]:
    rows = (
        db.query(MarketOdds)
        .filter(MarketOdds.match_id == match.id, MarketOdds.market == MarketType(market))
        .order_by(MarketOdds.id)
        .all()
    )
    if not rows:
        return []
    total = sum(1 / row.odds_value for row in rows if row.odds_value > 1)
    if total <= 0:
        return []
    return [
        {
            "key": row.outcome_key,
            "label": row.outcome_label,
            "odds": row.odds_value,
            "probability": (1 / row.odds_value) / total * 100,
        }
        for row in rows
        if row.odds_value > 1
    ]


def run_prediction(db: Session, match: Match, market: str, user_id: int | None) -> Prediction:
    model = get_active_model(db)
    dto = calculate_prediction(db, match, market)

    pred = Prediction(
        match_id=match.id,
        user_id=user_id,
        market=MarketType(market),
        home_prob=dto.home_prob,
        draw_prob=dto.draw_prob,
        away_prob=dto.away_prob,
        message=dto.message,
        input_ref=dto.input_ref,
        is_demo=dto.is_demo,
        model_version_id=model.id,
        status="completed" if dto.home_prob else "unavailable",
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred
