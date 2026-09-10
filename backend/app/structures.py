"""Estructuras narrativas reutilizables (Nivel IV de la Arquitectura Maestra).

La IA elige una según el ángulo y el objetivo; no es un selector del usuario.
Todas se acomodan dentro de la arquitectura madre del reel.
"""

NARRATIVE_STRUCTURES = [
    {
        "id": "problema",
        "label": "Problema",
        "flow": "PROBLEMA → CURIOSIDAD → CONSECUENCIA → EXPLICACIÓN → SOLUCIÓN",
        "when": "el ángulo es un dolor o un miedo, y la audiencia aún no dimensiona el riesgo",
    },
    {
        "id": "caso_real",
        "label": "Caso real",
        "flow": "SITUACIÓN → PROBLEMA → DESCUBRIMIENTO → ACCIÓN → RESULTADO → APRENDIZAJE",
        "when": "el ángulo es una historia o un caso del negocio",
    },
    {
        "id": "contracorriente",
        "label": "Contracorriente",
        "flow": "CREENCIA → CONTRADICCIÓN → EXPLICACIÓN → EVIDENCIA → NUEVA CREENCIA",
        "when": "el ángulo es un mito o una creencia equivocada que hay que desmontar",
    },
    {
        "id": "demostracion",
        "label": "Demostración",
        "flow": "PROMESA → PRUEBA → EXPLICACIÓN → RESULTADO → CTA",
        "when": "se puede mostrar algo en cámara: un proceso, la app, la bodega, una verificación",
    },
    {
        "id": "autoridad",
        "label": "Autoridad",
        "flow": "EXPERIENCIA → PROBLEMA → APRENDIZAJE → PRINCIPIO → CONSEJO",
        "when": "el ángulo es marca personal o se busca construir credibilidad",
    },
    {
        "id": "conversion",
        "label": "Conversión",
        "flow": "PROBLEMA → COSTO → SOLUCIÓN → DIFERENCIADOR → PRUEBA → CTA",
        "when": "el objetivo es que escriban o contraten, o el ángulo es una objeción",
    },
]


def structures_block() -> str:
    lines = [
        "ESTRUCTURAS NARRATIVAS DISPONIBLES — elige UNA, la que mejor sirva al ángulo "
        "y al objetivo, y desarróllala dentro de la arquitectura del reel:",
        "",
    ]
    for s in NARRATIVE_STRUCTURES:
        lines.append(f"- {s['label']}: {s['flow']}")
        lines.append(f"  Úsala cuando {s['when']}.")
    lines.extend([
        "",
        "No menciones el nombre de la estructura en el guion. Solo síguela por dentro.",
    ])
    return "\n".join(lines)
