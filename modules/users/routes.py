"""
Módulo Usuarios - Rutas y Endpoints
Gestión de usuarios y roles del sistema
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import UserService
from core.permissions import Permission

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Obtener usuarios"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = UserService(current_app.db_manager)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        result = service.get_users(page, per_page, search, role, active_only)
        return jsonify(result)
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Crear nuevo usuario"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_CREATE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = UserService(current_app.db_manager)
        new_user_id = service.create_user(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': new_user_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/users/<int:target_user_id>', methods=['GET'])
@jwt_required()
def get_user(target_user_id):
    """Obtener usuario específico"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = UserService(current_app.db_manager)
        user = service.get_user_by_id(target_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'success': True, 'data': user})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/users/<int:target_user_id>', methods=['PUT'])
@jwt_required()
def update_user(target_user_id):
    """Actualizar usuario"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = UserService(current_app.db_manager)
        updated = service.update_user(target_user_id, data, user_id)
        
        if not updated:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/users/<int:target_user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(target_user_id):
    """Activar usuario"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = UserService(current_app.db_manager)
        success = service.activate_user(target_user_id, user_id)
        
        if not success:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User activated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/users/<int:target_user_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_user(target_user_id):
    """Desactivar usuario"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = UserService(current_app.db_manager)
        success = service.deactivate_user(target_user_id, user_id)
        
        if not success:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'User deactivated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Obtener roles disponibles"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        roles = current_app.permission_manager.get_all_roles()
        return jsonify({'success': True, 'data': roles})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """Obtener permisos disponibles"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        permissions = current_app.permission_manager.get_all_permissions()
        return jsonify({'success': True, 'data': permissions})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Obtener estadísticas de usuarios"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.USERS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = UserService(current_app.db_manager)
        stats = service.get_user_statistics()
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        user_id = get_jwt_identity()
        service = UserService(current_app.db_manager)
        profile = service.get_user_profile(user_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({'success': True, 'data': profile})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario actual"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = UserService(current_app.db_manager)
        updated = service.update_user_profile(user_id, data)
        
        if not updated:
            return jsonify({'error': 'Failed to update profile'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario actual"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password required'}), 400
        
        service = UserService(current_app.db_manager)
        success = service.change_password(user_id, data['current_password'], data['new_password'])
        
        if not success:
            return jsonify({'error': 'Invalid current password'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)