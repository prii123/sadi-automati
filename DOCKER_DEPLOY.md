# 🐳 Guía de Despliegue en Docker

## Configuración para Docker

### 1. **CORS y Seguridad**

Como el frontend y backend se ejecutan en el **mismo contenedor** y **mismo origen** (localhost:5000), NO necesitas configuración especial de CORS. Sin embargo, la configuración ya está optimizada:

```env
CORS_ORIGINS=*
```

Para producción con dominio específico:
```env
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

### 2. **Variables de Entorno**

**Desarrollo:**
```bash
# Usar .env local
docker run -v $(pwd)/.env:/app/.env -p 5000:5000 sadi-app
```

**Producción:**
```bash
# Copiar .env.docker a .env
cp .env.docker .env

# Editar .env con tus valores
nano .env

# Construir y ejecutar
docker build -t sadi-app .
docker run --env-file .env -p 5000:5000 sadi-app
```

### 3. **API Base URL**

**En Docker:**
```env
API_BASE_URL=http://localhost:5000/api
```

**Con dominio:**
```env
API_BASE_URL=https://tudominio.com/api
```

### 4. **Persistencia de Datos**

La base de datos SQLite necesita un volumen:

```bash
docker run -v $(pwd)/data:/app/data -p 5000:5000 sadi-app
```

### 5. **Docker Compose (Recomendado)**

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  sadi-app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Ejecutar:
```bash
docker-compose up -d
```

### 6. **Configuraciones Importantes**

#### **✅ Lo que YA está configurado:**

1. **CORS**: Configurable vía `CORS_ORIGINS`
2. **API Base URL**: Configurable vía `API_BASE_URL`
3. **Host/Port**: Configurables para Docker
4. **Persistencia**: Volúmenes para `/app/data` y `/app/logs`
5. **Health Check**: Endpoint `/health` para verificar estado
6. **Usuario Admin**: Se crea automáticamente (admin/admin123)

#### **⚠️ Cambiar en Producción:**

1. **SECRET_KEY**: Generar una clave segura
2. **SMTP Credentials**: Tus credenciales reales
3. **API_DEBUG**: Cambiar a `False`
4. **CORS_ORIGINS**: Especificar dominios permitidos
5. **Admin Password**: Cambiar después del primer login

### 7. **Acceso a la Aplicación**

Después de desplegar:

```
Frontend: http://localhost:5000
Login: http://localhost:5000/login
API Docs: http://localhost:5000/docs
Health: http://localhost:5000/health
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **Cambiar la contraseña después del primer login**

### 8. **Verificar Despliegue**

```bash
# Ver logs
docker logs -f <container_id>

# Verificar health
curl http://localhost:5000/health

# Verificar API
curl http://localhost:5000/api

# Ver containers
docker ps
```

### 9. **Troubleshooting**

**Problema: Error 401 Unauthorized**
- ✅ Solución: El token se guarda en cookies y localStorage automáticamente
- ✅ El middleware acepta tokens de ambas fuentes
- ✅ No requiere configuración adicional en Docker

**Problema: CORS error**
- Verifica `CORS_ORIGINS` en .env
- En mismo origen (Docker), usa `*` o el dominio específico
- Reinicia el contenedor después de cambiar .env

**Problema: Base de datos no persiste**
- Asegúrate de montar el volumen: `-v $(pwd)/data:/app/data`
- Verifica permisos del directorio

### 10. **Mejores Prácticas**

1. ✅ Usar volúmenes para persistencia
2. ✅ Usar `.env` para configuración
3. ✅ NO incluir `.env` en el repositorio
4. ✅ Cambiar credenciales por defecto
5. ✅ Usar Docker Compose para orquestación
6. ✅ Configurar logs externos
7. ✅ Implementar backups de la base de datos
8. ✅ Usar reverse proxy (nginx) en producción

## Resumen de Configuración para Docker

**Todo está listo para Docker**, solo necesitas:

1. Copiar `.env.docker` a `.env`
2. Configurar tus credenciales SMTP
3. Ajustar `API_BASE_URL` si usas dominio
4. Construir: `docker build -t sadi-app .`
5. Ejecutar: `docker run --env-file .env -v $(pwd)/data:/app/data -p 5000:5000 sadi-app`

✅ **No hay problemas de CORS** porque frontend y backend están en el mismo origen.
✅ **Autenticación funciona** con cookies y localStorage.
✅ **Todo está parametrizado** via variables de entorno.
