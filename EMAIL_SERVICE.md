# 📧 Servicio de Envío de Notificaciones por Email

Este módulo permite enviar las notificaciones de vencimientos automáticamente por correo electrónico usando Gmail.

## 🚀 Configuración

### 1. Obtener Contraseña de Aplicación de Gmail

Para usar Gmail con este servicio, necesitas generar una **Contraseña de Aplicación**:

1. Ve a tu **Cuenta de Google**: https://myaccount.google.com/
2. En el menú izquierdo, selecciona **Seguridad**
3. En "Cómo inicias sesión en Google", activa la **Verificación en 2 pasos** (si no está activa)
4. Una vez activada, busca **Contraseñas de aplicaciones**
5. Selecciona:
   - App: **Correo**
   - Dispositivo: **Otro (nombre personalizado)** → escribe "Sistema Facturación"
6. Haz clic en **Generar**
7. Copia la **contraseña de 16 caracteres** que aparece

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (o edita el existente) y agrega:

```env
SMTP_USER=tucorreo@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Importante:** 
- `SMTP_USER` es tu email completo de Gmail
- `SMTP_PASSWORD` es la contraseña de aplicación de 16 caracteres (puedes incluir o no los espacios)

### 3. Instalar Dependencias

El módulo usa librerías estándar de Python, no requiere instalaciones adicionales.

## 📝 Uso

### Opción 1: Script de Prueba

El proyecto incluye un script interactivo para probar el envío:

```powershell
python scripts/test_email.py
```

Este script:
- Verifica que las credenciales estén configuradas
- Obtiene las notificaciones pendientes
- Muestra un resumen de las alertas
- Te permite enviar un email de prueba

### Opción 2: API REST

Una vez configurado, la API tiene los siguientes endpoints:

#### Enviar Notificaciones Pendientes

```http
POST /api/email/enviar-notificaciones
Content-Type: application/json

{
  "destinatarios": ["correo1@ejemplo.com", "correo2@ejemplo.com"]
}
```

**Respuesta:**
```json
{
  "success": true,
  "datos": {
    "message": "Email enviado exitosamente a 2 destinatario(s)",
    "destinatarios": ["correo1@ejemplo.com", "correo2@ejemplo.com"],
    "total_notificaciones": 15
  }
}
```

#### Enviar Email Simple

```http
POST /api/email/enviar-simple
Content-Type: application/json

{
  "destinatario": "correo@ejemplo.com",
  "asunto": "Prueba de Email",
  "mensaje": "Este es un mensaje de prueba"
}
```

#### Verificar Configuración

```http
GET /api/email/configurado
```

**Respuesta:**
```json
{
  "success": true,
  "configurado": true,
  "smtp_user": "tucorreo@gmail.com",
  "mensaje": "Configurado correctamente"
}
```

### Opción 3: Uso Programático

```python
from app.services.email_service import EmailService
from app.services.notificacion_service import NotificacionService

# Inicializar servicios
email_service = EmailService('tucorreo@gmail.com', 'tu_contraseña_app')
notif_service = NotificacionService(repository)

# Obtener notificaciones
resultado = notif_service.obtener_notificaciones_pendientes()
notificaciones = resultado.get('data', [])

# Enviar por email
resultado = email_service.enviar_notificaciones_vencimientos(
    destinatarios=['destinatario@ejemplo.com'],
    notificaciones=notificaciones
)

print(resultado)
```

## 📧 Formato del Email

El email enviado incluye:

- **Header**: Título y fecha del reporte
- **Resumen**: Conteo de notificaciones por prioridad
- **Notificaciones agrupadas por prioridad**:
  - 🚨 **Críticas** (0-5 días para vencer)
  - ⚠️ **Alta prioridad** (6-30 días para vencer)
  - ℹ️ **Prioridad media** (31-60 días para vencer)

Para cada notificación muestra:
- Nombre de la empresa y NIT
- Tipo de módulo (Certificado, Resolución, Documento)
- Motivo de la alerta
- Fecha de vencimiento
- Días restantes
- Estado de renovado/facturado

## 🔒 Seguridad

**Mejores Prácticas:**

1. ✅ **Nunca** incluyas el archivo `.env` en el control de versiones
2. ✅ Usa **contraseñas de aplicación**, no tu contraseña personal de Gmail
3. ✅ Limita los permisos de la contraseña de aplicación
4. ✅ En producción, usa variables de entorno del sistema
5. ✅ Revoca las contraseñas de aplicación que ya no uses

## ⚙️ Automatización (Opcional)

### Envío Diario Programado con Task Scheduler (Windows)

1. Crea un script `enviar_notificaciones_diarias.py`:

```python
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.email_service import EmailService
from app.services.notificacion_service import NotificacionService
from app.config.database_factory import DatabaseFactory
from app.config.settings import Settings

settings = Settings.from_env()
db_factory = DatabaseFactory(settings)
repository = db_factory.create_empresa_repository()

notif_service = NotificacionService(repository)
email_service = EmailService()

resultado = notif_service.obtener_notificaciones_pendientes()
notificaciones = resultado.get('data', [])

if notificaciones:
    email_service.enviar_notificaciones_vencimientos(
        destinatarios=['admin@tuempresa.com'],
        notificaciones=notificaciones
    )
```

2. En **Programador de tareas** de Windows:
   - Crea una nueva tarea básica
   - Desencadenador: Diariamente a las 8:00 AM
   - Acción: Iniciar programa
   - Programa: `python`
   - Argumentos: `ruta\al\enviar_notificaciones_diarias.py`

## 🐛 Solución de Problemas

### Error: "Authentication failed"

**Causas posibles:**
- Email o contraseña incorrectos
- No usaste una contraseña de aplicación
- La verificación en 2 pasos no está activa

**Solución:**
1. Verifica que `SMTP_USER` sea tu email completo
2. Asegúrate de usar la **contraseña de aplicación** de 16 caracteres
3. Activa la verificación en 2 pasos en tu cuenta de Google

### Error: "SMTP connection failed"

**Causas posibles:**
- Problemas de conexión a internet
- Firewall bloqueando el puerto 587
- Gmail bloqueando acceso desde tu ubicación

**Solución:**
1. Verifica tu conexión a internet
2. Intenta acceder a https://gmail.com para confirmar que funciona
3. Revisa la configuración del firewall

### El email no llega

**Causas posibles:**
- El email está en la carpeta de spam
- El email destino es incorrecto

**Solución:**
1. Revisa la carpeta de spam/correo no deseado
2. Verifica que el email destino esté bien escrito
3. Prueba enviando a otro email

## 📚 Referencias

- [Contraseñas de aplicaciones de Google](https://support.google.com/accounts/answer/185833)
- [SMTP de Gmail](https://support.google.com/mail/answer/7126229)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
