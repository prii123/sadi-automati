"""
Modelo de datos para Usuario
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """
    Modelo de datos para Usuario del sistema
    """
    username: str
    password_hash: str
    nombre: str
    email: str
    rol: str = "usuario"  # admin, usuario
    activo: int = 1
    id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario (sin password)"""
        return {
            'id': self.id,
            'username': self.username,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Crea una instancia de Usuario desde un diccionario"""
        return cls(
            id=data.get('id'),
            username=data['username'],
            password_hash=data['password_hash'],
            nombre=data['nombre'],
            email=data['email'],
            rol=data.get('rol', 'usuario'),
            activo=data.get('activo', 1),
            fecha_creacion=datetime.fromisoformat(data['fecha_creacion']) if data.get('fecha_creacion') else None,
            fecha_actualizacion=datetime.fromisoformat(data['fecha_actualizacion']) if data.get('fecha_actualizacion') else None,
            ultimo_acceso=datetime.fromisoformat(data['ultimo_acceso']) if data.get('ultimo_acceso') else None
        )
