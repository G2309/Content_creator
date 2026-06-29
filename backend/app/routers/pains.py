from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_active
from app.models import CustomerPain, User
from app.schemas import (
    ImportInsightsRequest,
    PainCreate,
    PainPublic,
    PainUpdate,
    SuggestedInsightItem,
)
from app.suggested_insights import SUGGESTED_INSIGHTS

router = APIRouter(prefix="/api/pains", tags=["pains"])


@router.get("", response_model=list[PainPublic])
def list_pains(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> list[CustomerPain]:
    return (
        db.query(CustomerPain)
        .filter(CustomerPain.user_id == current_user.id)
        .order_by(CustomerPain.category.asc(), CustomerPain.position.asc(), CustomerPain.id.asc())
        .all()
    )


@router.get("/suggested", response_model=list[SuggestedInsightItem])
def get_suggested(
    _: User = Depends(get_current_user_active),
) -> list[dict]:
    return SUGGESTED_INSIGHTS


@router.post("/import", response_model=list[PainPublic])
def import_insights(
    payload: ImportInsightsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> list[CustomerPain]:
    existing_count = (
        db.query(CustomerPain)
        .filter(CustomerPain.user_id == current_user.id)
        .count()
    )

    existing_labels = {
        (p.label.strip().lower(), p.category)
        for p in db.query(CustomerPain).filter(CustomerPain.user_id == current_user.id).all()
    }

    created: list[CustomerPain] = []
    position = existing_count
    for item in payload.items:
        key = (item.label.strip().lower(), item.category)
        if key in existing_labels:
            continue
        pain = CustomerPain(
            user_id=current_user.id,
            label=item.label.strip(),
            description=item.description.strip(),
            category=item.category,
            position=position,
        )
        db.add(pain)
        created.append(pain)
        existing_labels.add(key)
        position += 1

    db.commit()
    for p in created:
        db.refresh(p)
    return created


@router.post("", response_model=PainPublic, status_code=status.HTTP_201_CREATED)
def create_pain(
    payload: PainCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> CustomerPain:
    count = (
        db.query(CustomerPain)
        .filter(CustomerPain.user_id == current_user.id)
        .count()
    )
    pain = CustomerPain(
        user_id=current_user.id,
        label=payload.label.strip(),
        description=payload.description.strip(),
        category=payload.category,
        position=count,
    )
    db.add(pain)
    db.commit()
    db.refresh(pain)
    return pain


@router.put("/{pain_id}", response_model=PainPublic)
def update_pain(
    pain_id: int,
    payload: PainUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> CustomerPain:
    pain = db.get(CustomerPain, pain_id)
    if not pain or pain.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Insight no encontrado.")

    pain.label = payload.label.strip()
    pain.description = payload.description.strip()
    pain.category = payload.category
    if payload.position is not None:
        pain.position = payload.position
    db.commit()
    db.refresh(pain)
    return pain


@router.delete("/{pain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pain(
    pain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> None:
    pain = db.get(CustomerPain, pain_id)
    if not pain or pain.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Insight no encontrado.")

    db.delete(pain)
    db.commit()
