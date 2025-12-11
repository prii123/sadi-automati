# 🚀 Migración Rápida a PostgreSQL

## 🐧 Opción 0: Servidor sin Python (NUEVO)

Si tu servidor **NO tiene Python** instalado, usa el script bash:

```bash
chmod +x scripts/migrar_a_postgresql.sh
./scripts/migrar_a_postgresql.sh
```

**Ver guía completa:** [MIGRACION_SIN_PYTHON.md](MIGRACION_SIN_PYTHON.md)

---

## Opción 1: Asistente Automático (Recomendado con Python)

Ejecuta el asistente que te guiará paso a paso:

```bash
python scripts/asistente_migracion.py
```

El asistente hará:
1. ✅ Instalar dependencias necesarias
2. ✅ Verificar conexión a PostgreSQL
3. ✅ Crear archivo `.env` automáticamente
4. ✅ Migrar datos desde SQLite (si existen)

---

## Opción 2: Manual (3 pasos)

### 1️⃣ Verifica tu conexión a PostgreSQL

```bash
python scripts/verificar_postgresql.py
```

Esto creará automáticamente tu archivo `.env` con la configuración correcta.

### 2️⃣ Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Migra tus datos (si tienes datos en SQLite)

```bash
python scripts/migrar_sqlite_a_postgresql.py
```

---

## ▶️ Ejecutar la Aplicación

```bash
python servidor.py
```

---

## 📚 Documentación Completa

- **[MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md)** - Guía detallada paso a paso
- **[RESUMEN_MIGRACION.md](RESUMEN_MIGRACION.md)** - Cambios realizados en el código

---

## ⚡ Comandos Rápidos

```bash
# Instalar todo y migrar
python scripts/asistente_migracion.py

# Solo verificar conexión
python scripts/verificar_postgresql.py

# Solo migrar datos
python scripts/migrar_sqlite_a_postgresql.py

# Iniciar aplicación
python servidor.py
```

---

## 🔧 Configuración Manual del .env

Si prefieres crear el archivo `.env` manualmente:

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facturacion
DB_USER=postgres
DB_PASSWORD=tu_password
```

---

## ❓ ¿Problemas?

1. Verifica que PostgreSQL esté ejecutándose
2. Verifica las credenciales en el archivo `.env`
3. Lee [MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md) para solución de problemas

---

**¡Listo!** Tu aplicación ahora usa PostgreSQL 🎉
