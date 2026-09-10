"""Selector único de objetivo.

Una sola elección del usuario resuelve cuatro decisiones del sistema:
etapa del funnel, nivel de consciencia de la audiencia, objetivo del reel
y tipo de CTA. El usuario nunca ve esos cuatro campos.
"""

OBJECTIVES = [
    {
        "id": "descubrimiento",
        "label": "Que me descubra gente nueva",
        "description": "Para llegar a quien todavía no te conoce ni sabe que tiene el problema.",
        "funnel": "TOFU",
        "awareness": "Niveles 1 y 2 — no sabe que el problema existe, o apenas intuye que algo anda mal",
        "goal": "Alcance",
        "secondary_goal": "Seguidores",
        "instruction": (
            "ETAPA DEL FUNNEL: TOFU (descubrimiento). Le hablas a alguien que NO te conoce "
            "y que probablemente NO sabe que este problema existe.\n"
            "- Da por hecho CERO contexto previo: no menciones el nombre del negocio hasta el CTA, "
            "no asumas que conoce el servicio ni el vocabulario del sector.\n"
            "- El pensamiento que buscas provocar es: 'nunca había pensado en eso'.\n"
            "- Prioriza que sea compartible: algo que alguien le reenviaría a un conocido.\n"
            "- NO vendas. Ni una sola mención de tarifas, planes o por qué eres mejor.\n"
            "- CTA de bajo compromiso: guardar, compartir o comentar. "
            "Nunca pidas que escriban por privado ni que contraten."
        ),
    },
    {
        "id": "confianza",
        "label": "Que confíen en que sé de esto",
        "description": "Para quien ya reconoce el problema y está evaluando cómo resolverlo.",
        "funnel": "MOFU",
        "awareness": "Niveles 2 y 3 — reconoce el problema y entiende que necesita una solución mejor",
        "goal": "Autoridad",
        "secondary_goal": "Confianza",
        "instruction": (
            "ETAPA DEL FUNNEL: MOFU (autoridad y confianza). Le hablas a alguien que YA reconoce "
            "el problema y está evaluando cómo resolverlo.\n"
            "- El pensamiento que buscas provocar es: 'esta persona realmente sabe de esto'.\n"
            "- Apóyate en evidencia: un caso real, un proceso, un detrás de cámaras, una comparación.\n"
            "- Puedes usar vocabulario del sector; ya sabe de qué hablas.\n"
            "- Muestra el cómo, no solo el qué. La credibilidad está en el detalle operativo.\n"
            "- CTA de seguimiento: seguir la cuenta, guardar para después. "
            "Todavía no es momento de pedir la venta."
        ),
    },
    {
        "id": "conversion",
        "label": "Que me escriban para contratar",
        "description": "Para quien ya te conoce y está a un paso de decidirse.",
        "funnel": "BOFU",
        "awareness": "Niveles 4 y 5 — ya te conoce y está evaluando contratarte",
        "goal": "Leads",
        "secondary_goal": "Ventas",
        "instruction": (
            "ETAPA DEL FUNNEL: BOFU (consideración y conversión). Le hablas a alguien que YA te "
            "conoce y está evaluando contratarte.\n"
            "- El pensamiento que buscas provocar es: 'quiero que ellos se encarguen'.\n"
            "- Puedes hablar del servicio, de cómo funciona, de tarifas y de por qué eres distinto.\n"
            "- Resuelve una objeción concreta — la duda específica que lo tiene detenido.\n"
            "- Sé concreto sobre el siguiente paso: qué pasa exactamente después de que escriba.\n"
            "- CTA con palabra clave: pide que comenten o escriban una palabra específica. "
            "Si el usuario dio una palabra clave en su idea adicional, úsala literal."
        ),
    },
]


def get_objective_by_id(objective_id: str) -> dict | None:
    return next((o for o in OBJECTIVES if o["id"] == objective_id), None)
