"""
Modelo de datos para Empresa
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ModuloEmpresa:
    """
    Representa un módulo (certificado, resolución o documento) asociado a una empresa
    """
    activo: int = 0  # 0 o 1
    fecha_inicio: Optional[datetime] = None
    fecha_final: Optional[datetime] = None
    notificacion: Optional[str] = None
    renovado: int = 0  # 0 o 1
    facturado: int = 0  # 0 o 1
    comentarios: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte el módulo a diccionario"""
        return {
            'activo': self.activo,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_final': self.fecha_final.isoformat() if self.fecha_final else None,
            'notificacion': self.notificacion,
            'renovado': self.renovado,
            'facturado': self.facturado,
            'comentarios': self.comentarios
        }


@dataclass
class Empresa:
    """
    Modelo de datos para Empresa
    Representa toda la información de una empresa en el sistema
    """
    nit: str
    nombre: str
    tipo: str
    estado: str = "activo"
    id: Optional[int] = None
    
    # Módulos de la empresa
    certificado: ModuloEmpresa = field(default_factory=ModuloEmpresa)
    resolucion: ModuloEmpresa = field(default_factory=ModuloEmpresa)
    documento: ModuloEmpresa = field(default_factory=ModuloEmpresa)
    
    # Metadatos
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    def tiene_modulos_activos(self) -> bool:
        """Verifica si la empresa tiene al menos un módulo activo"""
        return (
            (self.certificado and self.certificado.activo == 1) or 
            (self.resolucion and self.resolucion.activo == 1) or 
            (self.documento and self.documento.activo == 1)
        )

    def to_dict(self) -> dict:
        """Convierte la empresa a diccionario"""
        return {
            'id': self.id,
            'nit': self.nit,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'estado': self.estado,
            'certificado': self.certificado.to_dict() if self.certificado else None,
            'resolucion': self.resolucion.to_dict() if self.resolucion else None,
            'documento': self.documento.to_dict() if self.documento else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Empresa':
        """Crea una instancia de Empresa desde un diccionario"""
        certificado = ModuloEmpresa(**data.get('certificado', {})) if 'certificado' in data else ModuloEmpresa()
        resolucion = ModuloEmpresa(**data.get('resolucion', {})) if 'resolucion' in data else ModuloEmpresa()
        documento = ModuloEmpresa(**data.get('documento', {})) if 'documento' in data else ModuloEmpresa()
        
        return cls(
            id=data.get('id'),
            nit=data['nit'],
            nombre=data['nombre'],
            tipo=data.get('tipo', 'Persona Jurídica'),
            estado=data.get('estado', 'activo'),
            certificado=certificado,
            resolucion=resolucion,
            documento=documento
        )
