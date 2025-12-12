"""
Scheduler automático para ejecutar triggers programados
Este servicio se ejecuta en segundo plano y verifica periódicamente
si hay triggers que deben ejecutarse según su configuración.
"""
import logging
from datetime import datetime
from typing import Optional
import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config.settings import Settings
from app.repositories.trigger_repository import TriggerRepository
from app.services.trigger_service import TriggerService
from app.services.email_service import EmailService
from app.services.notificacion_service import NotificacionService
from app.config.database_factory import DatabaseFactory

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TriggerScheduler:
    """Gestor de ejecución automática de triggers"""
    
    def __init__(self):
        """Inicializa el scheduler"""
        self.scheduler = BackgroundScheduler(timezone='America/Bogota')
        self.settings = Settings.from_env()
        self.trigger_repository = TriggerRepository(
            host=self.settings.DB_HOST,
            port=self.settings.DB_PORT,
            database=self.settings.DB_NAME,
            user=self.settings.DB_USER,
            password=self.settings.DB_PASSWORD
        )
        self.trigger_service = TriggerService(self.trigger_repository)
        self.is_running = False
        
        logger.info("TriggerScheduler inicializado")
    
    def start(self):
        """Inicia el scheduler"""
        if self.is_running:
            logger.warning("El scheduler ya está en ejecución")
            return
        
        try:
            # Cargar y programar todos los triggers activos
            self._load_all_triggers()
            
            # Iniciar el scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("✓ Scheduler iniciado correctamente")
            logger.info(f"  Trabajos programados: {len(self.scheduler.get_jobs())}")
            
        except Exception as e:
            logger.error(f"Error iniciando scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Detiene el scheduler"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Scheduler detenido")
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {str(e)}")
    
    def _load_all_triggers(self):
        """Carga y programa todos los triggers activos"""
        try:
            resultado = self.trigger_service.obtener_triggers()
            
            if not resultado['success']:
                logger.error(f"Error obteniendo triggers: {resultado.get('error')}")
                return
            
            triggers = resultado['data']
            activos = [t for t in triggers if t.get('activo') == 1]
            
            logger.info(f"Cargando {len(activos)} triggers activos...")
            
            for trigger in activos:
                self._schedule_trigger(trigger)
            
            logger.info(f"✓ {len(activos)} triggers programados")
            
        except Exception as e:
            logger.error(f"Error cargando triggers: {str(e)}")
    
    def _schedule_trigger(self, trigger: dict):
        """
        Programa un trigger según su configuración
        
        Args:
            trigger: Diccionario con datos del trigger
        """
        try:
            trigger_id = trigger['id']
            nombre = trigger['nombre']
            frecuencia = trigger['frecuencia']
            
            # Crear job_id único
            job_id = f"trigger_{trigger_id}"
            
            # Eliminar job existente si hay uno
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Configurar trigger según frecuencia
            if frecuencia == 'diaria':
                # Ejecutar todos los días a la hora especificada
                hora, minuto = self._parse_hora(trigger['hora'])
                cron_trigger = CronTrigger(hour=hora, minute=minuto)
                
                self.scheduler.add_job(
                    func=self._execute_trigger,
                    trigger=cron_trigger,
                    args=[trigger_id],
                    id=job_id,
                    name=nombre,
                    replace_existing=True
                )
                logger.info(f"  • {nombre}: Diaria a las {trigger['hora']}")
                
            elif frecuencia == 'semanal':
                # Ejecutar días específicos de la semana
                hora, minuto = self._parse_hora(trigger['hora'])
                dias_semana = trigger.get('dias_semana')
                
                if dias_semana:
                    import json
                    dias = json.loads(dias_semana) if isinstance(dias_semana, str) else dias_semana
                    
                    # Mapear días a números (0=lunes, 6=domingo)
                    dias_map = {
                        'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
                        'viernes': 4, 'sabado': 5, 'domingo': 6
                    }
                    day_of_week = ','.join(str(dias_map.get(d.lower(), 0)) for d in dias)
                    
                    cron_trigger = CronTrigger(
                        day_of_week=day_of_week,
                        hour=hora,
                        minute=minuto
                    )
                    
                    self.scheduler.add_job(
                        func=self._execute_trigger,
                        trigger=cron_trigger,
                        args=[trigger_id],
                        id=job_id,
                        name=nombre,
                        replace_existing=True
                    )
                    logger.info(f"  • {nombre}: Semanal ({', '.join(dias)}) a las {trigger['hora']}")
                
            elif frecuencia == 'mensual':
                # Ejecutar día específico del mes
                hora, minuto = self._parse_hora(trigger['hora'])
                dia_mes = trigger.get('dia_mes', 1)
                
                cron_trigger = CronTrigger(day=dia_mes, hour=hora, minute=minuto)
                
                self.scheduler.add_job(
                    func=self._execute_trigger,
                    trigger=cron_trigger,
                    args=[trigger_id],
                    id=job_id,
                    name=nombre,
                    replace_existing=True
                )
                logger.info(f"  • {nombre}: Mensual día {dia_mes} a las {trigger['hora']}")
                
            elif frecuencia == 'personalizada':
                # Ejecutar cada N horas
                intervalo = trigger.get('intervalo_horas', 1)
                
                interval_trigger = IntervalTrigger(hours=intervalo)
                
                self.scheduler.add_job(
                    func=self._execute_trigger,
                    trigger=interval_trigger,
                    args=[trigger_id],
                    id=job_id,
                    name=nombre,
                    replace_existing=True
                )
                logger.info(f"  • {nombre}: Cada {intervalo} hora(s)")
            
        except Exception as e:
            logger.error(f"Error programando trigger '{trigger.get('nombre')}': {str(e)}")
    
    def _parse_hora(self, hora_str: str) -> tuple:
        """
        Parsea string de hora a tupla (hora, minuto)
        
        Args:
            hora_str: String en formato "HH:MM"
            
        Returns:
            Tupla (hora, minuto)
        """
        try:
            parts = hora_str.split(':')
            hora = int(parts[0])
            minuto = int(parts[1]) if len(parts) > 1 else 0
            return (hora, minuto)
        except:
            return (8, 0)  # Default: 8:00 AM
    
    def _execute_trigger(self, trigger_id: int):
        """
        Ejecuta un trigger específico
        
        Args:
            trigger_id: ID del trigger a ejecutar
        """
        logger.info(f"=" * 60)
        logger.info(f"EJECUTANDO TRIGGER ID: {trigger_id}")
        logger.info(f"=" * 60)
        
        estado = 'exitoso'
        error_mensaje = None
        notificaciones_enviadas = 0
        empresas_procesadas = 0
        
        try:
            # Obtener información del trigger
            trigger = self.trigger_repository.get_by_id(trigger_id)
            if not trigger:
                logger.error(f"Trigger {trigger_id} no encontrado")
                return
            
            logger.info(f"Trigger: {trigger.nombre}")
            logger.info(f"Destinatarios: {trigger.destinatarios}")
            
            # Verificar credenciales SMTP
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not smtp_user or not smtp_password:
                error_mensaje = "Credenciales SMTP no configuradas"
                logger.error(f"❌ {error_mensaje}")
                estado = 'fallido'
                self._registrar_ejecucion(trigger_id, estado, 0, 0, error_mensaje)
                return
            
            # Parsear destinatarios del trigger
            destinatarios = [email.strip() for email in trigger.destinatarios.split(',') if email.strip()]
            
            if not destinatarios:
                error_mensaje = "No hay destinatarios configurados"
                logger.error(f"❌ {error_mensaje}")
                estado = 'fallido'
                self._registrar_ejecucion(trigger_id, estado, 0, 0, error_mensaje)
                return
            
            # Inicializar servicios
            db_factory = DatabaseFactory(self.settings)
            repository = db_factory.create_empresa_repository()
            notif_service = NotificacionService(repository)
            email_service = EmailService(smtp_user, smtp_password)
            
            # Obtener notificaciones según prioridades del trigger
            prioridades = trigger.prioridades.split(',')
            logger.info(f"Prioridades: {', '.join(prioridades)}")
            
            resultado_notif = notif_service.obtener_notificaciones_pendientes()
            
            if not resultado_notif['success']:
                error_mensaje = f"Error obteniendo notificaciones: {resultado_notif.get('error')}"
                logger.error(f"❌ {error_mensaje}")
                estado = 'fallido'
                self._registrar_ejecucion(trigger_id, estado, 0, 0, error_mensaje)
                return
            
            # Filtrar por prioridades
            todas_notif = resultado_notif.get('data', [])
            notificaciones = []
            
            for notif in todas_notif:
                alertas_filtradas = [
                    alerta for alerta in notif.get('alertas', [])
                    if alerta.get('prioridad') in prioridades
                ]
                if alertas_filtradas:
                    notif_copia = notif.copy()
                    notif_copia['alertas'] = alertas_filtradas
                    notificaciones.append(notif_copia)
            
            empresas_procesadas = len(notificaciones)
            total_alertas = sum(len(n.get('alertas', [])) for n in notificaciones)
            
            logger.info(f"✓ Empresas con alertas: {empresas_procesadas}")
            logger.info(f"✓ Total alertas: {total_alertas}")
            
            if total_alertas == 0:
                logger.info("ℹ️ No hay alertas que cumplan los criterios")
                import json
                detalles = json.dumps({
                    'empresas_revisadas': len(todas_notif),
                    'empresas_procesadas': 0,
                    'alertas': 0
                })
                self._registrar_ejecucion(trigger_id, 'exitoso', 0, len(todas_notif), None, detalles)
                return
            
            # Enviar email
            logger.info("⏳ Enviando notificaciones...")
            resultado = email_service.enviar_notificaciones_vencimientos(
                destinatarios,
                notificaciones
            )
            
            if resultado['success']:
                notificaciones_enviadas = resultado.get('total_notificaciones', 0)
                logger.info(f"✅ Email enviado exitosamente")
                logger.info(f"   Destinatarios: {len(destinatarios)}")
                logger.info(f"   Notificaciones: {notificaciones_enviadas}")
                
                import json
                detalles = json.dumps({
                    'empresas': empresas_procesadas,
                    'alertas': total_alertas,
                    'destinatarios': len(destinatarios),
                    'prioridades': prioridades
                })
                self._registrar_ejecucion(trigger_id, 'exitoso', notificaciones_enviadas, empresas_procesadas, None, detalles)
            else:
                error_mensaje = f"Error enviando email: {resultado.get('error')}"
                logger.error(f"❌ {error_mensaje}")
                estado = 'fallido'
                self._registrar_ejecucion(trigger_id, estado, 0, empresas_procesadas, error_mensaje)
            
        except Exception as e:
            error_mensaje = f"Error inesperado: {str(e)}"
            logger.error(f"❌ {error_mensaje}")
            import traceback
            logger.error(traceback.format_exc())
            self._registrar_ejecucion(trigger_id, 'fallido', notificaciones_enviadas, empresas_procesadas, error_mensaje)
        
        finally:
            logger.info(f"=" * 60)
            logger.info(f"FIN EJECUCIÓN TRIGGER ID: {trigger_id}")
            logger.info(f"=" * 60)
    
    def _registrar_ejecucion(self, trigger_id: int, estado: str, notificaciones: int, 
                            empresas: int, error: Optional[str] = None, detalles: Optional[str] = None):
        """Registra la ejecución en el historial"""
        try:
            datos = {
                'trigger_id': trigger_id,
                'estado': estado,
                'notificaciones_enviadas': notificaciones,
                'empresas_procesadas': empresas,
                'error_mensaje': error,
                'detalles': detalles
            }
            
            self.trigger_service.registrar_ejecucion(datos)
            logger.info("✓ Ejecución registrada en historial")
        except Exception as e:
            logger.error(f"⚠️ Error registrando ejecución: {str(e)}")
    
    def reload_triggers(self):
        """Recarga todos los triggers (útil cuando se actualizan)"""
        logger.info("Recargando triggers...")
        
        # Limpiar todos los jobs existentes
        for job in self.scheduler.get_jobs():
            self.scheduler.remove_job(job.id)
        
        # Recargar
        self._load_all_triggers()
        logger.info("✓ Triggers recargados")
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del scheduler
        
        Returns:
            Diccionario con información del scheduler
        """
        jobs = self.scheduler.get_jobs()
        
        return {
            'running': self.is_running,
            'total_jobs': len(jobs),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }


# Instancia global del scheduler
_scheduler_instance: Optional[TriggerScheduler] = None


def get_scheduler() -> TriggerScheduler:
    """Obtiene o crea la instancia global del scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = TriggerScheduler()
    
    return _scheduler_instance


def start_scheduler():
    """Inicia el scheduler global"""
    scheduler = get_scheduler()
    if not scheduler.is_running:
        scheduler.start()


def stop_scheduler():
    """Detiene el scheduler global"""
    global _scheduler_instance
    
    if _scheduler_instance and _scheduler_instance.is_running:
        _scheduler_instance.stop()
        _scheduler_instance = None
