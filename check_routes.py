import sys
sys.path.insert(0, '.')
from app.api.routes import empresas_router

print('Rutas en empresas_router:')
for route in empresas_router.routes:
    print(f'  {list(route.methods)[0] if route.methods else "GET"} {route.path}')
