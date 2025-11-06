#!/bin/bash
# Script de entrada para Sistema Electoral ERP

set -e

echo "🚀 Iniciando Sistema Electoral ERP..."

# Esperar a que la base de datos esté disponible
echo "⏳ Esperando conexión a la base de datos..."
while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
    sleep 1
done
echo "✅ Base de datos disponible"

# Ejecutar migraciones si es necesario
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "🔄 Ejecutando migraciones de base de datos..."
    python -c "
from app import create_app
from flask_migrate import upgrade
app = create_app()
with app.app_context():
    upgrade()
"
    echo "✅ Migraciones completadas"
fi

# Crear directorios necesarios
mkdir -p logs uploads

# Verificar configuración
echo "🔍 Verificando configuración..."
python -c "
import os
from config import config

env = os.environ.get('FLASK_ENV', 'production')
cfg = config[env]
print(f'Entorno: {env}')
print(f'Debug: {cfg.DEBUG if hasattr(cfg, \"DEBUG\") else False}')
print('✅ Configuración válida')
"

# Inicializar datos de prueba si es necesario
if [ "$INIT_DEMO_DATA" = "true" ]; then
    echo "📊 Inicializando datos de demostración..."
    python setup_demo_users.py
    echo "✅ Datos de demostración creados"
fi

echo "🎯 Sistema Electoral ERP listo para producción"
echo "🌐 Servidor iniciando en puerto ${PORT:-5000}"

# Ejecutar comando principal
exec "$@"