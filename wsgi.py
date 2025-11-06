#!/usr/bin/env python3
"""
WSGI entry point para Sistema Electoral ERP
Punto de entrada para servidores WSGI como Gunicorn
"""

import os
from app import create_app

# Configurar entorno
os.environ.setdefault('FLASK_ENV', 'production')

# Crear aplicación
app = create_app()

if __name__ == "__main__":
    # Solo para desarrollo local
    app.run(host='0.0.0.0', port=5000, debug=False)