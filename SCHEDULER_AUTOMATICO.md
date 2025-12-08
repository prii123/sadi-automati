# Scheduler Automático de Triggers

## 🚀 Descripción

El sistema ahora incluye un **scheduler automático** que ejecuta los triggers según su configuración de forma **completamente automática**, sin necesidad de tareas programadas del sistema operativo (cron, Windows Task Scheduler, etc.).

## ✨ Características

### 1. **Ejecución Automática**
- Se inicia automáticamente al levantar la aplicación
- Funciona dentro del contenedor Docker sin configuración adicional
- No requiere cron ni tareas externas

### 2. **Basado en APScheduler**
- Librería robusta y confiable de Python
- Soporta todas las frecuencias de triggers:
  - ⏰ **Diaria**: Ejecuta todos los días a una hora específica
  - 📅 **Semanal**: Ejecuta días específicos de la semana
  - 📆 **Mensual**: Ejecuta un día específico del mes
  - ⚡ **Personalizada**: Ejecuta cada N horas

### 3. **Recarga Automática**
- Se recarga automáticamente al crear/editar/eliminar triggers
- No necesitas reiniciar la aplicación
- Los cambios se aplican inmediatamente

### 4. **Registro Automático**
- Cada ejecución se registra en el historial
- Captura estado (exitoso/fallido)
- Guarda métricas y errores

## 🔧 Cómo Funciona

### Inicio Automático

Cuando inicias la aplicación:

```bash
uvicorn api:create_app --factory --host 0.0.0.0 --port 5000
```

Verás en la consola:

```
============================================================
🚀 INICIANDO SCHEDULER AUTOMÁTICO DE TRIGGERS
============================================================
INFO: TriggerScheduler inicializado
INFO: Cargando 2 triggers activos...
INFO:   • Notificación Diaria: Diaria a las 08:00
INFO:   • Reporte Semanal: Semanal (lunes, viernes) a las 15:00
INFO: ✓ 2 triggers programados
INFO: ✓ Scheduler iniciado correctamente
INFO:   Trabajos programados: 2
============================================================
```

### Ejecución de Triggers

Cuando un trigger se ejecuta, verás:

```
============================================================
EJECUTANDO TRIGGER ID: 1
============================================================
INFO: Trigger: Notificación Diaria
INFO: Destinatarios: admin@ejemplo.com
INFO: Prioridades: CRITICA, ALTA
INFO: ✓ Empresas con alertas: 5
INFO: ✓ Total alertas: 8
INFO: ⏳ Enviando notificaciones...
INFO: ✅ Email enviado exitosamente
INFO:    Destinatarios: 1
INFO:    Notificaciones: 8
INFO: ✓ Ejecución registrada en historial
============================================================
FIN EJECUCIÓN TRIGGER ID: 1
============================================================
```

## 📡 API del Scheduler

### GET /api/triggers/scheduler/status

Obtiene el estado del scheduler

**Respuesta:**
```json
{
  "success": true,
  "datos": {
    "running": true,
    "total_jobs": 2,
    "jobs": [
      {
        "id": "trigger_1",
        "name": "Notificación Diaria",
        "next_run": "2025-12-08T08:00:00"
      },
      {
        "id": "trigger_2",
        "name": "Reporte Semanal",
        "next_run": "2025-12-08T15:00:00"
      }
    ]
  }
}
```

### POST /api/triggers/scheduler/reload

Recarga manualmente todos los triggers

**Respuesta:**
```json
{
  "success": true,
  "message": "Scheduler recargado exitosamente",
  "datos": {
    "running": true,
    "total_jobs": 3
  }
}
```

## 🐳 Configuración en Docker

### Dockerfile (ya configurado)

El Dockerfile actual ya está listo para usar el scheduler:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El scheduler se inicia automáticamente con la aplicación
CMD ["uvicorn", "api:create_app", "--factory", "--host", "0.0.0.0", "--port", "5000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SMTP_USER=tu_email@gmail.com
      - SMTP_PASSWORD=tu_password
      - EMAIL_DESTINATARIOS=destino1@ejemplo.com,destino2@ejemplo.com
      - DB_PATH=/app/data/facturacion.db
    volumes:
      - ./data:/app/data  # Persistir base de datos
    restart: unless-stopped
```

## ⚙️ Variables de Entorno Requeridas

Para que los triggers funcionen, necesitas configurar en `.env`:

```bash
# Servidor SMTP (Gmail ejemplo)
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password

# Destinatarios por defecto (opcional, cada trigger puede tener los suyos)
EMAIL_DESTINATARIOS=admin@ejemplo.com,gerente@ejemplo.com

# Base de datos
DB_PATH=data/facturacion.db
```

## 🎯 Ejemplos de Uso

### 1. Crear un Trigger Diario

```bash
curl -X POST http://localhost:5000/api/triggers \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Notificación Diaria",
    "descripcion": "Envía alertas todos los días a las 8 AM",
    "frecuencia": "diaria",
    "hora": "08:00",
    "destinatarios": "admin@ejemplo.com",
    "prioridades": "CRITICA,ALTA",
    "activo": 1
  }'
```

El scheduler **automáticamente** lo programará para ejecutarse a las 8:00 AM cada día.

### 2. Crear un Trigger Semanal

```bash
curl -X POST http://localhost:5000/api/triggers \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Reporte Semanal",
    "descripcion": "Reporte de lunes y viernes",
    "frecuencia": "semanal",
    "hora": "15:00",
    "dias_semana": ["lunes", "viernes"],
    "destinatarios": "gerente@ejemplo.com",
    "prioridades": "CRITICA,ALTA,MEDIA",
    "activo": 1
  }'
```

Se ejecutará automáticamente los lunes y viernes a las 3:00 PM.

### 3. Crear un Trigger por Intervalos

```bash
curl -X POST http://localhost:5000/api/triggers \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Monitoreo Cada 4 Horas",
    "descripcion": "Revisa cada 4 horas",
    "frecuencia": "personalizada",
    "intervalo_horas": 4,
    "destinatarios": "soporte@ejemplo.com",
    "prioridades": "CRITICA",
    "activo": 1
  }'
```

Se ejecutará cada 4 horas automáticamente.

## 📊 Monitoreo

### Ver Estado del Scheduler

```bash
curl http://localhost:5000/api/triggers/scheduler/status
```

### Ver Historial de Ejecuciones

Ve a la interfaz web → Configuración → Historial

O usa la API:

```bash
curl http://localhost:5000/api/triggers/ejecuciones
```

## 🔍 Logs y Debugging

### En Docker

Ver logs en tiempo real:

```bash
docker-compose logs -f app
```

### Logs del Scheduler

Todos los logs del scheduler se muestran en la consola:

- ✅ Inicio del scheduler
- 📋 Triggers cargados
- ⏰ Próximas ejecuciones
- 🚀 Ejecuciones en progreso
- ✓ Ejecuciones completadas
- ❌ Errores

## 🛡️ Robustez

### Manejo de Errores

- Si un trigger falla, no afecta a los demás
- Los errores se registran en el historial
- El scheduler continúa funcionando

### Recuperación Automática

- Si se cae la aplicación, al reiniciar se recargan todos los triggers
- Las ejecuciones perdidas se pueden ver en el historial
- No se pierden configuraciones

### Zona Horaria

Por defecto usa `America/Bogota`. Para cambiar, edita `scheduler_service.py`:

```python
self.scheduler = BackgroundScheduler(timezone='America/Mexico_City')
```

## 🚀 Ventajas sobre Cron

| Característica | Scheduler Interno | Cron/Windows Tasks |
|----------------|-------------------|-------------------|
| Configuración | ✅ Automática | ❌ Manual |
| Funciona en Docker | ✅ Sí | ⚠️ Complicado |
| Interfaz Web | ✅ Sí | ❌ No |
| Actualización en tiempo real | ✅ Inmediata | ❌ Manual |
| Historial integrado | ✅ Sí | ❌ No |
| Portable | ✅ 100% | ❌ Depende del SO |

## 📝 Notas Importantes

1. **Persistencia**: La configuración se guarda en la base de datos, no se pierde al reiniciar

2. **Múltiples Instancias**: Si corres múltiples instancias de la aplicación, cada una ejecutará sus triggers. Para producción, considera usar un job queue como Celery o Redis.

3. **Zona Horaria**: Asegúrate de configurar la zona horaria correcta en el scheduler

4. **Recursos**: El scheduler es muy ligero, no consume recursos significativos

## 🔧 Solución de Problemas

### Los triggers no se ejecutan

1. Verifica que el trigger esté **activo** (activo=1)
2. Revisa los logs del scheduler
3. Verifica el estado: `GET /api/triggers/scheduler/status`

### No se envían emails

1. Verifica las credenciales SMTP en `.env`
2. Revisa los logs de ejecución
3. Consulta el historial para ver el error exacto

### Cambios no se aplican

Recarga manualmente el scheduler:

```bash
curl -X POST http://localhost:5000/api/triggers/scheduler/reload
```

## 🎓 Conclusión

El scheduler automático hace que tu sistema de notificaciones sea:

- ✅ **Autónomo**: No requiere intervención manual
- ✅ **Confiable**: Ejecuta triggers según configuración
- ✅ **Portable**: Funciona en cualquier entorno (local, Docker, cloud)
- ✅ **Fácil de usar**: Se configura desde la interfaz web
- ✅ **Auditable**: Todo se registra en el historial

¡Tu sistema está listo para producción! 🚀

---

**Versión:** 2.1.0  
**Fecha:** Diciembre 2025
