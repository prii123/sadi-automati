# Guía de Despliegue en Digital Ocean

## 📋 Requisitos Previos

- Cuenta en Digital Ocean
- Droplet Ubuntu 22.04 LTS (mínimo 1GB RAM)
- Acceso SSH al servidor
- Credenciales de Gmail configuradas

## 🚀 Opción 1: Despliegue Rápido (Recomendado)

### Paso 1: Crear Droplet en Digital Ocean

1. Ve a [Digital Ocean](https://www.digitalocean.com/)
2. Crea un nuevo Droplet:
   - **Imagen:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/mes - 1GB RAM, 1 vCPU)
   - **Región:** Selecciona la más cercana
   - **Autenticación:** SSH Key (recomendado) o contraseña
   - **Hostname:** sadi-facturacion

3. Espera a que el Droplet esté listo y anota la IP pública

### Paso 2: Conectar al Servidor

```bash
ssh root@TU_IP_PUBLICA
```

### Paso 3: Subir el Proyecto

**Opción A - Usando Git (Recomendado):**

```bash
# En el servidor
cd /opt
git clone https://github.com/tu-usuario/sadi.git
cd sadi
```

**Opción B - Usando SCP desde tu máquina local:**

```bash
# En tu máquina local (PowerShell)
scp -r C:\Users\Aurora Lozano\Downloads\sadi root@TU_IP_PUBLICA:/opt/
```

### Paso 4: Ejecutar Script de Instalación

```bash
cd /opt/sadi
chmod +x quick-deploy.sh
./quick-deploy.sh
```

El script te pedirá:
- Email de Gmail
- Contraseña de aplicación de Gmail
- Email(s) de destinatarios

¡Y listo! La aplicación estará corriendo en `http://TU_IP:5000`

---

## 🛠️ Opción 2: Despliegue Manual (Control Total)

### Paso 1: Preparar el Servidor

```bash
# Conectar al servidor
ssh root@TU_IP_PUBLICA

# Actualizar sistema
apt-get update && apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Paso 2: Configurar la Aplicación

```bash
# Ir al directorio del proyecto
cd /opt/sadi

# Crear archivo de configuración
cp .env.production.example .env.production
nano .env.production
```

Edita con tus valores:
```env
SMTP_USER=tucorreo@gmail.com
SMTP_PASSWORD=tu_contraseña_aplicacion
EMAIL_DESTINATARIOS=destinatario1@ejemplo.com,destinatario2@ejemplo.com
SECRET_KEY=$(openssl rand -base64 32)
```

### Paso 3: Ejecutar Script de Despliegue

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🔒 Configuración de Seguridad (Opcional pero Recomendado)

### Configurar Firewall

```bash
# Permitir SSH
ufw allow 22/tcp

# Permitir puerto de la aplicación
ufw allow 5000/tcp

# Activar firewall
ufw enable
```

### Configurar Nginx como Reverse Proxy

```bash
# Instalar Nginx
apt-get install -y nginx

# Crear configuración
cat > /etc/nginx/sites-available/sadi <<EOF
server {
    listen 80;
    server_name TU_DOMINIO.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activar configuración
ln -s /etc/nginx/sites-available/sadi /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
apt-get install -y certbot python3-certbot-nginx

# Obtener certificado SSL
certbot --nginx -d TU_DOMINIO.com

# Renovación automática
certbot renew --dry-run
```

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs de la Aplicación

```bash
docker-compose logs -f
```

### Ver Estado de Contenedores

```bash
docker-compose ps
```

### Reiniciar Aplicación

```bash
docker-compose restart
```

### Detener Aplicación

```bash
docker-compose down
```

### Actualizar Aplicación

```bash
# Si usas Git
git pull

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec web python -c "import shutil; shutil.copy('data/facturacion.db', 'data/backup_$(date +%Y%m%d).db')"

# Descargar backup a tu máquina local
scp root@TU_IP:/opt/sadi/data/backup_*.db ./
```

### Ver Uso de Recursos

```bash
docker stats sadi-facturacion
```

---

## 🔧 Solución de Problemas

### La aplicación no inicia

```bash
# Ver logs detallados
docker-compose logs web

# Verificar configuración
docker-compose config

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Error de base de datos

```bash
# Inicializar manualmente
docker-compose exec web python scripts/init_db.py
```

### Error de permisos

```bash
# Ajustar permisos
chmod -R 755 data logs
chown -R 1000:1000 data logs
```

### Contenedor se reinicia constantemente

```bash
# Ver logs
docker-compose logs --tail=50 web

# Verificar healthcheck
docker inspect sadi-facturacion | grep Health -A 10
```

---

## 📈 Optimizaciones para Producción

### 1. Configurar Swap (para servidores con poca RAM)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 2. Configurar Logs con Rotación

```bash
# Instalar logrotate
apt-get install -y logrotate

# Crear configuración
cat > /etc/logrotate.d/sadi <<EOF
/opt/sadi/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 3. Monitoreo con Uptime Robot

- Registrarte en [UptimeRobot](https://uptimerobot.com/)
- Crear monitor HTTP para `http://TU_IP:5000/api`
- Configurar alertas por email

### 4. Backup Automático

```bash
# Crear script de backup
cat > /opt/backup-sadi.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/sadi-backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /opt/sadi/data/facturacion.db $BACKUP_DIR/backup_$DATE.db
find $BACKUP_DIR -name "backup_*.db" -mtime +7 -delete
EOF

chmod +x /opt/backup-sadi.sh

# Programar con cron (diario a las 2 AM)
crontab -e
# Agregar: 0 2 * * * /opt/backup-sadi.sh
```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la configuración: `cat .env.production`
3. Comprueba el estado: `docker-compose ps`
4. Reinicia si es necesario: `docker-compose restart`

---

## 🎯 Checklist de Despliegue

- [ ] Droplet creado en Digital Ocean
- [ ] Proyecto subido al servidor
- [ ] Docker y Docker Compose instalados
- [ ] Archivo `.env.production` configurado
- [ ] Aplicación desplegada y corriendo
- [ ] Firewall configurado
- [ ] Nginx configurado (opcional)
- [ ] SSL configurado (opcional)
- [ ] Backup automático configurado
- [ ] Monitoreo configurado

¡Tu aplicación está lista para producción! 🚀
