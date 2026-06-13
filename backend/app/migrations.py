"""Migraciones forward-only ligeras.

`Base.metadata.create_all` solo CREA tablas que no existen. Si una tabla ya está
y le agregamos columnas en `models.py`, hay que aplicarlas con ALTER TABLE.

En Fase 2 conviene migrar a Alembic (que ya hace esto en serio, con rollback).
Para Fase 1 este helper es suficiente y evita romper despliegues existentes.
"""
from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def ensure_schema(engine: Engine, admin_email: str | None = None) -> None:
    """Aplica migraciones idempotentes. Se puede correr cualquier número de veces."""
    if engine.dialect.name != "postgresql":
        logger.warning(
            "Migraciones manuales asumen Postgres; dialecto detectado: %s — se omiten",
            engine.dialect.name,
        )
        return

    with engine.begin() as conn:
        # Verificar que la tabla users exista (la crea create_all en un primer arranque)
        users_exists = conn.execute(
            text(
                "SELECT to_regclass('public.users') IS NOT NULL"
            )
        ).scalar()
        if not users_exists:
            logger.info("Tabla users aún no existe — saltando migración")
            return

        # Añadir columnas nuevas si faltan (Postgres 9.6+)
        conn.execute(text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        conn.execute(text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE"
        ))

        # Promover al usuario admin (definido por ADMIN_EMAIL) si todavía no lo es.
        # Esto cubre el caso de despliegues existentes donde el seed ya corrió antes
        # de que existieran estos campos.
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

    logger.info("Migración de esquema aplicada (OK).")
