from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_optional
from app.models import User, UserSelection
from app.schemas import SelectionsIn

router = APIRouter(prefix="/selections", tags=["selections"])


@router.post("")
def save_selections(
    body: SelectionsIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    saved = 0
    for item in body.selections:
        db.add(
            UserSelection(
                user_id=user.id if user else None,
                match_id=item.match_id,
                market=item.market,
                outcome_key=item.outcome_key,
            )
        )
        saved += 1
    db.commit()
    return {"saved": saved}
