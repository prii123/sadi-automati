"""
Servicio para gestión de triggers de notificaciones
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from app.repositories.trigger_repository import TriggerRepository
from app.models.trigger import Trigger


class TriggerService:
    """Servicio para lógica de negocio de triggers"""
    
    def __init__(self, repository: TriggerRepository):
        """
        Inicializa el servicio
        
        Args:
            repository: Repositorio de triggers
        """
        self.repository = repository
    
    def crear_trigger(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo trigger
        
        Args:
            datos: Datos del trigger
            
        Returns:
            Resultado de la operación
        """
        try:
            # Validar datos
            if not datos.get('nombre'):
                return {'success': False, 'error': 'El nombre es obligatorio'}
            
            if not datos.get('destinatarios'):
                return {'success': False, 'error': 'Debe especificar al menos un destinatario'}
            
            # Procesar días de semana si es semanal
            dias_semana = None
            if datos.get('frecuencia') == 'semanal' and datos.get('dias_semana'):
                if isinstance(datos['dias_semana'], list):
                    dias_semana = json.dumps(datos['dias_semana'])
                else:
                    dias_semana = datos['dias_semana']
            
            # Crear trigger
            trigger = Trigger(
                nombre=datos.get('nombre'),
                descripcion=datos.get('descripcion', ''),
                frecuencia=datos.get('frecuencia', 'diaria'),
                hora=datos.get('hora', '08:00'),
                dias_semana=dias_semana,
                dia_mes=datos.get('dia_mes'),
                intervalo_horas=datos.get('intervalo_horas'),
                destinatarios=datos.get('destinatarios'),
                prioridades=datos.get('prioridades', 'CRITICA,ALTA,MEDIA'),
                activo=datos.get('activo', 1)
            )
            
            # Calcular próxima ejecución
            trigger.proxima_ejecucion = self._calcular_proxima_ejecucion(trigger)
            
            # Guardar
            trigger = self.repository.create(trigger)
            
            return {
                'success': True,
                'data': trigger.to_dict(),
                'message': 'Trigger creado exitosamente'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def obtener_triggers(self) -> Dict[str, Any]:
        """
        Obtiene todos los triggers
        
        Returns:
            Lista de triggers
        """
        try:
            triggers = self.repository.get_all()
            return {
                'success': True,
                'data': [t.to_dict() for t in triggers]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def obtener_trigger(self, trigger_id: int) -> Dict[str, Any]:
        """
        Obtiene un trigger por ID
        
        Args:
            trigger_id: ID del trigger
            
        Returns:
            Trigger encontrado
        """
        try:
            trigger = self.repository.get_by_id(trigger_id)
            if not trigger:
                return {'success': False, 'error': 'Trigger no encontrado'}
            
            return {
                'success': True,
                'data': trigger.to_dict()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def actualizar_trigger(self, trigger_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un trigger
        
        Args:
            trigger_id: ID del trigger
            datos: Datos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            trigger = self.repository.get_by_id(trigger_id)
            if not trigger:
                return {'success': False, 'error': 'Trigger no encontrado'}
            
            # Actualizar campos
            if 'nombre' in datos:
                trigger.nombre = datos['nombre']
            if 'descripcion' in datos:
                trigger.descripcion = datos['descripcion']
            if 'frecuencia' in datos:
                trigger.frecuencia = datos['frecuencia']
            if 'hora' in datos:
                trigger.hora = datos['hora']
            if 'dias_semana' in datos:
                if isinstance(datos['dias_semana'], list):
                    trigger.dias_semana = json.dumps(datos['dias_semana'])
                else:
                    trigger.dias_semana = datos['dias_semana']
            if 'dia_mes' in datos:
                trigger.dia_mes = datos['dia_mes']
            if 'intervalo_horas' in datos:
                trigger.intervalo_horas = datos['intervalo_horas']
            if 'destinatarios' in datos:
                trigger.destinatarios = datos['destinatarios']
            if 'prioridades' in datos:
                trigger.prioridades = datos['prioridades']
            if 'activo' in datos:
                trigger.activo = datos['activo']
            
            # Recalcular próxima ejecución
            trigger.proxima_ejecucion = self._calcular_proxima_ejecucion(trigger)
            
            # Guardar
            trigger = self.repository.update(trigger)
            
            return {
                'success': True,
                'data': trigger.to_dict(),
                'message': 'Trigger actualizado exitosamente'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def eliminar_trigger(self, trigger_id: int) -> Dict[str, Any]:
        """
        Elimina un trigger
        
        Args:
            trigger_id: ID del trigger
            
        Returns:
            Resultado de la operación
        """
        try:
            eliminado = self.repository.delete(trigger_id)
            if not eliminado:
                return {'success': False, 'error': 'Trigger no encontrado'}
            
            return {
                'success': True,
                'message': 'Trigger eliminado exitosamente'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cambiar_estado(self, trigger_id: int, activo: bool) -> Dict[str, Any]:
        """
        Activa o desactiva un trigger
        
        Args:
            trigger_id: ID del trigger
            activo: Nuevo estado
            
        Returns:
            Resultado de la operación
        """
        try:
            trigger = self.repository.get_by_id(trigger_id)
            if not trigger:
                return {'success': False, 'error': 'Trigger no encontrado'}
            
            trigger.activo = 1 if activo else 0
            
            # Recalcular próxima ejecución si se activa
            if activo:
                trigger.proxima_ejecucion = self._calcular_proxima_ejecucion(trigger)
            
            trigger = self.repository.update(trigger)
            
            return {
                'success': True,
                'data': trigger.to_dict(),
                'message': f'Trigger {"activado" if activo else "desactivado"} exitosamente'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calcular_proxima_ejecucion(self, trigger: Trigger) -> str:
        """
        Calcula la próxima fecha/hora de ejecución
        
        Args:
            trigger: Trigger a calcular
            
        Returns:
            Fecha/hora ISO de la próxima ejecución
        """
        now = datetime.now()
        hora_parts = trigger.hora.split(':')
        hora = int(hora_parts[0])
        minuto = int(hora_parts[1]) if len(hora_parts) > 1 else 0
        
        if trigger.frecuencia == 'diaria':
            proxima = now.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            if proxima <= now:
                proxima += timedelta(days=1)
        
        elif trigger.frecuencia == 'semanal':
            proxima = now.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            # Calcular próximo día de la semana configurado
            if trigger.dias_semana:
                dias = json.loads(trigger.dias_semana) if isinstance(trigger.dias_semana, str) else trigger.dias_semana
                dias_map = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3, 'viernes': 4, 'sabado': 5, 'domingo': 6}
                dias_num = sorted([dias_map.get(d.lower(), 0) for d in dias])
                
                dia_actual = now.weekday()
                encontrado = False
                
                for dia in dias_num:
                    if dia > dia_actual or (dia == dia_actual and proxima > now):
                        dias_adelante = dia - dia_actual
                        proxima = proxima + timedelta(days=dias_adelante)
                        encontrado = True
                        break
                
                if not encontrado:
                    dias_adelante = (7 - dia_actual) + dias_num[0]
                    proxima = proxima + timedelta(days=dias_adelante)
            else:
                if proxima <= now:
                    proxima += timedelta(weeks=1)
        
        elif trigger.frecuencia == 'mensual':
            dia_mes = trigger.dia_mes or 1
            proxima = now.replace(day=dia_mes, hour=hora, minute=minuto, second=0, microsecond=0)
            if proxima <= now:
                # Siguiente mes
                if now.month == 12:
                    proxima = proxima.replace(year=now.year + 1, month=1)
                else:
                    proxima = proxima.replace(month=now.month + 1)
        
        elif trigger.frecuencia == 'personalizada':
            intervalo = trigger.intervalo_horas or 1
            proxima = now + timedelta(hours=intervalo)
        
        else:
            proxima = now + timedelta(days=1)
        
        return proxima.isoformat()
    
    def obtener_triggers_pendientes(self) -> Dict[str, Any]:
        """
        Obtiene triggers que deben ejecutarse ahora
        
        Returns:
            Lista de triggers pendientes
        """
        try:
            triggers_activos = self.repository.get_activos()
            now = datetime.now()
            
            pendientes = []
            for trigger in triggers_activos:
                if trigger.proxima_ejecucion:
                    proxima = datetime.fromisoformat(trigger.proxima_ejecucion)
                    if proxima <= now:
                        pendientes.append(trigger.to_dict())
            
            return {
                'success': True,
                'data': pendientes
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
