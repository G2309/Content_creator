"""Crea el usuario admin inicial si la BD está vacía.

Se ejecuta una sola vez al arranque. No expone endpoint de registro — el único
modo de tener una primera cuenta es definir ADMIN_EMAIL/ADMIN_PASSWORD en
variables de entorno. Después, los demás usuarios los crea el admin desde la UI.
"""
import logging

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import BusinessContext, User
from app.security import hash_password

logger = logging.getLogger(__name__)


def seed_admin_user(db: Session) -> None:
    settings = get_settings()

    existing = db.query(User).first()
    if existing:
        logger.info("Ya existe al menos un usuario — seed omitido.")
        return

    email = settings.admin_email.lower().strip()
    password = settings.admin_password

    if not email or not password:
        logger.warning(
            "ADMIN_EMAIL / ADMIN_PASSWORD no están definidos — no se creó usuario inicial."
        )
        return

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        is_admin=True,             # el primer usuario siempre es admin
        must_change_password=False,  # tú la definiste, no necesitas cambiarla
    )
    db.add(user)
    db.flush()  # obtener user.id sin commit aún

    db.add(BusinessContext(user_id=user.id))
    db.commit()

    logger.info("Usuario admin creado: %s", email)
