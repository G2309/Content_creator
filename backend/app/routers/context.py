from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_active
from app.models import BusinessContext, User
from app.schemas import BusinessContextPublic, BusinessContextUpdate

router = APIRouter(prefix="/api/context", tags=["context"])


def _get_or_create(db: Session, user: User) -> BusinessContext:
    if user.business_context is not None:
        return user.business_context
    ctx = BusinessContext(user_id=user.id)
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


@router.get("", response_model=BusinessContextPublic)
def read_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    return _get_or_create(db, current_user)


@router.put("", response_model=BusinessContextPublic)
def update_context(
    payload: BusinessContextUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    ctx = _get_or_create(db, current_user)
    for field, value in payload.model_dump().items():
        setattr(ctx, field, value)
    db.commit()
    db.refresh(ctx)
    return ctx
