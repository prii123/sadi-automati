"""
Script para inicializar la base de datos con datos de ejemplo
"""
from datetime import datetime, timedelta
from app.config.settings import Settings
from app.config.database_factory import DatabaseFactory
from app.models.empresa import Empresa, ModuloEmpresa
from app.services.empresa_service import EmpresaService


def crear_datos_ejemplo():
    """Crea datos de ejemplo en la base de datos"""
    
    print("=" * 60)
    print("INICIALIZANDO BASE DE DATOS CON DATOS DE EJEMPLO")
    print("=" * 60)
    
    # Configuración
    settings = Settings.from_env()
    factory = DatabaseFactory(settings)
    repository = factory.create_empresa_repository()
    service = EmpresaService(repository)
    
    print(f"\n✓ Base de datos: {settings.DB_TYPE}")
    print(f"✓ Ubicación: {settings.DB_PATH}")
    
    # Datos de ejemplo
    empresas_ejemplo = [
        {
            'nit': '901747897',
            'nombre': 'Tech Solutions S.A.S',
            'tipo': 'Persona Jurídica',
            'certificado': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=365),
                'fecha_final': datetime.now() + timedelta(days=30),
                'notificacion': 'notificar@techsolutions.com',
                'renovado': 0,
                'facturado': 0,
                'comentarios': 'Pendiente renovación próxima'
            },
            'resolucion': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=180),
                'fecha_final': datetime.now() + timedelta(days=90),
                'notificacion': 'notificar@techsolutions.com',
                'renovado': 1,
                'facturado': 0,
                'comentarios': 'Renovado pero pendiente facturación'
            },
            'documento': {
                'activo': 0
            }
        },
        {
            'nit': '900123456',
            'nombre': 'Comercializadora Andina LTDA',
            'tipo': 'Persona Jurídica',
            'certificado': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=200),
                'fecha_final': datetime.now() + timedelta(days=165),
                'notificacion': 'admin@andina.com',
                'renovado': 1,
                'facturado': 1,
                'comentarios': 'Todo al día'
            },
            'resolucion': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=200),
                'fecha_final': datetime.now() + timedelta(days=165),
                'notificacion': 'admin@andina.com',
                'renovado': 1,
                'facturado': 1,
                'comentarios': 'Todo al día'
            },
            'documento': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=100),
                'fecha_final': datetime.now() + timedelta(days=265),
                'notificacion': 'admin@andina.com',
                'renovado': 1,
                'facturado': 0,
                'comentarios': 'Pendiente facturación'
            }
        },
        {
            'nit': '79123456',
            'nombre': 'Juan Pérez - Consultor',
            'tipo': 'Persona Natural',
            'certificado': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=300),
                'fecha_final': datetime.now() + timedelta(days=10),
                'notificacion': 'juan.perez@email.com',
                'renovado': 0,
                'facturado': 0,
                'comentarios': 'URGENTE: Vencimiento inminente'
            },
            'resolucion': {
                'activo': 0
            },
            'documento': {
                'activo': 0
            }
        },
        {
            'nit': '890345678',
            'nombre': 'Distribuciones del Norte S.A.',
            'tipo': 'Persona Jurídica',
            'certificado': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=150),
                'fecha_final': datetime.now() + timedelta(days=215),
                'notificacion': 'contacto@delnorte.co',
                'renovado': 1,
                'facturado': 1,
                'comentarios': None
            },
            'resolucion': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=150),
                'fecha_final': datetime.now() + timedelta(days=215),
                'notificacion': 'contacto@delnorte.co',
                'renovado': 0,
                'facturado': 1,
                'comentarios': 'Facturado pero pendiente renovación'
            },
            'documento': {
                'activo': 0
            }
        },
        {
            'nit': '900987654',
            'nombre': 'Servicios Integrales Colombia',
            'tipo': 'Persona Jurídica',
            'certificado': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=250),
                'fecha_final': datetime.now() + timedelta(days=115),
                'notificacion': 'info@serviciosintegrales.com',
                'renovado': 1,
                'facturado': 0,
                'comentarios': 'Renovado, falta facturar'
            },
            'resolucion': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=250),
                'fecha_final': datetime.now() + timedelta(days=115),
                'notificacion': 'info@serviciosintegrales.com',
                'renovado': 1,
                'facturado': 1,
                'comentarios': 'Completado'
            },
            'documento': {
                'activo': 1,
                'fecha_inicio': datetime.now() - timedelta(days=80),
                'fecha_final': datetime.now() + timedelta(days=285),
                'notificacion': 'info@serviciosintegrales.com',
                'renovado': 0,
                'facturado': 0,
                'comentarios': 'Reciente, aún sin gestionar'
            }
        }
    ]
    
    print("\n" + "-" * 60)
    print("CREANDO EMPRESAS DE EJEMPLO")
    print("-" * 60)
    
    empresas_creadas = 0
    empresas_omitidas = 0
    
    for datos in empresas_ejemplo:
        # Verificar si ya existe
        if repository.exists_by_nit(datos['nit']):
            print(f"\n⚠ {datos['nombre']} (NIT: {datos['nit']}) ya existe - omitida")
            empresas_omitidas += 1
            continue
        
        # Crear módulos
        certificado = ModuloEmpresa(**datos.get('certificado', {}))
        resolucion = ModuloEmpresa(**datos.get('resolucion', {}))
        documento = ModuloEmpresa(**datos.get('documento', {}))
        
        # Crear empresa
        empresa = Empresa(
            nit=datos['nit'],
            nombre=datos['nombre'],
            tipo=datos['tipo'],
            estado='activo',
            certificado=certificado,
            resolucion=resolucion,
            documento=documento
        )
        
        # Guardar
        resultado = service.crear_empresa(empresa)
        
        if resultado['success']:
            print(f"\n✓ Creada: {datos['nombre']}")
            print(f"  NIT: {datos['nit']}")
            print(f"  Certificado: {'✓' if certificado.activo else '✗'} | "
                  f"Renovado: {'✓' if certificado.renovado else '✗'} | "
                  f"Facturado: {'✓' if certificado.facturado else '✗'}")
            print(f"  Resolución:  {'✓' if resolucion.activo else '✗'} | "
                  f"Renovado: {'✓' if resolucion.renovado else '✗'} | "
                  f"Facturado: {'✓' if resolucion.facturado else '✗'}")
            print(f"  Documento:   {'✓' if documento.activo else '✗'} | "
                  f"Renovado: {'✓' if documento.renovado else '✗'} | "
                  f"Facturado: {'✓' if documento.facturado else '✗'}")
            empresas_creadas += 1
        else:
            print(f"\n✗ Error al crear {datos['nombre']}: {resultado.get('error')}")
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"✓ Empresas creadas: {empresas_creadas}")
    print(f"⚠ Empresas omitidas (ya existían): {empresas_omitidas}")
    print(f"📊 Total de empresas: {empresas_creadas + empresas_omitidas}")
    print("=" * 60)
    print("\n✓ Base de datos inicializada correctamente\n")


if __name__ == '__main__':
    crear_datos_ejemplo()
