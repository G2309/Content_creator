from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_active
from app.hooks import get_hook_by_id
from app.models import CustomerPain, SavedTemplate, User
from app.objectives import get_objective_by_id
from app.pillars import get_pillar_by_id
from app.routers.catalogs import get_format_by_id
from app.schemas import (
    LibraryInsights,
    SavedTemplateCreate,
    SavedTemplatePublic,
    SavedTemplateUpdate,
    TemplateResultsUpdate,
)
from app.services.insights import library_insights
from app.widths import get_width_by_id

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


@router.get("/insights", response_model=LibraryInsights)
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> dict:
    return library_insights(db, current_user.id)


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

    objective = get_objective_by_id(payload.objective_id) if payload.objective_id else None
    hook = get_hook_by_id(payload.hook_id) if payload.hook_id else None
    width = get_width_by_id(payload.width_id) if payload.width_id else None
    pillar = get_pillar_by_id(pain.pillar) if pain.pillar else None

    template = SavedTemplate(
        user_id=current_user.id,
        content=payload.content,
        pain_id=pain.id,
        pain_label=pain.label,
        format_id=format_item.id,
        format_label=format_item.label,
        objective_id=objective["id"] if objective else "",
        objective_label=objective["label"] if objective else "",
        pillar_id=pillar["id"] if pillar else "",
        pillar_label=pillar["label"] if pillar else "",
        hook_id=hook["id"] if hook else "",
        hook_label=hook["label"] if hook else "",
        width_id=width["id"] if width else "",
        angle_label=payload.angle_label.strip(),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/{template_id}", response_model=SavedTemplatePublic)
def update_template(
    template_id: int,
    payload: SavedTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> SavedTemplate:
    template = db.get(SavedTemplate, template_id)
    if not template or template.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada.")

    template.content = payload.content
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


@router.put("/{template_id}/results", response_model=SavedTemplatePublic)
def update_results(
    template_id: int,
    payload: TemplateResultsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> SavedTemplate:
    template = db.get(SavedTemplate, template_id)
    if not template or template.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada.")

    for field, value in payload.model_dump().items():
        setattr(template, field, value)
    has_any = any(v is not None for v in payload.model_dump().values())
    template.results_updated_at = datetime.now(timezone.utc) if has_any else None
    db.commit()
    db.refresh(template)
    return template
