import logging

from sqlalchemy.orm import Session

from app.config import get_settings
from app.default_pains import DEFAULT_PAINS
from app.models import BusinessContext, CustomerPain, User
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
        is_admin=True,
        must_change_password=False,
    )
    db.add(user)
    db.flush()

    db.add(BusinessContext(user_id=user.id))
    for idx, pain_data in enumerate(DEFAULT_PAINS):
        db.add(CustomerPain(
            user_id=user.id,
            label=pain_data["label"],
            description=pain_data["description"],
            position=idx,
        ))

    db.commit()
    logger.info("Usuario admin creado: %s", email)
