"""
Ejemplo adicional: Cómo usar el sistema de forma programática
"""
from app.config.settings import Settings
from app.config.database_factory import DatabaseFactory
from app.services.empresa_service import EmpresaService
from app.models.empresa import Empresa, ModuloEmpresa
from datetime import datetime, timedelta


def ejemplo_uso():
    """Ejemplo completo de uso del sistema"""
    
    # 1. Inicializar el sistema
    print("=" * 60)
    print("EJEMPLO DE USO DEL SISTEMA")
    print("=" * 60)
    
    settings = Settings.from_env()
    factory = DatabaseFactory(settings)
    repository = factory.create_empresa_repository()
    service = EmpresaService(repository)
    
    # 2. Crear una nueva empresa
    print("\n--- Creando nueva empresa ---")
    
    certificado = ModuloEmpresa(
        activo=1,
        fecha_inicio=datetime.now(),
        fecha_final=datetime.now() + timedelta(days=365),
        notificacion="contacto@ejemplo.com",
        renovado=0,
        facturado=0,
        comentarios="Nueva empresa de ejemplo"
    )
    
    nueva_empresa = Empresa(
        nit="900111222",
        nombre="Empresa de Ejemplo S.A.S",
        tipo="Persona Jurídica",
        estado="activo",
        certificado=certificado
    )
    
    resultado = service.crear_empresa(nueva_empresa)
    if resultado['success']:
        print(f"✓ Empresa creada: {resultado['data']['nombre']}")
    else:
        print(f"✗ Error: {resultado['error']}")
    
    # 3. Buscar empresa por NIT
    print("\n--- Buscando empresa por NIT ---")
    
    resultado = service.obtener_empresa_por_nit("900111222")
    if resultado['success']:
        empresa = resultado['data']
        print(f"✓ Encontrada: {empresa['nombre']}")
        print(f"  NIT: {empresa['nit']}")
        print(f"  Certificado activo: {empresa['certificado']['activo']}")
    
    # 4. Actualizar estado de módulo
    print("\n--- Actualizando estado ---")
    
    resultado = service.actualizar_estado_modulo(
        nit="900111222",
        modulo="certificado",
        campo="renovado",
        valor=1
    )
    if resultado['success']:
        print(f"✓ Estado actualizado correctamente")
    
    # 5. Listar todas las empresas activas
    print("\n--- Listando empresas activas ---")
    
    resultado = service.obtener_empresas_activas()
    if resultado['success']:
        print(f"✓ Total de empresas activas: {resultado['total']}")
        for emp in resultado['data'][:3]:
            print(f"  • {emp['nombre']} (NIT: {emp['nit']})")
    
    print("\n" + "=" * 60)
    print("EJEMPLO COMPLETADO")
    print("=" * 60)


if __name__ == '__main__':
    ejemplo_uso()
