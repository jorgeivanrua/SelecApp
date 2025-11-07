"""
Rutas del módulo de coordinación
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from .services import CoordinationService, MunicipalCoordinationService
from .models import WitnessData, AssignmentData

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
coordination_bp = Blueprint('coordination', __name__, url_prefix='/api/coordination')

# Instancias de servicios
coordination_service = CoordinationService()
municipal_service = MunicipalCoordinationService()

# ==================== ENDPOINTS DE DASHBOARD ====================

@coordination_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Obtener datos del dashboard de coordinación"""
    try:
        # TODO: Obtener coordinator_id del token de sesión
        coordinator_id = request.args.get('coordinator_id', 1, type=int)
        
        dashboard_data = coordination_service.get_dashboard_data(coordinator_id)
        
        if dashboard_data:
            return jsonify({
                'success': True,
                'data': dashboard_data.__dict__
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo obtener información del coordinador'
            }), 404
            
    except Exception as e:
        logger.error(f"Error obteniendo dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/statistics', methods=['GET'])
def get_coordination_statistics():
    """Obtener estadísticas de coordinación"""
    try:
        coordinator_id = request.args.get('coordinator_id', 1, type=int)
        
        statistics = coordination_service.get_coordination_statistics(coordinator_id)
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE TESTIGOS ====================

@coordination_bp.route('/witnesses', methods=['GET'])
def get_witnesses():
    """Obtener lista de testigos"""
    try:
        municipio_id = request.args.get('municipio_id', type=int)
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        
        if available_only:
            witnesses = coordination_service.get_available_witnesses(municipio_id)
        else:
            witnesses = municipal_service.get_testigos_by_municipio(municipio_id) if municipio_id else []
        
        return jsonify({
            'success': True,
            'data': witnesses,
            'total': len(witnesses)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo testigos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/witnesses', methods=['POST'])
def create_witness():
    """Crear nuevo testigo electoral"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['nombre_completo', 'cedula', 'telefono']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear objeto de datos del testigo
        witness_data = WitnessData(
            nombre_completo=data['nombre_completo'],
            cedula=data['cedula'],
            telefono=data['telefono'],
            email=data.get('email'),
            direccion=data.get('direccion'),
            partido_id=data.get('partido_id'),
            tipo_testigo=data.get('tipo_testigo', 'principal'),
            observaciones=data.get('observaciones'),
            activo=data.get('activo', True)
        )
        
        # Obtener usuario actual (simulado por ahora)
        created_by = data.get('created_by', 1)  # TODO: Obtener del token de sesión
        
        result = coordination_service.create_witness(witness_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando testigo: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/witnesses/available', methods=['GET'])
def get_available_witnesses():
    """Obtener testigos disponibles para asignación"""
    try:
        municipio_id = request.args.get('municipio_id', type=int)
        
        witnesses = coordination_service.get_available_witnesses(municipio_id)
        
        return jsonify({
            'success': True,
            'data': witnesses,
            'total': len(witnesses)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo testigos disponibles: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE ASIGNACIONES ====================

@coordination_bp.route('/assignments', methods=['POST'])
def assign_witness():
    """Asignar testigo a mesa electoral"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['testigo_id', 'mesa_id', 'proceso_electoral_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear objeto de datos de asignación
        assignment_data = AssignmentData(
            testigo_id=int(data['testigo_id']),
            mesa_id=int(data['mesa_id']),
            proceso_electoral_id=int(data['proceso_electoral_id']),
            hora_inicio=data.get('hora_inicio'),
            hora_fin=data.get('hora_fin'),
            observaciones=data.get('observaciones'),
            estado=data.get('estado', 'asignado')
        )
        
        # Obtener usuario actual (simulado por ahora)
        assigned_by = data.get('assigned_by', 1)  # TODO: Obtener del token de sesión
        
        result = coordination_service.assign_witness_to_mesa(assignment_data, assigned_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error asignando testigo: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/assignments/auto-assign', methods=['POST'])
def auto_assign_witnesses():
    """Asignación automática de testigos"""
    try:
        data = request.get_json()
        
        municipio_id = data.get('municipio_id')
        if not municipio_id:
            return jsonify({
                'success': False,
                'error': 'municipio_id es requerido'
            }), 400
        
        assigned_by = data.get('assigned_by', 1)  # TODO: Obtener del token
        
        result = municipal_service.auto_assign_witnesses(municipio_id, assigned_by)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en asignación automática: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE MESAS Y COBERTURA ====================

@coordination_bp.route('/voting-tables', methods=['GET'])
def get_voting_tables():
    """Obtener mesas de votación"""
    try:
        puesto_id = request.args.get('puesto_id', type=int)
        sin_cobertura = request.args.get('sin_cobertura', 'false').lower() == 'true'
        municipio_id = request.args.get('municipio_id', type=int)
        
        if sin_cobertura:
            tables = coordination_service.get_uncovered_tables(municipio_id)
        elif puesto_id:
            tables = municipal_service.get_mesas_by_puesto(puesto_id)
        else:
            tables = []
        
        return jsonify({
            'success': True,
            'data': tables,
            'total': len(tables)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo mesas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/coverage/summary', methods=['GET'])
def get_coverage_summary():
    """Obtener resumen de cobertura"""
    try:
        municipio_id = request.args.get('municipio_id', type=int)
        
        if not municipio_id:
            return jsonify({
                'success': False,
                'error': 'municipio_id es requerido'
            }), 400
        
        coverage_summary = coordination_service.get_coverage_summary(municipio_id)
        
        return jsonify({
            'success': True,
            'data': coverage_summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de cobertura: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE REPORTES ====================

@coordination_bp.route('/reports/coverage', methods=['GET'])
def generate_coverage_report():
    """Generar reporte de cobertura"""
    try:
        municipio_id = request.args.get('municipio_id', type=int)
        
        result = coordination_service.generate_coverage_report(municipio_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generando reporte de cobertura: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/reports/municipal/<int:municipio_id>', methods=['GET'])
def generate_municipal_report(municipio_id):
    """Generar reporte municipal completo"""
    try:
        result = municipal_service.generate_municipal_report(municipio_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generando reporte municipal: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS MUNICIPALES ====================

@coordination_bp.route('/municipal/overview/<int:municipio_id>', methods=['GET'])
def get_municipal_overview(municipio_id):
    """Obtener vista general municipal"""
    try:
        overview = municipal_service.get_municipal_overview(municipio_id)
        
        return jsonify({
            'success': True,
            'data': overview
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo vista municipal: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@coordination_bp.route('/municipal/puestos/<int:municipio_id>', methods=['GET'])
def get_puestos_by_municipio(municipio_id):
    """Obtener puestos por municipio"""
    try:
        puestos = municipal_service.get_puestos_by_municipio(municipio_id)
        
        return jsonify({
            'success': True,
            'data': puestos,
            'total': len(puestos)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo puestos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
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