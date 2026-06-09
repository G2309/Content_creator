from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models import User
from app.schemas import CatalogItem

router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])


PAINS: list[CatalogItem] = [
    CatalogItem(
        id="paquetes_retenidos_aduana",
        label="Paquetes retenidos en aduana",
        description="El cliente sufre demoras y trámites complicados al pasar mercancía por aduana.",
    ),
    CatalogItem(
        id="costos_sorpresa",
        label="Costos sorpresa al recibir la mercancía",
        description="Cobros inesperados al final que rompen el presupuesto del cliente.",
    ),
    CatalogItem(
        id="inventario_tardio",
        label="Inventario que no llega a tiempo",
        description="Retrasos que afectan ventas y planificación del negocio del cliente.",
    ),
    CatalogItem(
        id="paquetes_danados",
        label="Paquetes dañados o mal manejados",
        description="Mercancía que llega en mal estado por descuidos en la cadena logística.",
    ),
    CatalogItem(
        id="sin_seguimiento",
        label="Sin seguimiento ni comunicación del envío",
        description="El cliente queda a ciegas sobre dónde está su paquete y cuándo llegará.",
    ),
    CatalogItem(
        id="importaciones_volumen",
        label="Importaciones en volumen sin apoyo logístico",
        description="Empresas que necesitan importar mucho pero no tienen quién les acompañe.",
    ),
]

FORMATS: list[CatalogItem] = [
    CatalogItem(
        id="guion_video",
        label="Guion para video de Instagram",
        description="Hook + problema + solución + CTA. Para Reels y videos cortos.",
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


@router.get("/pains", response_model=list[CatalogItem])
def get_pains(_: User = Depends(get_current_user)) -> list[CatalogItem]:
    return PAINS


@router.get("/formats", response_model=list[CatalogItem])
def get_formats(_: User = Depends(get_current_user)) -> list[CatalogItem]:
    return FORMATS


def get_pain_by_id(pain_id: str) -> CatalogItem | None:
    return next((p for p in PAINS if p.id == pain_id), None)


def get_format_by_id(format_id: str) -> CatalogItem | None:
    return next((f for f in FORMATS if f.id == format_id), None)
