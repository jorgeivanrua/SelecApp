#!/usr/bin/env python3
"""
Sistema Electoral - Aplicación para Producción
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request

# Configurar codificación para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Configuración de producción
from config_production import ProductionConfig

# Importaciones opcionales
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

def create_production_app():
    """Factory para crear la aplicación Flask optimizada para producción"""
    
    app = Flask(__name__)
    
    # Configuración de producción
    app.config.update(ProductionConfig.get_config_dict())
    
    # Configurar UTF-8 para JSON
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Configurar logging para producción con codificación UTF-8
    logging.basicConfig(
        level=getattr(logging, ProductionConfig.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('electoral_system.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # CORS para producción
    if CORS_AVAILABLE:
        CORS(app, origins=ProductionConfig.CORS_ORIGINS)
    
    # Headers de seguridad y codificación UTF-8
    @app.after_request
    def add_security_headers(response):
        for header, value in ProductionConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Asegurar codificación UTF-8 para todas las respuestas
        if response.content_type.startswith('application/json'):
            response.content_type = 'application/json; charset=utf-8'
        elif response.content_type.startswith('text/html'):
            response.content_type = 'text/html; charset=utf-8'
        
        return response
    
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
        app.logger.info("Módulo de candidatos registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de candidatos no disponible: {e}")
    
    # Módulo de coordinación
    try:
        from modules.coordination.routes import coordination_bp
        app.register_blueprint(coordination_bp)
        app.logger.info("Módulo de coordinación registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de coordinacion no disponible: {e}")
    
    # Módulo de administración
    try:
        from modules.admin.routes import admin_bp
        app.register_blueprint(admin_bp)
        app.logger.info("Módulo de administración registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de administracion no disponible: {e}")
    
    # Módulo de usuarios
    try:
        from modules.users.routes import users_bp
        app.register_blueprint(users_bp)
        app.logger.info("Módulo de usuarios registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de usuarios no disponible: {e}")
    
    # Módulo de reportes
    try:
        from modules.reports.routes import reports_bp
        app.register_blueprint(reports_bp)
        app.logger.info("Módulo de reportes registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de reportes no disponible: {e}")
    
    # Módulo de dashboard
    try:
        from modules.dashboard.routes import dashboard_bp
        app.register_blueprint(dashboard_bp)
        app.logger.info("Módulo de dashboard registrado")
    except ImportError as e:
        app.logger.warning(f"Modulo de dashboard no disponible: {e}")

def register_error_handlers(app):
    """Registrar manejadores de errores para producción"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False, 
            'error': 'Recurso no encontrado',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error interno: {error}")
        return jsonify({
            'success': False, 
            'error': 'Error interno del servidor',
            'code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False, 
            'error': 'Solicitud incorrecta',
            'code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False, 
            'error': 'No autorizado',
            'code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False, 
            'error': 'Acceso prohibido',
            'code': 403
        }), 403

def register_main_routes(app):
    """Registrar rutas principales optimizadas para producción"""
    
    from flask import render_template
    
    @app.route('/')
    def index():
        """Página de inicio del sistema"""
        return render_template('index_home.html')
    
    @app.route('/api')
    def api_index():
        """Información de la API en formato JSON"""
        return jsonify({
            'success': True,
            'message': 'Sistema Electoral Caquetá - API Producción',
            'version': '2.0.0',
            'environment': 'production',
            'modules': get_registered_modules(app)
        })
    
    @app.route('/login')
    def login_page():
        """Página de login con diseño estilístico"""
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal con diseño moderno"""
        return render_template('dashboard_home.html')
    
    @app.route('/dashboard/<role>')
    def dashboard_role(role):
        """Dashboard específico por rol"""
        valid_roles = {
            # Super Admin
            'super_admin': 'super_admin',
            'admin': 'super_admin',
            # Administradores
            'admin_departamental': 'admin_departamental',
            'admin_municipal': 'admin_municipal',
            # Coordinadores
            'coordinador_electoral': 'coordinador_electoral',
            'coordinador_departamental': 'coordinador_departamental',
            'coordinador_municipal': 'coordinador_municipal',
            'coordinador_puesto': 'coordinador_puesto',
            'coordinator': 'coordinador_municipal',
            # Testigo (Unificado - incluye funciones de jurado)
            'testigo': 'testigo_mesa',
            'testigo_mesa': 'testigo_mesa',
            'testigo_electoral': 'testigo_mesa',
            'witness': 'testigo_mesa',
            # Auditor y Observador
            'auditor': 'auditor_electoral',
            'auditor_electoral': 'auditor_electoral',
            'observador': 'observador_internacional',
            'observador_internacional': 'observador_internacional'
        }
        
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'error': f"Rol '{role}' no válido"
            }), 404
        
        actual_role = valid_roles[role]
        template_path = f'roles/{actual_role}/dashboard.html'
        
        try:
            return render_template(template_path, user_role=actual_role)
        except Exception as e:
            app.logger.error(f"Error cargando dashboard para {role}: {e}")
            return render_template('dashboard.html', user_role=actual_role)
    
    @app.route('/health')
    def health_check():
        """Endpoint de verificación de salud para producción"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'environment': 'production',
            'timestamp': datetime.now().isoformat(),
            'database': check_database_connection()
        })
    
    @app.route('/api/info')
    def api_info():
        """Información de la API para producción"""
        return jsonify({
            'success': True,
            'api_version': '2.0.0',
            'environment': 'production',
            'modules': get_registered_modules(app),
            'total_endpoints': len(get_registered_endpoints(app))
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
        import sqlite3
        conn = sqlite3.connect('electoral_system_prod.db')
        conn.execute('SELECT 1')
        conn.close()
        return {
            'status': 'connected',
            'type': 'sqlite',
            'path': 'electoral_system_prod.db'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

# Crear aplicación para producción
app = create_production_app()

def main():
    """Función principal para ejecutar en producción"""
    
    # Configurar tiempo de inicio
    app.config['startup_time'] = datetime.now().isoformat()
    
    # Información de inicio
    app.logger.info("Sistema Electoral Caquetá - Iniciando en PRODUCCIÓN...")
    app.logger.info(f"Modo debug: {app.config['DEBUG']}")
    app.logger.info(f"Base de datos: {app.config['DATABASE_URL']}")
    app.logger.info(f"Módulos registrados: {len(app.blueprints)}")
    app.logger.info(f"Host: {ProductionConfig.HOST}")
    app.logger.info(f"Puerto: {ProductionConfig.PORT}")
    
    # Ejecutar aplicación
    app.run(
        host=ProductionConfig.HOST,
        port=ProductionConfig.PORT,
        debug=ProductionConfig.DEBUG,
        threaded=True
    )

if __name__ == '__main__':
    main()