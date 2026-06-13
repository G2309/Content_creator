from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user_active
from app.models import User
from app.schemas import ScrapeRequest, ScrapeResponse
from app.services.ai_service import extract_business_context
from app.services.scraper import ScraperError, scrape_site

router = APIRouter(prefix="/api/scraper", tags=["scraper"])
logger = logging.getLogger(__name__)


@router.post("/extract", response_model=ScrapeResponse)
async def extract_from_url(
    payload: ScrapeRequest,
    _: User = Depends(get_current_user_active),
) -> ScrapeResponse:
    try:
        result = await scrape_site(payload.url)
    except ScraperError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.exception("Error inesperado en el scraper")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo extraer información del sitio. Verifica que la URL sea válida y esté en línea.",
        )

    if not result.pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El sitio respondió pero no se encontró texto utilizable.",
        )

    try:
        proposed = extract_business_context(result.combined_text, result.origin_url)
    except Exception:
        logger.exception("Error al estructurar contexto con IA")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El sitio se descargó pero la IA no pudo estructurar el contenido. Intenta de nuevo.",
        )

    return ScrapeResponse(
        source_url=result.origin_url,
        site_title=result.site_title,
        pages_scraped=len(result.pages),
        page_urls=[p.url for p in result.pages],
        raw_text_preview=result.combined_text[:3000],
        proposed_context=proposed,
    )
