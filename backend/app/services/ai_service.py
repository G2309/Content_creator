from __future__ import annotations

import json
import logging
import re

import anthropic

from app.config import get_settings
from app.models import BusinessContext
from app.structures import structures_block

logger = logging.getLogger(__name__)
settings = get_settings()

_client = anthropic.Anthropic(
    api_key=settings.anthropic_api_key,
    timeout=settings.anthropic_timeout_seconds,
)


GUION_VIDEO_INSTRUCTION = (
    "Genera un GUION para Reel o video corto de Instagram. Duración objetivo: 1 a 3 minutos "
    "hablados (entre 200 y 450 palabras). Si te queda menos de 200, sigue desarrollando.\n\n"
    "REGLAS DE PACING (Instagram premia la rapidez emocional):\n"
    "- Frases CORTAS, ritmo Reel. Sin párrafos largos ni subordinadas. Una idea por línea.\n"
    "- Cada frase debe hacer avanzar el guion. Si una frase se puede borrar sin perder nada, bórrala.\n"
    "- Cifras concretas siempre vencen a descripciones abstractas.\n"
    "- El 'culpable' debe ser identificable: una práctica común, el sistema, un tipo de proveedor. "
    "Nunca una situación abstracta e impersonal.\n\n"
    "ARQUITECTURA OBLIGATORIA DEL REEL — marca cada sección con su nombre en MAYÚSCULAS.\n"
    "Las siete secciones van en este orden:\n\n"
    "INTERRUPCIÓN:\n"
    "Una sola línea que rompa el scroll en menos de 3 segundos. Sigue ESTRICTAMENTE la "
    "instrucción del tipo de gancho elegido. No es una introducción: es un golpe.\n\n"
    "PROMESA:\n"
    "Una o dos líneas. La razón para quedarse. El espectador debe entender que si sigue viendo "
    "va a descubrir algo. Tipo: 'y aquí está el problema' o 'te voy a mostrar qué puede pasar'.\n\n"
    "TENSIÓN:\n"
    "Aquí NO entregues todavía la respuesta. Construye presión con información incompleta, "
    "preguntas, contrastes o revelaciones progresivas. Frases cortas y secuenciales, cada una "
    "subiendo la apuesta. Esta sección es la que decide si el espectador llega al final.\n\n"
    "DESARROLLO (el núcleo, 40-50% del texto):\n"
    "Explica solo lo necesario para sostener UNA idea central. Sin tecnicismos innecesarios, "
    "sin repetir lo ya dicho. Cada frase avanza la historia.\n\n"
    "PRUEBA:\n"
    "Demuestra lo que afirmaste. Indica qué evidencia concreta se muestra en cámara: una foto, "
    "el inventario, la app, la bodega, un caso real, un testimonio. "
    "No digas 'tenemos control': enseña cómo se ve el control. "
    "Si no hay evidencia visual posible, usa un caso concreto y específico.\n\n"
    "RESOLUCIÓN:\n"
    "El espectador sale con una comprensión nueva más una salida. Es el cambio de creencia "
    "hecho explícito, en dos o tres líneas.\n\n"
    "CTA:\n"
    "Una línea final accionable, coherente con el objetivo elegido. "
    "Si el usuario dio un CTA o una palabra clave específica, úsalo literal.\n\n"
    "RETENCIÓN: cada pocos segundos debe aparecer al menos uno de estos elementos — información "
    "nueva, una pregunta, un contraste, una consecuencia, una revelación o una promesa pendiente. "
    "Si un tramo del guion no tiene ninguno, reescríbelo."
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
    "objection": (
        "El ángulo elegido es una OBJECIÓN que frena la compra. Tu objetivo es desarmarla "
        "sin sonar defensivo. Nómbrala tal como la diría el cliente, dale la razón en lo que "
        "tenga de válida, y después muestra lo que no está viendo."
    ),
    "myth": (
        "El ángulo elegido es un MITO que la audiencia da por cierto. Tu objetivo es "
        "desmontarlo. Enuncia la creencia como si la compartieras, y luego contradícela con "
        "un hecho concreto. El giro debe sentirse como una revelación, no como un regaño."
    ),
    "mistake": (
        "El ángulo elegido es un ERROR COMÚN. Tu objetivo es que el espectador se reconozca "
        "cometiéndolo. Descríbelo con detalle específico para que piense 'eso hago yo', "
        "y después muestra la consecuencia y la corrección."
    ),
    "question": (
        "El ángulo elegido es una PREGUNTA FRECUENTE. Tu objetivo es responderla mejor que "
        "nadie. Responde primero y explica después. Nada de rodeos previos: la respuesta va "
        "en las primeras líneas y el resto la sustenta."
    ),
    "opportunity": (
        "El ángulo elegido es una OPORTUNIDAD que el espectador se está perdiendo. "
        "Tu objetivo es que sienta el costo de no aprovecharla. Sé concreto sobre qué está "
        "dejando sobre la mesa y qué haría falta para tomarla."
    ),
    "case": (
        "El ángulo elegido es un CASO REAL. Tu objetivo es que funcione como prueba. "
        "Cuenta qué pasó con detalle específico — cifras, tiempos, qué se hizo — y cierra con "
        "el principio que deja. La credibilidad está en el detalle, no en el adjetivo."
    ),
}


def _context_lines(ctx: BusinessContext, label: str, full: bool = False) -> list[str]:
    """Bloque de contexto. `full` agrega marca y audiencia — solo para el negocio principal."""
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

    if full:
        if ctx.positioning.strip():
            lines.append(f"- Posicionamiento: {ctx.positioning.strip()}")
        if ctx.transformation_before.strip() or ctx.transformation_after.strip():
            lines.append(
                f"- Transformación que provoca: de [{ctx.transformation_before.strip() or '—'}] "
                f"a [{ctx.transformation_after.strip() or '—'}]"
            )
        if ctx.differentiators.strip():
            lines.append(f"- Diferenciadores reales: {ctx.differentiators.strip()}")
        if ctx.emotional_promise.strip():
            lines.append(f"- Promesa emocional: {ctx.emotional_promise.strip()}")
        if ctx.brand_concept.strip():
            lines.append(f"- Concepto de marca: {ctx.brand_concept.strip()}")

    lines.append(f"=== FIN {label} ===")
    return lines


def _beliefs_block(ctx: BusinessContext) -> list[str]:
    creencias = [b.strip() for b in ctx.beliefs.splitlines() if b.strip()]
    if not creencias:
        return []
    lines = [
        "",
        "CREENCIAS QUE EL CONTENIDO DEBE INSTALAR:",
        "Cada pieza debe empujar UNA de estas creencias. No las enuncies textualmente — "
        "haz que el espectador llegue solo a esa conclusión.",
    ]
    lines.extend(f"{i}. {c}" for i, c in enumerate(creencias, 1))
    return lines


def _audience_block(ctx: BusinessContext) -> list[str]:
    if not ctx.avatar.strip() and not ctx.anti_avatar.strip():
        return []
    lines = ["", "AUDIENCIA:"]
    if ctx.avatar.strip():
        lines.append(f"- Le escribes a: {ctx.avatar.strip()}")
    if ctx.anti_avatar.strip():
        lines.append(
            f"- NO le escribes a: {ctx.anti_avatar.strip()}. "
            "No optimices el contenido para este perfil ni intentes complacerlo. "
            "Si un argumento solo le sirve a él, quítalo."
        )
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
        ctx.positioning.strip(),
        ctx.transformation_before.strip(),
        ctx.transformation_after.strip(),
        ctx.differentiators.strip(),
        ctx.emotional_promise.strip(),
        ctx.brand_concept.strip(),
        ctx.beliefs.strip(),
        ctx.avatar.strip(),
        ctx.anti_avatar.strip(),
    ])

    if has_primary_data:
        parts.extend(_context_lines(ctx, "NEGOCIO PRINCIPAL", full=True))
        parts.extend(_beliefs_block(ctx))
        parts.extend(_audience_block(ctx))
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
    objective: dict | None = None,
    pillar: dict | None = None,
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
        "objection": "OBJECIÓN",
        "myth": "MITO",
        "mistake": "ERROR COMÚN",
        "question": "PREGUNTA FRECUENTE",
        "opportunity": "OPORTUNIDAD",
        "case": "CASO REAL",
    }
    cat_label = category_labels.get(pain_category, "DOLOR")

    parts = [
        f"ÁNGULO A USAR ({cat_label}): {pain_label}.",
        f"Detalle del ángulo: {pain_description or '—'}",
        "",
        f"CÓMO USAR ESTE ÁNGULO: {framing}",
    ]

    if objective:
        parts.extend([
            "",
            f"OBJETIVO DE ESTE CONTENIDO: {objective['label']}.",
            objective["instruction"],
        ])

    if pillar:
        parts.extend([
            "",
            f"PILAR DE CONTENIDO: {pillar['label']} — {pillar['description']}",
            pillar["instruction"],
        ])

    parts.extend(["", f"FORMATO: {instruction}"])

    if format_id == "guion_video":
        parts.extend(["", structures_block()])

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
    objective: dict | None = None,
    pillar: dict | None = None,
) -> tuple[str, str]:
    system = _build_system_prompt(business_context, reference_contexts)
    user_msg = _build_user_prompt(
        pain_label, pain_description, pain_category,
        format_id, format_label,
        hook_label, hook_instruction, extra_idea, variation,
        objective=objective, pillar=pillar,
    )

    kwargs: dict = {"system": system, "messages": [{"role": "user", "content": user_msg}]}

    if format_id == "guion_video":
        # Sonnet 5: razona antes de escribir. Rechaza temperature con 400, así que
        # la variedad entre versiones se pide por prompt (flag `variation`).
        # max_tokens cubre razonamiento + texto, por eso es holgado.
        kwargs["model"] = settings.anthropic_model_guion
        kwargs["max_tokens"] = settings.anthropic_max_tokens_guion
        kwargs["thinking"] = {"type": "adaptive"}
    else:
        # Haiku 4.5 para formatos cortos: no soporta thinking adaptativo.
        kwargs["model"] = settings.anthropic_model
        kwargs["max_tokens"] = settings.anthropic_max_tokens
        kwargs["temperature"] = 1.0 if variation else 0.85

    try:
        response = _client.messages.create(**kwargs)
    except anthropic.APITimeoutError as e:
        logger.warning("Anthropic timeout: %s", e)
        raise
    except anthropic.APIError as e:
        logger.exception("Anthropic API error: %s", e)
        raise

    text_parts = [block.text for block in response.content if block.type == "text"]
    content = "\n".join(text_parts).strip()
    return content, kwargs["model"]


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
