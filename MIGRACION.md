# 🔄 Migración a PostgreSQL

## 🚀 Inicio Rápido

### Método Automático (Recomendado)

Ejecuta el script que detectará automáticamente tu entorno:

```bash
chmod +x migrar.sh
./migrar.sh
```

Este script detectará si tienes Python instalado y te recomendará el mejor método.

---

## 📝 Métodos Disponibles

### 🐧 Servidor sin Python

**Para servidores Linux/Unix que NO tienen Python:**

```bash
chmod +x scripts/migrar_a_postgresql.sh
./scripts/migrar_a_postgresql.sh
```

📖 **Documentación completa:** [MIGRACION_SIN_PYTHON.md](MIGRACION_SIN_PYTHON.md)

**Requisitos:**
- bash
- sqlite3
- psql (cliente PostgreSQL)

---

### 🐍 Con Python

**Si tienes Python instalado:**

```bash
python scripts/asistente_migracion.py
```

📖 **Documentación completa:** [INICIO_RAPIDO_POSTGRESQL.md](INICIO_RAPIDO_POSTGRESQL.md)

**Requisitos:**
- Python 3.8+
- pip

---

## 📚 Documentación Completa

- **[README_POSTGRESQL.md](README_POSTGRESQL.md)** - Índice completo de documentación
- **[MIGRACION_SIN_PYTHON.md](MIGRACION_SIN_PYTHON.md)** - Guía para servidores sin Python
- **[INICIO_RAPIDO_POSTGRESQL.md](INICIO_RAPIDO_POSTGRESQL.md)** - Guía con Python
- **[MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md)** - Guía detallada paso a paso
- **[FAQ_POSTGRESQL.md](FAQ_POSTGRESQL.md)** - Preguntas frecuentes

---

## ⚡ Comandos Rápidos

```bash
# Detección automática y migración
./migrar.sh

# Solo servidor (sin Python)
./scripts/migrar_a_postgresql.sh

# Con Python
python scripts/asistente_migracion.py

# Solo verificar conexión
python scripts/verificar_postgresql.py
```

---

## 🆘 ¿Necesitas Ayuda?

1. Lee [FAQ_POSTGRESQL.md](FAQ_POSTGRESQL.md) para problemas comunes
2. Verifica que PostgreSQL esté ejecutándose
3. Verifica que la base de datos exista: `CREATE DATABASE facturacion;`

---

**¿Primera vez?** → Ejecuta `./migrar.sh` y sigue las instrucciones.
