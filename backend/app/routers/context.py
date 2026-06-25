from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_active
from app.models import BusinessContext, User
from app.schemas import (
    BusinessContextCreate,
    BusinessContextListItem,
    BusinessContextPublic,
    BusinessContextUpdate,
)

router = APIRouter(prefix="/api/contexts", tags=["contexts"])


def get_primary_context(db: Session, user: User) -> BusinessContext:
    ctx = (
        db.query(BusinessContext)
        .filter(BusinessContext.user_id == user.id, BusinessContext.is_primary.is_(True))
        .first()
    )
    if ctx:
        return ctx

    ctx = db.query(BusinessContext).filter(BusinessContext.user_id == user.id).first()
    if ctx:
        ctx.is_primary = True
        db.commit()
        db.refresh(ctx)
        return ctx

    ctx = BusinessContext(user_id=user.id, name="Principal", is_primary=True)
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


@router.get("", response_model=list[BusinessContextListItem])
def list_contexts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> list[BusinessContext]:
    return (
        db.query(BusinessContext)
        .filter(BusinessContext.user_id == current_user.id)
        .order_by(BusinessContext.is_primary.desc(), BusinessContext.updated_at.desc())
        .all()
    )


@router.get("/{context_id}", response_model=BusinessContextPublic)
def get_context(
    context_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    ctx = db.get(BusinessContext, context_id)
    if not ctx or ctx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contexto no encontrado.")
    return ctx


@router.post("", response_model=BusinessContextPublic, status_code=status.HTTP_201_CREATED)
def create_context(
    payload: BusinessContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    existing_count = (
        db.query(BusinessContext)
        .filter(BusinessContext.user_id == current_user.id)
        .count()
    )
    ctx = BusinessContext(
        user_id=current_user.id,
        is_primary=(existing_count == 0),
        **payload.model_dump(),
    )
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


@router.put("/{context_id}", response_model=BusinessContextPublic)
def update_context(
    context_id: int,
    payload: BusinessContextUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    ctx = db.get(BusinessContext, context_id)
    if not ctx or ctx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contexto no encontrado.")

    for field, value in payload.model_dump().items():
        setattr(ctx, field, value)
    db.commit()
    db.refresh(ctx)
    return ctx


@router.post("/{context_id}/set-primary", response_model=BusinessContextPublic)
def set_primary(
    context_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> BusinessContext:
    ctx = db.get(BusinessContext, context_id)
    if not ctx or ctx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contexto no encontrado.")

    db.query(BusinessContext).filter(
        BusinessContext.user_id == current_user.id
    ).update({"is_primary": False})

    ctx.is_primary = True
    db.commit()
    db.refresh(ctx)
    return ctx


@router.delete("/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_context(
    context_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> None:
    ctx = db.get(BusinessContext, context_id)
    if not ctx or ctx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contexto no encontrado.")

    was_primary = ctx.is_primary

    db.delete(ctx)
    db.flush()

    if was_primary:
        replacement = (
            db.query(BusinessContext)
            .filter(BusinessContext.user_id == current_user.id)
            .order_by(BusinessContext.updated_at.desc())
            .first()
        )
        if replacement:
            replacement.is_primary = True

    db.commit()
