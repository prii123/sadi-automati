"""
Modelos para gestión de triggers de notificaciones
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Trigger:
    """Representa un trigger de notificación programada"""
    id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    frecuencia: str = "diaria"  # diaria, semanal, mensual, personalizada
    hora: str = "08:00"
    dias_semana: Optional[str] = None  # JSON: ["lunes", "martes", ...]
    dia_mes: Optional[int] = None  # Para frecuencia mensual
    intervalo_horas: Optional[int] = None  # Para frecuencia personalizada
    destinatarios: str = ""  # Emails separados por comas
    prioridades: str = "CRITICA,ALTA,MEDIA"  # Prioridades a incluir
    activo: int = 1
    ultima_ejecucion: Optional[str] = None
    proxima_ejecucion: Optional[str] = None
    creado_en: Optional[str] = None
    actualizado_en: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte el trigger a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'frecuencia': self.frecuencia,
            'hora': self.hora,
            'dias_semana': self.dias_semana,
            'dia_mes': self.dia_mes,
            'intervalo_horas': self.intervalo_horas,
            'destinatarios': self.destinatarios,
            'prioridades': self.prioridades,
            'activo': self.activo,
            'ultima_ejecucion': self.ultima_ejecucion,
            'proxima_ejecucion': self.proxima_ejecucion,
            'creado_en': self.creado_en,
            'actualizado_en': self.actualizado_en
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Trigger':
        """Crea un trigger desde un diccionario"""
        return Trigger(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            frecuencia=data.get('frecuencia', 'diaria'),
            hora=data.get('hora', '08:00'),
            dias_semana=data.get('dias_semana'),
            dia_mes=data.get('dia_mes'),
            intervalo_horas=data.get('intervalo_horas'),
            destinatarios=data.get('destinatarios', ''),
            prioridades=data.get('prioridades', 'CRITICA,ALTA,MEDIA'),
            activo=data.get('activo', 1),
            ultima_ejecucion=data.get('ultima_ejecucion'),
            proxima_ejecucion=data.get('proxima_ejecucion'),
            creado_en=data.get('creado_en'),
            actualizado_en=data.get('actualizado_en')
        )
