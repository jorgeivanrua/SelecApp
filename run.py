#!/usr/bin/env python3
"""
Script de ejecución del Sistema Electoral ERP
"""

import os
import logging
from app import create_app
from config import get_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Función principal"""
    
    # Obtener configuración
    config_class = get_config()
    
    # Crear aplicación
    app = create_app()
    app.config.from_object(config_class)
    
    # Configurar logging según el entorno
    if app.config.get('DEBUG'):
        logging.getLogger().setLevel(logging.DEBUG)
        app.logger.info("Running in DEBUG mode")
    
    # Información del sistema
    app.logger.info("=" * 50)
    app.logger.info("Sistema Electoral ERP - Caquetá")
    app.logger.info("=" * 50)
    app.logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    app.logger.info(f"Database: {app.config.get('DATABASE_URL', 'Not configured')}")
    app.logger.info(f"Debug mode: {app.config.get('DEBUG', False)}")
    app.logger.info("=" * 50)
    
    # Verificar base de datos
    try:
        if app.db_manager.health_check():
            app.logger.info("✓ Database connection successful")
        else:
            app.logger.error("✗ Database connection failed")
    except Exception as e:
        app.logger.error(f"✗ Database error: {e}")
    
    # Configuración del servidor
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    app.logger.info(f"Starting server on {host}:{port}")
    
    # Ejecutar aplicación
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()