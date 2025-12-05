"""
Script para probar el envío de notificaciones por email
Uso: python scripts/test_email.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si no está instalado python-dotenv, cargar manualmente
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


def main():
    """Función principal"""
    print("=" * 60)
    print("Test de Envío de Notificaciones por Email")
    print("=" * 60)
    
    # Verificar credenciales
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("\n❌ ERROR: Credenciales SMTP no configuradas")
        print("\nPara configurar:")
        print("1. Crea un archivo .env copiando .env.example")
        print("2. Agrega tus credenciales:")
        print("   SMTP_USER=tucorreo@gmail.com")
        print("   SMTP_PASSWORD=tu_contraseña_de_aplicacion")
        print("\n📖 Consulta .env.example para obtener la contraseña de aplicación de Gmail")
        return
    
    print(f"\n✓ Usuario SMTP configurado: {smtp_user}")
    
    # Solicitar email destino
    email_destino = input("\n📧 Ingresa el email destino para la prueba: ").strip()
    
    if not email_destino or '@' not in email_destino:
        print("❌ Email inválido")
        return
    
    # Inicializar servicios
    print("\n⏳ Inicializando servicios...")
    settings = Settings.from_env()
    db_factory = DatabaseFactory(settings)
    repository = db_factory.create_empresa_repository()
    
    notif_service = NotificacionService(repository)
    email_service = EmailService(smtp_user, smtp_password)
    
    # Obtener notificaciones
    print("⏳ Obteniendo notificaciones pendientes...")
    resultado_notif = notif_service.obtener_notificaciones_pendientes()
    
    if not resultado_notif['success']:
        print(f"❌ Error al obtener notificaciones: {resultado_notif.get('error')}")
        return
    
    notificaciones = resultado_notif.get('data', [])
    
    # Contar alertas
    total_alertas = 0
    for notif in notificaciones:
        total_alertas += len(notif.get('alertas', []))
    
    print(f"✓ Notificaciones encontradas: {len(notificaciones)}")
    print(f"✓ Total de alertas: {total_alertas}")
    
    if total_alertas == 0:
        print("\n⚠️ No hay notificaciones pendientes para enviar")
        print("Tip: Puedes agregar empresas con fechas de vencimiento próximas")
        return
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("Resumen de Notificaciones a Enviar:")
    print("=" * 60)
    
    criticas = 0
    altas = 0
    medias = 0
    
    for notif in notificaciones:
        empresa = notif['empresa']
        alertas = notif.get('alertas', [])
        
        if alertas:
            print(f"\n📌 {empresa['nombre']} (NIT: {empresa['nit']})")
            
            for alerta in alertas:
                prioridad = alerta.get('prioridad', 'MEDIA')
                motivo = alerta.get('motivo', '')
                modulo = alerta.get('modulo', '')
                
                icono = '🚨' if prioridad == 'CRITICA' else '⚠️' if prioridad == 'ALTA' else 'ℹ️'
                print(f"  {icono} {modulo}: {motivo}")
                
                if prioridad == 'CRITICA':
                    criticas += 1
                elif prioridad == 'ALTA':
                    altas += 1
                else:
                    medias += 1
    
    print(f"\n📊 Total por prioridad:")
    print(f"   🚨 Críticas: {criticas}")
    print(f"   ⚠️ Altas: {altas}")
    print(f"   ℹ️ Medias: {medias}")
    
    # Confirmar envío
    print("\n" + "=" * 60)
    confirmar = input(f"¿Enviar notificaciones a {email_destino}? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("❌ Envío cancelado")
        return
    
    # Enviar email
    print("\n⏳ Enviando email...")
    resultado = email_service.enviar_notificaciones_vencimientos(
        [email_destino], 
        notificaciones
    )
    
    if resultado['success']:
        print("\n✅ Email enviado exitosamente!")
        print(f"   Destinatario: {email_destino}")
        print(f"   Notificaciones: {resultado.get('total_notificaciones', 0)}")
    else:
        print(f"\n❌ Error al enviar email: {resultado.get('error')}")
        
        if 'Authentication' in resultado.get('error', ''):
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que tu email y contraseña sean correctos")
            print("   2. Asegúrate de usar una 'Contraseña de aplicación' de Gmail")
            print("   3. Verifica que la verificación en 2 pasos esté activa")
            print("   4. Consulta: https://support.google.com/accounts/answer/185833")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
