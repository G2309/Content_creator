from fastapi import APIRouter, Depends

from app.deps import get_current_user_active
from app.hooks import HOOK_TYPES
from app.models import User
from app.schemas import CatalogItem

router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])


FORMATS: list[CatalogItem] = [
    CatalogItem(
        id="guion_video",
        label="Guion para video de Instagram",
        description="Hook + problema + enseñanza + solución + CTA. Para Reels y videos largos (1 a 3 minutos).",
    ),
    CatalogItem(
        id="caption_post",
        label="Caption para post o reel",
        description="Texto que acompaña la publicación con gancho fuerte y CTA.",
    ),
    CatalogItem(
        id="historia_ig",
        label="Historia de Instagram",
        description="Texto corto y directo pensado para stories.",
    ),
    CatalogItem(
        id="anuncio_pagado",
        label="Texto para anuncio pagado",
        description="Copy persuasivo orientado a conversión para campañas.",
    ),
]


@router.get("/formats", response_model=list[CatalogItem])
def get_formats(_: User = Depends(get_current_user_active)) -> list[CatalogItem]:
    return FORMATS


@router.get("/hooks", response_model=list[CatalogItem])
def get_hooks(_: User = Depends(get_current_user_active)) -> list[CatalogItem]:
    return [
        CatalogItem(id=h["id"], label=h["label"], description=h["description"])
        for h in HOOK_TYPES
    ]


def get_format_by_id(format_id: str) -> CatalogItem | None:
    return next((f for f in FORMATS if f.id == format_id), None)
