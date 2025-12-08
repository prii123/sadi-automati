# Historial de Ejecuciones de Triggers

## 📊 Descripción

Se ha agregado un sistema completo de historial de ejecuciones para los triggers automáticos de notificaciones. Ahora puedes revisar cuántas veces se ha ejecutado cada trigger, cuántas notificaciones se enviaron, y si hubo errores.

## ✨ Características Nuevas

### 1. **Registro Automático de Ejecuciones**
- Cada vez que un trigger se ejecuta, se registra automáticamente en el historial
- Se guarda: fecha/hora, estado (exitoso/fallido), notificaciones enviadas, empresas procesadas
- Los errores se registran con mensajes detallados

### 2. **Estadísticas por Trigger**
- Total de ejecuciones
- Ejecuciones exitosas y fallidas
- Tasa de éxito (porcentaje)
- Total de notificaciones enviadas
- Total de empresas procesadas

### 3. **Interfaz Web Mejorada**
En la sección "Configuración" (⚙️) ahora hay dos pestañas:

#### **📋 Triggers**
- Lista de todos los triggers configurados
- Crear, editar, eliminar triggers
- Activar/desactivar triggers

#### **📊 Historial**
- Ver todas las ejecuciones de todos los triggers
- Filtrar por trigger específico
- Mostrar últimas 50, 100 o 200 ejecuciones
- Estadísticas detalladas de cada trigger

## 🔧 Nuevos Endpoints API

### **GET /api/triggers/ejecuciones**
Obtiene todas las ejecuciones de todos los triggers

**Parámetros:**
- `limit` (opcional): Número máximo de registros (default: 100, max: 500)

**Respuesta:**
```json
{
  "success": true,
  "datos": [
    {
      "id": 1,
      "trigger_id": 1,
      "trigger_nombre": "Notificación Diaria",
      "fecha_ejecucion": "2025-12-07T08:00:00",
      "estado": "exitoso",
      "notificaciones_enviadas": 5,
      "empresas_procesadas": 10,
      "error_mensaje": null,
      "detalles": "{\"criticas\": 2, \"altas\": 3}"
    }
  ]
}
```

### **GET /api/triggers/{trigger_id}/ejecuciones**
Obtiene el historial de un trigger específico

**Parámetros:**
- `trigger_id`: ID del trigger
- `limit` (opcional): Número máximo de registros (default: 50, max: 200)

### **GET /api/triggers/{trigger_id}/estadisticas**
Obtiene estadísticas de un trigger

**Respuesta:**
```json
{
  "success": true,
  "datos": {
    "total_ejecuciones": 10,
    "exitosas": 9,
    "fallidas": 1,
    "tasa_exito": 90.0,
    "total_notificaciones": 45,
    "total_empresas": 100,
    "ultima_ejecucion": "2025-12-07T08:00:00"
  }
}
```

### **POST /api/triggers/ejecuciones**
Registra manualmente una ejecución

**Body:**
```json
{
  "trigger_id": 1,
  "estado": "exitoso",
  "notificaciones_enviadas": 5,
  "empresas_procesadas": 10,
  "error_mensaje": null,
  "detalles": "{\"info\": \"adicional\"}"
}
```

## 💾 Base de Datos

### Nueva Tabla: `trigger_ejecuciones`

```sql
CREATE TABLE trigger_ejecuciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_id INTEGER NOT NULL,
    trigger_nombre TEXT NOT NULL,
    fecha_ejecucion TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'exitoso',
    notificaciones_enviadas INTEGER DEFAULT 0,
    empresas_procesadas INTEGER DEFAULT 0,
    error_mensaje TEXT,
    detalles TEXT,
    FOREIGN KEY (trigger_id) REFERENCES triggers(id) ON DELETE CASCADE
);
```

### Índices para Optimización
- `idx_trigger_ejecuciones_trigger_id`: Para consultas por trigger
- `idx_trigger_ejecuciones_fecha`: Para consultas ordenadas por fecha

## 🚀 Uso

### Desde la Interfaz Web

1. Ve a **Configuración** (⚙️) en el menú lateral
2. Haz clic en la pestaña **📊 Historial**
3. Opciones disponibles:
   - **Filtrar por trigger**: Selecciona un trigger específico o "Todos los triggers"
   - **Límite de resultados**: Elige cuántas ejecuciones mostrar
   - **Ver estadísticas**: Si filtras por un trigger, se muestran sus estadísticas arriba

### Desde Scripts

El script `enviar_notificaciones_automaticas.py` ahora registra automáticamente cada ejecución:

```python
# Si el script es llamado por un trigger, pasa el ID:
enviar_notificaciones(trigger_id=1)
```

### Pruebas

Ejecuta el script de prueba:

```bash
python scripts/test_historial.py
```

Este script:
- Crea ejecuciones de prueba
- Verifica el registro en la base de datos
- Obtiene estadísticas
- Valida todos los endpoints

## 📈 Información Registrada

Para cada ejecución se guarda:

| Campo | Descripción |
|-------|-------------|
| `fecha_ejecucion` | Fecha y hora ISO de la ejecución |
| `estado` | "exitoso" o "fallido" |
| `notificaciones_enviadas` | Cantidad de notificaciones enviadas |
| `empresas_procesadas` | Cantidad de empresas procesadas |
| `error_mensaje` | Mensaje de error (si aplica) |
| `detalles` | JSON con información adicional (opcional) |

## 🔍 Ejemplo de Detalles JSON

```json
{
  "empresas": 10,
  "alertas": 15,
  "criticas": 3,
  "altas": 7,
  "medias": 5,
  "destinatarios": 2,
  "duracion_segundos": 2.5
}
```

## 🧹 Mantenimiento

Para limpiar ejecuciones antiguas (más de 90 días):

```python
from app.repositories.trigger_repository import TriggerRepository
from app.config.settings import Settings

settings = Settings.from_env()
repo = TriggerRepository(settings.DB_PATH)
eliminados = repo.limpiar_ejecuciones_antiguas(dias=90)
print(f"Eliminados: {eliminados} registros")
```

## 📝 Notas

- Las ejecuciones se registran automáticamente cuando se usa el script de notificaciones
- Los triggers inactivos no ejecutan ni registran ejecuciones
- Al eliminar un trigger, se eliminan todas sus ejecuciones (CASCADE)
- Las estadísticas se calculan en tiempo real desde la base de datos

## 🎯 Casos de Uso

1. **Monitoreo**: Ver si los triggers se están ejecutando correctamente
2. **Debugging**: Identificar errores recurrentes en las ejecuciones
3. **Reportes**: Generar estadísticas sobre el uso del sistema
4. **Auditoría**: Mantener un registro de todas las notificaciones enviadas
5. **Optimización**: Analizar patrones para mejorar la configuración de triggers

## 🔐 Seguridad

- Los endpoints están protegidos por los mismos mecanismos que el resto de la API
- Los errores se registran pero no se exponen detalles sensibles en la interfaz
- El historial se puede limpiar automáticamente para cumplir políticas de retención

---

**Versión:** 2.1.0  
**Fecha:** Diciembre 2025
