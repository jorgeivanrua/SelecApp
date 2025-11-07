"""
Rutas del módulo de administración
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime

from .services import AdminPanelService, ExcelImportService, PriorityService
from .models import UserManagementData, BulkActionData, PriorityData

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Instancias de servicios
admin_service = AdminPanelService()
excel_service = ExcelImportService()
priority_service = PriorityService()

# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@admin_bp.route('/statistics', methods=['GET'])
def get_system_statistics():
    """Obtener estadísticas del sistema"""
    try:
        stats = admin_service.get_system_statistics()
        
        return jsonify({
            'success': True,
            'data': stats.__dict__
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/health', methods=['GET'])
def get_system_health():
    """Obtener estado de salud del sistema"""
    try:
        health = admin_service.get_system_health()
        
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"Error verificando salud del sistema: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE GESTIÓN DE USUARIOS ====================

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Obtener todos los usuarios del sistema"""
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        users = admin_service.get_all_users(active_only=active_only)
        
        return jsonify({
            'success': True,
            'data': users,
            'total': len(users)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Crear nuevo usuario del sistema"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['nombre_completo', 'cedula', 'rol']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear objeto de datos del usuario
        user_data = UserManagementData(
            nombre_completo=data['nombre_completo'],
            cedula=data['cedula'],
            email=data.get('email', ''),
            telefono=data.get('telefono', ''),
            rol=data['rol'],
            municipio_id=data.get('municipio_id'),
            puesto_id=data.get('puesto_id'),
            activo=data.get('activo', True),
            password=data.get('password')
        )
        
        # Obtener usuario actual (simulado por ahora)
        created_by = data.get('created_by', 1)  # TODO: Obtener del token de sesión
        
        result = admin_service.create_user(user_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Actualizar usuario existente"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Crear objeto de datos del usuario
        user_data = UserManagementData(
            nombre_completo=data.get('nombre_completo', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            rol=data.get('rol', ''),
            municipio_id=data.get('municipio_id'),
            puesto_id=data.get('puesto_id'),
            activo=data.get('activo', True)
        )
        
        updated_by = data.get('updated_by', 1)  # TODO: Obtener del token
        
        result = admin_service.update_user(user_id, user_data, updated_by)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error actualizando usuario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Eliminar (desactivar) usuario"""
    try:
        deleted_by = request.args.get('deleted_by', 1, type=int)  # TODO: Obtener del token
        
        result = admin_service.delete_user(user_id, deleted_by)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/users/bulk-actions', methods=['POST'])
def bulk_user_actions():
    """Ejecutar acciones masivas en usuarios"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        if not data.get('action_type') or not data.get('target_ids'):
            return jsonify({
                'success': False,
                'error': 'action_type y target_ids son requeridos'
            }), 400
        
        action_data = BulkActionData(
            action_type=data['action_type'],
            target_ids=data['target_ids'],
            parameters=data.get('parameters', {}),
            executed_by=data.get('executed_by', 1),  # TODO: Obtener del token
            execution_date=datetime.now()
        )
        
        result = admin_service.bulk_user_actions(action_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en acciones masivas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE IMPORTACIÓN ====================

@admin_bp.route('/import/candidates', methods=['POST'])
def import_candidates_excel():
    """Importar candidatos desde archivo Excel"""
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo Excel'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo'
            }), 400
        
        # Verificar extensión
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Solo se permiten archivos Excel (.xlsx, .xls)'
            }), 400
        
        # Obtener parámetros adicionales
        election_type_id = request.form.get('election_type_id', type=int)
        if not election_type_id:
            return jsonify({
                'success': False,
                'error': 'election_type_id es requerido'
            }), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(temp_path)
        
        try:
            # Procesar archivo Excel
            imported_by = request.form.get('imported_by', 1, type=int)  # TODO: Obtener del token
            result = excel_service.import_candidates_from_excel(temp_path, election_type_id, imported_by)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400
                
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        logger.error(f"Error en importación de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error procesando archivo Excel'
        }), 500

@admin_bp.route('/import/witnesses', methods=['POST'])
def import_witnesses_excel():
    """Importar testigos desde archivo Excel"""
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo Excel'
            }), 400
        
        file = request.files['file']
        municipio_id = request.form.get('municipio_id', type=int)
        
        if not municipio_id:
            return jsonify({
                'success': False,
                'error': 'municipio_id es requerido'
            }), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        temp_path = os.path.join('/tmp', f"witnesses_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(temp_path)
        
        try:
            imported_by = request.form.get('imported_by', 1, type=int)
            result = excel_service.import_witnesses_from_excel(temp_path, municipio_id, imported_by)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify(result)
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        logger.error(f"Error en importación de testigos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error procesando archivo Excel'
        }), 500

@admin_bp.route('/import/template/<template_type>', methods=['GET'])
def get_import_template(template_type):
    """Obtener plantilla para importación"""
    try:
        result = excel_service.generate_excel_template(template_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error obteniendo plantilla: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE PRIORIDADES ====================

@admin_bp.route('/priorities', methods=['POST'])
def create_priority():
    """Crear nueva prioridad"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['entity_type', 'entity_id', 'priority_level', 'priority_reason', 'assigned_by']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        priority_data = PriorityData(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            priority_level=data['priority_level'],
            priority_reason=data['priority_reason'],
            assigned_by=data['assigned_by'],
            assigned_date=datetime.now(),
            active=data.get('active', True)
        )
        
        result = priority_service.create_priority(priority_data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando prioridad: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/priorities/<entity_type>', methods=['GET'])
def get_priorities_by_type(entity_type):
    """Obtener prioridades por tipo de entidad"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        priorities = priority_service.get_priorities_by_type(entity_type, active_only)
        
        return jsonify({
            'success': True,
            'data': priorities,
            'total': len(priorities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo prioridades: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/priorities/high-priority', methods=['GET'])
def get_high_priority_entities():
    """Obtener entidades de alta prioridad"""
    try:
        limit = request.args.get('limit', 10, type=int)
        priorities = priority_service.get_high_priority_entities(limit)
        
        return jsonify({
            'success': True,
            'data': priorities,
            'total': len(priorities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo alta prioridad: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@admin_bp.route('/priorities/statistics', methods=['GET'])
def get_priority_statistics():
    """Obtener estadísticas de prioridades"""
    try:
        result = priority_service.get_priority_statistics()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de prioridades: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@admin_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500