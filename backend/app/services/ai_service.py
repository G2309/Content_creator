from __future__ import annotations

import json
import logging
import re

import anthropic

from app.config import get_settings
from app.models import BusinessContext
from app.schemas import CatalogItem

logger = logging.getLogger(__name__)
settings = get_settings()

_client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    timeout=settings.anthropic_timeout_seconds,
)


FORMAT_INSTRUCTIONS: dict[str, str] = {
    "guion_video": (
        "Genera un GUION para video corto de Instagram (Reel). "
        "Estructura obligatoria: HOOK (1 línea fuerte), PROBLEMA (2-3 líneas), "
        "SOLUCIÓN (2-3 líneas) y CTA (1 línea). "
        "Marca claramente cada sección con su nombre en mayúsculas. "
        "Duración objetivo: 30-45 segundos hablados."
    ),
    "caption_post": (
        "Genera un CAPTION para post o reel de Instagram. "
        "Primera línea = gancho fuerte que detenga el scroll. "
        "Cuerpo: 3-5 líneas cortas, separadas para legibilidad móvil. "
        "Cierra con un CTA claro. "
        "Agrega 5-8 hashtags relevantes al final, en una sola línea."
    ),
    "historia_ig": (
        "Genera el texto para una HISTORIA de Instagram. "
        "Máximo 2-3 frases muy cortas. Directo, sin rodeos. "
        "Termina con una pregunta o CTA simple."
    ),
    "anuncio_pagado": (
        "Genera un COPY para ANUNCIO PAGADO de Instagram. "
        "Estructura: gancho con dolor concreto, beneficio principal, "
        "prueba o autoridad, y un CTA fuerte orientado a conversión. "
        "Tono persuasivo pero honesto, sin clickbait. Máximo 80 palabras."
    ),
}


def _build_system_prompt(ctx: BusinessContext) -> str:
    parts = [
        "Eres un copywriter experto en contenido orgánico y publicitario para Instagram en español.",
        "Tu trabajo es generar textos listos para publicar, sin meta-comentarios ni explicaciones.",
        "NO escribas frases como 'Aquí tienes', 'Espero te sirva' o similares. Devuelve solo el contenido pedido.",
        "",
        "CONTEXTO DEL NEGOCIO PARA EL QUE ESCRIBES:",
    ]
    has_context = False
    if ctx.business_name.strip():
        parts.append(f"- Nombre: {ctx.business_name.strip()}")
        has_context = True
    if ctx.description.strip():
        parts.append(f"- Descripción: {ctx.description.strip()}")
        has_context = True
    if ctx.services.strip():
        parts.append(f"- Servicios: {ctx.services.strip()}")
        has_context = True
    if ctx.target_audience.strip():
        parts.append(f"- A quién le hablan: {ctx.target_audience.strip()}")
        has_context = True
    if ctx.value_proposition.strip():
        parts.append(f"- Propuesta de valor: {ctx.value_proposition.strip()}")
        has_context = True
    if ctx.tone.strip():
        parts.append(f"- Tono de voz: {ctx.tone.strip()}")
        has_context = True
    if not has_context:
        parts.append("(Sin contexto configurado todavía — escribe de forma genérica pero profesional.)")
    return "\n".join(parts)


def _build_user_prompt(pain, format_item, extra_idea, variation):
    instruction = FORMAT_INSTRUCTIONS.get(
        format_item.id,
        f"Genera contenido en el formato: {format_item.label}.",
    )
    parts = [
        f"DOLOR DEL CLIENTE A ATACAR: {pain.label}.",
        f"Detalle del dolor: {pain.description or '—'}",
        "",
        f"FORMATO: {instruction}",
    ]
    if extra_idea.strip():
        parts.extend(["", f"IDEA O CONTEXTO ADICIONAL DEL USUARIO: {extra_idea.strip()}"])
    if variation:
        parts.extend([
            "",
            "Esta es una REGENERACIÓN: ofrece un ángulo claramente distinto al que daría "
            "una primera versión obvia. Cambia el hook, el enfoque o la metáfora.",
        ])
    parts.extend(["", "Devuelve únicamente el texto final, sin encabezados ni notas."])
    return "\n".join(parts)


def generate_content(
    *,
    business_context: BusinessContext,
    pain: CatalogItem,
    format_item: CatalogItem,
    extra_idea: str = "",
    variation: bool = False,
) -> str:
    system = _build_system_prompt(business_context)
    user_msg = _build_user_prompt(pain, format_item, extra_idea, variation)
    temperature = 1.0 if variation else 0.8

    try:
        response = _client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
    except anthropic.APITimeoutError as e:
        logger.warning("Anthropic timeout: %s", e)
        raise
    except anthropic.APIError as e:
        logger.exception("Anthropic API error: %s", e)
        raise

    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts).strip()


CONTEXT_EXTRACTION_SYSTEM = (
    "Eres un analista de marketing experto. Recibes el contenido extraído del sitio web de un negocio "
    "y tu tarea es identificar la información clave que permita generar contenido de redes sociales "
    "coherente con la marca.\n\n"
    "Devuelves EXCLUSIVAMENTE un objeto JSON válido con esta forma exacta:\n"
    "{\n"
    '  "business_name": "Nombre del negocio o marca",\n'
    '  "description": "Descripción del negocio en 2-3 frases naturales",\n'
    '  "services": "Lista de servicios o productos principales, uno por línea con guion",\n'
    '  "target_audience": "Descripción del cliente ideal — quién es, qué hace, qué necesita",\n'
    '  "value_proposition": "Qué hace especial a este negocio frente a competidores",\n'
    '  "tone": "Una sola línea describiendo el tono de comunicación del sitio"\n'
    "}\n\n"
    "Reglas estrictas:\n"
    "- Devuelve SOLO el JSON, sin texto antes ni después, sin bloques de código markdown.\n"
    "- Si un campo no puede inferirse del contenido, usa string vacío.\n"
    "- Responde en el mismo idioma que predomine en el contenido (probablemente español).\n"
    "- Sé conciso pero específico. No inventes información que no esté en el contenido."
)


def extract_business_context(scraped_text: str, source_url: str) -> dict:
    user_msg = (
        f"URL de origen: {source_url}\n\n"
        f"Contenido extraído del sitio:\n\n{scraped_text}"
    )

    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        temperature=0.2,
        system=CONTEXT_EXTRACTION_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = "".join(b.text for b in response.content if b.type == "text").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError("La IA no devolvió un JSON válido")
        data = json.loads(match.group(0))

    return {
        "business_name": str(data.get("business_name") or "").strip()[:255],
        "description": str(data.get("description") or "").strip()[:5000],
        "services": str(data.get("services") or "").strip()[:5000],
        "target_audience": str(data.get("target_audience") or "").strip()[:5000],
        "value_proposition": str(data.get("value_proposition") or "").strip()[:5000],
        "tone": str(data.get("tone") or "").strip()[:255],
    }
