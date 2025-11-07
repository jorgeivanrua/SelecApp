#!/usr/bin/env python3
"""
Script de inicio para producción con Gunicorn
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Verificar que los requisitos estén instalados"""
    try:
        import gunicorn
        print("✅ Gunicorn disponible")
    except ImportError:
        print("❌ Gunicorn no está instalado")
        print("Instalando Gunicorn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
        print("✅ Gunicorn instalado")

def setup_production_environment():
    """Configurar variables de entorno para producción"""
    
    # Variables de entorno por defecto para producción
    env_vars = {
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'False',
        'SECRET_KEY': 'electoral_system_secret_key_production_2024',
        'JWT_SECRET_KEY': 'jwt_secret_key_electoral_system_prod_2024',
        'DATABASE_URL': 'sqlite:///electoral_system_prod.db',
        'LOG_LEVEL': 'INFO',
        'HOST': '0.0.0.0',
        'PORT': '5000',
        'CORS_ORIGINS': '*'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("Variables de entorno configuradas para produccion")

def start_with_gunicorn():
    """Iniciar aplicación con Gunicorn para producción"""
    
    print("Iniciando Sistema Electoral en modo PRODUCCION con Gunicorn...")
    
    # Configuración de Gunicorn optimizada para producción
    gunicorn_config = [
        'gunicorn',
        '--bind', '0.0.0.0:5000',
        '--workers', '4',  # 4 workers para mejor rendimiento
        '--worker-class', 'sync',
        '--worker-connections', '1000',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--timeout', '30',
        '--keep-alive', '2',
        '--preload',  # Precargar aplicación para mejor rendimiento
        '--access-logfile', 'access.log',
        '--error-logfile', 'error.log',
        '--log-level', 'info',
        '--capture-output',
        'app_production:app'
    ]
    
    try:
        subprocess.run(gunicorn_config, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando con Gunicorn: {e}")
        print("Intentando con Flask development server...")
        start_with_flask()
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")

def start_with_flask():
    """Iniciar aplicación con Flask development server como fallback"""
    
    print("Iniciando Sistema Electoral con Flask development server...")
    
    try:
        from app_production import main
        main()
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")

def create_production_database():
    """Crear base de datos de producción si no existe"""
    
    db_path = 'electoral_system_prod.db'
    
    if not Path(db_path).exists():
        print("Creando base de datos de produccion...")
        
        try:
            # Copiar base de datos de desarrollo si existe
            dev_db = 'electoral_system.db'
            if Path(dev_db).exists():
                import shutil
                shutil.copy2(dev_db, db_path)
                print(f"✅ Base de datos copiada de {dev_db} a {db_path}")
            else:
                # Crear base de datos vacía
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.execute('CREATE TABLE IF NOT EXISTS system_info (key TEXT, value TEXT)')
                conn.execute('INSERT INTO system_info VALUES (?, ?)', 
                           ('created', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                print(f"✅ Base de datos de producción creada: {db_path}")
                
        except Exception as e:
            print(f"⚠️  Error creando base de datos: {e}")
    else:
        print(f"✅ Base de datos de producción existe: {db_path}")

def main():
    """Función principal"""
    
    print("=" * 60)
    print("SISTEMA ELECTORAL CAQUETA - INICIO PRODUCCION")
    print("=" * 60)
    
    # Verificar requisitos
    check_requirements()
    
    # Configurar entorno
    setup_production_environment()
    
    # Crear base de datos
    create_production_database()
    
    # Mostrar información
    print(f"Host: {os.environ.get('HOST', '0.0.0.0')}")
    print(f"Puerto: {os.environ.get('PORT', '5000')}")
    print(f"Base de datos: {os.environ.get('DATABASE_URL')}")
    print(f"Modo seguro: Produccion")
    print(f"Logs: access.log, error.log, electoral_system.log")
    
    print("\n" + "=" * 60)
    
    # Intentar iniciar con Gunicorn primero
    try:
        start_with_gunicorn()
    except Exception as e:
        print(f"❌ Error con Gunicorn: {e}")
        print("Iniciando con Flask development server...")
        start_with_flask()

if __name__ == '__main__':
    main()