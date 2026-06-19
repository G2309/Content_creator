from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.default_pains import DEFAULT_PAINS
from app.models import CustomerPain, User

logger = logging.getLogger(__name__)


def ensure_schema(engine: Engine, admin_email: str | None = None) -> None:
    if engine.dialect.name != "postgresql":
        logger.warning(
            "Migraciones manuales asumen Postgres; dialecto detectado: %s — se omiten",
            engine.dialect.name,
        )
        return

    with engine.begin() as conn:
        users_exists = conn.execute(
            text("SELECT to_regclass('public.users') IS NOT NULL")
        ).scalar()
        if not users_exists:
            logger.info("Tabla users aún no existe — saltando migración")
            return

        conn.execute(text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        conn.execute(text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE"
        ))

        if admin_email:
            result = conn.execute(
                text(
                    "UPDATE users SET is_admin = TRUE "
                    "WHERE LOWER(email) = LOWER(:email) AND is_admin = FALSE"
                ),
                {"email": admin_email},
            )
            if result.rowcount > 0:
                logger.info("Usuario admin existente promovido: %s", admin_email)

    logger.info("Migración de esquema aplicada.")


def seed_default_pains_for_existing_users(db: Session) -> None:
    users_without_pains = (
        db.query(User)
        .outerjoin(CustomerPain, CustomerPain.user_id == User.id)
        .filter(CustomerPain.id.is_(None))
        .all()
    )

    for user in users_without_pains:
        for idx, pain_data in enumerate(DEFAULT_PAINS):
            db.add(CustomerPain(
                user_id=user.id,
                label=pain_data["label"],
                description=pain_data["description"],
                position=idx,
            ))
        logger.info("Dolores por defecto sembrados para usuario %s", user.email)

    if users_without_pains:
        db.commit()
