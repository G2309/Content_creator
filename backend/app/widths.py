"""Anchura de audiencia (Arquitectura Maestra 2.0, Nivel II-4).

Se define antes de escribir el hook y determina cuánto conocimiento previo
asume el contenido. Es independiente del funnel: puede haber contenido de
descubrimiento amplio, relacionado o específico.

Solo se ofrece con objetivos de descubrimiento y seguidores; en autoridad y
conversión la audiencia ya conoce la categoría.
"""

AUDIENCE_WIDTHS = [
    {
        "id": "amplio",
        "label": "Amplio",
        "description": "Para que lo entienda cualquiera, aunque no compre en Estados Unidos.",
        "example": "Lo barato puede convertirse en lo más caro.",
        "instruction": (
            "ANCHURA AMPLIA. El contenido NO debe requerir que la persona piense en casilleros, "
            "importaciones ni logística para engancharse.\n"
            "- El hook y la tensión deben funcionar para cualquiera, sobre un principio general "
            "(dinero, confianza, decisiones, riesgo).\n"
            "- La categoría puede aparecer, pero solo después de que el interés ya esté ganado — "
            "nunca en la interrupción.\n"
            "- No uses vocabulario del sector en las primeras líneas: nada de PO Box, casillero, "
            "consolidación, aduana ni arancel.\n"
            "- Objetivo: máximo alcance y descubrimiento."
        ),
    },
    {
        "id": "relacionado",
        "label": "Relacionado",
        "description": "Para quien compra o revende, aunque no conozca el servicio.",
        "example": "Si compras productos para revender, hay costos que destruyen tu margen.",
        "instruction": (
            "ANCHURA RELACIONADA. Le hablas a alguien con contexto comercial pero que no "
            "necesariamente conoce la categoría.\n"
            "- Puedes dar por hecho que compra, revende o maneja mercancía.\n"
            "- NO des por hecho que usa un casillero ni que conoce el proceso de importación.\n"
            "- Explica cualquier término del sector la primera vez que lo uses.\n"
            "- Objetivo: atraer personas compatibles con el avatar."
        ),
    },
    {
        "id": "especifico",
        "label": "Específico",
        "description": "Para quien ya importa o usa un casillero.",
        "example": "Si usas un PO Box para comprar en Estados Unidos, revisa esto.",
        "instruction": (
            "ANCHURA ESPECÍFICA. Le hablas a alguien que ya está dentro de la categoría.\n"
            "- Puedes usar vocabulario del sector sin explicarlo.\n"
            "- Puedes entrar directo al detalle operativo.\n"
            "- Objetivo: relevancia y calificación, no alcance."
        ),
    },
]


def get_width_by_id(width_id: str) -> dict | None:
    return next((w for w in AUDIENCE_WIDTHS if w["id"] == width_id), None)


# Objetivos donde la anchura es una decisión relevante.
WIDTH_RELEVANT_OBJECTIVES = ("descubrimiento", "seguidores")
