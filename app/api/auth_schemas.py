"""
Schemas de autenticación para validación de datos
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema para login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UsuarioCreate(BaseModel):
    """Schema para crear usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=100)
    rol: str = Field(default="usuario", pattern="^(admin|usuario)$")


class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    rol: Optional[str] = Field(None, pattern="^(admin|usuario)$")


class CambiarPasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    password_actual: str = Field(..., min_length=6)
    password_nueva: str = Field(..., min_length=6)
