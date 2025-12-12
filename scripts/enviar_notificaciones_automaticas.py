"""
Script para enviar notificaciones automáticas por email
Se ejecuta como tarea programada y envía notificaciones según configuración
"""
import sys
import os
from datetime import datetime
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from app.services.email_service import EmailService
from app.services.notificacion_service import NotificacionService
from app.services.trigger_service import TriggerService
from app.repositories.trigger_repository import TriggerRepository
from app.config.database_factory import DatabaseFactory
from app.config.settings import Settings


def log(mensaje):
    """Escribe un mensaje de log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")


def enviar_notificaciones(trigger_id=None):
    """
    Función principal para enviar notificaciones
    
    Args:
        trigger_id: ID del trigger que ejecuta (opcional, para registrar en historial)
    """
    log("=" * 60)
    log("INICIO: Envío automático de notificaciones")
    if trigger_id:
        log(f"Ejecutado por trigger ID: {trigger_id}")
    log("=" * 60)
    
    # Variables para el registro de ejecución
    estado = 'exitoso'
    error_mensaje = None
    empresas_procesadas = 0
    notificaciones_enviadas = 0
    
    # Verificar credenciales 
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    destinatarios_env = os.getenv('EMAIL_DESTINATARIOS')
    
    if not smtp_user or not smtp_password:
        log("❌ ERROR: Credenciales SMTP no configuradas en .env")
        error_mensaje = "Credenciales SMTP no configuradas"
        if trigger_id:
            registrar_ejecucion_trigger(trigger_id, 'fallido', 0, 0, error_mensaje)
        return False
    
    if not destinatarios_env:
        log("❌ ERROR: EMAIL_DESTINATARIOS no configurado en .env")
        log("   Configura: EMAIL_DESTINATARIOS=correo1@ejemplo.com,correo2@ejemplo.com")
        error_mensaje = "EMAIL_DESTINATARIOS no configurado"
        if trigger_id:
            registrar_ejecucion_trigger(trigger_id, 'fallido', 0, 0, error_mensaje)
        return False
    
    # Parsear destinatarios
    destinatarios = [email.strip() for email in destinatarios_env.split(',') if email.strip()]
    
    if not destinatarios:
        log("❌ ERROR: No hay destinatarios válidos")
        error_mensaje = "No hay destinatarios válidos"
        if trigger_id:
            registrar_ejecucion_trigger(trigger_id, 'fallido', 0, 0, error_mensaje)
        return False
    
    log(f"✓ Usuario SMTP: {smtp_user}")
    log(f"✓ Destinatarios: {', '.join(destinatarios)}")
    
    try:
        # Inicializar servicios
        log("⏳ Inicializando servicios...")
        settings = Settings.from_env()
        db_factory = DatabaseFactory(settings)
        repository = db_factory.create_empresa_repository()
        
        notif_service = NotificacionService(repository)
        email_service = EmailService(smtp_user, smtp_password)
        
        # Obtener notificaciones
        log("⏳ Obteniendo notificaciones pendientes...")
        resultado_notif = notif_service.obtener_notificaciones_pendientes()
        
        if not resultado_notif['success']:
            error_mensaje = f"Error al obtener notificaciones: {resultado_notif.get('error')}"
            log(f"❌ {error_mensaje}")
            if trigger_id:
                registrar_ejecucion_trigger(trigger_id, 'fallido', 0, 0, error_mensaje)
            return False
        
        notificaciones = resultado_notif.get('data', [])
        empresas_procesadas = len(notificaciones)
        
        # Contar alertas
        total_alertas = 0
        criticas = 0
        altas = 0
        medias = 0
        
        for notif in notificaciones:
            for alerta in notif.get('alertas', []):
                total_alertas += 1
                prioridad = alerta.get('prioridad', 'MEDIA')
                if prioridad == 'CRITICA':
                    criticas += 1
                elif prioridad == 'ALTA':
                    altas += 1
                else:
                    medias += 1
        
        log(f"✓ Notificaciones encontradas: {len(notificaciones)}")
        log(f"✓ Total de alertas: {total_alertas}")
        log(f"   🚨 Críticas: {criticas}")
        log(f"   ⚠️ Altas: {altas}")
        log(f"   ℹ️ Medias: {medias}")
        
        if total_alertas == 0:
            log("ℹ️ No hay notificaciones pendientes para enviar")
            log("✅ Proceso completado sin envíos")
            if trigger_id:
                detalles = json.dumps({'empresas': empresas_procesadas, 'alertas': 0})
                registrar_ejecucion_trigger(trigger_id, 'exitoso', 0, empresas_procesadas, None, detalles)
            return True
        
        # Enviar email
        log("⏳ Enviando email...")
        resultado = email_service.enviar_notificaciones_vencimientos(
            destinatarios, 
            notificaciones
        )
        
        if resultado['success']:
            notificaciones_enviadas = resultado.get('total_notificaciones', 0)
            log("✅ Email enviado exitosamente!")
            log(f"   Destinatarios: {len(destinatarios)}")
            log(f"   Notificaciones: {notificaciones_enviadas}")
            
            if trigger_id:
                detalles = json.dumps({
                    'empresas': empresas_procesadas,
                    'alertas': total_alertas,
                    'criticas': criticas,
                    'altas': altas,
                    'medias': medias,
                    'destinatarios': len(destinatarios)
                })
                registrar_ejecucion_trigger(trigger_id, 'exitoso', notificaciones_enviadas, empresas_procesadas, None, detalles)
            
            return True
        else:
            error_mensaje = f"Error al enviar email: {resultado.get('error')}"
            log(f"❌ {error_mensaje}")
            
            if trigger_id:
                registrar_ejecucion_trigger(trigger_id, 'fallido', 0, empresas_procesadas, error_mensaje)
            
            return False
            
    except Exception as e:
        error_mensaje = f"Error inesperado: {str(e)}"
        log(f"❌ {error_mensaje}")
        import traceback
        log(traceback.format_exc())
        
        if trigger_id:
            registrar_ejecucion_trigger(trigger_id, 'fallido', notificaciones_enviadas, empresas_procesadas, error_mensaje)
        
        return False
    finally:
        log("=" * 60)
        log("FIN: Proceso de envío automático")
        log("=" * 60)


def registrar_ejecucion_trigger(trigger_id, estado, notificaciones, empresas, error=None, detalles=None):
    """Registra la ejecución de un trigger en el historial"""
    try:
        settings = Settings.from_env()
        trigger_repo = TriggerRepository(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        trigger_service = TriggerService(trigger_repo)
        
        datos = {
            'trigger_id': trigger_id,
            'estado': estado,
            'notificaciones_enviadas': notificaciones,
            'empresas_procesadas': empresas,
            'error_mensaje': error,
            'detalles': detalles
        }
        
        trigger_service.registrar_ejecucion(datos)
        log(f"✓ Ejecución registrada en historial")
    except Exception as e:
        log(f"⚠️ No se pudo registrar ejecución en historial: {str(e)}")


if __name__ == "__main__":
    try:
        exito = enviar_notificaciones()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        log("\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
