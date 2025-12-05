"""
Script para enviar notificaciones automáticas por email
Se ejecuta como tarea programada y envía notificaciones según configuración
"""
import sys
import os
from datetime import datetime

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
from app.config.database_factory import DatabaseFactory
from app.config.settings import Settings


def log(mensaje):
    """Escribe un mensaje de log con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")


def enviar_notificaciones():
    """Función principal para enviar notificaciones"""
    log("=" * 60)
    log("INICIO: Envío automático de notificaciones")
    log("=" * 60)
    
    # Verificar credenciales
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    destinatarios_env = os.getenv('EMAIL_DESTINATARIOS')
    
    if not smtp_user or not smtp_password:
        log("❌ ERROR: Credenciales SMTP no configuradas en .env")
        return False
    
    if not destinatarios_env:
        log("❌ ERROR: EMAIL_DESTINATARIOS no configurado en .env")
        log("   Configura: EMAIL_DESTINATARIOS=correo1@ejemplo.com,correo2@ejemplo.com")
        return False
    
    # Parsear destinatarios
    destinatarios = [email.strip() for email in destinatarios_env.split(',') if email.strip()]
    
    if not destinatarios:
        log("❌ ERROR: No hay destinatarios válidos")
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
            log(f"❌ Error al obtener notificaciones: {resultado_notif.get('error')}")
            return False
        
        notificaciones = resultado_notif.get('data', [])
        
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
            return True
        
        # Enviar email
        log("⏳ Enviando email...")
        resultado = email_service.enviar_notificaciones_vencimientos(
            destinatarios, 
            notificaciones
        )
        
        if resultado['success']:
            log("✅ Email enviado exitosamente!")
            log(f"   Destinatarios: {len(destinatarios)}")
            log(f"   Notificaciones: {resultado.get('total_notificaciones', 0)}")
            return True
        else:
            log(f"❌ Error al enviar email: {resultado.get('error')}")
            return False
            
    except Exception as e:
        log(f"❌ Error inesperado: {str(e)}")
        import traceback
        log(traceback.format_exc())
        return False
    finally:
        log("=" * 60)
        log("FIN: Proceso de envío automático")
        log("=" * 60)


if __name__ == "__main__":
    try:
        exito = enviar_notificaciones()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        log("\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
