# ❓ Preguntas Frecuentes - Migración PostgreSQL

## 🔧 Instalación y Configuración

### ¿Necesito tener PostgreSQL instalado?
**Sí**, necesitas tener PostgreSQL instalado y ejecutándose en tu servidor. Puedes descargarlo desde:
- Windows: https://www.postgresql.org/download/windows/
- Linux: `sudo apt-get install postgresql` (Ubuntu/Debian)
- macOS: `brew install postgresql`

### ¿Qué versión de PostgreSQL necesito?
La versión recomendada es **PostgreSQL 12 o superior**. El código es compatible con versiones modernas de PostgreSQL.

### ¿Dónde están mis credenciales de PostgreSQL?
Después de instalar PostgreSQL:
- **Usuario por defecto**: `postgres`
- **Puerto por defecto**: `5432`
- **Password**: La que definiste durante la instalación

### ¿Puedo usar PostgreSQL remoto?
**Sí**, solo cambia el `DB_HOST` en tu archivo `.env`:
```env
DB_HOST=mi-servidor.ejemplo.com
```

Asegúrate de que el firewall permita conexiones al puerto 5432.

---

## 💾 Migración de Datos

### ¿Se perderán mis datos al migrar?
**No**, el script de migración:
1. Lee los datos de SQLite
2. Los copia a PostgreSQL
3. **NO elimina** los datos de SQLite

Tu base de datos SQLite permanece intacta como respaldo.

### ¿Puedo ejecutar la migración varias veces?
**Sí**, el script usa `ON CONFLICT` para actualizar registros existentes en lugar de fallar.

### ¿Qué pasa si hay datos duplicados?
El script actualiza los registros existentes basándose en el NIT (que es único).

### ¿Cuánto tiempo toma la migración?
Depende del número de empresas:
- 100 empresas: ~5 segundos
- 1,000 empresas: ~30 segundos
- 10,000 empresas: ~5 minutos

---

## 🔄 Compatibilidad

### ¿Puedo volver a usar SQLite después?
**Sí**, simplemente cambia tu `.env`:
```env
DB_TYPE=sqlite
DB_PATH=data/facturacion.db
```

### ¿Funcionarán los triggers y usuarios?
**Parcialmente**. Actualmente:
- ✅ **Empresas**: Funcionan con PostgreSQL
- ⚠️ **Triggers**: Aún usan SQLite
- ⚠️ **Usuarios**: Aún usan SQLite

Esto significa que puedes tener empresas en PostgreSQL mientras triggers y usuarios siguen en SQLite.

### ¿Se actualizarán también triggers y usuarios?
No están incluidos en esta migración. Se pueden migrar posteriormente si es necesario.

---

## 🐛 Solución de Problemas

### Error: "connection refused"

**Causa**: PostgreSQL no está ejecutándose o está bloqueado.

**Solución**:
```bash
# Windows
net start postgresql-x64-15  # El nombre puede variar

# Linux
sudo systemctl start postgresql
sudo systemctl status postgresql

# macOS
brew services start postgresql
```

### Error: "authentication failed"

**Causa**: Usuario o contraseña incorrectos.

**Solución**:
1. Verifica las credenciales en `.env`
2. Prueba conectarte manualmente:
   ```bash
   psql -U postgres -d facturacion
   ```
3. Si olvidaste la contraseña, puedes restablecerla desde `psql`

### Error: "database does not exist"

**Causa**: La base de datos no existe.

**Solución**:
```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear la base de datos
CREATE DATABASE facturacion;

# Salir
\q
```

### Error: "no module named psycopg2"

**Causa**: El driver de PostgreSQL no está instalado.

**Solución**:
```bash
pip install psycopg2-binary
```

### Error: "could not connect to server"

**Causas posibles**:
1. PostgreSQL no está ejecutándose
2. Puerto incorrecto (debe ser 5432)
3. Firewall bloqueando la conexión
4. Host incorrecto

**Solución**:
```bash
# Verificar que PostgreSQL escucha en el puerto
netstat -an | findstr 5432  # Windows
netstat -an | grep 5432     # Linux/macOS
```

---

## 🔐 Seguridad

### ¿Es seguro poner la contraseña en .env?

**Para desarrollo local**: Sí, pero asegúrate de que `.env` esté en `.gitignore`.

**Para producción**: 
- Usa variables de entorno del sistema
- Considera usar secretos de Docker/Kubernetes
- No comprometas el archivo `.env` en el repositorio

### ¿Cómo protejo mi conexión?

Para producción, considera:
1. **SSL/TLS**: Configura PostgreSQL para usar conexiones cifradas
2. **Firewall**: Solo permite conexiones desde IPs conocidas
3. **Usuarios limitados**: Crea un usuario con permisos mínimos
4. **Contraseñas fuertes**: Usa contraseñas aleatorias largas

Ejemplo de usuario limitado:
```sql
CREATE USER sadi_app WITH PASSWORD 'contraseña_fuerte_aqui';
GRANT CONNECT ON DATABASE facturacion TO sadi_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sadi_app;
```

---

## 📊 Rendimiento

### ¿PostgreSQL es más rápido que SQLite?

**Depende**:
- SQLite: Excelente para < 100k registros, single-user
- PostgreSQL: Mejor para > 100k registros, multi-user, concurrencia

Para esta aplicación, PostgreSQL es mejor si:
- Múltiples usuarios acceden simultáneamente
- Tienes > 10,000 empresas
- Necesitas acceso remoto
- Planeas escalar la aplicación

### ¿Cómo optimizo PostgreSQL?

1. **Índices**: Ya están creados automáticamente en `nit` y `estado`
2. **VACUUM**: PostgreSQL lo hace automáticamente
3. **Connection pooling**: Para producción, considera usar pgBouncer
4. **Configuración**: Ajusta `postgresql.conf` según tu hardware

---

## 🐳 Docker

### ¿Puedo usar PostgreSQL en Docker?

**Sí**, ejemplo de `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: facturacion
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### ¿Cómo conecto desde mi app a PostgreSQL en Docker?

Si tu app está en el host:
```env
DB_HOST=localhost
```

Si tu app también está en Docker:
```env
DB_HOST=db  # Nombre del servicio
```

---

## 🔄 Backup y Restauración

### ¿Cómo hago backup de PostgreSQL?

```bash
# Backup
pg_dump -U postgres facturacion > backup.sql

# Backup comprimido
pg_dump -U postgres facturacion | gzip > backup.sql.gz
```

### ¿Cómo restauro un backup?

```bash
# Crear base de datos vacía
createdb -U postgres facturacion_nueva

# Restaurar
psql -U postgres facturacion_nueva < backup.sql

# O si está comprimido
gunzip < backup.sql.gz | psql -U postgres facturacion_nueva
```

### ¿Con qué frecuencia debo hacer backup?

**Recomendaciones**:
- Desarrollo: Semanal
- Producción: Diario (mínimo)
- Producción crítica: Cada hora + replicación

---

## 📈 Monitoreo

### ¿Cómo veo las consultas activas?

```sql
SELECT * FROM pg_stat_activity 
WHERE datname = 'facturacion';
```

### ¿Cómo veo el tamaño de la base de datos?

```sql
SELECT pg_size_pretty(pg_database_size('facturacion'));
```

### ¿Cómo veo estadísticas de tablas?

```sql
SELECT * FROM pg_stat_user_tables 
WHERE schemaname = 'public';
```

---

## 💡 Consejos Adicionales

### Desarrollo
- Usa `DB_TYPE=sqlite` para desarrollo rápido
- Cambia a PostgreSQL cuando pruebes en producción

### Producción
- Siempre usa PostgreSQL
- Configura backups automáticos
- Monitorea el rendimiento
- Usa SSL para conexiones remotas

### Testing
- Mantén una base de datos de pruebas separada
- Usa el script de migración para poblar datos de prueba
- No uses datos de producción para testing

---

¿Más preguntas? Revisa:
- [MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md) - Guía completa
- [RESUMEN_MIGRACION.md](RESUMEN_MIGRACION.md) - Cambios técnicos
- [INICIO_RAPIDO_POSTGRESQL.md](INICIO_RAPIDO_POSTGRESQL.md) - Comandos rápidos
