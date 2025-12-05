# Sistema de Gestión de Facturación Electrónica

Sistema completo con arquitectura en capas para gestionar notificaciones de facturación electrónica, certificados y resoluciones. API REST con **FastAPI**, frontend en JavaScript vanilla, y sistema de notificaciones por email con triggers programables.

## 🌟 Características Principales

- ✅ **API REST con FastAPI** - Framework moderno con documentación automática
- ✅ **Frontend SPA** - Interfaz de usuario completa sin frameworks
- ✅ **Sistema de Notificaciones** - Alertas automáticas por vencimientos
- ✅ **Email Automatizado** - Envío de notificaciones por Gmail
- ✅ **Triggers Configurables** - Programa envíos desde la interfaz web
- ✅ **Gestión de Empresas** - CRUD completo con módulos (Certificado, Resolución, Documento)
- ✅ **Dashboard** - Estadísticas y gráficos en tiempo real
- ✅ **Docker Ready** - Despliegue con un solo comando
- ✅ **Arquitectura Escalable** - Capas bien definidas, fácil de mantener

## 🏗️ Arquitectura del Proyecto

```
sadi/
├── app/
│   ├── models/              # Modelos de datos (Empresa, Trigger, etc.)
│   ├── repositories/        # Acceso a datos (SQLite/MySQL)
│   ├── services/            # Lógica de negocio
│   ├── api/                 # Endpoints REST y schemas
│   ├── web/                 # Rutas web y vistas
│   ├── static/              # Frontend (JS, CSS, imágenes)
│   ├── templates/           # HTML
│   └── config/              # Configuración y factory
├── scripts/                 # Scripts de utilidad
│   ├── init_db.py          # Inicializar BD
│   ├── test_email.py       # Probar envío de emails
│   └── enviar_notificaciones_automaticas.py
├── data/                    # Base de datos SQLite
├── logs/                    # Logs de aplicación
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Orquestación
├── deploy.sh               # Script de despliegue completo
├── quick-deploy.sh         # Instalación rápida
└── requirements.txt        # Dependencias Python
```

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🚀 Instalación

## 🚀 Inicio Rápido

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar proyecto
git clone https://github.com/tu-usuario/sadi.git
cd sadi

# 2. Configurar variables de entorno
cp .env.production.example .env.production
# Editar .env.production con tus credenciales

# 3. Iniciar con Docker
docker-compose up -d

# 4. Acceder a la aplicación
# http://localhost:5000
```

### Opción 2: Instalación Manual

```powershell
# 1. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
copy .env.example .env
# Editar .env con tus valores

# 4. Inicializar base de datos
python scripts/init_db.py

# 5. Iniciar aplicación
python api.py
```

La aplicación estará disponible en `http://localhost:5000`

**Documentación API:**
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 📱 Uso de la Aplicación

### Panel de Control (Dashboard)
- Visualiza estadísticas generales
- Empresas por estado
- Vencimientos próximos
- Alertas críticas

### Gestión de Empresas
- Crear/editar/eliminar empresas
- Gestionar módulos (Certificado, Resolución, Documento)
- Ver fechas de vencimiento
- Marcar como renovado/facturado

### Notificaciones
- Ver alertas de vencimientos
- Clasificadas por prioridad (Crítica, Alta, Media)
- Marcar como resueltas
- Ver detalles de cada empresa

### Configuración de Triggers
- Crear triggers de notificaciones automáticas
- Configurar frecuencia (diaria, semanal, mensual, personalizada)
- Definir destinatarios de emails
- Seleccionar prioridades a incluir
- Activar/desactivar triggers

## 📧 Sistema de Notificaciones por Email

### Configurar Gmail

1. Obtén una contraseña de aplicación:
   - Ve a https://myaccount.google.com/security
   - Activa "Verificación en 2 pasos"
   - Ve a "Contraseñas de aplicaciones"
   - Genera una contraseña para "Correo"

2. Configura en `.env`:
```env
SMTP_USER=tucorreo@gmail.com
SMTP_PASSWORD=tu_contraseña_de_16_caracteres
EMAIL_DESTINATARIOS=destinatario1@ejemplo.com,destinatario2@ejemplo.com
```

3. Prueba el envío:
```bash
python scripts/test_email.py
```

Ver documentación completa: `EMAIL_SERVICE.md`

## 📡 API REST Endpoints

### Empresas
- `GET /api/empresas` - Listar empresas
- `GET /api/empresas/{nit}` - Obtener por NIT
- `POST /api/empresas` - Crear empresa
- `PUT /api/empresas/{nit}` - Actualizar empresa
- `DELETE /api/empresas/{id}` - Eliminar empresa

### Notificaciones
- `GET /api/notificaciones/pendientes` - Notificaciones pendientes
- `GET /api/notificaciones/conteo` - Conteo por prioridad

### Estadísticas
- `GET /api/estadisticas/generales` - Estadísticas generales
- `GET /api/estadisticas/por-estado` - Empresas por estado

### Triggers
- `GET /api/triggers` - Listar triggers
- `POST /api/triggers` - Crear trigger
- `PUT /api/triggers/{id}` - Actualizar trigger
- `PATCH /api/triggers/{id}/estado` - Activar/desactivar
- `DELETE /api/triggers/{id}` - Eliminar trigger

### Email
- `POST /api/email/enviar-notificaciones` - Enviar notificaciones
- `GET /api/email/configurado` - Verificar configuración

- `GET /api/estadisticas` - Estadísticas generales del sistema
- `GET /api/estadisticas/pendientes` - Empresas con pendientes

### Notificaciones

- `GET /api/notificaciones?dias=30` - Notificaciones pendientes
- `GET /api/notificaciones/mes-actual` - Vencimientos del mes actual

## 📝 Ejemplos de uso de la API

### Obtener todas las empresas

```bash
curl http://localhost:5000/api/empresas
```

### Obtener empresa por NIT

```bash
curl http://localhost:5000/api/empresas/901747897
```

### Actualizar estado de módulo

```bash
curl -X PATCH http://localhost:5000/api/empresas/901747897/modulo \
  -H "Content-Type: application/json" \
  -d '{"modulo": "certificado", "campo": "renovado", "valor": 1}'
```

**Nota:** Con FastAPI también puedes probar todos los endpoints directamente desde `http://localhost:5000/docs`

### Obtener notificaciones

```bash
curl http://localhost:5000/api/notificaciones?dias=30
```

### Obtener estadísticas

```bash
curl http://localhost:5000/api/estadisticas
```

## 🔄 Cambiar de SQLite a MySQL

El sistema está diseñado para cambiar fácilmente de base de datos:

### 1. Crear la implementación MySQL

Crea el archivo `app/repositories/mysql_empresa_repository.py`:

```python
from app.repositories.base_repository import IRepository
# Implementar los mismos métodos que EmpresaRepository
# pero usando MySQL en lugar de SQLite
```

### 2. Actualizar el Factory

En `app/config/database_factory.py`, descomenta y completa la sección de MySQL.

### 3. Cambiar la configuración

Actualiza `.env` o variables de entorno:

```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=facturacion
DB_USER=root
DB_PASSWORD=tu_password
```

**¡Eso es todo!** No necesitas cambiar nada más en el código.

## 🏛️ Arquitectura - Capas

### 1. **Models** (Modelos de Datos)
- Define las estructuras de datos (`Empresa`, `ModuloEmpresa`)
- Sin lógica de negocio ni acceso a BD
- Inmutables y reutilizables

### 2. **Repositories** (Acceso a Datos)
- Única capa que accede a la base de datos
- Implementa la interfaz `IRepository`
- SQLite, MySQL, PostgreSQL - solo cambia esta capa

### 3. **Services** (Lógica de Negocio)
- Validaciones y reglas de negocio
- Orquesta operaciones complejas
- Independiente de la base de datos

### 4. **Config** (Configuración)
- Configuración centralizada
- Factory pattern para crear repositorios
- Variables de entorno

### 5. **API** (Capa de Presentación)
- Endpoints REST con FastAPI
- Validación automática con Pydantic
- Documentación automática (Swagger/ReDoc)
- Serialización de respuestas
- Type hints y async/await

## 🎨 Módulos del Sistema

El sistema maneja tres tipos de módulos por empresa:

1. **Certificado de Facturación Electrónica**
2. **Resolución de Facturación**
3. **Resolución Documentos Soporte**

Cada módulo tiene:
- Estado (activo/inactivo)
- Fechas (inicio/final)
- Flags (renovado/facturado)
- Notificación
- Comentarios

## 🔍 Funcionalidades Clave

### Gestión de Empresas
## 🐳 Despliegue en Digital Ocean

### Quick Deploy (5 minutos)

```bash
# 1. Crear Droplet Ubuntu 22.04 en Digital Ocean

# 2. Conectar al servidor
ssh root@TU_IP

# 3. Clonar proyecto
git clone https://github.com/tu-usuario/sadi.git
cd sadi

# 4. Ejecutar instalación automática
chmod +x quick-deploy.sh
./quick-deploy.sh
```

El script instalará Docker, configurará todo y dejará la aplicación corriendo.

### Deploy Manual (Control Total)

```bash
# 1. Preparar servidor
chmod +x deploy.sh
./deploy.sh
```

Ver guía completa en: `DEPLOY.md`

### Con Makefile

```bash
# Ver comandos disponibles
make help

# Construir e iniciar
make build
make up

# Ver logs
make logs

# Crear backup
make backup

# Desplegar en producción
make deploy
```

## 📚 Documentación

- `README.md` - Este archivo (documentación general)
- `DEPLOY.md` - Guía completa de despliegue
- `DOCKER.md` - Uso de Docker y contenedores
- `EMAIL_SERVICE.md` - Configuración de notificaciones por email
- `TRIGGERS_AUTOMATICOS.md` - Programación de envíos automáticos

## 🔧 Tecnologías Utilizadas

**Backend:**
- Python 3.11+
- FastAPI 2.0
- Uvicorn (ASGI server)
- SQLite / MySQL
- Pydantic (validación)

**Frontend:**
- JavaScript ES6+ (Vanilla)
- HTML5 + CSS3
- Chart.js (gráficos)

**DevOps:**
- Docker + Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)

**Notificaciones:**
- Gmail SMTP
- Sistema de triggers programables

## 🛠️ Desarrollo

### Estructura de Capas

```
Models (datos) → Repositories (acceso BD) → Services (lógica) → API (endpoints)
```

### Agregar Nueva Funcionalidad

1. **Modelo**: Define en `app/models/`
2. **Repositorio**: Crea operaciones CRUD en `app/repositories/`
3. **Servicio**: Implementa lógica en `app/services/`
4. **API**: Agrega endpoints en `app/api/routes.py`
5. **Frontend**: Crea vista en `app/static/js/`

### Comandos Útiles de Desarrollo

```bash
# Reiniciar BD con datos frescos
python scripts/init_db.py

# Probar email
python scripts/test_email.py

# Ver logs en tiempo real
tail -f logs/*.log

# Ejecutar tests
python scripts/test_sistema.py

# Reiniciar base de datos
rm data/facturacion.db
python scripts/init_db.py
```

## 📊 Datos de Ejemplo

El script `init_db.py` crea 5 empresas de ejemplo:

1. **Tech Solutions SAS** - Certificado por vencer en 30 días
2. **Comercializadora Andina** - Todo al día
3. **Juan Pérez E.U.** - Vencimiento inminente (10 días)
4. **Distribuciones del Norte** - Pendientes mixtos
5. **Servicios Integrales** - Módulos recientes

## 📦 Estructura de Respuestas API

Todas las respuestas siguen este formato estándar:

```json
{
  "success": true,
  "datos": { ... },
  "message": "Operación exitosa"
}
```

En caso de error:

```json
{
  "success": false,
  "error": "Descripción del error"
}
```

## 🔒 Seguridad

### Producción

- ✅ Cambia `SECRET_KEY` en `.env.production`
- ✅ Usa contraseñas de aplicación de Gmail (no tu contraseña personal)
- ✅ Configura firewall (ufw)
- ✅ Implementa SSL/TLS con Let's Encrypt
- ✅ Usa nginx como reverse proxy
- ✅ Mantén actualizadas las dependencias

### Buenas Prácticas

```bash
# Generar SECRET_KEY segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# No incluir .env en Git (ya está en .gitignore)
# Hacer backups regulares de la base de datos
# Monitorear logs para detectar problemas
```

## 🧪 Testing

```bash
# Ejecutar tests del sistema
python scripts/test_sistema.py

# Probar envío de email
python scripts/test_email.py

# Verificar API con curl
curl http://localhost:5000/api

# Health check
curl http://localhost:5000/api/notificaciones/conteo
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Changelog

### v2.0.0 (Diciembre 2025)
- ✨ Frontend SPA completo
- ✨ Sistema de notificaciones por email
- ✨ Triggers configurables desde interfaz web
- ✨ Docker y despliegue automatizado
- ✨ Dashboard con gráficos
- 🐛 Múltiples correcciones y mejoras

### v1.0.0 (Inicial)
- 🎉 API REST con FastAPI
- 🎉 CRUD de empresas
- 🎉 Sistema de notificaciones básico
- 🎉 Arquitectura en capas

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## 👨‍💻 Autor

Sistema desarrollado para SADI - Gestión de Facturación Electrónica

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- Digital Ocean por hosting confiable
- La comunidad Python por las herramientas

## 🔗 Enlaces Útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Digital Ocean Tutorials](https://www.digitalocean.com/community/tutorials)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Let's Encrypt](https://letsencrypt.org/)

---

⭐ **¿Te fue útil?** Dale una estrella al repositorio!

📫 **¿Preguntas?** Abre un issue en GitHub

🚀 **¡Feliz deployment!**

