# 📅 Configuración de Triggers para Notificaciones Automáticas

Esta guía te muestra cómo configurar envíos automáticos de notificaciones por email de forma programada (diaria, semanal, mensual, etc.)

## 🔧 Configuración Inicial

### 1. Configurar Destinatarios

Edita tu archivo `.env` y agrega la línea con los emails que recibirán las notificaciones:

```env
# Emails separados por comas
EMAIL_DESTINATARIOS=correo1@ejemplo.com,correo2@ejemplo.com,correo3@ejemplo.com
```

### 2. Verificar el Script

Prueba el script manualmente primero:

```powershell
python scripts/enviar_notificaciones_automaticas.py
```

Este script:
- Lee las credenciales y destinatarios del archivo `.env`
- Obtiene las notificaciones pendientes
- Envía un email automáticamente
- Genera logs con timestamp

---

## 🪟 Opción 1: Task Scheduler (Windows) - RECOMENDADO

### Envío Diario (todos los días a las 8:00 AM)

**Paso 1: Crear el script batch**

Crea un archivo `enviar_notificaciones.bat` en la carpeta del proyecto:

```batch
@echo off
cd /d "C:\Users\Aurora Lozano\Downloads\sadi"
python scripts/enviar_notificaciones_automaticas.py >> logs/notificaciones.log 2>&1
```

**Paso 2: Configurar tarea en Task Scheduler**

1. Abre **Programador de tareas** (Task Scheduler):
   - Presiona `Win + R`
   - Escribe `taskschd.msc`
   - Presiona Enter

2. Haz clic en **"Crear tarea básica..."**

3. **Nombre:** `Enviar Notificaciones Facturación`
   **Descripción:** `Envía notificaciones de vencimientos por email`

4. **Desencadenador:** Selecciona según tu preferencia:

   **Para envío DIARIO:**
   - Selecciona: **Diariamente**
   - Hora: `08:00:00` (8:00 AM)
   - Repetir cada: `1` días

   **Para envío SEMANAL:**
   - Selecciona: **Semanalmente**
   - Día: Lunes (o el que prefieras)
   - Hora: `08:00:00`

   **Para envío MENSUAL:**
   - Selecciona: **Mensualmente**
   - Día: `1` (primer día del mes)
   - Hora: `08:00:00`

5. **Acción:**
   - Selecciona: **Iniciar un programa**
   - Programa/script: `"C:\Users\Aurora Lozano\Downloads\sadi\enviar_notificaciones.bat"`

6. **Finalizar:** Revisa y haz clic en **Finalizar**

7. **Configuración adicional:**
   - Haz clic derecho en la tarea creada → **Propiedades**
   - Pestaña **General:**
     - ✅ Marcar: **Ejecutar tanto si el usuario inició sesión como si no**
     - ✅ Marcar: **Ejecutar con los privilegios más altos**
   - Pestaña **Configuración:**
     - ✅ Marcar: **Permitir ejecución de la tarea a petición**
     - ✅ Marcar: **Ejecutar la tarea lo antes posible después de un inicio programado perdido**

### Crear carpeta de logs

```powershell
New-Item -ItemType Directory -Path "logs" -Force
```

---

## 🐍 Opción 2: Script Python con Scheduler

Si prefieres programar desde Python, instala `schedule`:

```powershell
pip install schedule
```

Crea `scripts/scheduler.py`:

```python
import schedule
import time
from enviar_notificaciones_automaticas import enviar_notificaciones

# Programar envío diario a las 8:00 AM
schedule.every().day.at("08:00").do(enviar_notificaciones)

# Alternativas:
# schedule.every().monday.at("08:00").do(enviar_notificaciones)  # Semanal
# schedule.every().hour.do(enviar_notificaciones)  # Cada hora
# schedule.every(30).minutes.do(enviar_notificaciones)  # Cada 30 min

print("Scheduler iniciado. Presiona Ctrl+C para detener.")
print("Próxima ejecución:", schedule.next_run())

while True:
    schedule.run_pending()
    time.sleep(60)  # Verificar cada minuto
```

Ejecutar como servicio en segundo plano:

```powershell
# Usando pythonw (sin ventana)
pythonw scripts/scheduler.py

# O con nohup en PowerShell
Start-Process -NoNewWindow python -ArgumentList "scripts/scheduler.py"
```

---

## ⚙️ Opción 3: Configuraciones Avanzadas

### Envío en Múltiples Horarios

Crea múltiples tareas en Task Scheduler:

1. **Notificaciones Críticas:** Cada 2 horas (9:00, 11:00, 13:00, 15:00, 17:00)
2. **Notificaciones Generales:** Una vez al día (8:00 AM)
3. **Reporte Semanal:** Lunes a las 8:00 AM

### Filtrar Notificaciones por Prioridad

Modifica `enviar_notificaciones_automaticas.py`:

```python
# Solo enviar si hay notificaciones críticas o altas
if criticas > 0 or altas > 0:
    resultado = email_service.enviar_notificaciones_vencimientos(
        destinatarios, 
        notificaciones
    )
else:
    log("ℹ️ No hay notificaciones críticas/altas. Saltando envío.")
```

### Diferentes Destinatarios por Tipo

```env
# En .env
EMAIL_CRITICAS=gerencia@empresa.com,director@empresa.com
EMAIL_GENERALES=contabilidad@empresa.com,admin@empresa.com
```

---

## 📊 Monitoreo y Logs

### Ver logs de ejecución:

```powershell
Get-Content logs/notificaciones.log -Tail 50
```

### Ver historial de tareas en Task Scheduler:

1. Abre Task Scheduler
2. Encuentra tu tarea
3. Pestaña **Historial** → Ver todas las ejecuciones

### Logs con rotación (para no llenar disco):

Instala `logging` handler en Python:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/notificaciones.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # 5 archivos de respaldo
)
```

---

## 🔔 Opciones de Notificación Personalizadas

### 1. Solo días laborables

En Task Scheduler, marca solo: L, M, Mi, J, V

### 2. Alertas de fin de mes

Configura una tarea para el día 25-28 con recordatorio de cierres

### 3. Resumen semanal los viernes

Crea una tarea específica para los viernes con un formato de resumen

---

## 🧪 Probar la Tarea Programada

### Ejecutar manualmente desde Task Scheduler:

1. Abre Task Scheduler
2. Busca tu tarea
3. Clic derecho → **Ejecutar**
4. Verifica que el email llegue

### Probar el script directamente:

```powershell
# Ejecutar el script
python scripts/enviar_notificaciones_automaticas.py

# Ver el resultado
echo $LASTEXITCODE  # 0 = éxito, 1 = error
```

---

## 🔍 Solución de Problemas

### La tarea no se ejecuta

**Verificar:**
1. Que la ruta del script batch sea absoluta
2. Que el usuario tenga permisos
3. Revisar el historial de Task Scheduler

**Ver errores:**
```powershell
# Ver eventos del sistema
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 10
```

### Los emails no llegan

**Verificar:**
1. Que el archivo `.env` esté en la raíz del proyecto
2. Que `EMAIL_DESTINATARIOS` esté configurado
3. Ver el archivo `logs/notificaciones.log`

```powershell
# Verificar configuración
Get-Content .env | Select-String "EMAIL_DESTINATARIOS"
```

### Script se ejecuta pero no hace nada

**Revisar:**
```powershell
# Ejecutar con output completo
python scripts/enviar_notificaciones_automaticas.py
```

---

## 📝 Ejemplo de Configuración Completa

### Archivo `.env`

```env
# Gmail
SMTP_USER=sadi.automatizaciones@gmail.com
SMTP_PASSWORD=xhdc zzgk xbub vcff

# Destinatarios (separados por comas)
EMAIL_DESTINATARIOS=admin@empresa.com,gerencia@empresa.com

# Opcional: diferentes grupos
EMAIL_CRITICAS=gerencia@empresa.com
EMAIL_GENERALES=contabilidad@empresa.com
```

### Script batch `enviar_notificaciones.bat`

```batch
@echo off
REM Script para enviar notificaciones automáticas
cd /d "C:\Users\Aurora Lozano\Downloads\sadi"

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

REM Ejecutar script con logs
python scripts/enviar_notificaciones_automaticas.py >> logs/notificaciones.log 2>&1

REM Verificar errores
if %ERRORLEVEL% NEQ 0 (
    echo Error al enviar notificaciones >> logs/notificaciones.log
)
```

### Programación en Task Scheduler

- **Tarea 1:** "Notificaciones Diarias"
  - Desencadenador: Diariamente a las 8:00 AM
  - Días: Lunes a Viernes

- **Tarea 2:** "Alertas Críticas"
  - Desencadenador: Cada 4 horas (8:00, 12:00, 16:00)
  - Días: Todos los días

- **Tarea 3:** "Resumen Semanal"
  - Desencadenador: Lunes a las 8:00 AM
  - Envía resumen completo de la semana

---

## ✅ Verificación Final

Después de configurar, verifica:

1. ✅ El script se ejecuta manualmente sin errores
2. ✅ La tarea programada aparece en Task Scheduler
3. ✅ Los logs se generan en `logs/notificaciones.log`
4. ✅ Los emails llegan a los destinatarios
5. ✅ La tarea se ejecuta en el horario programado

**Comando rápido de verificación:**

```powershell
# Ejecutar y verificar
python scripts/enviar_notificaciones_automaticas.py; echo "Exit code: $LASTEXITCODE"

# Ver último log
Get-Content logs/notificaciones.log -Tail 20
```

---

## 🚀 Tips Adicionales

1. **Backup automático:** Programa un backup de la base de datos antes del envío
2. **Reporte de estadísticas:** Envía un resumen mensual con gráficos
3. **Alertas por WhatsApp:** Integra Twilio para notificaciones críticas
4. **Dashboard web:** Crea una vista para ver el historial de envíos
5. **Testing:** Usa un destinatario de prueba los primeros días

¿Necesitas ayuda configurando alguna de estas opciones?
