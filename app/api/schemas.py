"""
Esquemas Pydantic para validación de datos en la API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ModuloRequest(BaseModel):
    """Modelo para crear/actualizar un módulo"""
    activo: int = Field(0, ge=0, le=1, description="0 o 1")
    fecha_inicio: Optional[datetime] = None
    fecha_final: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None  # Alias para fecha_final
    notificacion: Optional[str] = None
    renovado: int = Field(0, ge=0, le=1)
    facturado: int = Field(0, ge=0, le=1)
    comentarios: Optional[str] = None
    
    def dict(self, **kwargs):
        """Override dict para manejar fecha_vencimiento como alias de fecha_final"""
        data = super().dict(**kwargs)
        # Si viene fecha_vencimiento y no fecha_final, usar fecha_vencimiento
        if data.get('fecha_vencimiento') and not data.get('fecha_final'):
            data['fecha_final'] = data['fecha_vencimiento']
        # Remover fecha_vencimiento del dict final
        data.pop('fecha_vencimiento', None)
        return data


class EmpresaRequest(BaseModel):
    """Modelo para crear una empresa"""
    nit: str = Field(..., min_length=6, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=200)
    tipo: str = Field("Persona Jurídica", max_length=50)
    estado: str = Field("activo", max_length=20)
    certificado: Optional[ModuloRequest] = None
    resolucion: Optional[ModuloRequest] = None
    documento: Optional[ModuloRequest] = None


class ActualizarModuloRequest(BaseModel):
    """Modelo para actualizar estado de módulo"""
    modulo: str = Field(..., pattern="^(certificado|resolucion|documento)$")
    campo: str = Field(..., pattern="^(renovado|facturado)$")
    valor: int = Field(..., ge=0, le=1)
