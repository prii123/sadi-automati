"""
Rutas para servir las vistas HTML del frontend
"""
import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Obtener rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Crear router para las vistas
views_router = APIRouter(tags=["Frontend"])


def inject_env_vars(html_content: str) -> str:
    """Inyecta variables de entorno en el HTML"""
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
    return html_content.replace('${API_BASE_URL}', api_base_url)


def serve_index():
    """Función helper para servir el index.html"""
    index_path = TEMPLATES_DIR / "index.html"
    
    if not index_path.exists():
        return HTMLResponse(
            content="<h1>Error 404</h1><p>No se encontró la página index.html</p>",
            status_code=404
        )
    
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Inyectar variables de entorno
    content = inject_env_vars(content)
    
    return HTMLResponse(content=content)


def serve_login():
    """Función helper para servir el login.html"""
    login_path = TEMPLATES_DIR / "login.html"
    
    if not login_path.exists():
        return HTMLResponse(
            content="<h1>Error 404</h1><p>No se encontró la página login.html</p>",
            status_code=404
        )
    
    with open(login_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Inyectar variables de entorno
    content = inject_env_vars(content)
    
    return HTMLResponse(content=content)


@views_router.get("/login", response_class=HTMLResponse)
async def login():
    """Sirve la página de login"""
    return serve_login()


@views_router.get("/", response_class=HTMLResponse)
async def root():
    """Sirve la página principal en la ruta raíz"""
    return serve_index()


@views_router.get("/app", response_class=HTMLResponse)
async def index():
    """Sirve la página principal de la aplicación web"""
    return serve_index()


@views_router.get("/app/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Redirige al dashboard (misma página principal)"""
    return await index()


@views_router.get("/app/empresas", response_class=HTMLResponse)
async def empresas():
    """Redirige a la vista de empresas (misma página principal)"""
    return await index()


@views_router.get("/app/notificaciones", response_class=HTMLResponse)
async def notificaciones():
    """Redirige a la vista de notificaciones (misma página principal)"""
    return await index()


@views_router.get("/app/formulario", response_class=HTMLResponse)
async def formulario():
    """Redirige al formulario (misma página principal)"""
    return await index()


def get_static_files_app():
    """Retorna la aplicación de archivos estáticos"""
    return StaticFiles(directory=str(STATIC_DIR))
