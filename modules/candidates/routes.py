"""
Módulo Candidatos - Rutas y Endpoints
Gestión de candidatos, partidos políticos y coaliciones
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import CandidateService
from core.permissions import Permission

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/candidates', methods=['GET'])
@jwt_required()
def get_candidates():
    """Obtener candidatos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = CandidateService(current_app.db_manager)
        
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        election_type_id = request.args.get('election_type_id', type=int)
        party_id = request.args.get('party_id', type=int)
        cargo = request.args.get('cargo', '')
        
        result = service.get_candidates(page, per_page, search, election_type_id, party_id, cargo)
        return jsonify(result)
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/candidates', methods=['POST'])
@jwt_required()
def create_candidate():
    """Crear nuevo candidato"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_REGISTER.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = CandidateService(current_app.db_manager)
        candidate_id = service.create_candidate(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Candidate created successfully',
            'candidate_id': candidate_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/candidates/<int:candidate_id>', methods=['GET'])
@jwt_required()
def get_candidate(candidate_id):
    """Obtener candidato específico"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = CandidateService(current_app.db_manager)
        candidate = service.get_candidate_by_id(candidate_id)
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify({'success': True, 'data': candidate})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/candidates/<int:candidate_id>', methods=['PUT'])
@jwt_required()
def update_candidate(candidate_id):
    """Actualizar candidato"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = CandidateService(current_app.db_manager)
        updated = service.update_candidate(candidate_id, data, user_id)
        
        if not updated:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Candidate updated successfully'
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/parties', methods=['GET'])
@jwt_required()
def get_political_parties():
    """Obtener partidos políticos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = CandidateService(current_app.db_manager)
        parties = service.get_political_parties()
        
        return jsonify({'success': True, 'data': parties})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/parties', methods=['POST'])
@jwt_required()
def create_political_party():
    """Crear nuevo partido político"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = CandidateService(current_app.db_manager)
        party_id = service.create_political_party(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Political party created successfully',
            'party_id': party_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/coalitions', methods=['GET'])
@jwt_required()
def get_coalitions():
    """Obtener coaliciones"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = CandidateService(current_app.db_manager)
        coalitions = service.get_coalitions()
        
        return jsonify({'success': True, 'data': coalitions})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/coalitions', methods=['POST'])
@jwt_required()
def create_coalition():
    """Crear nueva coalición"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = CandidateService(current_app.db_manager)
        coalition_id = service.create_coalition(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Coalition created successfully',
            'coalition_id': coalition_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/results', methods=['GET'])
@jwt_required()
def get_candidate_results():
    """Obtener resultados de candidatos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = CandidateService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        candidate_id = request.args.get('candidate_id', type=int)
        party_id = request.args.get('party_id', type=int)
        
        results = service.get_candidate_results(election_type_id, candidate_id, party_id)
        return jsonify({'success': True, 'data': results})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/results/calculate', methods=['POST'])
@jwt_required()
def calculate_results():
    """Calcular resultados de candidatos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_MANAGE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        election_type_id = data.get('election_type_id') if data else None
        
        service = CandidateService(current_app.db_manager)
        success = service.calculate_candidate_results(election_type_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Results calculated successfully'
            })
        else:
            return jsonify({'error': 'Failed to calculate results'}), 400
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@candidates_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_candidate_data():
    """Validar datos de candidato"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.CANDIDATES_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = CandidateService(current_app.db_manager)
        validation_result = service.validate_candidate_data(data)
        
        return jsonify({
            'success': True,
            'validation': validation_result
        })
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)