HOOK_TYPES = [
    {
        "id": "problema",
        "label": "Problema",
        "description": "Se enfoca en un dolor específico del cliente.",
        "instruction": (
            "Empieza con UNA línea que nombre un dolor concreto y específico del cliente. "
            "Tipo: '¿Te ha pasado que...?' o 'El mayor error al... no ocurre cuando...'. "
            "Que la persona se sienta identificada en los primeros 2 segundos."
        ),
    },
    {
        "id": "curiosidad",
        "label": "Curiosidad",
        "description": "Deja una pregunta sin responder, genera misterio.",
        "instruction": (
            "Empieza con UNA línea que insinúe algo poco conocido sin revelarlo. "
            "Tipo: 'Descubrí algo que casi nadie revisa antes de...' o "
            "'Hay una razón por la que algunas personas nunca tienen problemas con...'. "
            "Debe obligar a quedarse a saber qué es."
        ),
    },
    {
        "id": "contra_corriente",
        "label": "Contra corriente",
        "description": "Va en contra de lo que todos creen.",
        "instruction": (
            "Empieza con UNA línea que contradiga la creencia común del público. "
            "Tipo: 'No necesitas X.' o 'Comprar en línea no es la parte difícil.'. "
            "Debe sonar provocador pero honesto."
        ),
    },
    {
        "id": "error",
        "label": "Error común",
        "description": "Señala una equivocación que mucha gente comete.",
        "instruction": (
            "Empieza con UNA línea que apunte directamente a un error que el espectador podría estar cometiendo. "
            "Tipo: 'Estás usando X de la forma incorrecta.' o "
            "'Este error puede hacer que tu envío te cueste más.'. "
            "Debe poner al espectador en alerta."
        ),
    },
    {
        "id": "advertencia",
        "label": "Advertencia",
        "description": "Genera urgencia, alerta sobre algo a tiempo.",
        "instruction": (
            "Empieza con UNA línea de advertencia urgente, en imperativo. "
            "Tipo: 'No envíes nada a México sin revisar esto primero.' o "
            "'Ojalá alguien me hubiera dicho esto antes de...'. "
            "Debe transmitir que ignorarlo tiene consecuencias."
        ),
    },
    {
        "id": "secreto",
        "label": "Secreto",
        "description": "Promete información poco conocida, exclusiva.",
        "instruction": (
            "Empieza con UNA línea que ofrezca conocimiento privilegiado. "
            "Tipo: 'El secreto para evitar...' o 'Lo que las personas con experiencia revisan antes de...'. "
            "Sin clichés tipo 'lo que no quieren que sepas'."
        ),
    },
    {
        "id": "lista",
        "label": "Lista",
        "description": "Promete información rápida y concreta en bullets.",
        "instruction": (
            "Empieza con UNA línea que anuncie un número específico de puntos. "
            "Tipo: '3 errores que encarecen tus envíos.' o "
            "'5 cosas que debes revisar antes de comprar en línea.'. "
            "Después del hook, el cuerpo debe efectivamente listar esos puntos."
        ),
    },
    {
        "id": "historia",
        "label": "Historia real",
        "description": "Empieza con una situación concreta que pasó.",
        "instruction": (
            "Empieza con UNA línea que abra una historia real, breve y específica. "
            "Tipo: 'Un cliente recibió una sorpresa desagradable cuando...' o "
            "'Hace unos días una persona me llamó muy preocupada por...'. "
            "Debe sentirse anecdótica, no teórica. El resto del guion desarrolla y cierra esa historia."
        ),
    },
    {
        "id": "resultado",
        "label": "Resultado",
        "description": "Muestra el beneficio primero, atrae con la promesa.",
        "instruction": (
            "Empieza con UNA línea que prometa el resultado deseado de forma directa. "
            "Tipo: 'Así puedes evitar cargos inesperados en tus envíos.' o "
            "'Cómo recibir tus compras en México con mayor tranquilidad.'. "
            "Promete claro, después el cuerpo explica el cómo."
        ),
    },
    {
        "id": "polemica",
        "label": "Polémica",
        "description": "Genera debate, opinión fuerte.",
        "instruction": (
            "Empieza con UNA línea que provoque debate o emita una opinión fuerte. "
            "Tipo: 'La mayoría de los casilleros no tienen el problema que crees.' o "
            "'El precio más barato puede salirte más caro.'. "
            "Que invite a estar de acuerdo o en desacuerdo, no a la indiferencia."
        ),
    },
    {
        "id": "confesion",
        "label": "Confesión",
        "description": "Humaniza al narrador, conecta por vulnerabilidad.",
        "instruction": (
            "Empieza con UNA línea en primera persona que admita algo. "
            "Tipo: 'No soy experto grabando videos.' o 'Cometí este error cuando empecé en la paquetería.'. "
            "Debe sentirse honesto y bajar la guardia del espectador."
        ),
    },
    {
        "id": "pregunta",
        "label": "Pregunta directa",
        "description": "Invita a que la audiencia se identifique y responda.",
        "instruction": (
            "Empieza con UNA pregunta directa al espectador que lo obligue a pensar en su propia situación. "
            "Tipo: '¿Cuánto dinero has perdido por cargos sorpresa?' o '¿Confías en tu PoBox actual?'. "
            "Que sea específica, no genérica."
        ),
    },
    {
        "id": "pov",
        "label": "Punto de vista (POV)",
        "description": "Posicionamiento fuerte sobre el tema.",
        "instruction": (
            "Empieza con UNA línea que tome posición de forma marcada, casi como un manifiesto. "
            "Tipo: 'Voy a decir algo que a los PoBoxes tradicionales no les va a gustar.' o "
            "'Hasta que viste todos los cargos extras para recibirlo en México.'. "
            "Es un anuncio de postura, no una pregunta."
        ),
    },
]


def get_hook_by_id(hook_id: str) -> dict | None:
    return next((h for h in HOOK_TYPES if h["id"] == hook_id), None)
