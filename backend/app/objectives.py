"""Selector único de objetivo.

Una sola elección del usuario resuelve la etapa del funnel, el objetivo del
reel y el tipo de CTA. El nivel de consciencia se declara como RANGO, no como
equivalencia fija: la IA elige dentro del rango según el insight, porque funnel
y consciencia son variables independientes (Arquitectura 2.0, Nivel III).
"""

OBJECTIVES = [
    {
        "id": "descubrimiento",
        "label": "Que me descubra gente nueva",
        "description": "Para llegar a quien todavía no te conoce ni sabe que tiene el problema.",
        "funnel": "TOFU",
        "awareness_range": "Niveles 1 a 2",
        "goal": "Alcance",
        "metric": "Alcance, compartidos y retención inicial",
        "instruction": (
            "ETAPA DEL FUNNEL: TOFU (descubrimiento). Le hablas a alguien que NO te conoce.\n"
            "- CONSCIENCIA: elige tú el nivel entre 1 y 2 según el insight. Nivel 1 si la persona "
            "no sabe que el problema existe ('no sabía que esto podía pasar'); nivel 2 si ya lo "
            "siente pero no lo ha nombrado ('sí, esto me pasa'). Declara en la ficha cuál usaste.\n"
            "- Da por hecho CERO contexto previo sobre el negocio: no menciones su nombre hasta el CTA.\n"
            "- El pensamiento que buscas es: 'esto me llamó la atención' o 'no lo había visto así'.\n"
            "- Prioriza que sea compartible: algo que alguien le reenviaría a un conocido.\n"
            "- NO vendas. Ni una mención de tarifas, planes o por qué eres mejor.\n"
            "- CTA de bajo compromiso: compartir o comentar. Nunca pidas que escriban por privado."
        ),
    },
    {
        "id": "seguidores",
        "label": "Que me sigan",
        "description": "Para convertir a quien te vio una vez en alguien que te sigue.",
        "funnel": "TOFU",
        "awareness_range": "Niveles 1 a 3",
        "goal": "Seguidores",
        "metric": "Seguidores ganados y visitas al perfil",
        "instruction": (
            "ETAPA DEL FUNNEL: TOFU, con objetivo de SEGUIDORES. Le hablas a alguien que acaba "
            "de descubrirte y tiene que decidir si vale la pena seguirte.\n"
            "- CONSCIENCIA: elige el nivel entre 1 y 3 según el insight y decláralo en la ficha.\n"
            "- La clave es dejar clara la PROMESA DE LA CUENTA: que se note que aquí va a seguir "
            "aprendiendo cosas así. Este contenido debe sentirse como el primero de una serie.\n"
            "- Entrega valor completo en este reel — nada de 'sígueme y te cuento'. "
            "Se sigue a quien ya dio algo, no a quien lo promete.\n"
            "- NO vendas nada. Un CTA comercial aquí es la razón principal por la que la gente "
            "no sigue una cuenta.\n"
            "- CTA de seguimiento, conectado al tema: invita a seguir para más contenido de este "
            "tipo, nombrando el tipo. Ej: 'sígueme si compras en Estados Unidos'."
        ),
    },
    {
        "id": "confianza",
        "label": "Que confíen en que sé de esto",
        "description": "Para quien ya reconoce el problema y evalúa cómo resolverlo.",
        "funnel": "MOFU",
        "awareness_range": "Niveles 2 a 3",
        "goal": "Autoridad",
        "metric": "Guardados, tiempo de visualización y visitas al perfil",
        "instruction": (
            "ETAPA DEL FUNNEL: MOFU (autoridad y confianza). Le hablas a alguien que YA reconoce "
            "el problema y está evaluando cómo resolverlo.\n"
            "- CONSCIENCIA: elige el nivel entre 2 y 3 y decláralo en la ficha.\n"
            "- El pensamiento que buscas es: 'esta persona realmente sabe de esto'.\n"
            "- Apóyate en evidencia: un caso real, un proceso, un detrás de cámaras, una comparación.\n"
            "- Muestra el cómo, no solo el qué. La credibilidad está en el detalle operativo.\n"
            "- CTA de guardado o de consumir el siguiente contenido. Todavía no pidas la venta."
        ),
    },
    {
        "id": "conversion",
        "label": "Que me escriban para contratar",
        "description": "Para quien ya te conoce y está a un paso de decidirse.",
        "funnel": "BOFU",
        "awareness_range": "Niveles 4 a 5",
        "goal": "Leads y conversión",
        "metric": "Mensajes recibidos, cotizaciones y clientes",
        "instruction": (
            "ETAPA DEL FUNNEL: BOFU (consideración y conversión). Le hablas a alguien que YA te "
            "conoce y está evaluando contratarte.\n"
            "- CONSCIENCIA: elige el nivel entre 4 y 5 y decláralo en la ficha.\n"
            "- Puedes hablar del servicio, de cómo funciona, de tarifas y de por qué eres distinto.\n"
            "- Resuelve una objeción concreta: la duda específica que lo tiene detenido.\n"
            "- Sé concreto sobre el siguiente paso: qué pasa exactamente después de que escriba.\n"
            "- CTA con palabra clave: pide que comenten o escriban una palabra específica. "
            "Si el usuario dio una palabra clave en su idea adicional, úsala literal."
        ),
    },
]


def get_objective_by_id(objective_id: str) -> dict | None:
    return next((o for o in OBJECTIVES if o["id"] == objective_id), None)
