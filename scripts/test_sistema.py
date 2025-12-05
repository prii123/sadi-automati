"""
Script para probar las funcionalidades del sistema
"""
from app.config.settings import Settings
from app.config.database_factory import DatabaseFactory
from app.services.empresa_service import EmpresaService
from app.services.estadisticas_service import EstadisticasService
from app.services.notificacion_service import NotificacionService


def probar_sistema():
    """Ejecuta pruebas básicas del sistema"""
    
    print("=" * 80)
    print("PRUEBAS DEL SISTEMA DE GESTIÓN DE FACTURACIÓN")
    print("=" * 80)
    
    # Inicializar servicios
    settings = Settings.from_env()
    factory = DatabaseFactory(settings)
    repository = factory.create_empresa_repository()
    
    empresa_service = EmpresaService(repository)
    stats_service = EstadisticasService(repository)
    notif_service = NotificacionService(repository)
    
    print(f"\n✓ Configuración cargada")
    print(f"  Base de datos: {settings.DB_TYPE}")
    print(f"  Ubicación: {settings.DB_PATH}")
    
    # Prueba 1: Obtener empresas activas
    print("\n" + "-" * 80)
    print("PRUEBA 1: Obtener empresas activas")
    print("-" * 80)
    
    resultado = empresa_service.obtener_empresas_activas()
    if resultado['success']:
        print(f"✓ Se encontraron {resultado['total']} empresas activas")
        for empresa in resultado['data'][:3]:  # Mostrar solo las primeras 3
            print(f"\n  • {empresa['nombre']} (NIT: {empresa['nit']})")
            print(f"    Certificado: {'Activo' if empresa['certificado']['activo'] else 'Inactivo'}")
            print(f"    Resolución: {'Activa' if empresa['resolucion']['activo'] else 'Inactiva'}")
            print(f"    Documento: {'Activo' if empresa['documento']['activo'] else 'Inactivo'}")
    else:
        print(f"✗ Error: {resultado['error']}")
    
    # Prueba 2: Estadísticas generales
    print("\n" + "-" * 80)
    print("PRUEBA 2: Estadísticas generales")
    print("-" * 80)
    
    resultado = stats_service.obtener_estadisticas_generales()
    if resultado['success']:
        stats = resultado['data']
        print(f"\n✓ Total de empresas: {stats['total_empresas']}")
        
        print(f"\n  📜 CERTIFICADOS:")
        print(f"     Activos: {stats['certificados']['activos']}")
        print(f"     Renovados: {stats['certificados']['renovados']}")
        print(f"     Facturados: {stats['certificados']['facturados']}")
        print(f"     Pendientes Renovación: {stats['certificados']['pendientes_renovacion']}")
        print(f"     Pendientes Facturación: {stats['certificados']['pendientes_facturacion']}")
        
        print(f"\n  📋 RESOLUCIONES:")
        print(f"     Activas: {stats['resoluciones']['activos']}")
        print(f"     Renovadas: {stats['resoluciones']['renovados']}")
        print(f"     Facturadas: {stats['resoluciones']['facturados']}")
        print(f"     Pendientes Renovación: {stats['resoluciones']['pendientes_renovacion']}")
        print(f"     Pendientes Facturación: {stats['resoluciones']['pendientes_facturacion']}")
        
        print(f"\n  📄 DOCUMENTOS:")
        print(f"     Activos: {stats['documentos']['activos']}")
        print(f"     Renovados: {stats['documentos']['renovados']}")
        print(f"     Facturados: {stats['documentos']['facturados']}")
        print(f"     Pendientes Renovación: {stats['documentos']['pendientes_renovacion']}")
        print(f"     Pendientes Facturación: {stats['documentos']['pendientes_facturacion']}")
    else:
        print(f"✗ Error: {resultado['error']}")
    
    # Prueba 3: Notificaciones pendientes
    print("\n" + "-" * 80)
    print("PRUEBA 3: Notificaciones pendientes (30 días)")
    print("-" * 80)
    
    resultado = notif_service.obtener_notificaciones_pendientes(30)
    if resultado['success']:
        print(f"\n✓ {resultado['total']} empresas requieren atención\n")
        
        for notif in resultado['data'][:3]:  # Mostrar solo las primeras 3
            empresa = notif['empresa']
            print(f"  🔔 {empresa['nombre']} (NIT: {empresa['nit']})")
            
            for alerta in notif['alertas']:
                urgencia_emoji = "🔴" if alerta['urgencia'] == 'alta' else "🟡" if alerta['urgencia'] == 'media' else "🟢"
                print(f"     {urgencia_emoji} {alerta['modulo']}")
                print(f"        Vence en: {alerta['dias_restantes']} días")
                print(f"        Renovado: {'✓' if alerta['renovado'] else '✗'}")
                print(f"        Facturado: {'✓' if alerta['facturado'] else '✗'}")
            print()
    else:
        print(f"✗ Error: {resultado['error']}")
    
    # Prueba 4: Actualizar estado
    print("\n" + "-" * 80)
    print("PRUEBA 4: Actualizar estado de módulo")
    print("-" * 80)
    
    # Obtener la primera empresa para probar
    empresas = empresa_service.obtener_empresas_activas()
    if empresas['success'] and empresas['data']:
        empresa_test = empresas['data'][0]
        nit_test = empresa_test['nit']
        
        print(f"\nActualizando certificado_renovado de {empresa_test['nombre']}")
        print(f"Valor actual: {empresa_test['certificado']['renovado']}")
        
        nuevo_valor = 1 if empresa_test['certificado']['renovado'] == 0 else 0
        resultado = empresa_service.actualizar_estado_modulo(
            nit_test, 
            'certificado', 
            'renovado', 
            nuevo_valor
        )
        
        if resultado['success']:
            print(f"✓ Actualizado a: {nuevo_valor}")
            
            # Revertir el cambio
            resultado_revert = empresa_service.actualizar_estado_modulo(
                nit_test, 
                'certificado', 
                'renovado', 
                empresa_test['certificado']['renovado']
            )
            if resultado_revert['success']:
                print(f"✓ Revertido al valor original: {empresa_test['certificado']['renovado']}")
        else:
            print(f"✗ Error: {resultado['error']}")
    
    # Prueba 5: Empresas pendientes
    print("\n" + "-" * 80)
    print("PRUEBA 5: Empresas con pendientes")
    print("-" * 80)
    
    resultado = stats_service.obtener_empresas_pendientes()
    if resultado['success']:
        resumen = resultado['resumen']
        print(f"\n✓ Resumen de pendientes:")
        print(f"  Pendientes Renovación: {resumen['pendientes_renovacion']}")
        print(f"  Pendientes Facturación: {resumen['pendientes_facturacion']}")
        print(f"  Totalmente Completadas: {resumen['completadas']}")
    else:
        print(f"✗ Error: {resultado['error']}")
    
    print("\n" + "=" * 80)
    print("PRUEBAS COMPLETADAS")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    probar_sistema()
