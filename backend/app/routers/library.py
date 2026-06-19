from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_active
from app.models import CustomerPain, SavedTemplate, User
from app.routers.catalogs import get_format_by_id
from app.schemas import SavedTemplateCreate, SavedTemplatePublic

router = APIRouter(prefix="/api/library", tags=["library"])


@router.get("", response_model=list[SavedTemplatePublic])
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> list[SavedTemplate]:
    return (
        db.query(SavedTemplate)
        .filter(SavedTemplate.user_id == current_user.id)
        .order_by(SavedTemplate.created_at.desc())
        .all()
    )


@router.post("", response_model=SavedTemplatePublic, status_code=status.HTTP_201_CREATED)
def save_template(
    payload: SavedTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> SavedTemplate:
    pain = db.get(CustomerPain, payload.pain_id)
    if not pain or pain.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Dolor del cliente no válido.")

    format_item = get_format_by_id(payload.format_id)
    if not format_item:
        raise HTTPException(status_code=400, detail="Formato no válido.")

    template = SavedTemplate(
        user_id=current_user.id,
        content=payload.content,
        pain_id=pain.id,
        pain_label=pain.label,
        format_id=format_item.id,
        format_label=format_item.label,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> None:
    template = db.get(SavedTemplate, template_id)
    if not template or template.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada.")

    db.delete(template)
    db.commit()
