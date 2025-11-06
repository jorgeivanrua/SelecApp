"""
Módulo Electoral - Rutas y Endpoints
Gestión de procesos electorales, jornadas y tipos de elección
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import ElectoralService
from core.permissions import Permission

electoral_bp = Blueprint('electoral', __name__)

@electoral_bp.route('/processes', methods=['GET'])
@jwt_required()
def get_electoral_processes():
    """Obtener procesos electorales"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        result = service.get_electoral_processes(page, per_page, search, status)
        return jsonify(result)
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/processes', methods=['POST'])
@jwt_required()
def create_electoral_process():
    """Crear nuevo proceso electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = ElectoralService(current_app.db_manager)
        process_id = service.create_electoral_process(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Electoral process created successfully',
            'process_id': process_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/processes/<int:process_id>', methods=['GET'])
@jwt_required()
def get_electoral_process(process_id):
    """Obtener proceso electoral específico"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        process = service.get_electoral_process_by_id(process_id)
        
        if not process:
            return jsonify({'error': 'Electoral process not found'}), 404
        
        return jsonify({'success': True, 'data': process})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/processes/<int:process_id>', methods=['PUT'])
@jwt_required()
def update_electoral_process(process_id):
    """Actualizar proceso electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = ElectoralService(current_app.db_manager)
        updated = service.update_electoral_process(process_id, data, user_id)
        
        if not updated:
            return jsonify({'error': 'Electoral process not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Electoral process updated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/journeys', methods=['GET'])
@jwt_required()
def get_electoral_journeys():
    """Obtener jornadas electorales"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        journeys = service.get_electoral_journeys()
        
        return jsonify({'success': True, 'data': journeys})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/journeys', methods=['POST'])
@jwt_required()
def create_electoral_journey():
    """Crear nueva jornada electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = ElectoralService(current_app.db_manager)
        journey_id = service.create_electoral_journey(data)
        
        return jsonify({
            'success': True,
            'message': 'Electoral journey created successfully',
            'journey_id': journey_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/types', methods=['GET'])
@jwt_required()
def get_election_types():
    """Obtener tipos de elección"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        types = service.get_election_types()
        
        return jsonify({'success': True, 'data': types})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/mesas', methods=['GET'])
@jwt_required()
def get_electoral_mesas():
    """Obtener mesas electorales"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        municipio_id = request.args.get('municipio_id', type=int)
        puesto_id = request.args.get('puesto_id', type=int)
        estado = request.args.get('estado', '')
        
        result = service.get_electoral_mesas(page, per_page, municipio_id, puesto_id, estado)
        return jsonify(result)
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/mesas/<int:mesa_id>/assign-witness', methods=['POST'])
@jwt_required()
def assign_mesa_witness(mesa_id):
    """Asignar testigo a mesa electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data or 'testigo_id' not in data:
            return jsonify({'error': 'Testigo ID required'}), 400
        
        service = ElectoralService(current_app.db_manager)
        success = service.assign_mesa_witness(mesa_id, data['testigo_id'], user_id)
        
        if not success:
            return jsonify({'error': 'Failed to assign witness'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Witness assigned successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/results/summary', methods=['GET'])
@jwt_required()
def get_results_summary():
    """Obtener resumen de resultados electorales"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_RESULTS.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        
        process_id = request.args.get('process_id', type=int)
        election_type_id = request.args.get('election_type_id', type=int)
        
        summary = service.get_results_summary(process_id, election_type_id)
        return jsonify({'success': True, 'data': summary})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@electoral_bp.route('/locations', methods=['GET'])
@jwt_required()
def get_locations():
    """Obtener ubicaciones (departamentos, municipios, puestos)"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.ELECTORAL_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ElectoralService(current_app.db_manager)
        
        location_type = request.args.get('type', '')  # DEPARTAMENTO, MUNICIPIO, PUESTO
        parent_id = request.args.get('parent_id', type=int)
        
        locations = service.get_locations(location_type, parent_id)
        return jsonify({'success': True, 'data': locations})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)