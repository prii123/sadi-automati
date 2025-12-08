"""
Modelos para gestión de triggers de notificaciones
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class TriggerEjecucion:
    """Representa una ejecución de un trigger"""
    id: Optional[int] = None
    trigger_id: int = 0
    trigger_nombre: str = ""
    fecha_ejecucion: Optional[str] = None
    estado: str = "exitoso"  # exitoso, fallido
    notificaciones_enviadas: int = 0
    empresas_procesadas: int = 0
    error_mensaje: Optional[str] = None
    detalles: Optional[str] = None  # JSON con información adicional
    
    def to_dict(self) -> dict:
        """Convierte la ejecución a diccionario"""
        return {
            'id': self.id,
            'trigger_id': self.trigger_id,
            'trigger_nombre': self.trigger_nombre,
            'fecha_ejecucion': self.fecha_ejecucion,
            'estado': self.estado,
            'notificaciones_enviadas': self.notificaciones_enviadas,
            'empresas_procesadas': self.empresas_procesadas,
            'error_mensaje': self.error_mensaje,
            'detalles': self.detalles
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TriggerEjecucion':
        """Crea una ejecución desde un diccionario"""
        return TriggerEjecucion(
            id=data.get('id'),
            trigger_id=data.get('trigger_id', 0),
            trigger_nombre=data.get('trigger_nombre', ''),
            fecha_ejecucion=data.get('fecha_ejecucion'),
            estado=data.get('estado', 'exitoso'),
            notificaciones_enviadas=data.get('notificaciones_enviadas', 0),
            empresas_procesadas=data.get('empresas_procesadas', 0),
            error_mensaje=data.get('error_mensaje'),
            detalles=data.get('detalles')
        )


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
