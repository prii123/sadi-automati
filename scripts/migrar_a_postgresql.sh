#!/bin/bash

################################################################################
# Script de migración de SQLite a PostgreSQL
# Este script NO requiere Python - usa solo herramientas de línea de comandos
################################################################################

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir banner
print_banner() {
    echo -e "${BLUE}"
    echo "======================================================================"
    echo "  $1"
    echo "======================================================================"
    echo -e "${NC}"
}

# Función para imprimir paso
print_step() {
    echo -e "\n${YELLOW}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}PASO $1: $2${NC}"
    echo -e "${YELLOW}────────────────────────────────────────────────────────────────────${NC}\n"
}

# Función para verificar comando
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ Error: $1 no está instalado${NC}"
        echo -e "${YELLOW}  Instala $1 para continuar${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 encontrado${NC}"
        return 0
    fi
}

################################################################################
# INICIO DEL SCRIPT
################################################################################

print_banner "MIGRACIÓN DE SQLITE A POSTGRESQL (SIN PYTHON)"

echo -e "${BLUE}Este script migrará tus datos de SQLite a PostgreSQL${NC}"
echo -e "${BLUE}usando solo herramientas nativas de bash y SQL${NC}\n"

# Verificar herramientas necesarias
print_step 1 "Verificación de Herramientas"

ALL_OK=true
check_command "sqlite3" || ALL_OK=false
check_command "psql" || ALL_OK=false

if [ "$ALL_OK" = false ]; then
    echo -e "\n${RED}✗ Faltan herramientas necesarias. Abortando.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Todas las herramientas están disponibles${NC}"

################################################################################
# CONFIGURACIÓN
################################################################################

print_step 2 "Configuración de Conexiones"

# SQLite
echo -e "${YELLOW}Configuración de SQLite:${NC}"
read -p "Ruta al archivo SQLite [./data/facturacion.db]: " SQLITE_PATH
SQLITE_PATH=${SQLITE_PATH:-./data/facturacion.db}

if [ ! -f "$SQLITE_PATH" ]; then
    echo -e "${RED}✗ Archivo SQLite no encontrado: $SQLITE_PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Archivo SQLite encontrado${NC}"

# PostgreSQL
echo -e "\n${YELLOW}Configuración de PostgreSQL:${NC}"
read -p "Host [localhost]: " PG_HOST
PG_HOST=${PG_HOST:-localhost}

read -p "Puerto [5432]: " PG_PORT
PG_PORT=${PG_PORT:-5432}

read -p "Base de datos [facturacion]: " PG_DB
PG_DB=${PG_DB:-facturacion}

read -p "Usuario [postgres]: " PG_USER
PG_USER=${PG_USER:-postgres}

read -sp "Contraseña: " PG_PASSWORD
echo

# Exportar password para psql
export PGPASSWORD="$PG_PASSWORD"

################################################################################
# VERIFICAR CONEXIÓN POSTGRESQL
################################################################################

print_step 3 "Verificación de Conexión PostgreSQL"

if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conexión exitosa a PostgreSQL${NC}"
    PG_VERSION=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -t -c "SELECT version();" 2>/dev/null)
    echo -e "${BLUE}  Versión: $PG_VERSION${NC}"
else
    echo -e "${RED}✗ No se pudo conectar a PostgreSQL${NC}"
    echo -e "${YELLOW}  Verifica las credenciales y que PostgreSQL esté ejecutándose${NC}"
    exit 1
fi

################################################################################
# CREAR TABLA EN POSTGRESQL
################################################################################

print_step 4 "Creación de Tabla en PostgreSQL"

echo "Creando tabla 'empresas' en PostgreSQL..."

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
CREATE TABLE IF NOT EXISTS empresas (
    id SERIAL PRIMARY KEY,
    nit TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo',
    
    -- Certificado de Facturación Electrónica
    cert_activo INTEGER DEFAULT 0,
    cert_fecha_inicio TIMESTAMP,
    cert_fecha_final TIMESTAMP,
    cert_notificacion TEXT,
    cert_renovado INTEGER DEFAULT 0,
    cert_facturado INTEGER DEFAULT 0,
    cert_comentarios TEXT,
    
    -- Resolución de Facturación
    resol_activo INTEGER DEFAULT 0,
    resol_fecha_inicio TIMESTAMP,
    resol_fecha_final TIMESTAMP,
    resol_notificacion TEXT,
    resol_renovado INTEGER DEFAULT 0,
    resol_facturado INTEGER DEFAULT 0,
    resol_comentarios TEXT,
    
    -- Resolución Documentos Soporte
    doc_activo INTEGER DEFAULT 0,
    doc_fecha_inicio TIMESTAMP,
    doc_fecha_final TIMESTAMP,
    doc_notificacion TEXT,
    doc_renovado INTEGER DEFAULT 0,
    doc_facturado INTEGER DEFAULT 0,
    doc_comentarios TEXT,
    
    -- Metadatos
    fecha_creacion TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nit ON empresas(nit);
CREATE INDEX IF NOT EXISTS idx_estado ON empresas(estado);
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tabla creada/verificada correctamente${NC}"
else
    echo -e "${RED}✗ Error al crear tabla${NC}"
    exit 1
fi

################################################################################
# CONTAR REGISTROS EN SQLITE
################################################################################

print_step 5 "Análisis de Datos en SQLite"

TOTAL_EMPRESAS=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM empresas;")
echo -e "${BLUE}Total de empresas en SQLite: $TOTAL_EMPRESAS${NC}"

if [ "$TOTAL_EMPRESAS" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No hay datos para migrar${NC}"
    read -p "¿Deseas continuar de todas formas? (s/n): " CONTINUAR
    if [ "$CONTINUAR" != "s" ]; then
        echo "Migración cancelada"
        exit 0
    fi
fi

################################################################################
# PREGUNTAR SI LIMPIAR TABLA
################################################################################

echo -e "\n${YELLOW}⚠ ADVERTENCIA:${NC}"
read -p "¿Deseas limpiar la tabla PostgreSQL antes de migrar? (s/n): " LIMPIAR

if [ "$LIMPIAR" = "s" ]; then
    echo "Limpiando tabla empresas en PostgreSQL..."
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c "DELETE FROM empresas;" > /dev/null
    echo -e "${GREEN}✓ Tabla limpiada${NC}"
fi

################################################################################
# EXPORTAR DATOS DE SQLITE A CSV
################################################################################

print_step 6 "Exportación de Datos desde SQLite"

TMP_CSV="/tmp/empresas_migration_$$.csv"

echo "Exportando datos a CSV temporal..."

sqlite3 "$SQLITE_PATH" << EOF
.mode csv
.headers on
.output $TMP_CSV
SELECT 
    nit,
    nombre,
    tipo,
    estado,
    cert_activo,
    cert_fecha_inicio,
    cert_fecha_final,
    cert_notificacion,
    cert_renovado,
    cert_facturado,
    cert_comentarios,
    resol_activo,
    resol_fecha_inicio,
    resol_fecha_final,
    resol_notificacion,
    resol_renovado,
    resol_facturado,
    resol_comentarios,
    doc_activo,
    doc_fecha_inicio,
    doc_fecha_final,
    doc_notificacion,
    doc_renovado,
    doc_facturado,
    doc_comentarios,
    fecha_creacion,
    fecha_actualizacion
FROM empresas;
.quit
EOF

if [ ! -f "$TMP_CSV" ]; then
    echo -e "${RED}✗ Error al exportar datos${NC}"
    exit 1
fi

LINES_CSV=$(wc -l < "$TMP_CSV")
RECORDS_CSV=$((LINES_CSV - 1)) # Restar header
echo -e "${GREEN}✓ Datos exportados: $RECORDS_CSV registros${NC}"

################################################################################
# IMPORTAR DATOS A POSTGRESQL
################################################################################

print_step 7 "Importación de Datos a PostgreSQL"

echo "Importando datos desde CSV..."

# Crear tabla temporal para importación
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
CREATE TEMP TABLE temp_empresas (
    nit TEXT,
    nombre TEXT,
    tipo TEXT,
    estado TEXT,
    cert_activo INTEGER,
    cert_fecha_inicio TEXT,
    cert_fecha_final TEXT,
    cert_notificacion TEXT,
    cert_renovado INTEGER,
    cert_facturado INTEGER,
    cert_comentarios TEXT,
    resol_activo INTEGER,
    resol_fecha_inicio TEXT,
    resol_fecha_final TEXT,
    resol_notificacion TEXT,
    resol_renovado INTEGER,
    resol_facturado INTEGER,
    resol_comentarios TEXT,
    doc_activo INTEGER,
    doc_fecha_inicio TEXT,
    doc_fecha_final TEXT,
    doc_notificacion TEXT,
    doc_renovado INTEGER,
    doc_facturado INTEGER,
    doc_comentarios TEXT,
    fecha_creacion TEXT,
    fecha_actualizacion TEXT
);
EOF

# Copiar CSV a tabla temporal
psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << EOF
\COPY temp_empresas FROM '$TMP_CSV' WITH CSV HEADER;
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error al importar CSV${NC}"
    rm -f "$TMP_CSV"
    exit 1
fi

# Insertar en tabla final con conversión de tipos
echo "Insertando datos en tabla final..."

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" << 'EOF'
INSERT INTO empresas (
    nit, nombre, tipo, estado,
    cert_activo, cert_fecha_inicio, cert_fecha_final, cert_notificacion,
    cert_renovado, cert_facturado, cert_comentarios,
    resol_activo, resol_fecha_inicio, resol_fecha_final, resol_notificacion,
    resol_renovado, resol_facturado, resol_comentarios,
    doc_activo, doc_fecha_inicio, doc_fecha_final, doc_notificacion,
    doc_renovado, doc_facturado, doc_comentarios,
    fecha_creacion, fecha_actualizacion
)
SELECT 
    nit, nombre, tipo, estado,
    cert_activo,
    CASE WHEN cert_fecha_inicio = '' THEN NULL ELSE cert_fecha_inicio::TIMESTAMP END,
    CASE WHEN cert_fecha_final = '' THEN NULL ELSE cert_fecha_final::TIMESTAMP END,
    NULLIF(cert_notificacion, ''),
    cert_renovado, cert_facturado,
    NULLIF(cert_comentarios, ''),
    resol_activo,
    CASE WHEN resol_fecha_inicio = '' THEN NULL ELSE resol_fecha_inicio::TIMESTAMP END,
    CASE WHEN resol_fecha_final = '' THEN NULL ELSE resol_fecha_final::TIMESTAMP END,
    NULLIF(resol_notificacion, ''),
    resol_renovado, resol_facturado,
    NULLIF(resol_comentarios, ''),
    doc_activo,
    CASE WHEN doc_fecha_inicio = '' THEN NULL ELSE doc_fecha_inicio::TIMESTAMP END,
    CASE WHEN doc_fecha_final = '' THEN NULL ELSE doc_fecha_final::TIMESTAMP END,
    NULLIF(doc_notificacion, ''),
    doc_renovado, doc_facturado,
    NULLIF(doc_comentarios, ''),
    fecha_creacion::TIMESTAMP,
    fecha_actualizacion::TIMESTAMP
FROM temp_empresas
ON CONFLICT (nit) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    tipo = EXCLUDED.tipo,
    estado = EXCLUDED.estado,
    cert_activo = EXCLUDED.cert_activo,
    cert_fecha_inicio = EXCLUDED.cert_fecha_inicio,
    cert_fecha_final = EXCLUDED.cert_fecha_final,
    cert_notificacion = EXCLUDED.cert_notificacion,
    cert_renovado = EXCLUDED.cert_renovado,
    cert_facturado = EXCLUDED.cert_facturado,
    cert_comentarios = EXCLUDED.cert_comentarios,
    resol_activo = EXCLUDED.resol_activo,
    resol_fecha_inicio = EXCLUDED.resol_fecha_inicio,
    resol_fecha_final = EXCLUDED.resol_fecha_final,
    resol_notificacion = EXCLUDED.resol_notificacion,
    resol_renovado = EXCLUDED.resol_renovado,
    resol_facturado = EXCLUDED.resol_facturado,
    resol_comentarios = EXCLUDED.resol_comentarios,
    doc_activo = EXCLUDED.doc_activo,
    doc_fecha_inicio = EXCLUDED.doc_fecha_inicio,
    doc_fecha_final = EXCLUDED.doc_fecha_final,
    doc_notificacion = EXCLUDED.doc_notificacion,
    doc_renovado = EXCLUDED.doc_renovado,
    doc_facturado = EXCLUDED.doc_facturado,
    doc_comentarios = EXCLUDED.doc_comentarios,
    fecha_actualizacion = EXCLUDED.fecha_actualizacion;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Datos importados correctamente${NC}"
else
    echo -e "${RED}✗ Error al insertar datos${NC}"
    rm -f "$TMP_CSV"
    exit 1
fi

# Limpiar archivo temporal
rm -f "$TMP_CSV"

################################################################################
# VERIFICACIÓN FINAL
################################################################################

print_step 8 "Verificación de Migración"

PG_COUNT=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -t -c "SELECT COUNT(*) FROM empresas;" | tr -d ' ')

echo -e "${BLUE}Registros en SQLite:    $TOTAL_EMPRESAS${NC}"
echo -e "${BLUE}Registros en PostgreSQL: $PG_COUNT${NC}"

if [ "$TOTAL_EMPRESAS" -eq "$PG_COUNT" ]; then
    echo -e "\n${GREEN}✓ Migración exitosa - Todos los registros fueron transferidos${NC}"
else
    echo -e "\n${YELLOW}⚠ Advertencia: Los números no coinciden${NC}"
    echo -e "${YELLOW}  Esto puede ser normal si había duplicados${NC}"
fi

################################################################################
# CREAR ARCHIVO .ENV
################################################################################

print_step 9 "Creación de Archivo .env"

read -p "¿Deseas crear/actualizar el archivo .env con la configuración PostgreSQL? (s/n): " CREAR_ENV

if [ "$CREAR_ENV" = "s" ]; then
    ENV_FILE=".env"
    
    if [ -f "$ENV_FILE" ]; then
        BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$ENV_FILE" "$BACKUP_FILE"
        echo -e "${YELLOW}  Backup creado: $BACKUP_FILE${NC}"
    fi
    
    cat > "$ENV_FILE" << EOF
# Base de datos PostgreSQL
DB_TYPE=postgresql
DB_HOST=$PG_HOST
DB_PORT=$PG_PORT
DB_NAME=$PG_DB
DB_USER=$PG_USER
DB_PASSWORD=$PG_PASSWORD

# API
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# CORS
CORS_ORIGINS=*

# Email (Gmail)
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Destinatarios de notificaciones
EMAIL_DESTINATARIOS=destinatario1@example.com

# Notificaciones
NOTIFICACION_DIAS_ANTICIPACION=30

# Seguridad
SECRET_KEY=change-this-to-a-random-secret-key-in-production
EOF

    echo -e "${GREEN}✓ Archivo .env creado/actualizado${NC}"
    echo -e "${YELLOW}  ⚠ IMPORTANTE: Revisa y actualiza las configuraciones de EMAIL y SECRET_KEY${NC}"
fi

################################################################################
# RESUMEN FINAL
################################################################################

print_banner "RESUMEN DE MIGRACIÓN"

echo -e "${GREEN}✅ Migración completada exitosamente${NC}\n"
echo -e "${BLUE}Estadísticas:${NC}"
echo -e "  • Registros migrados: $PG_COUNT"
echo -e "  • Base de datos origen: $SQLITE_PATH"
echo -e "  • Base de datos destino: $PG_DB @ $PG_HOST:$PG_PORT"

echo -e "\n${BLUE}Próximos pasos:${NC}"
echo -e "  1. Instala las dependencias Python:"
echo -e "     ${YELLOW}pip install -r requirements.txt${NC}"
echo -e "\n  2. Verifica el archivo .env (especialmente EMAIL y SECRET_KEY)"
echo -e "\n  3. Inicia la aplicación:"
echo -e "     ${YELLOW}python servidor.py${NC}"

echo -e "\n${BLUE}Verificación en PostgreSQL:${NC}"
echo -e "  ${YELLOW}psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DB${NC}"
echo -e "  ${YELLOW}SELECT COUNT(*) FROM empresas;${NC}"

print_banner "¡MIGRACIÓN COMPLETADA!"

# Limpiar variables de entorno
unset PGPASSWORD

exit 0
