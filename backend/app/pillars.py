PILLARS = [
    {
        "id": "problemas_invisibles",
        "label": "Problemas invisibles",
        "description": "Lo que puede salir mal y el cliente no está considerando.",
        "topics": "daños, faltantes, productos equivocados, errores de dirección, problemas durante el proceso",
        "instruction": (
            "Haz visible un riesgo que el espectador no está considerando. "
            "El contenido debe provocar 'nunca había pensado en eso'. "
            "No adviertas en abstracto: nombra el escenario concreto y su consecuencia."
        ),
    },
    {
        "id": "dinero",
        "label": "Dinero y rentabilidad",
        "description": "El costo real no siempre es el precio anunciado.",
        "topics": "comisiones, membresías, costos ocultos, consolidación, margen, precio por libra",
        "instruction": (
            "Demuestra que el costo real difiere del precio anunciado. "
            "Usa cifras concretas siempre que puedas — una comparación numérica "
            "vale más que cualquier adjetivo."
        ),
    },
    {
        "id": "control",
        "label": "Control y visibilidad",
        "description": "Por qué el cliente necesita saber qué pasa con sus compras.",
        "topics": "fotografías, inventario, notificaciones, seguimiento, verificación, tecnología",
        "instruction": (
            "Muestra la diferencia entre saber y no saber qué está pasando. "
            "No digas 'tenemos control': enseña cómo se ve el control."
        ),
    },
    {
        "id": "educacion",
        "label": "Educación",
        "description": "Convertir conocimiento especializado en contenido útil y sencillo.",
        "topics": "cómo importar, cómo comprar, cómo elegir proveedor, aduana, costos, errores comunes",
        "instruction": (
            "Enseña algo aplicable hoy. Una sola idea, explicada de forma que "
            "alguien sin experiencia la entienda al primer intento."
        ),
    },
    {
        "id": "autoridad",
        "label": "Autoridad y evidencia",
        "description": "Demostrar que la marca sabe lo que ocurre detrás del proceso.",
        "topics": "casos reales, procesos, detrás de cámaras, problemas resueltos, operación real",
        "instruction": (
            "Apóyate en evidencia concreta: un caso, un proceso, algo que se pueda "
            "mostrar en cámara. La autoridad se demuestra, no se declara."
        ),
    },
    {
        "id": "marca_personal",
        "label": "Marca personal",
        "description": "Humanizar la autoridad y construir conexión.",
        "topics": "experiencias, aprendizajes, opiniones, decisiones, errores, filosofía, día a día",
        "instruction": (
            "Habla en primera persona desde una experiencia real. "
            "Puede ser un error, una decisión difícil o una opinión con la que no todos "
            "estarán de acuerdo. La conexión viene de la honestidad, no de la perfección."
        ),
    },
]


def get_pillar_by_id(pillar_id: str) -> dict | None:
    return next((p for p in PILLARS if p["id"] == pillar_id), None)
