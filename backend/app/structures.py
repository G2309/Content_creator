"""Estructuras narrativas reutilizables (Arquitectura Maestra 2.0, Nivel VII).

La IA elige una según el ángulo y el objetivo; no es un selector del usuario.
Todas se acomodan dentro de la arquitectura madre del reel.
"""

NARRATIVE_STRUCTURES = [
    {
        "id": "problema",
        "label": "Problema",
        "flow": "PROBLEMA → CURIOSIDAD → CONSECUENCIA → EXPLICACIÓN → SOLUCIÓN",
        "when": "el ángulo es un dolor o un miedo y la audiencia aún no dimensiona el riesgo",
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
        "flow": "CREENCIA → CONTRADICCIÓN → EVIDENCIA → EXPLICACIÓN → NUEVA CREENCIA",
        "when": "hay una creencia equivocada que conviene desmontar con evidencia",
    },
    {
        "id": "demostracion",
        "label": "Demostración",
        "flow": "RESULTADO → PRUEBA → EXPLICACIÓN → IMPLICACIÓN",
        "when": "se puede mostrar algo en cámara: un proceso, la app, la bodega, una verificación",
    },
    {
        "id": "autoridad",
        "label": "Autoridad",
        "flow": "EXPERIENCIA → APRENDIZAJE → PRINCIPIO → CONSEJO",
        "when": "el ángulo es marca personal o se busca construir credibilidad",
    },
    {
        "id": "conversion",
        "label": "Conversión",
        "flow": "PROBLEMA → COSTO → SOLUCIÓN → DIFERENCIADOR → EVIDENCIA → CTA",
        "when": "el objetivo es que escriban o contraten, o el ángulo es una objeción",
    },
    {
        "id": "open_loop",
        "label": "Open loop",
        "flow": "RESULTADO → PREGUNTA → PISTAS → EXPLICACIÓN → REVELACIÓN",
        "when": "quieres máxima retención: abres con el desenlace y lo explicas al final",
    },
    {
        "id": "antes_despues",
        "label": "Antes / después",
        "flow": "ANTES → FRICCIÓN → CAMBIO → DESPUÉS → APRENDIZAJE",
        "when": "el ángulo es un deseo o una transformación concreta",
    },
    {
        "id": "pov_operativo",
        "label": "POV operativo",
        "flow": "SITUACIÓN → DECISIÓN → ACCIÓN → RESULTADO → EXPLICACIÓN",
        "when": "puedes narrar desde dentro de la operación, en primera persona",
    },
    {
        "id": "mito_realidad",
        "label": "Mito vs. realidad",
        "flow": "CREENCIA → CONTRADICCIÓN → EVIDENCIA → REALIDAD → IMPLICACIÓN",
        "when": "el ángulo es un mito o un error común muy extendido",
    },
]


def structures_block() -> str:
    lines = [
        "ESTRUCTURAS NARRATIVAS — elige UNA, la que mejor cuente esta idea, "
        "y desarróllala dentro de la arquitectura del reel:",
        "",
    ]
    for s in NARRATIVE_STRUCTURES:
        lines.append(f"- {s['label']}: {s['flow']}")
        lines.append(f"  Úsala cuando {s['when']}.")
    lines.extend([
        "",
        "No menciones el nombre de la estructura dentro del guion; solo síguela por dentro. "
        "Sí debes declararla en la ficha final.",
    ])
    return "\n".join(lines)
