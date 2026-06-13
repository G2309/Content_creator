"""Dependencias compartidas de FastAPI (auth, db)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

# tokenUrl es informativo para docs — apuntamos a nuestro endpoint real
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Solo permite el paso a usuarios con is_admin=True."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción requiere permisos de administrador.",
        )
    return current_user


def get_current_user_unrestricted(current_user: User = Depends(get_current_user)) -> User:
    """Igual que get_current_user, pero pasa también si must_change_password=True.

    Se usa SOLO en el endpoint de cambio de contraseña, que es la única acción
    permitida mientras el usuario tenga la contraseña temporal pendiente.
    """
    return current_user


def get_current_user_active(current_user: User = Depends(get_current_user)) -> User:
    """get_current_user + bloquea si el usuario debe cambiar la contraseña.

    Esta es la dependencia "por defecto" para endpoints que requieren un usuario
    en estado normal. Fuerza al frontend a redirigir a /cambiar-password antes
    de poder hacer otra cosa.
    """
    if current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes cambiar tu contraseña antes de continuar.",
        )
    return current_user
