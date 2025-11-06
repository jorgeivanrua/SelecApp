"""
Core API Manager
Funcionalidades comunes para APIs y decoradores
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

class APIManager:
    """Gestor de APIs y funcionalidades comunes"""
    
    def __init__(self, db_manager, auth_manager, permission_manager):
        self.db = db_manager
        self.auth = auth_manager
        self.permissions = permission_manager
    
    def require_permission(self, permission):
        """Decorador para requerir permisos específicos"""
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                user_id = get_jwt_identity()
                
                if not self.permissions.has_permission(user_id, permission):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_any_permission(self, permissions):
        """Decorador para requerir cualquiera de los permisos especificados"""
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                user_id = get_jwt_identity()
                
                if not self.permissions.has_any_permission(user_id, permissions):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def require_role(self, role):
        """Decorador para requerir rol específico"""
        def decorator(f):
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs):
                user_id = get_jwt_identity()
                user = self.auth.get_user_by_id(user_id)
                
                if not user or user['rol'] != role:
                    return jsonify({'error': 'Insufficient role'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def paginate_query(self, base_query, page=1, per_page=20):
        """Paginación de consultas"""
        try:
            offset = (page - 1) * per_page
            
            # Contar total de registros
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            total_result = self.db.execute_query(count_query)
            total = total_result[0][0] if total_result else 0
            
            # Obtener registros paginados
            paginated_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            data = self.db.execute_query(paginated_query)
            
            return {
                'data': data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Pagination error: {e}")
            raise
    
    def validate_request_data(self, required_fields, optional_fields=None):
        """Validar datos de request"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
                
                # Verificar campos requeridos
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
                
                # Filtrar solo campos permitidos
                allowed_fields = required_fields + (optional_fields or [])
                filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                
                # Pasar datos filtrados a la función
                return f(filtered_data, *args, **kwargs)
            return decorated_function
        return decorator
    
    def handle_api_error(self, error):
        """Manejo centralizado de errores de API"""
        logger.error(f"API Error: {error}")
        
        if isinstance(error, ValueError):
            return jsonify({'error': 'Invalid data provided'}), 400
        elif isinstance(error, PermissionError):
            return jsonify({'error': 'Permission denied'}), 403
        else:
            return jsonify({'error': 'Internal server error'}), 500
    
    def format_response(self, data, message=None, status_code=200):
        """Formatear respuesta estándar de API"""
        response = {
            'success': status_code < 400,
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return jsonify(response), status_code
    
    def get_current_user(self):
        """Obtener usuario actual desde JWT"""
        try:
            user_id = get_jwt_identity()
            return self.auth.get_user_by_id(user_id)
        except:
            return None
    
    def log_user_action(self, user_id, action, resource, details=None):
        """Registrar acción de usuario (para auditoría)"""
        try:
            query = """
                INSERT INTO user_actions (user_id, action, resource, details, timestamp)
                VALUES (:user_id, :action, :resource, :details, datetime('now'))
            """
            
            params = {
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'details': details
            }
            
            self.db.execute_insert(query, params)
            
        except Exception as e:
            logger.error(f"Log user action error: {e}")
    
    def search_filter(self, base_query, search_fields, search_term):
        """Agregar filtro de búsqueda a query"""
        if not search_term:
            return base_query
        
        search_conditions = []
        for field in search_fields:
            search_conditions.append(f"{field} LIKE '%{search_term}%'")
        
        search_clause = " OR ".join(search_conditions)
        
        if "WHERE" in base_query.upper():
            return f"{base_query} AND ({search_clause})"
        else:
            return f"{base_query} WHERE ({search_clause})"