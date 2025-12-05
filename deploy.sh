#!/bin/bash

#######################################################
# Script de despliegue para Digital Ocean
# Sistema de Gestión de Facturación
#######################################################

set -e  # Salir si hay errores

echo "======================================================"
echo "   SADI - Sistema de Gestión de Facturación"
echo "   Despliegue en Digital Ocean"
echo "======================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encuentra docker-compose.yml. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

print_info "Verificando requisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker instalado correctamente"
else
    print_success "Docker encontrado: $(docker --version)"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose instalado correctamente"
else
    print_success "Docker Compose encontrado: $(docker-compose --version)"
fi

# Verificar archivo de configuración
if [ ! -f ".env.production" ]; then
    print_warning "No se encuentra .env.production"
    print_info "Creando desde plantilla..."
    
    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env.production
        print_warning "Se ha creado .env.production desde la plantilla"
        print_warning "IMPORTANTE: Edita .env.production con tus credenciales reales antes de continuar"
        
        read -p "¿Deseas editar .env.production ahora? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            ${EDITOR:-nano} .env.production
        else
            print_error "Debes configurar .env.production antes de desplegar"
            exit 1
        fi
    else
        print_error "No se encuentra .env.production.example"
        exit 1
    fi
fi

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p data logs
chmod 755 data logs
print_success "Directorios creados"

# Detener contenedores existentes
print_info "Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true

# Construir imagen
print_info "Construyendo imagen Docker..."
docker-compose build --no-cache

# Cargar variables de entorno
print_info "Cargando variables de entorno..."
export $(cat .env.production | grep -v '^#' | xargs)

# Iniciar contenedores
print_info "Iniciando contenedores..."
docker-compose up -d

# Esperar a que la aplicación esté lista
print_info "Esperando a que la aplicación inicie..."
sleep 10

# Inicializar base de datos si no existe
if [ ! -f "data/facturacion.db" ]; then
    print_info "Inicializando base de datos..."
    docker-compose exec -T web python scripts/init_db.py || print_warning "No se pudo inicializar la BD automáticamente"
fi

# Verificar estado
print_info "Verificando estado de los contenedores..."
docker-compose ps

# Verificar health
sleep 5
if docker-compose ps | grep -q "healthy\|Up"; then
    print_success "✓ Aplicación desplegada correctamente!"
else
    print_warning "La aplicación está iniciando. Verifica los logs con: docker-compose logs -f"
fi

echo ""
echo "======================================================"
echo "   DESPLIEGUE COMPLETADO"
echo "======================================================"
echo ""
echo "🌐 La aplicación está disponible en:"
echo "   http://$(curl -s ifconfig.me):5000"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs:              docker-compose logs -f"
echo "   Reiniciar:             docker-compose restart"
echo "   Detener:               docker-compose down"
echo "   Ver estado:            docker-compose ps"
echo "   Ejecutar comando:      docker-compose exec web [comando]"
echo ""
echo "📊 Monitoreo:"
echo "   Healthcheck:           docker inspect sadi-facturacion | grep Health -A 10"
echo "   Uso de recursos:       docker stats sadi-facturacion"
echo ""
echo "🔒 Seguridad:"
echo "   - Asegúrate de configurar un firewall (ufw)"
echo "   - Considera usar un reverse proxy (nginx)"
echo "   - Configura SSL/TLS para producción"
echo ""
print_warning "IMPORTANTE: Configura el firewall y SSL para producción"
echo ""
