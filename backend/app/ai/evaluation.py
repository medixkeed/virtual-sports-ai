"""Evaluate predictions against recorded match outcomes."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import MarketType, Match, MatchStatus, Prediction, PredictionResult


def actual_1x2_outcome(match: Match) -> str | None:
    if match.status != MatchStatus.finished:
        return None
    if match.home_score is None or match.away_score is None:
        return None
    if match.home_score > match.away_score:
        return "home"
    if match.home_score < match.away_score:
        return "away"
    return "draw"


def brier_score_1x2(home_p: float, draw_p: float, away_p: float, actual: str) -> float:
    probs = {"home": home_p / 100, "draw": draw_p / 100, "away": away_p / 100}
    return sum((probs[k] - (1.0 if k == actual else 0.0)) ** 2 for k in probs)


def evaluate_finished_predictions(db: Session) -> int:
    count = 0
    preds = (
        db.query(Prediction)
        .filter(Prediction.market == MarketType.X1X2)
        .outerjoin(PredictionResult)
        .filter(PredictionResult.id.is_(None))
        .all()
    )
    for p in preds:
        match = db.query(Match).filter(Match.id == p.match_id).first()
        if not match:
            continue
        actual = actual_1x2_outcome(match)
        if not actual or p.home_prob is None:
            continue
        bs = brier_score_1x2(p.home_prob, p.draw_prob or 0, p.away_prob or 0, actual)
        db.add(
            PredictionResult(
                prediction_id=p.id,
                actual_outcome=actual,
                brier_score=bs,
                evaluated_at=datetime.utcnow(),
            )
        )
        count += 1
    db.commit()
    return count
