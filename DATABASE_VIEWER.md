# 🗄️ Database Viewer - Visualización Segura de Base de Datos

## 📋 Descripción

Sistema de visualización de base de datos integrado en la aplicación SADI que permite a los administradores consultar y explorar las tablas de SQLite de forma segura y directa desde el navegador.

## 🔐 Seguridad

### Características de Seguridad Implementadas:

1. **Autenticación Obligatoria**
   - Solo usuarios autenticados pueden acceder
   - Requiere rol de **administrador** para todas las operaciones
   - Protegido mediante `require_admin` dependency

2. **Solo Lectura (Read-Only)**
   - Solo se permiten consultas `SELECT`
   - Palabras prohibidas: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER`, `TRUNCATE`
   - Validación en backend antes de ejecutar cualquier consulta

3. **Acceso Controlado**
   - El menú "Database Viewer" solo se muestra a usuarios con rol `admin`
   - Los usuarios normales no pueden ver ni acceder a esta funcionalidad

## 🚀 Funcionalidades

### 1. **Vista de Tablas**
```
GET /api/database/tables
```
- Lista todas las tablas de la base de datos
- Muestra número de registros y columnas por tabla
- Incluye esquema de cada tabla

### 2. **Visualización de Datos**
```
GET /api/database/tables/{table_name}?limit=100
```
- Muestra datos de una tabla específica
- Límite configurable (1-1000 registros)
- Incluye esquema y metadatos

### 3. **Consultas SQL Personalizadas**
```
POST /api/database/query
Body: { "query": "SELECT * FROM empresas WHERE estado='activo'" }
```
- Ejecuta consultas SELECT personalizadas
- Validación automática de seguridad
- Resultados en formato JSON

### 4. **Esquema de Tablas**
```
GET /api/database/schema/{table_name}
```
- Obtiene la estructura completa de una tabla
- Nombres de columnas, tipos de datos, constraints

### 5. **Exportación a CSV**
- Exporta datos de cualquier tabla a archivo CSV
- Hasta 10,000 registros por exportación
- Descarga directa desde el navegador

## 💻 Uso desde la Interfaz Web

### Acceder al Database Viewer:

1. **Login como administrador**
   - Usuario: `admin`
   - Contraseña: `admin123` (o la que hayas configurado)

2. **Navegar al menú**
   - Click en "🗄️ Database Viewer" en el sidebar
   - El menú solo aparece si eres administrador

3. **Explorar tablas**
   - Ver lista de todas las tablas con estadísticas
   - Click en cualquier tabla para ver sus datos
   - Navegar por los registros

4. **Ejecutar consultas**
   - Escribir consulta SQL en el editor
   - Ejemplo: `SELECT * FROM empresas WHERE estado='activo' LIMIT 50`
   - Click en "▶️ Ejecutar Consulta"
   - Ver resultados en tabla

5. **Exportar datos**
   - Abrir cualquier tabla
   - Click en "📥 Exportar CSV"
   - Archivo se descarga automáticamente

## 📡 Uso desde API

### Ejemplo con cURL:

```bash
# 1. Login para obtener token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Obtener lista de tablas
curl http://localhost:5000/api/database/tables \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Ver datos de una tabla
curl "http://localhost:5000/api/database/tables/empresas?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Ejecutar consulta personalizada
curl -X POST http://localhost:5000/api/database/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT nombre, estado FROM empresas LIMIT 5"}'
```

### Ejemplo con Python:

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['datos']['token']

headers = {'Authorization': f'Bearer {token}'}

# Obtener tablas
tables = requests.get('http://localhost:5000/api/database/tables', headers=headers)
print(tables.json())

# Consulta personalizada
query_result = requests.post('http://localhost:5000/api/database/query',
    headers=headers,
    json={'query': 'SELECT * FROM empresas LIMIT 5'}
)
print(query_result.json())
```

## 🛡️ Restricciones y Validaciones

### Consultas Permitidas:
✅ `SELECT * FROM empresas`
✅ `SELECT nombre, nit FROM empresas WHERE estado='activo'`
✅ `SELECT COUNT(*) FROM triggers`
✅ `SELECT * FROM empresas JOIN certificados ON ...`

### Consultas Prohibidas:
❌ `INSERT INTO empresas ...`
❌ `UPDATE empresas SET ...`
❌ `DELETE FROM empresas`
❌ `DROP TABLE empresas`
❌ `CREATE TABLE ...`
❌ `ALTER TABLE ...`
❌ Cualquier consulta que modifique datos

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/database/tables` | GET | Lista todas las tablas | Admin |
| `/api/database/tables/{name}` | GET | Datos de una tabla | Admin |
| `/api/database/query` | POST | Ejecuta consulta SELECT | Admin |
| `/api/database/schema/{name}` | GET | Esquema de una tabla | Admin |

## ⚙️ Configuración

El Database Viewer utiliza la configuración de base de datos del sistema:

```python
# app/config/settings.py
DB_TYPE = 'sqlite'  # Actualmente solo SQLite soportado
DB_PATH = 'data/facturacion.db'
```

## 🎨 Interfaz de Usuario

### Componentes:
1. **Grid de Tablas** - Cards clicables con estadísticas
2. **Visor de Datos** - Tabla responsive con paginación
3. **Editor SQL** - Textarea con syntax highlighting (monospace)
4. **Resultados** - Tabla con resultados de consultas
5. **Acciones** - Exportar, refrescar, ejecutar

### Estilos Personalizados:
- Cards hover con animación
- Textarea monospace para SQL
- Badges para valores NULL
- Iconos para booleanos (✅/❌)
- Responsive design

## 🐛 Manejo de Errores

### Errores Comunes:

**Error 401 - No autorizado**
```json
{
  "detail": "No autenticado"
}
```
Solución: Login como administrador

**Error 400 - Consulta inválida**
```json
{
  "detail": "Solo se permiten consultas SELECT"
}
```
Solución: Usar solo consultas SELECT

**Error 500 - Error en consulta**
```json
{
  "detail": "no such table: tabla_inexistente"
}
```
Solución: Verificar nombre de tabla

## 🔍 Casos de Uso

### 1. Auditoría de Datos
Verificar integridad de datos sin modificar la base de datos:
```sql
SELECT COUNT(*) as total FROM empresas;
SELECT estado, COUNT(*) as cantidad FROM empresas GROUP BY estado;
```

### 2. Debugging
Verificar valores específicos durante desarrollo:
```sql
SELECT * FROM triggers WHERE activo=1;
SELECT * FROM usuarios WHERE rol='admin';
```

### 3. Reportes Personalizados
Crear reportes ad-hoc sin modificar código:
```sql
SELECT e.nombre, c.fecha_final 
FROM empresas e 
LEFT JOIN certificados c ON e.id = c.empresa_id
WHERE c.fecha_final < DATE('now', '+30 days');
```

### 4. Análisis de Datos
Explorar relaciones y patrones:
```sql
SELECT 
  COUNT(*) as total_empresas,
  SUM(CASE WHEN estado='activo' THEN 1 ELSE 0 END) as activas,
  SUM(CASE WHEN estado='inactivo' THEN 1 ELSE 0 END) as inactivas
FROM empresas;
```

## ⚠️ Consideraciones Importantes

1. **Solo para Administradores**
   - No exponer a usuarios regulares
   - Mantener credenciales de admin seguras

2. **Límites de Resultados**
   - Máximo 1000 registros por consulta vía API
   - Interfaz web limita a 100 por defecto
   - Exportación CSV hasta 10,000 registros

3. **Performance**
   - Consultas complejas pueden ser lentas
   - SQLite no soporta consultas concurrentes de escritura
   - Considerar índices para tablas grandes

4. **Seguridad en Producción**
   - Cambiar contraseña de admin por defecto
   - Considerar deshabilitar en producción si no es necesario
   - Monitorear logs de acceso

## 🚀 Mejoras Futuras

- [ ] Soporte para MySQL/PostgreSQL
- [ ] Syntax highlighting en editor SQL
- [ ] Historial de consultas ejecutadas
- [ ] Guardado de consultas favoritas
- [ ] Paginación en resultados grandes
- [ ] Visualizaciones gráficas de datos
- [ ] Exportación a otros formatos (Excel, JSON)
- [ ] Query builder visual

## 📝 Notas de Desarrollo

### Archivos Creados:
- `app/services/database_service.py` - Servicio de base de datos
- `app/static/js/database.js` - Frontend JavaScript
- `app/static/css/database.css` - Estilos personalizados

### Archivos Modificados:
- `app/api/routes.py` - Endpoints de database viewer
- `app/templates/index.html` - Vista y navegación
- `app/static/js/main.js` - Integración con navegación

## 🆘 Soporte

Si encuentras problemas:
1. Verificar que eres administrador
2. Revisar logs del servidor
3. Probar endpoints directamente con curl
4. Verificar permisos de archivo de base de datos

---

**Desarrollado para SADI - Sistema de Administración de Documentos Integrado**
