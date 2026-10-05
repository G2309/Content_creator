import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import anthropic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user_active
from app.hooks import get_hook_by_id
from app.models import BusinessContext, CustomerPain, User
from app.objectives import get_objective_by_id
from app.pillars import get_pillar_by_id
from app.routers.catalogs import get_format_by_id
from app.routers.context import get_primary_context
from app.schemas import GenerateRequest, GenerateResponse, GenerateVariantsResponse
from app.services.ai_service import generate_content
from app.services.insights import learnings_for_prompt
from app.widths import WIDTH_RELEVANT_OBJECTIVES, get_width_by_id

router = APIRouter(prefix="/api/content", tags=["content"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Tres ángulos distintos por objetivo, para que las versiones no se parezcan.
VARIANT_ANGLES = {
    "descubrimiento": ("Contracorriente", "Curiosidad", "Historia"),
    "seguidores": ("Educación", "Revelación", "Error"),
    "confianza": ("Demostración", "Comparación", "Historia"),
    "conversion": ("Consecuencia", "Comparación", "Demostración"),
}
DEFAULT_VARIANT_ANGLES = ("Problema", "Contracorriente", "Historia")


@dataclass
class _Plan:
    pain: CustomerPain
    format_item: object
    hook: dict | None
    objective: dict | None
    width: dict | None
    pillar: dict | None
    primary_ctx: BusinessContext
    reference_contexts: list[BusinessContext]
    learnings: str


def _build_plan(payload: GenerateRequest, db: Session, user: User) -> _Plan:
    pain = db.get(CustomerPain, payload.pain_id)
    if not pain or pain.user_id != user.id:
        raise HTTPException(status_code=400, detail="Ángulo no válido.")

    format_item = get_format_by_id(payload.format_id)
    if not format_item:
        raise HTTPException(status_code=400, detail="Formato no válido.")

    hook = None
    if payload.hook_id:
        hook = get_hook_by_id(payload.hook_id)
        if not hook:
            raise HTTPException(status_code=400, detail="Tipo de gancho no válido.")

    objective = None
    if payload.objective_id:
        objective = get_objective_by_id(payload.objective_id)
        if not objective:
            raise HTTPException(status_code=400, detail="Objetivo no válido.")

    # La anchura solo aplica a objetivos de descubrimiento y seguidores.
    width = None
    if payload.width_id:
        width = get_width_by_id(payload.width_id)
        if not width:
            raise HTTPException(status_code=400, detail="Anchura no válida.")
        if not objective or objective["id"] not in WIDTH_RELEVANT_OBJECTIVES:
            width = None

    # El pilar viene del insight, no lo elige el usuario al generar.
    pillar = get_pillar_by_id(pain.pillar) if pain.pillar else None

    primary_ctx = get_primary_context(db, user)

    reference_contexts: list[BusinessContext] = []
    clean_ids = [i for i in payload.reference_context_ids if i != primary_ctx.id]
    if clean_ids:
        reference_contexts = (
            db.query(BusinessContext)
            .filter(BusinessContext.id.in_(clean_ids), BusinessContext.user_id == user.id)
            .all()
        )

    learnings = learnings_for_prompt(db, user.id) if format_item.id == "guion_video" else ""

    # La sesión no es segura entre hilos: cargar todo antes de generar en paralelo.
    for obj in (pain, primary_ctx, *reference_contexts):
        for column in obj.__table__.columns:
            getattr(obj, column.key)

    return _Plan(pain, format_item, hook, objective, width, pillar,
                 primary_ctx, reference_contexts, learnings)


def _run(plan: _Plan, payload: GenerateRequest, angle_label: str, variation: bool) -> GenerateResponse:
    content, model_used = generate_content(
        business_context=plan.primary_ctx,
        reference_contexts=plan.reference_contexts,
        pain_label=plan.pain.label,
        pain_description=plan.pain.description,
        pain_category=plan.pain.category,
        format_id=plan.format_item.id,
        format_label=plan.format_item.label,
        hook_label=plan.hook["label"] if plan.hook else "",
        hook_instruction=plan.hook["instruction"] if plan.hook else "",
        extra_idea=payload.extra_idea,
        variation=variation,
        objective=plan.objective,
        pillar=plan.pillar,
        width=plan.width,
        angle_label=angle_label,
        learnings=plan.learnings,
        duration_seconds=payload.duration_seconds,
    )
    if not content:
        raise ValueError("respuesta vacía")

    return GenerateResponse(
        content=content,
        pain_id=plan.pain.id,
        pain_label=plan.pain.label,
        pain_category=plan.pain.category,
        format_id=plan.format_item.id,
        format_label=plan.format_item.label,
        hook_id=plan.hook["id"] if plan.hook else "",
        hook_label=plan.hook["label"] if plan.hook else "",
        objective_id=plan.objective["id"] if plan.objective else "",
        objective_label=plan.objective["label"] if plan.objective else "",
        width_id=plan.width["id"] if plan.width else "",
        width_label=plan.width["label"] if plan.width else "",
        pillar_id=plan.pillar["id"] if plan.pillar else "",
        pillar_label=plan.pillar["label"] if plan.pillar else "",
        angle_label=angle_label,
        model=model_used,
    )


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, anthropic.APITimeoutError):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="La IA tardó demasiado en responder. Intenta de nuevo.",
        )
    if isinstance(exc, anthropic.AuthenticationError):
        logger.error("Anthropic API key inválida")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de configuración del servidor.",
        )
    if isinstance(exc, anthropic.RateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Se alcanzó el límite de la IA. Espera unos segundos y vuelve a intentar.",
        )
    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La IA devolvió una respuesta vacía. Intenta de nuevo.",
        )
    logger.error("Error al generar contenido: %r", exc, exc_info=exc)
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="No fue posible generar el contenido en este momento.",
    )


@router.post("/generate", response_model=GenerateResponse)
def generate(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> GenerateResponse:
    plan = _build_plan(payload, db, current_user)
    try:
        return _run(plan, payload, angle_label="", variation=payload.variation)
    except Exception as exc:
        raise _http_error(exc)


@router.post("/generate-variants", response_model=GenerateVariantsResponse)
def generate_variants(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_active),
) -> GenerateVariantsResponse:
    """Tres versiones con ángulos distintos, en paralelo: tarda lo mismo que una."""
    plan = _build_plan(payload, db, current_user)
    angles = VARIANT_ANGLES.get(
        plan.objective["id"] if plan.objective else "", DEFAULT_VARIANT_ANGLES
    )

    with ThreadPoolExecutor(max_workers=len(angles)) as pool:
        futures = [
            pool.submit(_run, plan, payload, angle, payload.variation) for angle in angles
        ]

    variants: list[GenerateResponse] = []
    errors: list[Exception] = []
    for future in futures:
        try:
            variants.append(future.result())
        except Exception as exc:
            errors.append(exc)

    if not variants:
        raise _http_error(errors[0])
    if errors:
        logger.warning("Fallaron %d de %d versiones: %s", len(errors), len(angles), errors[0])

    return GenerateVariantsResponse(variants=variants, failed=len(errors))
