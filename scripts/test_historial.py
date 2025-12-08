"""
Script para probar el sistema de historial de ejecuciones de triggers
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.settings import Settings
from app.repositories.trigger_repository import TriggerRepository
from app.services.trigger_service import TriggerService
from app.models.trigger import Trigger, TriggerEjecucion
from datetime import datetime

def test_historial():
    """Prueba el sistema de historial"""
    print("=" * 60)
    print("PRUEBA: Sistema de Historial de Ejecuciones")
    print("=" * 60)
    
    # Inicializar
    settings = Settings.from_env()
    repository = TriggerRepository(settings.DB_PATH)
    service = TriggerService(repository)
    
    print("\n✓ Servicios inicializados")
    
    # Verificar que las tablas existen
    print("\n📋 Verificando tablas de base de datos...")
    
    # Obtener triggers existentes
    resultado = service.obtener_triggers()
    if resultado['success']:
        triggers = resultado['data']
        print(f"✓ Triggers en sistema: {len(triggers)}")
        
        if len(triggers) > 0:
            trigger_id = triggers[0]['id']
            trigger_nombre = triggers[0]['nombre']
            print(f"   Usando trigger: '{trigger_nombre}' (ID: {trigger_id})")
            
            # Crear ejecución de prueba
            print("\n📝 Registrando ejecución de prueba...")
            datos_ejecucion = {
                'trigger_id': trigger_id,
                'estado': 'exitoso',
                'notificaciones_enviadas': 5,
                'empresas_procesadas': 10,
                'detalles': '{"test": true, "timestamp": "' + datetime.now().isoformat() + '"}'
            }
            
            resultado_ejec = service.registrar_ejecucion(datos_ejecucion)
            if resultado_ejec['success']:
                print(f"✓ Ejecución registrada: ID {resultado_ejec['data']['id']}")
            else:
                print(f"❌ Error registrando ejecución: {resultado_ejec.get('error')}")
                return False
            
            # Obtener historial
            print("\n📊 Obteniendo historial del trigger...")
            resultado_hist = service.obtener_historial_trigger(trigger_id, 10)
            if resultado_hist['success']:
                historial = resultado_hist['data']
                print(f"✓ Ejecuciones encontradas: {len(historial)}")
                
                if len(historial) > 0:
                    print("\n   Últimas ejecuciones:")
                    for ejec in historial[:3]:
                        print(f"   - {ejec['fecha_ejecucion']}: {ejec['estado']} "
                              f"({ejec['notificaciones_enviadas']} notif, {ejec['empresas_procesadas']} empresas)")
            else:
                print(f"❌ Error obteniendo historial: {resultado_hist.get('error')}")
                return False
            
            # Obtener estadísticas
            print("\n📈 Obteniendo estadísticas del trigger...")
            resultado_stats = service.obtener_estadisticas_trigger(trigger_id)
            if resultado_stats['success']:
                stats = resultado_stats['data']
                print(f"✓ Estadísticas calculadas:")
                print(f"   Total ejecuciones: {stats['total_ejecuciones']}")
                print(f"   Exitosas: {stats['exitosas']}")
                print(f"   Fallidas: {stats['fallidas']}")
                print(f"   Tasa de éxito: {stats['tasa_exito']}%")
                print(f"   Total notificaciones: {stats['total_notificaciones']}")
                print(f"   Total empresas: {stats['total_empresas']}")
            else:
                print(f"❌ Error obteniendo estadísticas: {resultado_stats.get('error')}")
                return False
            
            # Crear una ejecución fallida de prueba
            print("\n📝 Registrando ejecución fallida de prueba...")
            datos_fallida = {
                'trigger_id': trigger_id,
                'estado': 'fallido',
                'notificaciones_enviadas': 0,
                'empresas_procesadas': 8,
                'error_mensaje': 'Error de prueba: No se pudo conectar al servidor SMTP'
            }
            
            resultado_fail = service.registrar_ejecucion(datos_fallida)
            if resultado_fail['success']:
                print(f"✓ Ejecución fallida registrada: ID {resultado_fail['data']['id']}")
            
            # Obtener todas las ejecuciones
            print("\n📋 Obteniendo todas las ejecuciones...")
            resultado_todas = service.obtener_todas_ejecuciones(20)
            if resultado_todas['success']:
                todas = resultado_todas['data']
                print(f"✓ Total ejecuciones en sistema: {len(todas)}")
                
                # Agrupar por estado
                exitosas = sum(1 for e in todas if e['estado'] == 'exitoso')
                fallidas = sum(1 for e in todas if e['estado'] == 'fallido')
                print(f"   Exitosas: {exitosas}")
                print(f"   Fallidas: {fallidas}")
            
            print("\n✅ Todas las pruebas completadas exitosamente!")
            return True
        else:
            print("⚠️ No hay triggers en el sistema para probar")
            print("   Crea un trigger desde la interfaz web primero")
            return False
    else:
        print(f"❌ Error obteniendo triggers: {resultado.get('error')}")
        return False


if __name__ == "__main__":
    try:
        print()
        exito = test_historial()
        print("\n" + "=" * 60)
        print(f"RESULTADO: {'ÉXITO ✓' if exito else 'FALLÓ ✗'}")
        print("=" * 60 + "\n")
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
