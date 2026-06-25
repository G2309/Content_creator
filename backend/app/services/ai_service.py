from __future__ import annotations

import json
import logging
import re

import anthropic

from app.config import get_settings
from app.models import BusinessContext

logger = logging.getLogger(__name__)
settings = get_settings()

_client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    timeout=settings.anthropic_timeout_seconds,
)


GUION_VIDEO_INSTRUCTION = (
    "Genera un GUION para video de Instagram (Reel largo o video de feed) "
    "que dure entre 1 y 3 minutos hablados — entre 200 y 450 palabras aproximadamente. "
    "NO devuelvas un texto corto: si te queda menos de 200 palabras, sigue desarrollando.\n\n"
    "ESTRUCTURA OBLIGATORIA — marca cada sección con su nombre en MAYÚSCULAS:\n\n"
    "HOOK:\n"
    "Una sola línea muy fuerte que detenga el scroll en los primeros 2 segundos. "
    "Sigue ESTRICTAMENTE la instrucción del tipo de gancho elegido.\n\n"
    "PROBLEMA (70% del guion — la sección más larga):\n"
    "Desarrolla el dolor PROFUNDAMENTE. Esta es la parte más extensa, donde generas "
    "tensión emocional y amplificas las consecuencias del problema. Toca el problema "
    "desde varios ángulos: cómo se siente, qué se pierde, qué pasa cuando se ignora, "
    "casos concretos donde aparece. NO basta con describirlo — el espectador debe "
    "incomodarse e identificarse. Usa frases cortas y directas para sonar natural al hablar.\n\n"
    "ENSEÑANZA / MORALEJA (20% del guion):\n"
    "La lección que se desprende del problema. Qué patrón hay detrás, qué tendría que "
    "cambiar de mentalidad la audiencia para no caer en esto. No es la solución todavía, "
    "es la reflexión que conecta el dolor con el aprendizaje.\n\n"
    "SOLUCIÓN (10% del guion — la parte más breve):\n"
    "Recién aquí presentas cómo se resuelve. Concreto, sin extenderse. "
    "Es el alivio después del dolor, no un sermón comercial.\n\n"
    "CTA:\n"
    "Una línea final accionable que conecte con la audiencia."
)


FORMAT_INSTRUCTIONS: dict[str, str] = {
    "guion_video": GUION_VIDEO_INSTRUCTION,
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


def _context_lines(ctx: BusinessContext, label: str) -> list[str]:
    lines = [f"=== {label}: \"{ctx.name}\" ==="]
    if ctx.business_name.strip():
        lines.append(f"- Nombre: {ctx.business_name.strip()}")
    if ctx.description.strip():
        lines.append(f"- Descripción: {ctx.description.strip()}")
    if ctx.services.strip():
        lines.append(f"- Servicios: {ctx.services.strip()}")
    if ctx.target_audience.strip():
        lines.append(f"- A quién le hablan: {ctx.target_audience.strip()}")
    if ctx.value_proposition.strip():
        lines.append(f"- Propuesta de valor: {ctx.value_proposition.strip()}")
    if ctx.tone.strip():
        lines.append(f"- Tono de voz: {ctx.tone.strip()}")
    lines.append(f"=== FIN {label} ===")
    return lines


def _build_system_prompt(
    ctx: BusinessContext,
    reference_contexts: list[BusinessContext] | None = None,
) -> str:
    parts = [
        "Eres un copywriter experto en contenido orgánico y publicitario para Instagram en español.",
        "Tu trabajo es generar textos listos para publicar, sin meta-comentarios ni explicaciones.",
        "NO escribas frases como 'Aquí tienes', 'Espero te sirva' o similares. Devuelve solo el contenido pedido.",
        "",
        "REGLAS CRÍTICAS:",
        "- Si el usuario te da una IDEA O CONTEXTO ADICIONAL, debes incorporarla LITERALMENTE en el resultado.",
        "- Si esa idea adicional contiene un CTA específico (ej. 'comenta la palabra X y te enviamos info'), "
        "ese CTA debe aparecer textualmente al final, sin reformularlo ni reemplazarlo por uno genérico.",
        "- Si la idea adicional menciona una promoción, fecha, palabra clave o detalle concreto, "
        "ese detalle debe aparecer en el contenido final.",
        "",
        "CONTEXTO DEL NEGOCIO PARA EL QUE ESCRIBES (este es el negocio principal, "
        "el contenido debe sonar a su voz y resolver sus objetivos):",
    ]

    has_primary_data = any([
        ctx.business_name.strip(),
        ctx.description.strip(),
        ctx.services.strip(),
        ctx.target_audience.strip(),
        ctx.value_proposition.strip(),
        ctx.tone.strip(),
    ])

    if has_primary_data:
        parts.extend(_context_lines(ctx, "NEGOCIO PRINCIPAL"))
    else:
        parts.append("(Sin contexto configurado todavía — escribe de forma genérica pero profesional.)")

    if reference_contexts:
        parts.extend([
            "",
            "CONTEXTOS DE REFERENCIA (otros negocios, competidores o marcas que el usuario quiere tener "
            "disponibles para comparar, contrastar o mencionar si la idea adicional lo pide):",
        ])
        for ref in reference_contexts:
            parts.extend(_context_lines(ref, "REFERENCIA"))
        parts.extend([
            "",
            "Importante sobre las referencias:",
            "- NUNCA escribas como si fueras el negocio de referencia. La voz siempre es la del NEGOCIO PRINCIPAL.",
            "- Úsalas solo si la idea adicional del usuario pide comparación o contraste explícito.",
            "- Si las comparas, resalta lo que diferencia y favorece al NEGOCIO PRINCIPAL.",
        ])

    return "\n".join(parts)


def _build_user_prompt(
    pain_label: str,
    pain_description: str,
    format_id: str,
    format_label: str,
    hook_label: str,
    hook_instruction: str,
    extra_idea: str,
    variation: bool,
) -> str:
    instruction = FORMAT_INSTRUCTIONS.get(
        format_id,
        f"Genera contenido en el formato: {format_label}.",
    )
    parts = [
        f"DOLOR DEL CLIENTE A ATACAR: {pain_label}.",
        f"Detalle del dolor: {pain_description or '—'}",
        "",
        f"FORMATO: {instruction}",
    ]

    if hook_instruction:
        parts.extend([
            "",
            f"TIPO DE GANCHO ELEGIDO: {hook_label}.",
            f"INSTRUCCIÓN DEL GANCHO (cúmplela al pie de la letra): {hook_instruction}",
        ])

    if extra_idea.strip():
        parts.extend([
            "",
            "=== IDEA O CONTEXTO ADICIONAL DEL USUARIO (PRIORIDAD MÁXIMA) ===",
            extra_idea.strip(),
            "=== FIN DE LA IDEA ADICIONAL ===",
            "",
            "Esta idea adicional NO es opcional. Si contiene un CTA, una promoción, una palabra clave "
            "o cualquier dato específico, DEBE aparecer textualmente en el contenido final. "
            "Si pide comparar con un contexto de referencia, hazlo usando los datos disponibles.",
        ])

    if variation:
        parts.extend([
            "",
            "Esta es una REGENERACIÓN: ofrece un ángulo claramente distinto al que daría "
            "una primera versión obvia. Cambia el enfoque, la metáfora o el ejemplo principal — "
            "pero mantén el tipo de gancho elegido y respeta la idea adicional del usuario si la hay.",
        ])
    parts.extend(["", "Devuelve únicamente el texto final, sin encabezados ni notas."])
    return "\n".join(parts)


def generate_content(
    *,
    business_context: BusinessContext,
    reference_contexts: list[BusinessContext] | None = None,
    pain_label: str,
    pain_description: str,
    format_id: str,
    format_label: str,
    hook_label: str = "",
    hook_instruction: str = "",
    extra_idea: str = "",
    variation: bool = False,
) -> str:
    system = _build_system_prompt(business_context, reference_contexts)
    user_msg = _build_user_prompt(
        pain_label, pain_description, format_id, format_label,
        hook_label, hook_instruction, extra_idea, variation,
    )
    temperature = 1.0 if variation else 0.8

    max_tokens = settings.anthropic_max_tokens
    if format_id == "guion_video":
        max_tokens = max(max_tokens, 2048)

    try:
        response = _client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
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
