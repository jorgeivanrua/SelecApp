#!/usr/bin/env python3
"""
API para herramientas de coordinación municipal
Endpoints para gestión de testigos, asignaciones, mesas y reportes
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import logging
from services.coordination_service import CoordinationService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
coordination_bp = Blueprint('coordination', __name__, url_prefix='/api/coordination')

# Inicializar servicios
coordination_service = CoordinationService()

def require_coordinator_auth(f):
    """Decorador para requerir autenticación de coordinador municipal"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        user_id = session['user_id']
        
        # Verificar que el usuario es coordinador municipal
        coordinator_info = coordination_service.get_coordinator_info(user_id)
        if not coordinator_info:
            return jsonify({'error': 'No autorizado como coordinador municipal'}), 403
        
        # Pasar información del coordinador a la función
        return f(coordinator_info=coordinator_info, *args, **kwargs)
    
    return decorated_function

# ==================== DASHBOARD Y INFORMACIÓN GENERAL ====================

@coordination_bp.route('/dashboard', methods=['GET'])
@require_coordinator_auth
def get_dashboard(coordinator_info):
    """Obtener datos del dashboard de coordinación"""
    try:
        coordinator_id = coordinator_info['id']
        dashboard_data = coordination_service.get_coordination_dashboard(coordinator_id)
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/summary', methods=['GET'])
@require_coordinator_auth
def get_coordination_summary(coordinator_info):
    """Obtener resumen ejecutivo de coordinación"""
    try:
        coordinator_id = coordinator_info['id']
        summary = coordination_service.get_coordination_summary(coordinator_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== GESTIÓN DE TESTIGOS ====================

@coordination_bp.route('/witnesses', methods=['GET'])
@require_coordinator_auth
def get_witnesses(coordinator_info):
    """Obtener testigos del coordinador con filtros"""
    try:
        coordinator_id = coordinator_info['id']
        
        # Obtener filtros de query parameters
        filters = {}
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('partido_id'):
            filters['partido_id'] = int(request.args.get('partido_id'))
        if request.args.get('tipo_testigo'):
            filters['tipo_testigo'] = request.args.get('tipo_testigo')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        witnesses = coordination_service.get_witnesses(coordinator_id, filters)
        
        return jsonify({
            'success': True,
            'data': witnesses,
            'total': len(witnesses)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo testigos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/witnesses', methods=['POST'])
@require_coordinator_auth
def create_witness(coordinator_info):
    """Crear nuevo testigo electoral"""
    try:
        coordinator_id = coordinator_info['id']
        witness_data = request.get_json()
        
        if not witness_data:
            return jsonify({
                'success': False,
                'error': 'Datos del testigo requeridos'
            }), 400
        
        witness_id = coordination_service.create_witness(coordinator_id, witness_data)
        
        return jsonify({
            'success': True,
            'data': {'witness_id': witness_id},
            'message': 'Testigo creado exitosamente'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creando testigo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/witnesses/<int:witness_id>', methods=['PUT'])
@require_coordinator_auth
def update_witness(coordinator_info, witness_id):
    """Actualizar testigo electoral"""
    try:
        coordinator_id = coordinator_info['id']
        witness_data = request.get_json()
        
        if not witness_data:
            return jsonify({
                'success': False,
                'error': 'Datos del testigo requeridos'
            }), 400
        
        success = coordination_service.update_witness(witness_id, witness_data, coordinator_id)
        
        return jsonify({
            'success': success,
            'message': 'Testigo actualizado exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error actualizando testigo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/witnesses/available', methods=['GET'])
@require_coordinator_auth
def get_available_witnesses(coordinator_info):
    """Obtener testigos disponibles para asignación"""
    try:
        coordinator_id = coordinator_info['id']
        mesa_id = request.args.get('mesa_id', type=int)
        
        witnesses = coordination_service.get_available_witnesses_for_assignment(
            coordinator_id, mesa_id
        )
        
        return jsonify({
            'success': True,
            'data': witnesses,
            'total': len(witnesses)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo testigos disponibles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== GESTIÓN DE MESAS Y PUESTOS ====================

@coordination_bp.route('/voting-tables', methods=['GET'])
@require_coordinator_auth
def get_voting_tables(coordinator_info):
    """Obtener mesas de votación del municipio"""
    try:
        coordinator_id = coordinator_info['id']
        
        # Obtener filtros
        filters = {}
        if request.args.get('puesto_id'):
            filters['puesto_id'] = int(request.args.get('puesto_id'))
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('sin_cobertura') == 'true':
            filters['sin_cobertura'] = True
        
        tables = coordination_service.get_voting_tables(coordinator_id, filters)
        
        return jsonify({
            'success': True,
            'data': tables,
            'total': len(tables)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo mesas de votación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/voting-stations', methods=['GET'])
@require_coordinator_auth
def get_voting_stations(coordinator_info):
    """Obtener puestos de votación del municipio"""
    try:
        coordinator_id = coordinator_info['id']
        stations = coordination_service.get_voting_stations(coordinator_id)
        
        return jsonify({
            'success': True,
            'data': stations,
            'total': len(stations)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo puestos de votación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== GESTIÓN DE ASIGNACIONES ====================

@coordination_bp.route('/assignments', methods=['GET'])
@require_coordinator_auth
def get_assignments(coordinator_info):
    """Obtener asignaciones del coordinador"""
    try:
        coordinator_id = coordinator_info['id']
        
        # Obtener filtros
        filters = {}
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('proceso_id'):
            filters['proceso_id'] = int(request.args.get('proceso_id'))
        if request.args.get('mesa_id'):
            filters['mesa_id'] = int(request.args.get('mesa_id'))
        
        assignments = coordination_service.get_assignments(coordinator_id, filters)
        
        return jsonify({
            'success': True,
            'data': assignments,
            'total': len(assignments)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo asignaciones: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/assignments', methods=['POST'])
@require_coordinator_auth
def create_assignment(coordinator_info):
    """Asignar testigo a mesa de votación"""
    try:
        coordinator_id = coordinator_info['id']
        assignment_data = request.get_json()
        
        if not assignment_data:
            return jsonify({
                'success': False,
                'error': 'Datos de asignación requeridos'
            }), 400
        
        assignment_id = coordination_service.assign_witness_to_table(
            assignment_data, coordinator_id
        )
        
        return jsonify({
            'success': True,
            'data': {'assignment_id': assignment_id},
            'message': 'Asignación creada exitosamente'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creando asignación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/assignments/<int:assignment_id>/status', methods=['PUT'])
@require_coordinator_auth
def update_assignment_status(coordinator_info, assignment_id):
    """Actualizar estado de asignación"""
    try:
        coordinator_id = coordinator_info['id']
        data = request.get_json()
        
        if not data or 'estado' not in data:
            return jsonify({
                'success': False,
                'error': 'Estado requerido'
            }), 400
        
        new_status = data['estado']
        observations = data.get('observaciones')
        
        success = coordination_service.update_assignment_status(
            assignment_id, new_status, coordinator_id, observations
        )
        
        return jsonify({
            'success': success,
            'message': 'Estado de asignación actualizado exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error actualizando estado de asignación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== GESTIÓN DE TAREAS ====================

@coordination_bp.route('/tasks', methods=['GET'])
@require_coordinator_auth
def get_tasks(coordinator_info):
    """Obtener tareas del coordinador"""
    try:
        coordinator_id = coordinator_info['id']
        
        # Obtener filtros
        filters = {}
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('prioridad'):
            filters['prioridad'] = int(request.args.get('prioridad'))
        if request.args.get('tipo_tarea'):
            filters['tipo_tarea'] = request.args.get('tipo_tarea')
        
        tasks = coordination_service.get_tasks(coordinator_id, filters)
        
        return jsonify({
            'success': True,
            'data': tasks,
            'total': len(tasks)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo tareas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/tasks/<int:task_id>/progress', methods=['PUT'])
@require_coordinator_auth
def update_task_progress(coordinator_info, task_id):
    """Actualizar progreso de tarea"""
    try:
        coordinator_id = coordinator_info['id']
        data = request.get_json()
        
        if not data or 'progreso' not in data:
            return jsonify({
                'success': False,
                'error': 'Progreso requerido'
            }), 400
        
        progress = data['progreso']
        observations = data.get('observaciones')
        
        success = coordination_service.update_task_progress(
            task_id, progress, coordinator_id, observations
        )
        
        return jsonify({
            'success': success,
            'message': 'Progreso de tarea actualizado exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error actualizando progreso de tarea: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== REPORTES ====================

@coordination_bp.route('/reports/coverage', methods=['GET'])
@require_coordinator_auth
def generate_coverage_report(coordinator_info):
    """Generar reporte de cobertura de mesas"""
    try:
        coordinator_id = coordinator_info['id']
        process_id = request.args.get('proceso_id', type=int)
        
        report = coordination_service.generate_coverage_report(coordinator_id, process_id)
        
        return jsonify({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte de cobertura: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/statistics/update', methods=['POST'])
@require_coordinator_auth
def update_statistics(coordinator_info):
    """Actualizar estadísticas de coordinación"""
    try:
        coordinator_id = coordinator_info['id']
        success = coordination_service.update_coordination_statistics(coordinator_id)
        
        return jsonify({
            'success': success,
            'message': 'Estadísticas actualizadas exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error actualizando estadísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== NOTIFICACIONES ====================

@coordination_bp.route('/notifications', methods=['POST'])
@require_coordinator_auth
def create_notification(coordinator_info):
    """Crear notificación para coordinador"""
    try:
        coordinator_id = coordinator_info['id']
        notification_data = request.get_json()
        
        if not notification_data:
            return jsonify({
                'success': False,
                'error': 'Datos de notificación requeridos'
            }), 400
        
        notification_id = coordination_service.create_notification(
            coordinator_id, notification_data
        )
        
        return jsonify({
            'success': True,
            'data': {'notification_id': notification_id},
            'message': 'Notificación creada exitosamente'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creando notificación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@require_coordinator_auth
def mark_notification_read(coordinator_info, notification_id):
    """Marcar notificación como leída"""
    try:
        coordinator_id = coordinator_info['id']
        success = coordination_service.mark_notification_as_read(
            notification_id, coordinator_id
        )
        
        return jsonify({
            'success': success,
            'message': 'Notificación marcada como leída'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== UTILIDADES ====================

@coordination_bp.route('/export/assignments', methods=['GET'])
@require_coordinator_auth
def export_assignments(coordinator_info):
    """Exportar asignaciones a Excel/CSV"""
    try:
        coordinator_id = coordinator_info['id']
        format_type = request.args.get('format', 'json')  # json, csv, excel
        
        assignments = coordination_service.get_assignments(coordinator_id)
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'data': assignments,
                'total': len(assignments)
            })
        
        # TODO: Implementar exportación a CSV/Excel
        return jsonify({
            'success': False,
            'error': 'Formato de exportación no implementado aún'
        }), 501
        
    except Exception as e:
        logger.error(f"Error exportando asignaciones: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coordination_bp.route('/bulk-assign', methods=['POST'])
@require_coordinator_auth
def bulk_assign_witnesses(coordinator_info):
    """Asignación masiva de testigos"""
    try:
        coordinator_id = coordinator_info['id']
        bulk_data = request.get_json()
        
        if not bulk_data or 'assignments' not in bulk_data:
            return jsonify({
                'success': False,
                'error': 'Datos de asignación masiva requeridos'
            }), 400
        
        assignments = bulk_data['assignments']
        results = []
        errors = []
        
        for assignment_data in assignments:
            try:
                assignment_id = coordination_service.assign_witness_to_table(
                    assignment_data, coordinator_id
                )
                results.append({
                    'assignment_id': assignment_id,
                    'testigo_id': assignment_data['testigo_id'],
                    'mesa_id': assignment_data['mesa_id'],
                    'success': True
                })
            except Exception as e:
                errors.append({
                    'testigo_id': assignment_data.get('testigo_id'),
                    'mesa_id': assignment_data.get('mesa_id'),
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'successful_assignments': len(results),
                'failed_assignments': len(errors),
                'results': results,
                'errors': errors
            },
            'message': f'{len(results)} asignaciones creadas, {len(errors)} errores'
        })
        
    except Exception as e:
        logger.error(f"Error en asignación masiva: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== MANEJO DE ERRORES ====================

@coordination_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@coordination_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@coordination_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500