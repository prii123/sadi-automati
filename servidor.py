"""
Script para ejecutar el servidor FastAPI
"""
import uvicorn
from app.config.settings import Settings
from api import create_app


def main():
    """Función principal para ejecutar el servidor"""
    settings = Settings.from_env()
    
    print("=" * 70)
    print("🚀 SISTEMA DE GESTIÓN DE FACTURACIÓN - FastAPI")
    print("=" * 70)
    print(f"Base de datos: {settings.DB_TYPE}")
    print(f"Servidor corriendo en: http://{settings.API_HOST}:{settings.API_PORT}")
    print("=" * 70)
    print("\n📚 Documentación automática:")
    print(f"  • Swagger UI: http://localhost:{settings.API_PORT}/docs")
    print(f"  • ReDoc: http://localhost:{settings.API_PORT}/redoc")
    print("\n🌐 Aplicación Web:")
    print(f"  • Página Principal: http://localhost:{settings.API_PORT}/")
    print(f"  • Dashboard: http://localhost:{settings.API_PORT}/app/dashboard")
    print(f"  • Empresas: http://localhost:{settings.API_PORT}/app/empresas")
    print(f"  • Notificaciones: http://localhost:{settings.API_PORT}/app/notificaciones")
    print("\n🔗 Endpoints principales API:")
    print(f"  • Información API: http://localhost:{settings.API_PORT}/api")
    print(f"  • Health: http://localhost:{settings.API_PORT}/health")
    print(f"  • Empresas: http://localhost:{settings.API_PORT}/api/empresas")
    print(f"  • Estadísticas: http://localhost:{settings.API_PORT}/api/estadisticas/resumen")
    print(f"  • Notificaciones: http://localhost:{settings.API_PORT}/api/notificaciones/vencimientos")
    print("\n" + "=" * 70 + "\n")
    
    # Crear aplicación
    app = create_app()
    
    # Ejecutar servidor
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )


if __name__ == '__main__':
    main()
