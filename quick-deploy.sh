#!/bin/bash

#######################################################
# Script de despliegue simplificado para Digital Ocean
# Configuración rápida en un solo paso
#######################################################

set -e

echo "======================================================"
echo "   SADI - Instalación Rápida"
echo "======================================================"
echo ""

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Instalar Docker Compose
echo "🔧 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Git
echo "📥 Instalando Git..."
sudo apt-get install -y git

# Clonar repositorio (ajusta la URL)
echo "📂 Clonando repositorio..."
echo "NOTA: Ajusta la siguiente línea con tu repositorio Git"
# git clone https://github.com/tu-usuario/sadi.git
# cd sadi

# Si ya estás en el directorio del proyecto:
echo "⚙️ Configurando aplicación..."

# Crear archivo .env.production
if [ ! -f ".env.production" ]; then
    echo "📝 Configurando variables de entorno..."
    
    read -p "Email SMTP (Gmail): " smtp_user
    read -sp "Contraseña de aplicación Gmail: " smtp_pass
    echo ""
    read -p "Email(s) destinatarios (separados por comas): " destinatarios
    
    cat > .env.production <<EOF
SMTP_USER=$smtp_user
SMTP_PASSWORD=$smtp_pass
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_DESTINATARIOS=$destinatarios
SECRET_KEY=$(openssl rand -base64 32)
EOF
    
    echo "✓ Configuración guardada en .env.production"
fi

# Crear directorios
mkdir -p data logs

# Construir e iniciar
echo "🚀 Construyendo y desplegando aplicación..."
docker-compose build
docker-compose up -d

# Esperar inicialización
echo "⏳ Esperando inicialización..."
sleep 15

# Inicializar BD
echo "💾 Inicializando base de datos..."
docker-compose exec -T web python scripts/init_db.py 2>/dev/null || echo "⚠️ Ejecuta manualmente: docker-compose exec web python scripts/init_db.py"

# Configurar firewall
echo "🔒 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

# Obtener IP pública
IP=$(curl -s ifconfig.me)

echo ""
echo "======================================================"
echo "   ✅ INSTALACIÓN COMPLETADA"
echo "======================================================"
echo ""
echo "🌐 Accede a tu aplicación en:"
echo "   http://$IP:5000"
echo ""
echo "📋 Credenciales configuradas:"
echo "   SMTP User: $smtp_user"
echo "   Destinatarios: $destinatarios"
echo ""
echo "🔧 Comandos útiles:"
echo "   Ver logs:    docker-compose logs -f"
echo "   Reiniciar:   docker-compose restart"
echo "   Detener:     docker-compose down"
echo ""
echo "⚠️ SIGUIENTE PASO RECOMENDADO:"
echo "   Configura un dominio y SSL con nginx + certbot"
echo ""
