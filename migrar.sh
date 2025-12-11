#!/bin/bash

################################################################################
# Script de detección automática para elegir el método de migración
################################################################################

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================================================"
echo "  ASISTENTE DE MIGRACIÓN A POSTGRESQL"
echo "======================================================================"
echo -e "${NC}\n"

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    HAS_PYTHON=true
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
    HAS_PYTHON=true
else
    HAS_PYTHON=false
fi

# Detectar herramientas bash
HAS_SQLITE3=$(command -v sqlite3 &> /dev/null && echo true || echo false)
HAS_PSQL=$(command -v psql &> /dev/null && echo true || echo false)

echo -e "${YELLOW}Análisis del sistema:${NC}\n"

if [ "$HAS_PYTHON" = true ]; then
    echo -e "${GREEN}✓ Python encontrado: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}✗ Python no encontrado${NC}"
fi

if [ "$HAS_SQLITE3" = true ]; then
    echo -e "${GREEN}✓ sqlite3 encontrado${NC}"
else
    echo -e "${YELLOW}✗ sqlite3 no encontrado${NC}"
fi

if [ "$HAS_PSQL" = true ]; then
    echo -e "${GREEN}✓ psql encontrado${NC}"
else
    echo -e "${YELLOW}✗ psql no encontrado${NC}"
fi

echo -e "\n${BLUE}======================================================================"
echo "  MÉTODO RECOMENDADO"
echo "======================================================================${NC}\n"

# Recomendar método
if [ "$HAS_PYTHON" = true ]; then
    echo -e "${GREEN}Se detectó Python instalado${NC}"
    echo -e "Recomendación: Usar el asistente Python (más completo)\n"
    
    read -p "¿Deseas usar el asistente Python? (s/n): " USAR_PYTHON
    
    if [ "$USAR_PYTHON" = "s" ] || [ "$USAR_PYTHON" = "S" ]; then
        echo -e "\n${GREEN}Ejecutando asistente Python...${NC}\n"
        $PYTHON_CMD scripts/asistente_migracion.py
        exit 0
    fi
fi

# Si no usa Python o no está disponible
if [ "$HAS_SQLITE3" = true ] && [ "$HAS_PSQL" = true ]; then
    echo -e "${GREEN}Se detectaron las herramientas necesarias para migración bash${NC}"
    echo -e "Recomendación: Usar el script bash (sin dependencias Python)\n"
    
    read -p "¿Deseas usar el script bash? (s/n): " USAR_BASH
    
    if [ "$USAR_BASH" = "s" ] || [ "$USAR_BASH" = "S" ]; then
        echo -e "\n${GREEN}Ejecutando script bash...${NC}\n"
        chmod +x scripts/migrar_a_postgresql.sh
        ./scripts/migrar_a_postgresql.sh
        exit 0
    fi
else
    echo -e "${YELLOW}⚠ Faltan herramientas necesarias${NC}\n"
    
    if [ "$HAS_SQLITE3" = false ]; then
        echo "Instala sqlite3:"
        echo "  Ubuntu/Debian: sudo apt-get install sqlite3"
        echo "  CentOS/RHEL:   sudo yum install sqlite"
    fi
    
    if [ "$HAS_PSQL" = false ]; then
        echo "Instala postgresql-client:"
        echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
        echo "  CentOS/RHEL:   sudo yum install postgresql"
    fi
    
    echo ""
fi

# Menú manual
echo -e "\n${BLUE}======================================================================"
echo "  SELECCIÓN MANUAL"
echo "======================================================================${NC}\n"
echo "1. Asistente Python (requiere Python)"
echo "2. Script Bash (requiere sqlite3 y psql)"
echo "3. Ver documentación"
echo "0. Salir"
echo ""

read -p "Selecciona una opción: " OPCION

case $OPCION in
    1)
        if [ "$HAS_PYTHON" = true ]; then
            $PYTHON_CMD scripts/asistente_migracion.py
        else
            echo -e "\n${YELLOW}Python no está instalado${NC}"
        fi
        ;;
    2)
        if [ "$HAS_SQLITE3" = true ] && [ "$HAS_PSQL" = true ]; then
            chmod +x scripts/migrar_a_postgresql.sh
            ./scripts/migrar_a_postgresql.sh
        else
            echo -e "\n${YELLOW}Faltan herramientas necesarias${NC}"
        fi
        ;;
    3)
        echo -e "\n${BLUE}Documentación disponible:${NC}"
        echo "  - README_POSTGRESQL.md       - Índice principal"
        echo "  - MIGRACION_SIN_PYTHON.md    - Guía para script bash"
        echo "  - INICIO_RAPIDO_POSTGRESQL.md - Guía para Python"
        echo "  - FAQ_POSTGRESQL.md          - Preguntas frecuentes"
        ;;
    0)
        echo -e "\n${YELLOW}Saliendo...${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${YELLOW}Opción inválida${NC}"
        exit 1
        ;;
esac
