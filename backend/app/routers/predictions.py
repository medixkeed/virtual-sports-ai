from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.ai.engine import run_prediction
from app.ai.evaluation import evaluate_finished_predictions
from app.database import get_db
from app.deps import get_current_user
from app.models import Match, ModelVersion, Prediction, User
from app.schemas import PaginatedPredictions, PredictionCreateIn, PredictionOut

router = APIRouter(tags=["predictions"])


def _pred_out(db: Session, p: Prediction) -> PredictionOut:
    model_name = "baseline-v1"
    if p.model_version_id:
        mv = db.query(ModelVersion).filter(ModelVersion.id == p.model_version_id).first()
        if mv:
            model_name = mv.name
    return PredictionOut(
        id=p.id,
        match_id=p.match_id,
        market=p.market.value,
        home_prob=p.home_prob,
        draw_prob=p.draw_prob,
        away_prob=p.away_prob,
        message=p.message,
        is_demo=p.is_demo,
        model_version=model_name,
        status=p.status,
        created_at=p.created_at,
    )


@router.get("/matches/{match_id}/predictions", response_model=list[PredictionOut])
def match_predictions(match_id: int, db: Session = Depends(get_db)):
    preds = (
        db.query(Prediction)
        .filter(Prediction.match_id == match_id)
        .order_by(Prediction.created_at.desc())
        .limit(20)
        .all()
    )
    return [_pred_out(db, p) for p in preds]


@router.get("/predictions/history", response_model=PaginatedPredictions)
def prediction_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Prediction).count()
    items = (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedPredictions(
        items=[_pred_out(db, p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/predictions", response_model=PredictionOut)
def create_prediction(
    body: PredictionCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.services.auth import can_create_prediction

    ok, msg = can_create_prediction(user, db)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)

    match = db.query(Match).filter(Match.id == body.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    pred = run_prediction(db, match, body.market, user.id)
    user.predictions_used_today += 1
    db.commit()
    evaluate_finished_predictions(db)
    return _pred_out(db, pred)
