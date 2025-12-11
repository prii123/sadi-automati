# 🗄️ Migración a PostgreSQL - Índice de Documentación

## 🚀 Inicio Rápido

### 🐧 En el Servidor (Sin Python)

**Si tu servidor NO tiene Python instalado:**

```bash
chmod +x scripts/migrar_a_postgresql.sh
./scripts/migrar_a_postgresql.sh
```

Este script bash usa solo herramientas nativas (sqlite3, psql) - **[Ver guía completa](MIGRACION_SIN_PYTHON.md)**

### 🐍 En Windows/Local (Con Python)

**Si tienes Python instalado:**

```bash
python scripts/asistente_migracion.py
```

Este comando ejecutará un asistente interactivo que te guiará por todo el proceso.

---

## 📚 Documentación Disponible

### Para Usuarios

0. **[MIGRACION_SIN_PYTHON.md](MIGRACION_SIN_PYTHON.md)** 🐧 **NUEVO**
   - Migración en servidor Linux/Unix SIN Python
   - Usa solo bash, sqlite3 y psql
   - **Perfecto para servidores de producción**

1. **[INICIO_RAPIDO_POSTGRESQL.md](INICIO_RAPIDO_POSTGRESQL.md)** ⚡
   - Comandos rápidos para migrar
   - 3 opciones: Asistente, Manual rápida, Manual completa
   - **Lee esto primero si quieres migrar YA**

2. **[FAQ_POSTGRESQL.md](FAQ_POSTGRESQL.md)** ❓
   - Preguntas frecuentes
   - Solución de problemas comunes
   - Consejos de seguridad y rendimiento
   - **Lee esto si tienes problemas**

3. **[MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md)** 📖
   - Guía completa paso a paso
   - Instrucciones detalladas
   - Comparación SQLite vs PostgreSQL
   - Configuración de Docker
   - **Lee esto para entender el proceso completo**

### Para Desarrolladores

4. **[RESUMEN_MIGRACION.md](RESUMEN_MIGRACION.md)** 🔧
   - Cambios técnicos realizados
   - Archivos creados/modificados
   - Checklist de migración
   - Próximos pasos recomendados
   - **Lee esto para entender los cambios en el código**

---

## 🛠️ Scripts Disponibles

### 0. Script Bash para Servidor (Sin Python) - NUEVO ⭐
```bash
chmod +x scripts/migrar_a_postgresql.sh
./scripts/migrar_a_postgresql.sh
```
**Qué hace:**
- ✅ Verifica herramientas (sqlite3, psql)
- ✅ Conecta a PostgreSQL
- ✅ Crea tabla automáticamente
- ✅ Exporta SQLite → CSV → PostgreSQL
- ✅ Crea archivo `.env`

**Cuándo usar:** Servidor Linux/Unix sin Python instalado

---

### 1. Asistente de Migración (Recomendado)
```bash
python scripts/asistente_migracion.py
```
**Qué hace:**
- ✅ Instala dependencias
- ✅ Verifica conexión a PostgreSQL
- ✅ Crea archivo `.env` automáticamente
- ✅ Migra datos desde SQLite

**Cuándo usar:** Primera migración, quieres todo automatizado

---

### 2. Verificar Conexión
```bash
python scripts/verificar_postgresql.py
```
**Qué hace:**
- ✅ Prueba la conexión a PostgreSQL
- ✅ Muestra la versión de PostgreSQL
- ✅ Opción de crear archivo `.env`

**Cuándo usar:** Antes de migrar, para verificar que todo está configurado

---

### 3. Migrar Datos
```bash
python scripts/migrar_sqlite_a_postgresql.py
```
**Qué hace:**
- ✅ Lee datos de SQLite
- ✅ Los transfiere a PostgreSQL
- ✅ Muestra progreso y resumen
- ✅ Maneja duplicados automáticamente

**Cuándo usar:** Cuando ya tienes datos en SQLite que quieres transferir

---

## 📋 Proceso Completo

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. Instalar PostgreSQL                                │
│     └─ https://www.postgresql.org/download/           │
│                                                         │
│  2. Crear base de datos                                │
│     └─ CREATE DATABASE facturacion;                    │
│                                                         │
│  3. Ejecutar asistente                                 │
│     └─ python scripts/asistente_migracion.py          │
│                                                         │
│  4. Iniciar aplicación                                 │
│     └─ python servidor.py                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 ¿Qué Opción Elegir?

### Mi servidor NO tiene Python
→ **[MIGRACION_SIN_PYTHON.md](MIGRACION_SIN_PYTHON.md)** 🐧

### Quiero migrar AHORA sin complicaciones (con Python)
→ **[INICIO_RAPIDO_POSTGRESQL.md](INICIO_RAPIDO_POSTGRESQL.md)**

### Tengo un error y no sé qué hacer
→ **[FAQ_POSTGRESQL.md](FAQ_POSTGRESQL.md)**

### Quiero entender todo el proceso detalladamente
→ **[MIGRACION_POSTGRESQL.md](MIGRACION_POSTGRESQL.md)**

### Soy desarrollador y quiero ver los cambios en el código
→ **[RESUMEN_MIGRACION.md](RESUMEN_MIGRACION.md)**

---

## ✅ Checklist Rápido

Antes de empezar, asegúrate de tener:

- [ ] PostgreSQL instalado y ejecutándose
- [ ] Base de datos `facturacion` creada
- [ ] Usuario y contraseña de PostgreSQL
- [ ] Python 3.8+ instalado
- [ ] Backup de tu base de datos SQLite (si tienes datos)

---

## 🆘 Ayuda Rápida

### Error al conectar
```bash
# Verifica que PostgreSQL esté ejecutándose
# Windows:
net start postgresql-x64-15

# Linux:
sudo systemctl status postgresql
```

### Error de módulo psycopg2
```bash
pip install psycopg2-binary
```

### Error de base de datos no existe
```sql
CREATE DATABASE facturacion;
```

### ¿Más problemas?
Lee **[FAQ_POSTGRESQL.md](FAQ_POSTGRESQL.md)** sección "Solución de Problemas"

---

## 📞 Soporte

1. **Revisa la documentación** según tu necesidad (arriba)
2. **Ejecuta el script de verificación** para diagnosticar
3. **Revisa los logs** de la aplicación y PostgreSQL
4. **Consulta FAQ** para problemas comunes

---

## 🔄 Estado de la Migración

### ✅ Completado
- Repositorio de Empresas → PostgreSQL
- Scripts de migración
- Configuración automática
- Documentación completa

### ⏳ Pendiente (Opcional)
- Repositorio de Triggers → PostgreSQL
- Repositorio de Usuarios → PostgreSQL

**Nota:** La aplicación funciona perfectamente con empresas en PostgreSQL y triggers/usuarios en SQLite.

---

## 📊 Archivos Importantes

```
sadi-automati/
├── .env                          # Tu configuración (crear desde .env.example)
├── .env.example                  # Plantilla de configuración
├── requirements.txt              # Dependencias (incluye psycopg2)
│
├── INICIO_RAPIDO_POSTGRESQL.md   # ⚡ Para migrar rápido
├── FAQ_POSTGRESQL.md             # ❓ Preguntas frecuentes
├── MIGRACION_POSTGRESQL.md       # 📖 Guía completa
├── RESUMEN_MIGRACION.md          # 🔧 Cambios técnicos
├── README_POSTGRESQL.md          # 📑 Este archivo
│
├── app/
│   ├── config/
│   │   ├── settings.py           # Configuración (modificado)
│   │   └── database_factory.py   # Factory (modificado)
│   └── repositories/
│       ├── empresa_repository.py           # SQLite (original)
│       └── postgresql_empresa_repository.py # PostgreSQL (nuevo)
│
└── scripts/
    ├── asistente_migracion.py              # 🤖 Asistente completo
    ├── verificar_postgresql.py             # 🔍 Verificar conexión
    └── migrar_sqlite_a_postgresql.py       # 🔄 Migrar datos
```

---

**¡Listo para empezar!** 🚀

Ejecuta: `python scripts/asistente_migracion.py`
