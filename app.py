#!/usr/bin/env python3
"""
Sistema Electoral ERP - Aplicación Principal
Arquitectura modular inspirada en Frappe Framework
"""

from flask import Flask, request, jsonify, session, render_template, redirect, url_for
import os
from datetime import datetime, timedelta

# Importaciones opcionales
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

try:
    from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    from werkzeug.security import check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    WERKZEUG_AVAILABLE = False

def create_app():
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///caqueta_electoral.db')
    
    # Extensiones opcionales
    if CORS_AVAILABLE:
        CORS(app)
    
    if JWT_AVAILABLE:
        jwt = JWTManager(app)
    
    def get_role_display_name(role):
        """Obtener nombre de display para el rol"""
        role_names = {
            'super_admin': 'Super Administrador',
            'admin_departamental': 'Administrador Departamental',
            'admin_municipal': 'Administrador Municipal', 
            'coordinador_electoral': 'Coordinador Electoral',
            'coordinador_departamental': 'Coordinador Departamental',
            'coordinador_municipal': 'Coordinador Municipal',
            'coordinador_puesto': 'Coordinador de Puesto',
            'testigo_electoral': 'Testigo Electoral',
            'jurado_votacion': 'Jurado de Votación',
            'testigo_mesa': 'Testigo de Mesa',
            'auditor_electoral': 'Auditor Electoral',
            'observador_internacional': 'Observador Internacional'
        }
        return role_names.get(role, role.replace('_', ' ').title())
    
    def get_dashboard_data(role):
        """Obtener datos específicos para el dashboard del rol"""
        base_data = {
            'stats': {},
            'recent_activity': [],
            'notifications': [],
            'quick_actions': [],
            'current_user': {'nombre_completo': f'Usuario {role}', 'rol': role},
            'current_year': datetime.now().year
        }
        
        if role == 'super_admin':
            base_data.update({
                'stats': {
                    'total_users': 156,
                    'active_processes': 3,
                    'total_municipalities': 16,
                    'system_health': 98
                },
                'quick_actions': [
                    {'name': 'Gestionar Usuarios', 'url': '/users', 'icon': 'fas fa-users'},
                    {'name': 'Configurar Sistema', 'url': '/config', 'icon': 'fas fa-cogs'},
                    {'name': 'Ver Reportes', 'url': '/reports', 'icon': 'fas fa-chart-bar'},
                    {'name': 'Auditoría', 'url': '/audit', 'icon': 'fas fa-shield-alt'}
                ]
            })
        elif role == 'admin_departamental':
            base_data.update({
                'stats': {
                    'municipalities': 16,
                    'active_processes': 2,
                    'total_tables': 450,
                    'coverage': 95
                },
                'quick_actions': [
                    {'name': 'Gestionar Municipios', 'url': '/municipalities', 'icon': 'fas fa-city'},
                    {'name': 'Procesos Electorales', 'url': '/electoral', 'icon': 'fas fa-vote-yea'},
                    {'name': 'Reportes Departamentales', 'url': '/reports/departmental', 'icon': 'fas fa-chart-line'},
                    {'name': 'Supervisar Mesas', 'url': '/tables/monitor', 'icon': 'fas fa-eye'}
                ]
            })
        elif role == 'admin_municipal':
            base_data.update({
                'stats': {
                    'local_tables': 28,
                    'registered_voters': 15420,
                    'candidates': 12,
                    'participation': 67
                },
                'quick_actions': [
                    {'name': 'Gestionar Mesas', 'url': '/tables', 'icon': 'fas fa-table'},
                    {'name': 'Candidatos Locales', 'url': '/candidates/local', 'icon': 'fas fa-users'},
                    {'name': 'Reportes Municipales', 'url': '/reports/municipal', 'icon': 'fas fa-chart-pie'},
                    {'name': 'Configurar Puestos', 'url': '/voting-stations', 'icon': 'fas fa-map-marker-alt'}
                ]
            })
        elif role == 'coordinador_electoral':
            base_data.update({
                'stats': {
                    'active_processes': 2,
                    'scheduled_tasks': 8,
                    'pending_approvals': 3,
                    'completion': 78
                },
                'quick_actions': [
                    {'name': 'Coordinar Procesos', 'url': '/coordination', 'icon': 'fas fa-tasks'},
                    {'name': 'Cronograma Electoral', 'url': '/schedule', 'icon': 'fas fa-calendar'},
                    {'name': 'Supervisar Avance', 'url': '/progress', 'icon': 'fas fa-chart-line'},
                    {'name': 'Generar Reportes', 'url': '/reports/coordination', 'icon': 'fas fa-file-alt'}
                ]
            })
        elif role == 'jurado_votacion':
            base_data.update({
                'stats': {
                    'assigned_table': '001-A',
                    'registered_votes': 234,
                    'eligible_voters': 350,
                    'participation': 67
                },
                'quick_actions': [
                    {'name': 'Registrar Voto', 'url': '/voting/register', 'icon': 'fas fa-plus'},
                    {'name': 'Ver Resultados', 'url': '/voting/results', 'icon': 'fas fa-chart-pie'},
                    {'name': 'Generar Acta', 'url': '/voting/certificate', 'icon': 'fas fa-file-pdf'},
                    {'name': 'Reportar Incidencia', 'url': '/incidents/report', 'icon': 'fas fa-exclamation-triangle'}
                ]
            })
        elif role == 'testigo_mesa':
            base_data.update({
                'stats': {
                    'observations': 5,
                    'incidents': 1,
                    'verification_progress': 85,
                    'alerts': 0
                },
                'quick_actions': [
                    {'name': 'Nueva Observación', 'url': '/observations/new', 'icon': 'fas fa-eye'},
                    {'name': 'Reportar Incidente', 'url': '/incidents/new', 'icon': 'fas fa-exclamation'},
                    {'name': 'Lista Verificación', 'url': '/checklist', 'icon': 'fas fa-check-square'},
                    {'name': 'Generar Reporte', 'url': '/reports/witness', 'icon': 'fas fa-file-alt'}
                ]
            })
        elif role == 'auditor_electoral':
            base_data.update({
                'stats': {
                    'active_audits': 5,
                    'irregularities': 2,
                    'compliance': 95,
                    'reports_generated': 12
                },
                'quick_actions': [
                    {'name': 'Iniciar Auditoría', 'url': '/audit/start', 'icon': 'fas fa-play'},
                    {'name': 'Revisar Irregularidades', 'url': '/audit/irregularities', 'icon': 'fas fa-exclamation-triangle'},
                    {'name': 'Reporte Cumplimiento', 'url': '/audit/compliance', 'icon': 'fas fa-check-circle'},
                    {'name': 'Exportar Datos', 'url': '/audit/export', 'icon': 'fas fa-download'}
                ]
            })
        elif role == 'observador_internacional':
            base_data.update({
                'stats': {
                    'observed_processes': 8,
                    'standards_evaluated': 15,
                    'global_compliance': 92,
                    'reports_sent': 6
                },
                'quick_actions': [
                    {'name': 'Nueva Observación', 'url': '/observation/new', 'icon': 'fas fa-eye'},
                    {'name': 'Evaluar Estándares', 'url': '/observation/standards', 'icon': 'fas fa-check-double'},
                    {'name': 'Reporte Internacional', 'url': '/observation/report', 'icon': 'fas fa-globe'},
                    {'name': 'Enviar a Organización', 'url': '/observation/send', 'icon': 'fas fa-paper-plane'}
                ]
            })
        
        return base_data
    

    
    # Inicializar managers solo si están disponibles
    try:
        from core.database import DatabaseManager
        from core.auth import AuthManager
        from core.permissions import PermissionManager
        from core.api import APIManager
        
        db_manager = DatabaseManager(app.config['DATABASE_URL'])
        auth_manager = AuthManager(db_manager)
        permission_manager = PermissionManager(db_manager)
        api_manager = APIManager(db_manager, auth_manager, permission_manager)
        
        # Almacenar managers en app context
        app.db_manager = db_manager
        app.auth_manager = auth_manager
        app.permission_manager = permission_manager
        app.api_manager = api_manager
    except ImportError:
        # Modo simplificado sin módulos core
        pass
    
    # Registrar blueprints (módulos) si están disponibles
    try:
        from modules.electoral.routes import electoral_bp
        from modules.candidates.routes import candidates_bp
        from modules.users.routes import users_bp
        from modules.reports.routes import reports_bp
        from modules.dashboard.routes import dashboard_bp
        
        app.register_blueprint(electoral_bp, url_prefix='/api/electoral')
        app.register_blueprint(candidates_bp, url_prefix='/api/candidates')
        app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    except ImportError:
        # Modo simplificado sin módulos
        pass
    
    # Rutas principales
    @app.route('/')
    def index():
        """Página principal del sistema"""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Página de login"""
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal (solo para super admin)"""
        # En una implementación real, verificaríamos la sesión/token aquí
        # Por ahora, mostramos el dashboard general solo para super admin
        return render_template('dashboard.html')
    
    @app.route('/dashboard/<role>')
    def dashboard_role(role):
        """Dashboard específico por rol"""
        # Mapeo de roles válidos con aliases
        valid_roles = {
            'super_admin': 'super_admin',
            'admin_departamental': 'admin_departamental', 
            'admin_municipal': 'admin_municipal',
            'coordinador_electoral': 'coordinador_electoral',
            'coordinador_departamental': 'coordinador_departamental',
            'coordinador_municipal': 'coordinador_municipal',
            'coordinador_puesto': 'coordinador_puesto',
            'testigo_electoral': 'testigo_electoral',
            'jurado_votacion': 'jurado_votacion',
            'testigo_mesa': 'testigo_mesa',
            'testigo': 'testigo_mesa',  # Alias para testigo
            'auditor': 'auditor_electoral',
            'auditor_electoral': 'auditor_electoral',
            'observador': 'observador_internacional',
            'observador_internacional': 'observador_internacional'
        }
        
        if role not in valid_roles:
            return render_template('error.html', 
                                 error="Rol no válido", 
                                 message=f"El rol '{role}' no existe en el sistema"), 404
        
        actual_role = valid_roles[role]
        template_path = f'roles/{actual_role}/dashboard.html'
        
        # Datos específicos para el dashboard
        dashboard_data = get_dashboard_data(actual_role)
        
        try:
            return render_template(template_path, 
                                 user_role=actual_role,
                                 role_name=get_role_display_name(actual_role),
                                 **dashboard_data)
        except Exception as e:
            # Si no existe el template, mostrar dashboard genérico
            return render_template('dashboard_generic.html',
                                 user_role=actual_role,
                                 role_name=get_role_display_name(actual_role),
                                 error=f"Template no encontrado: {template_path}",
                                 **dashboard_data)
    
    @app.route('/test-login')
    def test_login_page():
        """Página de prueba de login"""
        return render_template('test_login.html')
    
    # Rutas adicionales para funcionalidades de los dashboards
    @app.route('/audit/start')
    def audit_start():
        """Formulario para iniciar nueva auditoría"""
        return render_template('forms/audit_form.html')
    
    @app.route('/observation/new')
    def observation_new():
        """Formulario para nueva observación internacional"""
        return render_template('forms/observation_form.html')
    
    @app.route('/users')
    def users_management():
        """Gestión de usuarios (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='super_admin',
                             role_name='Gestión de Usuarios',
                             stats={'total_users': 156, 'active_users': 142, 'pending_approvals': 8},
                             quick_actions=[
                                 {'name': 'Nuevo Usuario', 'url': '/users/new', 'icon': 'fas fa-user-plus'},
                                 {'name': 'Roles y Permisos', 'url': '/users/roles', 'icon': 'fas fa-user-shield'},
                                 {'name': 'Usuarios Inactivos', 'url': '/users/inactive', 'icon': 'fas fa-user-slash'}
                             ])
    
    @app.route('/municipalities')
    def municipalities_management():
        """Gestión de municipios (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='admin_departamental',
                             role_name='Gestión de Municipios',
                             stats={'total_municipalities': 16, 'active_processes': 3, 'coverage': 95},
                             quick_actions=[
                                 {'name': 'Nuevo Municipio', 'url': '/municipalities/new', 'icon': 'fas fa-city'},
                                 {'name': 'Configurar Zonas', 'url': '/municipalities/zones', 'icon': 'fas fa-map'},
                                 {'name': 'Estadísticas', 'url': '/municipalities/stats', 'icon': 'fas fa-chart-bar'}
                             ])
    
    # Rutas específicas para testigo electoral
    @app.route('/testigo/resultados')
    def testigo_resultados():
        """Página de captura de resultados E14 para testigo electoral"""
        return render_template('roles/testigo_electoral/resultados.html')
    
    @app.route('/testigo/observacion')
    def testigo_observacion():
        """Página de observaciones para testigo electoral"""
        return render_template('roles/testigo_electoral/observaciones.html')
    
    @app.route('/testigo/reportes')
    def testigo_reportes():
        """Página de reportes para testigo electoral"""
        return render_template('roles/testigo_electoral/reportes.html')
    
    @app.route('/testigo/incidencias')
    def testigo_incidencias():
        """Página de incidencias para testigo electoral"""
        return render_template('roles/testigo_electoral/incidencias.html')
    
    @app.route('/testigo/e14')
    def testigo_e14():
        """Página de captura de E14 para testigo electoral"""
        return render_template('roles/testigo_electoral/e14.html')
    
    @app.route('/testigo/e24')
    def testigo_e24():
        """Página de captura de E24 para testigo electoral"""
        return render_template('roles/testigo_electoral/e24.html')
    
    @app.route('/api/user/location/<int:user_id>')
    def get_user_location(user_id):
        """Obtener información de ubicación del usuario"""
        try:
            import sqlite3
            conn = sqlite3.connect('caqueta_electoral.db')
            cursor = conn.cursor()
            
            query = """
                SELECT u.*, m_mun.nombre as municipio_nombre, m_mun.codigo as municipio_codigo,
                       pv.nombre as puesto_nombre, pv.direccion as puesto_direccion,
                       mv.numero as mesa_numero
                FROM users u
                LEFT JOIN municipios m_mun ON u.municipio_id = m_mun.id
                LEFT JOIN puestos_votacion pv ON u.puesto_id = pv.id
                LEFT JOIN mesas_votacion mv ON u.mesa_id = mv.id
                WHERE u.id = ?
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                user_data = dict(zip(columns, result))
                
                location_info = {
                    'departamento': 'Caquetá',
                    'municipio': user_data.get('municipio_nombre'),
                    'municipio_codigo': user_data.get('municipio_codigo'),
                    'puesto': user_data.get('puesto_nombre'),
                    'puesto_direccion': user_data.get('puesto_direccion'),
                    'mesa': user_data.get('mesa_numero'),
                    'rol': user_data.get('rol'),
                    'nombre_completo': user_data.get('nombre_completo'),
                    'partido_politico': user_data.get('partido_politico')
                }
                
                return jsonify({'success': True, 'location': location_info})
            else:
                return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/mesas/puesto/<int:puesto_id>')
    def get_mesas_puesto(puesto_id):
        """Obtener todas las mesas de un puesto para testigos"""
        try:
            import sqlite3
            conn = sqlite3.connect('caqueta_electoral.db')
            cursor = conn.cursor()
            
            query = """
                SELECT mv.*, 
                       CASE WHEN e14.id IS NOT NULL THEN 1 ELSE 0 END as tiene_e14,
                       e14.fecha_captura,
                       e14.testigo_id as e14_testigo_id,
                       u.nombre_completo as e14_testigo_nombre
                FROM mesas_votacion mv
                LEFT JOIN e14_capturas e14 ON mv.id = e14.mesa_id
                LEFT JOIN users u ON e14.testigo_id = u.id
                WHERE mv.puesto_id = ? AND mv.activa = 1
                ORDER BY mv.numero
            """
            
            cursor.execute(query, (puesto_id,))
            results = cursor.fetchall()
            conn.close()
            
            mesas = []
            for row in results:
                columns = [description[0] for description in cursor.description]
                mesa_data = dict(zip(columns, row))
                mesas.append(mesa_data)
            
            return jsonify({'success': True, 'mesas': mesas})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/e14/validar-mesa/<int:mesa_id>')
    def validar_e14_mesa(mesa_id):
        """Validar si una mesa ya tiene E14 capturado"""
        try:
            import sqlite3
            conn = sqlite3.connect('caqueta_electoral.db')
            cursor = conn.cursor()
            
            query = """
                SELECT e14.*, u.nombre_completo as testigo_nombre, mv.numero as mesa_numero
                FROM e14_capturas e14
                LEFT JOIN users u ON e14.testigo_id = u.id
                LEFT JOIN mesas_votacion mv ON e14.mesa_id = mv.id
                WHERE e14.mesa_id = ?
                ORDER BY e14.fecha_captura DESC
                LIMIT 1
            """
            
            cursor.execute(query, (mesa_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                e14_data = dict(zip(columns, result))
                
                return jsonify({
                    'success': True,
                    'tiene_e14': True,
                    'e14_info': e14_data,
                    'mensaje': f'Esta mesa ya tiene un E14 capturado por {e14_data["testigo_nombre"]} el {e14_data["fecha_captura"]}'
                })
            else:
                return jsonify({
                    'success': True,
                    'tiene_e14': False,
                    'mensaje': 'Mesa disponible para captura de E14'
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/e14/capturar', methods=['POST'])
    def capturar_e14():
        """Capturar E14 con validaciones"""
        try:
            data = request.get_json()
            mesa_id = data.get('mesa_id')
            testigo_id = data.get('testigo_id')
            
            # Validar que la mesa no tenga E14 ya capturado
            import sqlite3
            conn = sqlite3.connect('caqueta_electoral.db')
            cursor = conn.cursor()
            
            # Verificar E14 existente
            cursor.execute("SELECT id FROM e14_capturas WHERE mesa_id = ?", (mesa_id,))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'Esta mesa ya tiene un E14 capturado. No se permite duplicados.',
                    'codigo_error': 'E14_DUPLICADO'
                }), 400
            
            # Insertar nuevo E14
            query = """
                INSERT INTO e14_capturas 
                (mesa_id, testigo_id, imagen_e14, votos_validos, votos_blanco, votos_nulos, 
                 observaciones, confirmado, fecha_captura)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            cursor.execute(query, (
                mesa_id,
                testigo_id,
                data.get('imagen_e14'),
                data.get('votos_validos'),
                data.get('votos_blanco'),
                data.get('votos_nulos'),
                data.get('observaciones'),
                1 if data.get('confirmado') else 0
            ))
            
            e14_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'E14 capturado exitosamente',
                'e14_id': e14_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/tables')
    def tables_management():
        """Gestión de mesas de votación (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='admin_municipal',
                             role_name='Gestión de Mesas',
                             stats={'total_tables': 28, 'configured_tables': 25, 'pending_setup': 3},
                             quick_actions=[
                                 {'name': 'Nueva Mesa', 'url': '/tables/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Configurar Mesa', 'url': '/tables/configure', 'icon': 'fas fa-cogs'},
                                 {'name': 'Asignar Jurados', 'url': '/tables/assign', 'icon': 'fas fa-users'}
                             ])
    
    @app.route('/voting/register')
    def voting_register():
        """Registro de votos (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='jurado_votacion',
                             role_name='Registro de Votos',
                             stats={'votes_registered': 234, 'eligible_voters': 350, 'participation': 67},
                             quick_actions=[
                                 {'name': 'Registrar Voto', 'url': '/voting/new', 'icon': 'fas fa-vote-yea'},
                                 {'name': 'Ver Resultados', 'url': '/voting/results', 'icon': 'fas fa-chart-pie'},
                                 {'name': 'Generar Acta', 'url': '/voting/certificate', 'icon': 'fas fa-file-pdf'}
                             ])
    
    @app.route('/observations/new')
    def observations_new():
        """Nueva observación de testigo (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='testigo_mesa',
                             role_name='Nueva Observación',
                             stats={'observations': 5, 'incidents': 1, 'verification_progress': 85},
                             quick_actions=[
                                 {'name': 'Registrar Observación', 'url': '/observations/register', 'icon': 'fas fa-eye'},
                                 {'name': 'Reportar Incidente', 'url': '/incidents/new', 'icon': 'fas fa-exclamation'},
                                 {'name': 'Lista Verificación', 'url': '/checklist', 'icon': 'fas fa-check-square'}
                             ])
    
    @app.route('/profile')
    def profile():
        """Perfil de usuario (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='user',
                             role_name='Mi Perfil',
                             stats={'profile_completion': 85, 'last_login': '2024-11-05', 'sessions': 24},
                             quick_actions=[
                                 {'name': 'Editar Información', 'url': '/profile/edit', 'icon': 'fas fa-edit'},
                                 {'name': 'Cambiar Contraseña', 'url': '/profile/password', 'icon': 'fas fa-key'},
                                 {'name': 'Configuración', 'url': '/settings', 'icon': 'fas fa-cogs'}
                             ])
    
    @app.route('/settings')
    def settings():
        """Configuración del sistema (placeholder)"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Configuración del Sistema',
                             stats={'active_settings': 12, 'pending_updates': 3, 'system_health': 98},
                             quick_actions=[
                                 {'name': 'Configuración General', 'url': '/settings/general', 'icon': 'fas fa-cogs'},
                                 {'name': 'Seguridad', 'url': '/settings/security', 'icon': 'fas fa-shield-alt'},
                                 {'name': 'Notificaciones', 'url': '/settings/notifications', 'icon': 'fas fa-bell'}
                             ])
    
    
    # Rutas adicionales para dashboards específicos
    @app.route('/coordination')
    def coordination():
        """Coordinación de procesos electorales"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Coordinación de Procesos',
                             stats={'active_processes': 2, 'pending_tasks': 5, 'completion': 78},
                             quick_actions=[
                                 {'name': 'Nuevo Proceso', 'url': '/electoral/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Cronograma', 'url': '/schedule', 'icon': 'fas fa-calendar'},
                                 {'name': 'Monitorear', 'url': '/monitor', 'icon': 'fas fa-eye'}
                             ])
    
    @app.route('/schedule')
    def schedule():
        """Cronograma electoral"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Cronograma Electoral',
                             stats={'scheduled_events': 12, 'completed': 8, 'pending': 4},
                             quick_actions=[
                                 {'name': 'Nuevo Evento', 'url': '/schedule/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Ver Calendario', 'url': '/calendar', 'icon': 'fas fa-calendar-alt'},
                                 {'name': 'Recordatorios', 'url': '/reminders', 'icon': 'fas fa-bell'}
                             ])
    
    @app.route('/progress')
    def progress():
        """Supervisar avance"""
        return render_template('dashboard_generic.html',
                             user_role='coordinador_electoral',
                             role_name='Supervisión de Avance',
                             stats={'overall_progress': 78, 'on_track': 85, 'delayed': 15},
                             quick_actions=[
                                 {'name': 'Ver Detalles', 'url': '/progress/details', 'icon': 'fas fa-chart-line'},
                                 {'name': 'Generar Reporte', 'url': '/reports/progress', 'icon': 'fas fa-file-alt'},
                                 {'name': 'Alertas', 'url': '/alerts', 'icon': 'fas fa-exclamation-triangle'}
                             ])
    
    @app.route('/electoral')
    def electoral():
        """Procesos electorales"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Procesos Electorales',
                             stats={'active_processes': 3, 'total_processes': 15, 'completion': 85},
                             quick_actions=[
                                 {'name': 'Nuevo Proceso', 'url': '/electoral/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Ver Todos', 'url': '/electoral/list', 'icon': 'fas fa-list'},
                                 {'name': 'Configurar', 'url': '/electoral/config', 'icon': 'fas fa-cogs'}
                             ])
    
    @app.route('/candidates')
    def candidates():
        """Gestión de candidatos"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Gestión de Candidatos',
                             stats={'total_candidates': 45, 'approved': 42, 'pending': 3},
                             quick_actions=[
                                 {'name': 'Nuevo Candidato', 'url': '/candidates/new', 'icon': 'fas fa-user-plus'},
                                 {'name': 'Aprobar Pendientes', 'url': '/candidates/approve', 'icon': 'fas fa-check'},
                                 {'name': 'Ver Lista', 'url': '/candidates/list', 'icon': 'fas fa-list'}
                             ])
    
    @app.route('/reports')
    def reports():
        """Reportes del sistema"""
        return render_template('dashboard_generic.html',
                             user_role='admin',
                             role_name='Reportes del Sistema',
                             stats={'generated_reports': 25, 'scheduled': 8, 'pending': 3},
                             quick_actions=[
                                 {'name': 'Nuevo Reporte', 'url': '/reports/new', 'icon': 'fas fa-plus'},
                                 {'name': 'Programar', 'url': '/reports/schedule', 'icon': 'fas fa-clock'},
                                 {'name': 'Exportar', 'url': '/reports/export', 'icon': 'fas fa-download'}
                             ])

    @app.route('/logout')
    def logout():
        """Cerrar sesión (placeholder)"""
        return redirect(url_for('index'))
    
    # Rutas específicas para testigo de mesa (legacy - mantenidas para compatibilidad)
    @app.route('/testigo/captura')
    def testigo_captura():
        """Módulo de captura de datos electorales"""
        return render_template('testigo/captura_datos.html',
                             mesa={'numero': '001-A', 'municipio': 'Florencia', 'puesto': 'Escuela Central'},
                             candidatos=[
                                 {'id': 1, 'nombre': 'Juan Pérez', 'partido': 'Partido A'},
                                 {'id': 2, 'nombre': 'María García', 'partido': 'Partido B'},
                                 {'id': 3, 'nombre': 'Carlos López', 'partido': 'Partido C'},
                                 {'id': 4, 'nombre': 'Ana Rodríguez', 'partido': 'Partido D'}
                             ])
    
    @app.route('/api/testigo/votos', methods=['POST'])
    def api_registrar_votos():
        """API para registrar votos"""
        try:
            data = request.get_json()
            candidato = data.get('candidato')
            votos = data.get('votos')
            mesa = data.get('mesa')
            
            # Aquí se guardarían los datos en la base de datos
            # Por ahora solo simulamos la respuesta
            
            return jsonify({
                'success': True,
                'message': f'Registrados {votos} votos para {candidato} en mesa {mesa}',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/testigo/incidencia', methods=['POST'])
    def api_reportar_incidencia():
        """API para reportar incidencias"""
        try:
            data = request.get_json()
            tipo = data.get('tipo')
            descripcion = data.get('descripcion')
            mesa = data.get('mesa')
            
            return jsonify({
                'success': True,
                'message': f'Incidencia reportada para mesa {mesa}',
                'id_incidencia': 'INC-' + str(int(datetime.now().timestamp())),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Endpoint de autenticación con cédula"""
        try:
            data = request.get_json()
            cedula = data.get('cedula') or data.get('username')  # Soportar ambos
            password = data.get('password')
            
            if not cedula or not password:
                return jsonify({'error': 'Cédula and password required'}), 400
            
            # Buscar usuario por cédula o username
            import sqlite3
            conn = sqlite3.connect('caqueta_electoral.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, nombre_completo, password_hash, rol, activo
                FROM users 
                WHERE (cedula = ? OR username = ?) AND activo = 1
            """, (cedula, cedula))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            # Verificar password (simplificado para demo)
            if WERKZEUG_AVAILABLE:
                if not check_password_hash(user_data[3], password):
                    return jsonify({'error': 'Invalid credentials'}), 401
            else:
                # Verificación simple para demo
                if password != 'demo123':
                    return jsonify({'error': 'Invalid credentials'}), 401
            
            # Crear token JWT si está disponible
            if JWT_AVAILABLE:
                access_token = create_access_token(
                    identity=user_data[0],
                    additional_claims={
                        'username': user_data[1],
                        'role': user_data[4]
                    }
                )
            else:
                access_token = 'demo-token'
            
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user_data[0],
                    'username': user_data[1],
                    'nombre_completo': user_data[2],
                    'rol': user_data[4]
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    def get_current_user():
        """Obtener información del usuario actual"""
        try:
            if JWT_AVAILABLE:
                user_id = get_jwt_identity()
                if hasattr(app, 'auth_manager'):
                    user = app.auth_manager.get_user_by_id(user_id)
                    if not user:
                        return jsonify({'error': 'User not found'}), 404
                    
                    return jsonify({
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'nombre_completo': user['nombre_completo'],
                            'rol': user['rol'],
                            'permissions': app.permission_manager.get_user_permissions(user['id'])
                        }
                    })
            
            # Modo demo
            return jsonify({
                'user': {
                    'id': 1,
                    'username': 'demo',
                    'nombre_completo': 'Usuario Demo',
                    'rol': 'super_admin',
                    'permissions': ['all']
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/info', methods=['GET'])
    def system_info():
        """Información del sistema"""
        return jsonify({
            'name': 'Sistema Electoral ERP',
            'version': '1.0.0',
            'description': 'Sistema modular de gestión electoral',
            'department': 'Caquetá',
            'country': 'Colombia',
            'modules': [
                'electoral',
                'candidates', 
                'users',
                'reports',
                'dashboard'
            ],
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check para monitoreo"""
        try:
            # Verificar conexión a base de datos si está disponible
            db_status = 'ok'
            try:
                # Aquí se haría una consulta simple a la BD
                pass
            except:
                db_status = 'error'
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'database': db_status,
                'uptime': 'ok'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT callbacks solo si JWT está disponible
    if JWT_AVAILABLE:
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({'error': 'Token has expired'}), 401
        
        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({'error': 'Invalid token'}), 401
    
    # Registrar APIs RESTful
    try:
        from api_endpoints import register_api_routes
        register_api_routes(app)
        print("✅ APIs RESTful registradas exitosamente")
    except ImportError as e:
        print(f"⚠️  No se pudieron cargar las APIs: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)