import logging

import anthropic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user_active
from app.hooks import get_hook_by_id
from app.models import BusinessContext, CustomerPain, User
from app.routers.catalogs import get_format_by_id
from app.schemas import GenerateRequest, GenerateResponse
from app.services.ai_service import generate_content

router = APIRouter(prefix="/api/content", tags=["content"])
logger = logging.getLogger(__name__)
settings = get_settings()


def _get_context(db: Session, user: User) -> BusinessContext:
    if user.business_context:
        return user.business_context
    ctx = BusinessContext(user_id=user.id)
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


@router.post("/generate", response_model=GenerateResponse)
def generate(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> GenerateResponse:
    pain = db.get(CustomerPain, payload.pain_id)
    if not pain or pain.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Dolor del cliente no válido.")

    format_item = get_format_by_id(payload.format_id)
    if not format_item:
        raise HTTPException(status_code=400, detail="Formato no válido.")

    hook = None
    if payload.hook_id:
        hook = get_hook_by_id(payload.hook_id)
        if not hook:
            raise HTTPException(status_code=400, detail="Tipo de gancho no válido.")

    ctx = _get_context(db, current_user)

    try:
        content = generate_content(
            business_context=ctx,
            pain_label=pain.label,
            pain_description=pain.description,
            format_id=format_item.id,
            format_label=format_item.label,
            hook_label=hook["label"] if hook else "",
            hook_instruction=hook["instruction"] if hook else "",
            extra_idea=payload.extra_idea,
            variation=payload.variation,
        )
    except anthropic.APITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="La IA tardó demasiado en responder. Intenta de nuevo.",
        )
    except anthropic.AuthenticationError:
        logger.error("Anthropic API key inválida")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración del servidor.",
        )
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se alcanzó el límite de la IA. Espera unos segundos y vuelve a intentar.",
        )
    except anthropic.APIError as e:
        logger.exception("Error de la API de IA: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible generar el contenido en este momento.",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La IA devolvió una respuesta vacía. Intenta de nuevo.",
        )

    return GenerateResponse(
        content=content,
        pain_id=pain.id,
        pain_label=pain.label,
        format_id=format_item.id,
        format_label=format_item.label,
        hook_id=hook["id"] if hook else "",
        hook_label=hook["label"] if hook else "",
        model=settings.anthropic_model,
    )
