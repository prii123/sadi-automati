"""
Inicialización de la aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from app.config.settings import Settings
from app.config.database_factory import DatabaseFactory
from app.services.empresa_service import EmpresaService
from app.services.estadisticas_service import EstadisticasService
from app.services.notificacion_service import NotificacionService
from app.services.trigger_service import TriggerService
from app.services.auth_service import AuthService
from app.repositories.trigger_repository import TriggerRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.api.auth_middleware import AuthMiddleware

# Importar routers
from app.api.routes import (
    info_router, 
    auth_router,
    empresas_router, 
    estadisticas_router, 
    notificaciones_router,
    email_router,
    triggers_router,
    db_router,
    init_services
)
from app.web.views import views_router, get_static_files_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación
    Se ejecuta al iniciar y detener la aplicación
    """
    # Startup: Iniciar el scheduler automático
    print("\n" + "=" * 60)
    print("🚀 INICIANDO SCHEDULER AUTOMÁTICO DE TRIGGERS")
    print("=" * 60)
    try:
        start_scheduler()
        print("✅ Scheduler iniciado correctamente")
    except Exception as e:
        print(f"⚠️  Error iniciando scheduler: {str(e)}")
    print("=" * 60 + "\n")
    
    yield  # La aplicación está corriendo
    
    # Shutdown: Detener el scheduler
    print("\n" + "=" * 60)
    print("🛑 DETENIENDO SCHEDULER")
    print("=" * 60)
    try:
        stop_scheduler()
        print("✅ Scheduler detenido correctamente")
    except Exception as e:
        print(f"⚠️  Error deteniendo scheduler: {str(e)}")
    print("=" * 60 + "\n")


def create_app() -> FastAPI:
    """
    Factory para crear y configurar la aplicación FastAPI
    
    Returns:
        FastAPI: Aplicación configurada
    """
    # Configuración
    settings = Settings.from_env()
    
    # Crear aplicación FastAPI con lifespan
    app = FastAPI(
        title="Sistema de Gestión de Facturación",
        description="API REST para gestión de notificaciones de facturación electrónica",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configurar CORS
    # En Docker, el frontend y backend están en el mismo origen
    cors_origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS != ['*'] else ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
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
    
    # Inicializar servicio de triggers con PostgreSQL
    trigger_repository = TriggerRepository(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    trigger_service = TriggerService(trigger_repository)
    
    # Inicializar servicio de autenticación con PostgreSQL
    usuario_repository = UsuarioRepository(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    auth_service = AuthService(usuario_repository)
    
    # Inicializar servicios en las rutas
    init_services(empresa_service, stats_service, notif_service, auth_service, trigger_service)
    
    # Agregar middleware de autenticación
    app.add_middleware(AuthMiddleware, auth_service=auth_service)
    
    # Registrar router de vistas web primero (para capturar la ruta raíz)
    app.include_router(views_router)
    
    # Registrar routers de la API
    app.include_router(info_router)
    app.include_router(auth_router)
    app.include_router(empresas_router)
    app.include_router(estadisticas_router)
    app.include_router(notificaciones_router)
    app.include_router(email_router)
    app.include_router(triggers_router)
    app.include_router(db_router)
    
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
