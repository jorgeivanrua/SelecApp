#!/bin/bash
# Script de despliegue para Sistema Electoral ERP

set -e

echo "🚀 DESPLIEGUE DEL SISTEMA ELECTORAL ERP"
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

print_success "Docker y Docker Compose están disponibles"

# Verificar archivos de configuración
print_status "Verificando archivos de configuración..."

if [ ! -f ".env.production" ]; then
    print_warning "Archivo .env.production no encontrado. Creando desde plantilla..."
    cp .env.production.template .env.production 2>/dev/null || true
fi

if [ ! -f "docker-compose.yml" ]; then
    print_error "Archivo docker-compose.yml no encontrado"
    exit 1
fi

print_success "Archivos de configuración verificados"

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p logs uploads backups ssl static

# Configurar permisos
chmod +x entrypoint.sh scripts/backup.sh

print_success "Directorios creados"

# Verificar configuración de SSL
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    print_warning "Certificados SSL no encontrados. Generando certificados auto-firmados para desarrollo..."
    mkdir -p ssl
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
        -subj "/C=CO/ST=Caqueta/L=Florencia/O=Gobernacion del Caqueta/CN=sistema-electoral.caqueta.gov.co"
    print_warning "IMPORTANTE: Reemplaza los certificados auto-firmados con certificados válidos en producción"
fi

# Construir imágenes
print_status "Construyendo imágenes Docker..."
docker-compose build --no-cache

print_success "Imágenes construidas exitosamente"

# Detener servicios existentes si están corriendo
print_status "Deteniendo servicios existentes..."
docker-compose down --remove-orphans

# Iniciar servicios
print_status "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_status "Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado de los servicios
print_status "Verificando estado de los servicios..."

services=("sistema-electoral-db" "sistema-electoral-redis" "sistema-electoral-app" "sistema-electoral-nginx")
all_healthy=true

for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" | grep -q $service; then
        print_success "✅ $service está ejecutándose"
    else
        print_error "❌ $service no está ejecutándose"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    print_success "🎉 Todos los servicios están ejecutándose correctamente"
    
    # Mostrar información de acceso
    echo ""
    echo "🌐 INFORMACIÓN DE ACCESO"
    echo "======================="
    echo "URL Principal: https://localhost"
    echo "URL HTTP: http://localhost (redirige a HTTPS)"
    echo "API Base: https://localhost/api"
    echo ""
    
    # Mostrar logs de la aplicación
    print_status "Mostrando logs de la aplicación (últimas 20 líneas)..."
    docker-compose logs --tail=20 app
    
    echo ""
    print_success "🚀 Despliegue completado exitosamente!"
    print_status "Para ver logs en tiempo real: docker-compose logs -f"
    print_status "Para detener servicios: docker-compose down"
    print_status "Para ver estado: docker-compose ps"
    
else
    print_error "❌ Algunos servicios no se iniciaron correctamente"
    print_status "Mostrando logs para diagnóstico..."
    docker-compose logs --tail=50
    exit 1
fi

# Crear backup inicial
print_status "Creando backup inicial..."
sleep 10
docker-compose exec -T backup /backup.sh

print_success "✅ Sistema Electoral ERP desplegado y listo para producción!"