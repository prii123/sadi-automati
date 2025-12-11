# 🚀 Migración en Servidor (Sin Python)

## Para servidores Linux/Unix que NO tienen Python instalado

Este script bash realiza la migración de SQLite a PostgreSQL usando solo herramientas nativas del sistema.

---

## 📋 Requisitos

Solo necesitas tener instalado:
- ✅ **bash** (incluido en todos los sistemas Linux/Unix)
- ✅ **sqlite3** (cliente de línea de comandos)
- ✅ **psql** (cliente de PostgreSQL)
- ✅ **PostgreSQL** ejecutándose con una base de datos creada

---

## 🔧 Instalación de Herramientas

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install sqlite3 postgresql-client
```

### CentOS/RHEL
```bash
sudo yum install sqlite postgresql
```

### Alpine Linux (Docker)
```bash
apk add sqlite postgresql-client bash
```

---

## 🚀 Uso del Script

### 1. Dar permisos de ejecución
```bash
chmod +x scripts/migrar_a_postgresql.sh
```

### 2. Ejecutar el script
```bash
./scripts/migrar_a_postgresql.sh
```

El script te guiará paso a paso:

1. ✅ Verifica que `sqlite3` y `psql` estén instalados
2. 📝 Te pide la configuración de SQLite y PostgreSQL
3. 🔍 Verifica la conexión a PostgreSQL
4. 📊 Crea la tabla en PostgreSQL
5. 📤 Exporta datos de SQLite a CSV
6. 📥 Importa datos a PostgreSQL
7. ✅ Verifica que la migración fue exitosa
8. 📝 Opcionalmente crea el archivo `.env`

---

## 📖 Ejemplo de Ejecución

```bash
$ ./scripts/migrar_a_postgresql.sh

======================================================================
  MIGRACIÓN DE SQLITE A POSTGRESQL (SIN PYTHON)
======================================================================

────────────────────────────────────────────────────────────────────
PASO 1: Verificación de Herramientas
────────────────────────────────────────────────────────────────────

✓ sqlite3 encontrado
✓ psql encontrado

✓ Todas las herramientas están disponibles

────────────────────────────────────────────────────────────────────
PASO 2: Configuración de Conexiones
────────────────────────────────────────────────────────────────────

Configuración de SQLite:
Ruta al archivo SQLite [./data/facturacion.db]: 
✓ Archivo SQLite encontrado

Configuración de PostgreSQL:
Host [localhost]: 
Puerto [5432]: 
Base de datos [facturacion]: 
Usuario [postgres]: 
Contraseña: ********

────────────────────────────────────────────────────────────────────
PASO 3: Verificación de Conexión PostgreSQL
────────────────────────────────────────────────────────────────────

✓ Conexión exitosa a PostgreSQL

... continúa con todos los pasos ...

======================================================================
  ¡MIGRACIÓN COMPLETADA!
======================================================================
```

---

## 🔍 Verificación Post-Migración

Después de ejecutar el script, verifica:

### 1. Contar registros en PostgreSQL
```bash
psql -h localhost -U postgres -d facturacion -c "SELECT COUNT(*) FROM empresas;"
```

### 2. Ver algunas empresas
```bash
psql -h localhost -U postgres -d facturacion -c "SELECT id, nit, nombre FROM empresas LIMIT 5;"
```

### 3. Verificar estructura de tabla
```bash
psql -h localhost -U postgres -d facturacion -c "\d empresas"
```

---

## 📝 Archivo .env

El script puede crear automáticamente tu archivo `.env`. Si lo creas manualmente:

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facturacion
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
```

---

## ⚠️ Notas Importantes

### Backup Automático
El script NO elimina tu base de datos SQLite original. Si quieres hacer un backup adicional:

```bash
cp data/facturacion.db data/facturacion.db.backup
```

### Duplicados
El script usa `ON CONFLICT (nit) DO UPDATE`, lo que significa:
- Si el NIT ya existe en PostgreSQL, **actualiza** el registro
- Si el NIT no existe, **inserta** un nuevo registro

### Contraseña de PostgreSQL
El script usa la variable `PGPASSWORD` temporalmente. Esta se limpia al finalizar.

Para no introducir la contraseña cada vez, puedes usar `~/.pgpass`:

```bash
# Crear archivo .pgpass
echo "localhost:5432:facturacion:postgres:tu_password" > ~/.pgpass
chmod 600 ~/.pgpass
```

---

## 🐛 Solución de Problemas

### Error: "sqlite3: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install sqlite3

# CentOS/RHEL
sudo yum install sqlite
```

### Error: "psql: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# CentOS/RHEL
sudo yum install postgresql
```

### Error: "connection refused"
PostgreSQL no está ejecutándose o el puerto está incorrecto.

```bash
# Verificar que PostgreSQL está ejecutándose
sudo systemctl status postgresql

# Verificar el puerto
sudo netstat -tlnp | grep 5432
```

### Error: "database does not exist"
Debes crear la base de datos primero:

```bash
psql -U postgres -c "CREATE DATABASE facturacion;"
```

### Error: "authentication failed"
Verifica:
1. El usuario existe: `psql -U postgres -l`
2. La contraseña es correcta
3. El archivo `pg_hba.conf` permite la conexión

---

## 🔄 Migración desde Windows WSL

Si estás en Windows pero tu servidor es Linux, puedes:

1. **Copiar el script al servidor:**
   ```bash
   scp scripts/migrar_a_postgresql.sh usuario@servidor:/ruta/
   ```

2. **Copiar la base de datos SQLite:**
   ```bash
   scp data/facturacion.db usuario@servidor:/ruta/
   ```

3. **Conectarte por SSH y ejecutar:**
   ```bash
   ssh usuario@servidor
   cd /ruta/
   chmod +x migrar_a_postgresql.sh
   ./migrar_a_postgresql.sh
   ```

---

## 🐳 Docker

Si PostgreSQL está en Docker:

```bash
# Obtener el ID del contenedor
docker ps | grep postgres

# O usar docker-compose
docker-compose ps

# Ejecutar el script apuntando al puerto expuesto
# El script preguntará por host (usa 'localhost') y puerto (usa el mapeado, ej: 5432)
./scripts/migrar_a_postgresql.sh
```

---

## 📊 Comparación de Métodos

| Método | Requiere | Ventajas | Desventajas |
|--------|----------|----------|-------------|
| **Script Bash** | sqlite3, psql | No requiere Python | Menos flexible |
| **Script Python** | Python, psycopg2 | Más control | Requiere Python |
| **Manual SQL** | psql | Control total | Más laborioso |

---

## 🎯 Comandos Rápidos

```bash
# Todo en un comando (con valores por defecto)
chmod +x scripts/migrar_a_postgresql.sh && ./scripts/migrar_a_postgresql.sh

# Verificar instalación de herramientas
which sqlite3 && which psql && echo "✓ Todo listo"

# Verificar PostgreSQL está ejecutándose
pg_isready -h localhost -p 5432

# Ver logs de PostgreSQL (Ubuntu/Debian)
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## 📚 Recursos Adicionales

- [Documentación PostgreSQL](https://www.postgresql.org/docs/)
- [Cliente psql](https://www.postgresql.org/docs/current/app-psql.html)
- [SQLite Command Line](https://www.sqlite.org/cli.html)

---

**¿Necesitas ayuda?** Revisa la sección de Solución de Problemas arriba o consulta los logs del script.
