"""
Rutas del módulo de usuarios
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from .services import UserService, AuthService
from .models import LoginData, PasswordChangeData

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Instancias de servicios
user_service = UserService()
auth_service = AuthService()

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@users_bp.route('/auth/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username y password son requeridos'
            }), 400
        
        # Crear datos de login
        login_data = LoginData(
            username=data['username'],
            password=data['password'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            remember_me=data.get('remember_me', False)
        )
        
        # Autenticar usuario
        result = auth_service.authenticate_user(login_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@users_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Cerrar sesión de usuario"""
    try:
        # Obtener token de sesión del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token de sesión requerido'
            }), 401
        
        session_token = auth_header.split(' ')[1]
        
        # Primero validar el token para obtener el user_id
        token_data = auth_service.validate_token(session_token)
        if not token_data:
            return jsonify({
                'success': False,
                'error': 'Token inválido'
            }), 401
        
        # Cerrar sesión usando el token
        result = auth_service.logout_user(session_token, token_data['user_id'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@users_bp.route('/auth/validate', methods=['GET'])
def validate_session():
    """Validar sesión actual"""
    try:
        # Obtener token de sesión del header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token de sesión requerido'
            }), 401
        
        session_token = auth_header.split(' ')[1]
        
        token_data = auth_service.validate_token(session_token)
        
        if token_data:
            return jsonify({
                'success': True,
                'token_data': token_data,
                'valid': True
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Token inválido o expirado'
            }), 401
            
    except Exception as e:
        logger.error(f"Error validando sesión: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE PERFIL DE USUARIO ====================

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Obtener perfil de usuario"""
    try:
        profile = user_service.get_user_profile(user_id)
        
        if profile:
            return jsonify({
                'success': True,
                'data': {
                    'user_data': profile.user_data.__dict__,
                    'location_info': profile.location_info,
                    'role_permissions': profile.role_permissions,
                    'activity_summary': profile.activity_summary,
                    'preferences': profile.preferences
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@users_bp.route('/profile/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """Actualizar perfil de usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        result = user_service.update_user_profile(user_id, data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error actualizando perfil: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@users_bp.route('/profile/<int:user_id>/change-password', methods=['POST'])
def change_password(user_id):
    """Cambiar contraseña de usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['current_password', 'new_password', 'confirm_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        password_data = PasswordChangeData(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password'],
            confirm_password=data['confirm_password']
        )
        
        result = user_service.change_password(password_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE ACTIVIDAD ====================

@users_bp.route('/activity/<int:user_id>', methods=['GET'])
def get_user_activities(user_id):
    """Obtener actividades del usuario"""
    try:
        limit = request.args.get('limit', 50, type=int)
        activities = user_service.get_user_activities(user_id, limit)
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'user_id': activity.user_id,
                'action': activity.action,
                'description': activity.description,
                'ip_address': activity.ip_address,
                'user_agent': activity.user_agent,
                'timestamp': activity.timestamp,
                'additional_data': activity.additional_data
            })
        
        return jsonify({
            'success': True,
            'data': activities_data,
            'total': len(activities_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo actividades: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE INFORMACIÓN ====================

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Obtener usuario por ID"""
    try:
        user = user_service.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'data': user.__dict__
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@users_bp.route('/username/<username>', methods=['GET'])
def get_user_by_username(username):
    """Obtener usuario por username"""
    try:
        user = user_service.get_user_by_username(username)
        
        if user:
            return jsonify({
                'success': True,
                'data': user.__dict__
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE MANTENIMIENTO ====================

@users_bp.route('/auth/cleanup-sessions', methods=['POST'])
def cleanup_expired_sessions():
    """Limpiar sesiones expiradas"""
    try:
        cleaned_count = auth_service.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'cleaned_sessions': cleaned_count,
            'message': f'Se limpiaron {cleaned_count} sesiones expiradas'
        })
        
    except Exception as e:
        logger.error(f"Error limpiando sesiones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@users_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@users_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@users_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500