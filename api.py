"""
Inicialización de la aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import Settings
from app.config.database_factory import DatabaseFactory
from app.services.empresa_service import EmpresaService
from app.services.estadisticas_service import EstadisticasService
from app.services.notificacion_service import NotificacionService
from app.services.trigger_service import TriggerService
from app.repositories.trigger_repository import TriggerRepository

# Importar routers
from app.api.routes import (
    info_router, 
    empresas_router, 
    estadisticas_router, 
    notificaciones_router,
    email_router,
    triggers_router,
    init_services
)
from app.web.views import views_router, get_static_files_app


def create_app() -> FastAPI:
    """
    Factory para crear y configurar la aplicación FastAPI
    
    Returns:
        FastAPI: Aplicación configurada
    """
    # Configuración
    settings = Settings.from_env()
    
    # Crear aplicación FastAPI
    app = FastAPI(
        title="Sistema de Gestión de Facturación",
        description="API REST para gestión de notificaciones de facturación electrónica",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especifica los dominios permitidos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Inicializar servicios
    factory = DatabaseFactory(settings)
    repository = factory.create_empresa_repository()
    
    empresa_service = EmpresaService(repository)
    stats_service = EstadisticasService(repository)
    notif_service = NotificacionService(repository)
    
    # Inicializar servicio de triggers
    trigger_repository = TriggerRepository(settings.DB_PATH)
    trigger_service = TriggerService(trigger_repository)
    
    # Inicializar servicios en las rutas
    init_services(empresa_service, stats_service, notif_service, trigger_service)
    
    # Registrar router de vistas web primero (para capturar la ruta raíz)
    app.include_router(views_router)
    
    # Registrar routers de la API
    app.include_router(info_router)
    app.include_router(empresas_router)
    app.include_router(estadisticas_router)
    app.include_router(notificaciones_router)
    app.include_router(email_router)
    app.include_router(triggers_router)
    
    # Montar archivos estáticos
    app.mount("/static", get_static_files_app(), name="static")
    
    # Manejadores de errores personalizados
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={
                'success': False,
                'error': 'Recurso no encontrado'
            }
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'error': 'Error interno del servidor'
            }
        )
    
    return app
