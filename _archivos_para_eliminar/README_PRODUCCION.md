# Sistema Electoral ERP - Despliegue en Producción

## 🚀 Guía de Despliegue para Producción

### Requisitos del Sistema

#### Hardware Mínimo
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Almacenamiento**: 100 GB SSD
- **Red**: Conexión estable a internet

#### Software Requerido
- **Sistema Operativo**: Ubuntu 20.04 LTS o superior
- **Docker**: 20.10 o superior
- **Docker Compose**: 2.0 o superior
- **Nginx**: (incluido en contenedor)
- **PostgreSQL**: (incluido en contenedor)

### 📋 Pasos de Instalación

#### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar cambios de grupo
```

#### 2. Clonar y Configurar la Aplicación

```bash
# Clonar repositorio
git clone <repository-url> sistema-electoral
cd sistema-electoral

# Copiar configuración de producción
cp .env.production .env

# Editar configuración (IMPORTANTE)
nano .env
```

#### 3. Configurar Variables de Entorno

Editar el archivo `.env` con los valores de producción:

```bash
# Configuración crítica a cambiar
SECRET_KEY=tu-clave-secreta-super-segura-aqui
JWT_SECRET_KEY=tu-jwt-secreto-super-seguro-aqui
DATABASE_URL=postgresql://electoral_user:password_seguro@db:5432/caqueta_electoral

# Configuración de correo
MAIL_SERVER=smtp.caqueta.gov.co
MAIL_USERNAME=sistema.electoral@caqueta.gov.co
MAIL_PASSWORD=password_del_correo

# Administradores
ADMINS=admin@caqueta.gov.co,soporte@caqueta.gov.co
```

#### 4. Configurar SSL (Certificados)

```bash
# Para certificados Let's Encrypt (recomendado)
sudo apt install certbot
sudo certbot certonly --standalone -d sistema-electoral.caqueta.gov.co

# Copiar certificados
sudo cp /etc/letsencrypt/live/sistema-electoral.caqueta.gov.co/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/sistema-electoral.caqueta.gov.co/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

#### 5. Desplegar la Aplicación

```bash
# Hacer ejecutable el script de despliegue
chmod +x deploy.sh

# Ejecutar despliegue
./deploy.sh
```

### 🔧 Comandos de Administración

#### Gestión de Servicios

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f app

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Actualizar aplicación
git pull
docker-compose build --no-cache
docker-compose up -d
```

#### Gestión de Base de Datos

```bash
# Backup manual
docker-compose exec backup /backup.sh

# Restaurar backup
docker-compose exec -T db psql -U electoral_user -d caqueta_electoral < backup.sql

# Acceder a la base de datos
docker-compose exec db psql -U electoral_user -d caqueta_electoral

# Inicializar datos
docker-compose exec app python init_db.py
```

#### Monitoreo

```bash
# Ver recursos utilizados
docker stats

# Ver logs de Nginx
docker-compose logs nginx

# Ver logs de la aplicación
docker-compose logs app

# Health check
curl https://localhost/api/health
```

### 🔒 Configuración de Seguridad

#### Firewall

```bash
# Configurar UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5432/tcp  # PostgreSQL solo interno
```

#### Actualizaciones Automáticas

```bash
# Configurar actualizaciones automáticas
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Backup Automático

El sistema incluye backup automático diario a las 2:00 AM. Los backups se almacenan en `./backups/` y se mantienen por 30 días.

### 📊 Monitoreo y Logs

#### Ubicaciones de Logs

- **Aplicación**: `./logs/sistema_electoral.log`
- **Nginx**: `/var/log/nginx/`
- **PostgreSQL**: Logs del contenedor
- **Backup**: `./backups/backup.log`

#### Métricas de Rendimiento

```bash
# Ver uso de recursos
docker-compose exec app python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'RAM: {psutil.virtual_memory().percent}%')
print(f'Disco: {psutil.disk_usage(\"/\").percent}%')
"
```

### 🚨 Solución de Problemas

#### Problemas Comunes

1. **Servicios no inician**
   ```bash
   docker-compose logs
   docker-compose down && docker-compose up -d
   ```

2. **Error de conexión a base de datos**
   ```bash
   docker-compose restart db
   docker-compose logs db
   ```

3. **Certificados SSL expirados**
   ```bash
   sudo certbot renew
   sudo cp /etc/letsencrypt/live/*/fullchain.pem ssl/cert.pem
   sudo cp /etc/letsencrypt/live/*/privkey.pem ssl/key.pem
   docker-compose restart nginx
   ```

4. **Espacio en disco lleno**
   ```bash
   # Limpiar contenedores no utilizados
   docker system prune -a
   
   # Limpiar logs antiguos
   sudo journalctl --vacuum-time=7d
   ```

### 📞 Soporte

#### Contactos de Emergencia
- **Administrador del Sistema**: admin@caqueta.gov.co
- **Soporte Técnico**: soporte@caqueta.gov.co
- **Teléfono de Emergencia**: +57 (8) 123-4567

#### Información del Sistema
- **Versión**: 1.0.0
- **Entorno**: Producción
- **Base de Datos**: PostgreSQL 15
- **Servidor Web**: Nginx + Gunicorn
- **Monitoreo**: Health checks automáticos

### 🔄 Actualizaciones

#### Proceso de Actualización

1. **Backup completo**
   ```bash
   docker-compose exec backup /backup.sh
   ```

2. **Descargar nueva versión**
   ```bash
   git pull origin main
   ```

3. **Actualizar servicios**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Verificar funcionamiento**
   ```bash
   curl https://localhost/api/health
   ```

### ✅ Lista de Verificación Post-Despliegue

- [ ] Servicios ejecutándose correctamente
- [ ] SSL configurado y funcionando
- [ ] Base de datos inicializada
- [ ] Backup automático configurado
- [ ] Firewall configurado
- [ ] Monitoreo funcionando
- [ ] Usuarios administradores creados
- [ ] Pruebas de funcionalidad completadas
- [ ] Documentación entregada al equipo

---

**Sistema Electoral ERP v1.0.0**  
**Departamento del Caquetá - Colombia**  
**Noviembre 2024**