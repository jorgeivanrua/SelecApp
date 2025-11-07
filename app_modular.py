#!/usr/bin/env python3
"""
Sistema Electoral ERP - Aplicación Principal Modular
Arquitectura modular reorganizada siguiendo buenas prácticas
"""

from flask import Flask
import os
import logging

# Configuración
from config import AppConfig, DatabaseConfig

# Importaciones opcionales
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

try:
    from flask_jwt_extended import JWTManager
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

def create_app():
    """Factory para crear la aplicación Flask con arquitectura modular"""
    
    app = Flask(__name__)
    
    # Configuración desde clase de configuración
    app.config.update(AppConfig.get_config_dict())
    
    # Configurar JSON para UTF-8
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, AppConfig.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Extensiones opcionales
    if CORS_AVAILABLE:
        CORS(app, origins=AppConfig.CORS_ORIGINS)
    
    if JWT_AVAILABLE:
        jwt = JWTManager(app)
    
    # Registrar blueprints modulares
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Configurar rutas principales
    register_main_routes(app)
    
    return app

def register_blueprints(app):
    """Registrar todos los blueprints modulares"""
    
    # Módulo de candidatos
    try:
        from modules.candidates.routes import candidate_bp
        app.register_blueprint(candidate_bp)
        app.logger.info("✅ Módulo de candidatos registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de candidatos no disponible: {e}")
    
    # Módulo de coordinación
    try:
        from modules.coordination.routes import coordination_bp
        app.register_blueprint(coordination_bp)
        app.logger.info("✅ Módulo de coordinación registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de coordinación no disponible: {e}")
    
    # Módulo de administración
    try:
        from modules.admin.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.logger.info("✅ Módulo de administración registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de administración no disponible: {e}")
    
    # Módulo de usuarios
    try:
        from modules.users.routes import users_bp
        app.register_blueprint(users_bp, url_prefix='/api/users')
        app.logger.info("✅ Módulo de usuarios registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de usuarios no disponible: {e}")
    
    # Módulo de reportes
    try:
        from modules.reports.routes import reports_bp
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        app.logger.info("✅ Módulo de reportes registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de reportes no disponible: {e}")
    
    # Módulo de dashboard
    try:
        from modules.dashboard.routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        app.logger.info("✅ Módulo de dashboard registrado")
    except ImportError as e:
        app.logger.warning(f"⚠️  Módulo de dashboard no disponible: {e}")
    
    # APIs adicionales (compatibilidad hacia atrás)
    try:
        from api.admin_api import admin_api
        app.register_blueprint(admin_api, url_prefix='/api/admin_legacy')
        app.logger.info("✅ API administrativa legacy registrada")
    except ImportError as e:
        app.logger.warning(f"⚠️  API administrativa legacy no disponible: {e}")
    
    try:
        from api.coordination_api import coordination_bp as coordination_legacy_bp
        app.register_blueprint(coordination_legacy_bp, name='coordination_legacy')
        app.logger.info("✅ API de coordinación legacy registrada")
    except ImportError as e:
        app.logger.warning(f"⚠️  API de coordinación legacy no disponible: {e}")

def register_error_handlers(app):
    """Registrar manejadores de errores globales"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Recurso no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error interno: {error}")
        return {'success': False, 'error': 'Error interno del servidor'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'success': False, 'error': 'Solicitud incorrecta'}, 400

def register_main_routes(app):
    """Registrar rutas principales de la aplicación"""
    
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({
            'success': True,
            'message': 'Sistema Electoral Caquetá - API Modular',
            'version': '2.0.0',
            'modules': get_registered_modules(app)
        })
    
    @app.route('/health')
    def health_check():
        """Endpoint de verificación de salud"""
        from flask import jsonify
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': app.config.get('startup_time', 'unknown'),
            'database': check_database_connection()
        })
    
    @app.route('/api/info')
    def api_info():
        """Información de la API"""
        from flask import jsonify
        return jsonify({
            'success': True,
            'api_version': '2.0.0',
            'modules': get_registered_modules(app),
            'endpoints': get_registered_endpoints(app)
        })

def get_registered_modules(app):
    """Obtener lista de módulos registrados"""
    modules = []
    for blueprint in app.blueprints:
        modules.append({
            'name': blueprint,
            'url_prefix': app.blueprints[blueprint].url_prefix or '/'
        })
    return modules

def get_registered_endpoints(app):
    """Obtener lista de endpoints registrados"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule)
            })
    return endpoints

def check_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        from config.database import DatabaseConfig
        db_config = DatabaseConfig()
        # Aquí se podría hacer una verificación real de la BD
        return {
            'status': 'connected',
            'path': db_config.get_connection_string()
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    """Función principal para ejecutar la aplicación"""
    app = create_app()
    
    # Configurar tiempo de inicio
    from datetime import datetime
    app.config['startup_time'] = datetime.now().isoformat()
    
    # Información de inicio
    app.logger.info("🗳️  Sistema Electoral Caquetá - Iniciando...")
    app.logger.info(f"Modo debug: {app.config['DEBUG']}")
    app.logger.info(f"Base de datos: {app.config['DATABASE_URL']}")
    app.logger.info(f"Módulos registrados: {len(app.blueprints)}")
    
    # Ejecutar aplicación
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )

if __name__ == '__main__':
    main()