# 🐳 Docker - Despliegue con Contenedores

## 📦 Archivos Creados

- `Dockerfile` - Imagen Docker de la aplicación
- `docker-compose.yml` - Orquestación de contenedores
- `.env.production.example` - Plantilla de variables de entorno
- `deploy.sh` - Script completo de despliegue
- `quick-deploy.sh` - Script de instalación rápida
- `nginx.conf` - Configuración de Nginx como reverse proxy
- `.gitignore` - Archivos a ignorar en Git
- `DEPLOY.md` - Guía completa de despliegue

## 🚀 Uso Local con Docker

### Construcción y Ejecución

```bash
# Construir la imagen
docker-compose build

# Iniciar los contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Acceder a la Aplicación

Una vez iniciado, accede en: http://localhost:5000

## 🌐 Despliegue en Digital Ocean

### Opción 1: Quick Deploy (Más Rápido)

```bash
# 1. Conectar al servidor
ssh root@TU_IP

# 2. Descargar proyecto
git clone https://github.com/tu-usuario/sadi.git
cd sadi

# 3. Ejecutar instalación automática
chmod +x quick-deploy.sh
./quick-deploy.sh
```

### Opción 2: Deploy Completo (Más Control)

```bash
# 1. Conectar al servidor
ssh root@TU_IP

# 2. Clonar proyecto
git clone https://github.com/tu-usuario/sadi.git
cd sadi

# 3. Configurar variables
cp .env.production.example .env.production
nano .env.production

# 4. Ejecutar despliegue
chmod +x deploy.sh
./deploy.sh
```

## 📋 Variables de Entorno Requeridas

Crea `.env.production` con:

```env
SMTP_USER=tucorreo@gmail.com
SMTP_PASSWORD=contraseña_aplicacion_gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL_DESTINATARIOS=correo1@ejemplo.com,correo2@ejemplo.com
SECRET_KEY=clave_segura_generada
```

## 🔧 Comandos Útiles

```bash
# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f web

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Reconstruir
docker-compose build --no-cache

# Ejecutar comando dentro del contenedor
docker-compose exec web python scripts/init_db.py

# Backup de BD
docker-compose exec web python -c "import shutil; shutil.copy('data/facturacion.db', 'data/backup.db')"

# Ver uso de recursos
docker stats sadi-facturacion
```

## 🔒 Seguridad

### Configurar Firewall

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Configurar SSL (Opcional)

1. Instalar Nginx: `apt-get install nginx`
2. Copiar configuración: `cp nginx.conf /etc/nginx/sites-available/sadi`
3. Activar sitio: `ln -s /etc/nginx/sites-available/sadi /etc/nginx/sites-enabled/`
4. Instalar Certbot: `apt-get install certbot python3-certbot-nginx`
5. Obtener certificado: `certbot --nginx -d tudominio.com`

## 📊 Monitoreo

### Healthcheck

El contenedor incluye healthcheck automático que verifica cada 30 segundos:

```bash
docker inspect sadi-facturacion | grep Health -A 10
```

### Logs

Los logs se guardan en el directorio `logs/` y en la salida de Docker:

```bash
# Ver logs de aplicación
tail -f logs/*.log

# Ver logs de Docker
docker-compose logs --tail=100 -f
```

## 🔄 Actualización

```bash
# Si usas Git
git pull

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d
```

## 🆘 Troubleshooting

### Contenedor no inicia

```bash
docker-compose logs web
```

### Base de datos corrupta

```bash
docker-compose exec web python scripts/init_db.py
```

### Puerto ocupado

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8000:5000"  # Usar puerto 8000 en lugar de 5000
```

### Problemas de permisos

```bash
chmod -R 755 data logs
```

## 📖 Documentación Completa

Ver `DEPLOY.md` para la guía completa de despliegue con todas las opciones y configuraciones avanzadas.

## ✅ Checklist Pre-Despliegue

- [ ] Archivo `.env.production` configurado
- [ ] Credenciales de Gmail válidas
- [ ] Puerto 5000 disponible (o modificado)
- [ ] Docker y Docker Compose instalados
- [ ] Suficiente espacio en disco (mínimo 1GB)
- [ ] Firewall configurado
- [ ] Backup de datos importantes

¡Listo para desplegar! 🚀
