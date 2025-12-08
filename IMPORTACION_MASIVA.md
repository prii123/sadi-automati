# 📥 Importación Masiva de Empresas

## 🎯 Descripción

Sistema completo para importar empresas masivamente desde archivos Excel. Permite crear o actualizar múltiples empresas de una sola vez, con validación de datos y reportes detallados.

## ✨ Características

### 1. **Plantilla Excel**
- Descarga automática de plantilla con formato correcto
- Incluye ejemplos de datos
- Columnas claramente definidas

### 2. **Validación de Datos**
- Verifica estructura del archivo
- Valida tipos de datos
- Detecta errores antes de importar
- Reporte detallado de errores

### 3. **Importación Inteligente**
- **Crear**: Empresas nuevas (NIT no existe)
- **Actualizar**: Empresas existentes (mismo NIT)
- Procesa múltiples formatos de fecha
- Maneja valores booleanos flexibles

### 4. **Reporte Detallado**
- Total de filas procesadas
- Empresas creadas
- Empresas actualizadas
- Empresas fallidas
- Lista de errores específicos

## 📋 Estructura del Excel

### Columnas Requeridas

| Columna | Tipo | Obligatorio | Descripción | Ejemplo |
|---------|------|-------------|-------------|---------|
| **NIT** | Texto | ✅ Sí | Número de identificación tributaria | `900123456` |
| **RAZON_SOCIAL** | Texto | ✅ Sí | Nombre legal de la empresa | `Empresa Ejemplo S.A.S` |
| **ESTADO** | Texto | ❌ No | Estado de la empresa | `activo` / `inactivo` / `suspendido` |
| **CERTIFICADO_VENCIMIENTO** | Fecha | ❌ No | Fecha de vencimiento del certificado | `2025-12-31` |
| **CERTIFICADO_RENOVADO** | Booleano | ❌ No | Si el certificado fue renovado | `SI` / `NO` / `1` / `0` |
| **CERTIFICADO_FACTURADO** | Booleano | ❌ No | Si el certificado fue facturado | `SI` / `NO` / `1` / `0` |
| **RESOLUCION_VENCIMIENTO** | Fecha | ❌ No | Fecha de vencimiento de la resolución | `2025-06-30` |
| **RESOLUCION_RENOVADO** | Booleano | ❌ No | Si la resolución fue renovada | `SI` / `NO` / `1` / `0` |
| **RESOLUCION_FACTURADO** | Booleano | ❌ No | Si la resolución fue facturada | `SI` / `NO` / `1` / `0` |
| **DOCUMENTO_VENCIMIENTO** | Fecha | ❌ No | Fecha de vencimiento del documento | `2025-09-15` |
| **DOCUMENTO_RENOVADO** | Booleano | ❌ No | Si el documento fue renovado | `SI` / `NO` / `1` / `0` |
| **DOCUMENTO_FACTURADO** | Booleano | ❌ No | Si el documento fue facturado | `SI` / `NO` / `1` / `0` |

### Valores Válidos

#### Estado
- `activo` (por defecto)
- `inactivo`
- `suspendido`

#### Fechas
Formatos aceptados:
- `YYYY-MM-DD` → `2025-12-31`
- `DD/MM/YYYY` → `31/12/2025`
- `DD-MM-YYYY` → `31-12-2025`
- `YYYY/MM/DD` → `2025/12/31`

#### Booleanos
Valores que representan **SÍ** (verdadero):
- `SI`, `SÍ`, `si`, `sí`
- `YES`, `yes`
- `TRUE`, `true`
- `1`
- `X`, `x`

Valores que representan **NO** (falso):
- `NO`, `no`
- Vacío
- `0`

## 🚀 Uso

### Paso 1: Descargar Plantilla

1. Ve a la sección **"Importar Excel"** en el menú
2. Haz clic en **"📥 Descargar Plantilla Excel"**
3. Se descargará `plantilla_empresas.xlsx`

### Paso 2: Completar Datos

Abre el archivo en Excel y completa los datos:

```
NIT        | RAZON_SOCIAL              | ESTADO  | CERTIFICADO_VENCIMIENTO | ...
-----------|---------------------------|---------|-------------------------|----
900123456  | Empresa Ejemplo S.A.S     | activo  | 2025-12-31              | ...
800987654  | Comercializadora XYZ Ltda | activo  | 2025-11-20              | ...
700456789  | Industrias ABC S.A.       | inactivo|                         | ...
```

**💡 Consejos:**
- No modifiques los nombres de las columnas
- Mantén el formato de la primera fila (encabezados)
- Puedes eliminar las filas de ejemplo
- Deja vacías las celdas opcionales si no aplican

### Paso 3: Importar Archivo

1. Haz clic en **"📤 Seleccionar y Cargar Excel"**
2. Selecciona tu archivo completado
3. Confirma la importación
4. Espera el proceso (verás un indicador de carga)
5. Revisa los resultados

### Ejemplo de Resultado

```
📊 Resultados de la Importación

Total procesadas:    50
✅ Creadas:          35
🔄 Actualizadas:     10
❌ Fallidas:         5

⚠️ Errores encontrados:
• Fila 12: NIT es obligatorio
• Fila 23: Estado inválido "pendiente". Debe ser: activo, inactivo o suspendido
• Fila 34: Razón Social es obligatoria
• Fila 45: Error al crear empresa - Duplicate entry
• Fila 56: Fecha inválida en CERTIFICADO_VENCIMIENTO
```

## 📡 API Endpoints

### POST /api/empresas/importar

Importa empresas desde un archivo Excel.

**Request:**
```http
POST /api/empresas/importar
Content-Type: multipart/form-data

file: <archivo.xlsx>
```

**Response (Éxito):**
```json
{
  "success": true,
  "message": "Importación completada: 35 creadas, 10 actualizadas, 5 fallidas",
  "datos": {
    "total": 50,
    "exitosas": 35,
    "actualizadas": 10,
    "fallidas": 5,
    "duplicadas": 0,
    "errores": [
      "Fila 12: NIT es obligatorio",
      "Fila 23: Estado inválido"
    ],
    "empresas_creadas": [
      {"nit": "900123456", "razon_social": "Empresa Ejemplo S.A.S"},
      {"nit": "800987654", "razon_social": "Comercializadora XYZ"}
    ],
    "empresas_actualizadas": [
      {"nit": "700456789", "razon_social": "Industrias ABC S.A."}
    ]
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "El archivo debe ser un Excel (.xlsx o .xls)"
}
```

### GET /api/empresas/plantilla-excel

Descarga la plantilla Excel con ejemplos.

**Request:**
```http
GET /api/empresas/plantilla-excel
```

**Response:**
- Archivo Excel descargable
- Nombre: `plantilla_empresas.xlsx`
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

## 🔧 Uso Programático

### Python

```python
import requests

# Descargar plantilla
response = requests.get('http://localhost:5000/api/empresas/plantilla-excel')
with open('plantilla.xlsx', 'wb') as f:
    f.write(response.content)

# Importar archivo
with open('empresas.xlsx', 'rb') as f:
    files = {'file': ('empresas.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    response = requests.post('http://localhost:5000/api/empresas/importar', files=files)
    resultado = response.json()
    
print(f"Creadas: {resultado['datos']['exitosas']}")
print(f"Actualizadas: {resultado['datos']['actualizadas']}")
print(f"Fallidas: {resultado['datos']['fallidas']}")
```

### cURL

```bash
# Descargar plantilla
curl -O http://localhost:5000/api/empresas/plantilla-excel

# Importar archivo
curl -X POST http://localhost:5000/api/empresas/importar \
  -F "file=@empresas.xlsx" \
  | jq .
```

### JavaScript

```javascript
// Descargar plantilla
async function descargarPlantilla() {
  const response = await fetch('/api/empresas/plantilla-excel');
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'plantilla_empresas.xlsx';
  a.click();
}

// Importar archivo
async function importarExcel(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/empresas/importar', {
    method: 'POST',
    body: formData
  });
  
  const resultado = await response.json();
  console.log(`✅ Creadas: ${resultado.datos.exitosas}`);
  console.log(`🔄 Actualizadas: ${resultado.datos.actualizadas}`);
}
```

## ⚠️ Consideraciones

### Límites
- **Tamaño máximo**: Depende de la configuración del servidor (por defecto FastAPI no tiene límite)
- **Filas recomendadas**: Hasta 1000 empresas por archivo
- **Tiempo de procesamiento**: ~1-2 segundos por cada 100 empresas

### Errores Comunes

#### 1. "El archivo debe ser un Excel"
- ✅ **Solución**: Usa archivos `.xlsx` o `.xls`, no CSV

#### 2. "Faltan columnas"
- ✅ **Solución**: No modifiques los nombres de columnas de la plantilla

#### 3. "NIT es obligatorio"
- ✅ **Solución**: Todas las filas deben tener NIT

#### 4. "Razón Social es obligatoria"
- ✅ **Solución**: Todas las filas deben tener nombre de empresa

#### 5. "Estado inválido"
- ✅ **Solución**: Usa solo: `activo`, `inactivo` o `suspendido`

#### 6. "Fecha inválida"
- ✅ **Solución**: Usa formato `YYYY-MM-DD` o `DD/MM/YYYY`

### Mejores Prácticas

1. **Validar antes de importar**
   - Revisa los datos en Excel
   - Asegúrate de que los NITs sean únicos
   - Verifica el formato de fechas

2. **Importaciones grandes**
   - Divide en archivos de máximo 500 empresas
   - Importa en horarios de baja actividad

3. **Backup**
   - Haz respaldo de la base de datos antes de importaciones masivas
   - Guarda copia del archivo Excel usado

4. **Pruebas**
   - Primero importa 5-10 empresas de prueba
   - Verifica que los datos se cargaron correctamente
   - Luego procede con el archivo completo

## 🐳 Docker

El servicio de importación está completamente integrado y funciona en Docker sin configuración adicional.

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data  # Base de datos persistente
```

## 📝 Notas Técnicas

### Tecnologías Usadas
- **openpyxl**: Lectura y escritura de archivos Excel
- **python-multipart**: Manejo de uploads en FastAPI
- **FastAPI**: Framework para API REST

### Validaciones Implementadas
- ✅ Estructura del archivo (columnas)
- ✅ Tipos de datos (fechas, booleanos, texto)
- ✅ Campos obligatorios (NIT, Razón Social)
- ✅ Valores válidos (estados)
- ✅ Duplicados (por NIT)

### Rendimiento
- Procesamiento en memoria (sin archivos temporales)
- Transacciones individuales por empresa
- Rollback automático en caso de error
- No bloquea otras operaciones

## 🎓 Conclusión

La importación masiva facilita:
- ✅ **Migración** desde otros sistemas
- ✅ **Carga inicial** de datos
- ✅ **Actualizaciones masivas** periódicas
- ✅ **Integración** con sistemas externos

¡Tu sistema está listo para manejar grandes volúmenes de datos! 📊

---

**Versión:** 1.0.0  
**Fecha:** Diciembre 2025
