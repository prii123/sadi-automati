"""
Middleware de autenticación para proteger rutas
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida tokens de autenticación en todas las rutas
    """
    
    # Rutas públicas que no requieren autenticación
    RUTAS_PUBLICAS = [
        "/api/auth/login",
        "/health",
        "/api",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    # Rutas estáticas
    RUTAS_ESTATICAS = [
        "/static",
        "/favicon.ico"
    ]
    
    def __init__(self, app, auth_service):
        """
        Inicializa el middleware
        
        Args:
            app: Aplicación FastAPI
            auth_service: Servicio de autenticación
        """
        super().__init__(app)
        self.auth_service = auth_service

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Procesa cada request y valida autenticación
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware/handler
            
        Returns:
            Response
        """
        path = request.url.path
        
        # Permitir rutas públicas
        if path in self.RUTAS_PUBLICAS:
            return await call_next(request)
        
        # Permitir rutas estáticas
        for ruta_estatica in self.RUTAS_ESTATICAS:
            if path.startswith(ruta_estatica):
                return await call_next(request)
        
        # Verificar si es la página de login
        if path == "/" or path == "/login":
            return await call_next(request)
        
        # print(f"\n🔍 AUTH MIDDLEWARE - Path: {path}")
        # print(f"🔍 Headers recibidos: {dict(request.headers)}")
        # print(f"🔍 Cookies recibidas: {dict(request.cookies)}")
        
        # Intentar obtener token desde header Authorization o cookies
        token = None
        auth_header = request.headers.get("Authorization")
        
        # print(f"🔍 Authorization header: {auth_header}")
        
        if auth_header:
            # Extraer token del header (formato: "Bearer TOKEN")
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != 'bearer':
                    print(f"⚠️ Esquema inválido: {scheme}")
                    token = None
                else:
                    print(f"✅ Token extraído del header: {token[:20]}...")
            except ValueError:
                print(f"❌ Error al parsear Authorization header")
                token = None
        
        # Si no hay token en el header, intentar obtenerlo de cookies
        if not token:
            token = request.cookies.get("token")
            if token:
                print(f"✅ Token obtenido de cookie: {token[:20]}...")
            else:
                print(f"❌ No hay token en cookies")
        
        # Si aún no hay token, retornar 401
        if not token:
            print(f"❌ NO HAY TOKEN - Retornando 401")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    'success': False,
                    'error': 'No autorizado. Token requerido.',
                    'redirect': '/login'
                }
            )
        
        print(f"🔐 Validando token: {token[:20]}...")
        
        # Validar token
        datos_token = self.auth_service.validar_token(token)
        
        if not datos_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    'success': False,
                    'error': 'Token inválido o expirado',
                    'redirect': '/login'
                }
            )
        
        # Agregar datos del usuario al request
        request.state.usuario = datos_token
        request.state.token = token
        
        # Continuar con la request
        return await call_next(request)


def require_auth(request: Request):
    """
    Dependency para verificar autenticación en rutas específicas
    
    Args:
        request: Request HTTP
        
    Returns:
        Datos del usuario autenticado
        
    Raises:
        HTTPException si no está autenticado
    """
    if not hasattr(request.state, 'usuario'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    
    return request.state.usuario


def require_admin(request: Request):
    """
    Dependency para verificar que el usuario sea admin
    
    Args:
        request: Request HTTP
        
    Returns:
        Datos del usuario admin
        
    Raises:
        HTTPException si no es admin
    """
    usuario = require_auth(request)
    
    if usuario.get('rol') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador."
        )
    
    return usuario
