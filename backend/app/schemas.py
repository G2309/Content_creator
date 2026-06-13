"""Esquemas Pydantic — validación de entrada y forma de las respuestas."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------- Auth ----------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # segundos
    must_change_password: bool = False


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class UserPublic(BaseModel):
    """Forma del usuario que ve el propio usuario logueado."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    must_change_password: bool
    created_at: datetime


# ---------------------- Gestión de usuarios (solo admin) ----------------------
class UserCreate(BaseModel):
    email: EmailStr
    temporary_password: str = Field(min_length=8, max_length=255)
    is_admin: bool = False


class UserListItem(BaseModel):
    """Forma del usuario que ve un admin al listar."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    must_change_password: bool
    created_at: datetime


# ---------------------- Contexto de negocio ----------------------
class BusinessContextBase(BaseModel):
    business_name: str = Field(default="", max_length=255)
    description: str = Field(default="", max_length=5000)
    services: str = Field(default="", max_length=5000)
    target_audience: str = Field(default="", max_length=5000)
    value_proposition: str = Field(default="", max_length=5000)
    tone: str = Field(default="", max_length=255)


class BusinessContextUpdate(BusinessContextBase):
    pass


class BusinessContextPublic(BusinessContextBase):
    model_config = ConfigDict(from_attributes=True)
    updated_at: datetime


# ---------------------- Catálogos ----------------------
class CatalogItem(BaseModel):
    id: str
    label: str
    description: str | None = None


# ---------------------- Generación de contenido ----------------------
class GenerateRequest(BaseModel):
    pain_id: str = Field(min_length=1, max_length=64)
    format_id: str = Field(min_length=1, max_length=64)
    extra_idea: str = Field(default="", max_length=2000)
    variation: bool = False


class GenerateResponse(BaseModel):
    content: str
    pain_id: str
    format_id: str
    model: str


class ScrapeRequest(BaseModel):
    url: str = Field(min_length=4, max_length=2048)


class ProposedBusinessContext(BaseModel):
    business_name: str = ""
    description: str = ""
    services: str = ""
    target_audience: str = ""
    value_proposition: str = ""
    tone: str = ""


class ScrapeResponse(BaseModel):
    source_url: str
    site_title: str = ""
    pages_scraped: int
    page_urls: list[str]
    raw_text_preview: str
    proposed_context: ProposedBusinessContext
