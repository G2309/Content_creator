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
    "Genera un GUION para Reel o video corto de Instagram. Duración objetivo: 1 a 3 minutos hablados "
    "(entre 200 y 450 palabras). Si te queda menos de 200, sigue desarrollando hasta cumplir.\n\n"
    "REGLAS DE PACING (las más importantes — Instagram premia la rapidez emocional):\n"
    "- Frases CORTAS, ritmo Reel. Sin párrafos largos ni subordinadas. Una idea por línea.\n"
    "- El dolor y la consecuencia económica deben aparecer en los PRIMEROS 15 segundos del guion.\n"
    "- NO más de 3 frases de contexto antes de revelar la consecuencia o la pérdida.\n"
    "- Mientras más cifras concretas de dinero, mejor (ej: '$2,500 cotizados → $3,200 pagados').\n"
    "- El 'culpable' debe ser claro y específico (el sistema, una práctica común, una empresa tipo) — "
    "NO una situación abstracta o impersonal.\n"
    "- Incluye al menos UN 'momento de revelación' — un dato concreto que haga al espectador pensar "
    "'no sabía eso' o 'eso me podría pasar'.\n\n"
    "ESTRUCTURA OBLIGATORIA — marca cada sección con su nombre en MAYÚSCULAS:\n\n"
    "HOOK:\n"
    "Una sola línea. Debe amenazar una pérdida concreta o golpear con un hecho específico en menos "
    "de 3 segundos. Sigue ESTRICTAMENTE la instrucción del tipo de gancho elegido. "
    "Si en el ángulo del cliente hay una cifra de dinero, úsala aquí.\n\n"
    "PROBLEMA (núcleo del guion, 60-70% del texto):\n"
    "Empieza con la CONSECUENCIA, no con el contexto. Después contextualiza. "
    "Desarrolla con micro-conflictos: situaciones concretas, momentos específicos. "
    "Usa frases cortas, secuenciales, cada una añadiendo presión. "
    "Nombra al culpable claramente (la industria, la práctica común, el competidor genérico).\n\n"
    "ENSEÑANZA / MORALEJA (15-20% del texto):\n"
    "Una línea de transición que conecta el dolor con un cambio de mentalidad. "
    "Qué tendría que ENTENDER el espectador para no caer en esto. No es la solución todavía.\n\n"
    "SOLUCIÓN (10% del texto — la parte más breve):\n"
    "Cómo se resuelve, concreto y rápido. Sin sermón comercial. "
    "Es el alivio después del dolor.\n\n"
    "CTA:\n"
    "Una línea final accionable. Si el usuario te dio un CTA específico, úsalo literal."
)


FORMAT_INSTRUCTIONS: dict[str, str] = {
    "guion_video": GUION_VIDEO_INSTRUCTION,
    "caption_post": (
        "Genera un CAPTION para post o reel de Instagram. "
        "Primera línea = gancho fuerte que detenga el scroll, idealmente con cifra de dinero si aplica. "
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
        "Estructura: gancho con dolor o pérdida económica concreta, beneficio principal, "
        "prueba o autoridad, y un CTA fuerte orientado a conversión. "
        "Tono persuasivo pero honesto, sin clickbait. Máximo 80 palabras."
    ),
}


CATEGORY_FRAMING = {
    "pain": (
        "El ángulo elegido es un DOLOR del cliente. Tu objetivo es amplificar la incomodidad "
        "y que el espectador se sienta identificado con ese problema. Usa cifras de dinero "
        "perdido si aplica."
    ),
    "desire": (
        "El ángulo elegido es un DESEO del cliente. Tu objetivo es pintar vívidamente el "
        "resultado deseado para que el espectador lo quiera. Pero empieza por el contraste: "
        "la pérdida actual por NO tenerlo, antes de revelar cómo se logra."
    ),
    "fear": (
        "El ángulo elegido es un MIEDO del cliente. Tu objetivo es activar ese miedo de forma "
        "concreta, con un escenario específico, no abstracto. Mientras más visceral y cercano, "
        "mejor detendrá el scroll."
    ),
    "story": (
        "El ángulo elegido es una HISTORIA real del negocio. Tu objetivo es contarla con un "
        "arco emocional: situación → tensión → decisión → desenlace → moraleja. "
        "Es la historia la que carga el mensaje. No es un dolor del cliente — es un momento "
        "del negocio que demuestra carácter, aprendizaje o valor. El hook puede ser una "
        "confesión, una contradicción o un titular sorprendente sobre la historia."
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
        "Eres un copywriter experto en contenido orgánico y publicitario para Instagram en español, "
        "con foco en RETENCIÓN y SCROLL-STOPPING, no en claridad informativa.",
        "Generas textos listos para publicar, sin meta-comentarios, sin explicaciones, sin disclaimers.",
        "NO escribes frases como 'Aquí tienes', 'Espero te sirva' o similares.",
        "",
        "PRINCIPIOS QUE DEBES SEGUIR SIEMPRE:",
        "- Primero el dolor o la pérdida concreta. Después el contexto. Nunca al revés.",
        "- Cifras de dinero específicas siempre vencen a descripciones abstractas. "
        "'$2,500 → $3,200' impacta más que 'cargos sorpresa'.",
        "- Frases cortas. Una idea por línea. Ritmo de Reel.",
        "- El culpable debe ser identificable: 'la industria de paqueteros tradicionales', "
        "'el sistema de cotización opaco', no 'las situaciones inesperadas'.",
        "- Contraste emocional: el dolor debe ser visceral, la solución debe ser un alivio sentido.",
        "- Optimizas para que el espectador piense 'no sabía eso', 'eso me podría pasar' o "
        "'eso ya me pasó' — NO para que aprenda algo nuevo intelectualmente.",
        "",
        "REGLAS DE INSTRUCCIONES DEL USUARIO:",
        "- Si el usuario te da una IDEA O CONTEXTO ADICIONAL, debes incorporarla LITERALMENTE.",
        "- Si esa idea contiene un CTA específico (ej. 'comenta la palabra X y te enviamos info'), "
        "ese CTA debe aparecer textualmente al final, sin reformularlo.",
        "- Si menciona una promoción, fecha, palabra clave o cifra concreta, debe aparecer textualmente.",
        "",
        "CONTEXTO DEL NEGOCIO PARA EL QUE ESCRIBES (este es el negocio principal, "
        "el contenido suena a su voz y resuelve sus objetivos):",
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
    pain_category: str,
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
    framing = CATEGORY_FRAMING.get(pain_category, CATEGORY_FRAMING["pain"])

    category_labels = {
        "pain": "DOLOR",
        "desire": "DESEO",
        "fear": "MIEDO",
        "story": "HISTORIA REAL DEL NEGOCIO",
    }
    cat_label = category_labels.get(pain_category, "DOLOR")

    parts = [
        f"ÁNGULO A USAR ({cat_label}): {pain_label}.",
        f"Detalle del ángulo: {pain_description or '—'}",
        "",
        f"CÓMO USAR ESTE ÁNGULO: {framing}",
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
            "o cualquier dato específico, DEBE aparecer textualmente en el contenido final.",
        ])

    if variation:
        parts.extend([
            "",
            "Esta es una REGENERACIÓN: ofrece un ángulo claramente distinto al que daría "
            "una primera versión obvia. Cambia el hook, el enfoque, el ejemplo o la metáfora — "
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
    pain_category: str = "pain",
    format_id: str,
    format_label: str,
    hook_label: str = "",
    hook_instruction: str = "",
    extra_idea: str = "",
    variation: bool = False,
) -> tuple[str, str]:
    system = _build_system_prompt(business_context, reference_contexts)
    user_msg = _build_user_prompt(
        pain_label, pain_description, pain_category,
        format_id, format_label,
        hook_label, hook_instruction, extra_idea, variation,
    )
    temperature = 1.0 if variation else 0.85

    if format_id == "guion_video":
        model = settings.anthropic_model_guion
        max_tokens = 2048
    else:
        model = settings.anthropic_model
        max_tokens = settings.anthropic_max_tokens

    try:
        response = _client.messages.create(
            model=model,
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
    content = "\n".join(text_parts).strip()
    return content, model


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
