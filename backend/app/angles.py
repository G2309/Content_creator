"""Ángulos de contenido (Arquitectura Maestra 2.0, Nivel V-7).

Una misma idea se convierte en varios contenidos cambiando el ángulo.
La IA elige el ángulo; cuando se generan varias versiones, cada una usa uno
distinto. No es un selector del usuario.
"""

ANGLES = [
    {"id": "problema", "label": "Problema", "example": "Esto puede salir mal."},
    {"id": "contracorriente", "label": "Contracorriente", "example": "Lo barato puede costarte más."},
    {"id": "curiosidad", "label": "Curiosidad", "example": "Hay algo que probablemente nadie está revisando."},
    {"id": "advertencia", "label": "Advertencia", "example": "Antes de hacer esto, revisa…"},
    {"id": "consecuencia", "label": "Consecuencia", "example": "Este error puede comerse tu margen."},
    {"id": "comparacion", "label": "Comparación", "example": "Recibir no es lo mismo que verificar."},
    {"id": "demostracion", "label": "Demostración", "example": "Mira lo que encontramos."},
    {"id": "historia", "label": "Historia", "example": "Esto ocurrió con un paquete."},
    {"id": "opinion", "label": "Opinión", "example": "Yo nunca haría esto."},
    {"id": "educacion", "label": "Educación", "example": "Así funciona realmente."},
    {"id": "revelacion", "label": "Revelación", "example": "Esto ocurre detrás de tu envío."},
    {"id": "error", "label": "Error", "example": "El error que veo constantemente…"},
    {"id": "mito", "label": "Mito", "example": "Pagar menos por libra no significa gastar menos."},
]


def angles_block(preferred: str = "") -> str:
    lines = ["ÁNGULOS DISPONIBLES (el ángulo es lo que hace interesante la idea):"]
    lines.extend(f"- {a['label']}: «{a['example']}»" for a in ANGLES)
    if preferred:
        lines.append("")
        lines.append(
            f"Para esta versión usa el ángulo: {preferred}. "
            "Declara en la ficha cuál usaste."
        )
    else:
        lines.append("")
        lines.append("Elige el ángulo que mejor sirva a la idea y decláralo en la ficha.")
    return "\n".join(lines)


def get_angle_by_id(angle_id: str) -> dict | None:
    return next((a for a in ANGLES if a["id"] == angle_id), None)
