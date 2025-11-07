"""
Rutas del módulo de candidatos
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime

from .services import CandidateManagementService, CandidateReportingService, E14CandidateIntegrationService
from .models import PoliticalPartyData, CoalitionData, CandidateData

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
candidate_bp = Blueprint('candidates', __name__, url_prefix='/api/candidates')

# Instancias de servicios
candidate_service = CandidateManagementService()
reporting_service = CandidateReportingService()
e14_service = E14CandidateIntegrationService()

# ==================== ENDPOINTS DE PARTIDOS POLÍTICOS ====================

@candidate_bp.route('/parties', methods=['GET'])
def get_political_parties():
    """Obtener lista de partidos políticos"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        parties = candidate_service.get_political_parties(active_only=active_only)
        
        return jsonify({
            'success': True,
            'data': parties,
            'total': len(parties)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo partidos políticos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_bp.route('/parties', methods=['POST'])
def create_political_party():
    """Crear un nuevo partido político"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['nombre_oficial', 'siglas']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear objeto de datos del partido
        party_data = PoliticalPartyData(
            nombre_oficial=data['nombre_oficial'],
            siglas=data['siglas'].upper(),
            color_representativo=data.get('color_representativo'),
            logo_url=data.get('logo_url'),
            descripcion=data.get('descripcion'),
            fundacion_year=data.get('fundacion_year'),
            ideologia=data.get('ideologia'),
            activo=data.get('activo', True),
            reconocido_oficialmente=data.get('reconocido_oficialmente', True)
        )
        
        # Obtener usuario actual (simulado por ahora)
        created_by = data.get('created_by', 1)  # TODO: Obtener del token de sesión
        
        result = candidate_service.create_political_party(party_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando partido político: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE CANDIDATOS ====================

@candidate_bp.route('/', methods=['GET'])
def get_candidates():
    """Obtener lista de candidatos con filtros opcionales"""
    try:
        # Obtener parámetros de filtro
        election_type_id = request.args.get('election_type_id', type=int)
        party_id = request.args.get('party_id', type=int)
        coalition_id = request.args.get('coalition_id', type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        candidates = candidate_service.get_candidates(
            election_type_id=election_type_id,
            party_id=party_id,
            coalition_id=coalition_id,
            active_only=active_only
        )
        
        return jsonify({
            'success': True,
            'data': candidates,
            'total': len(candidates)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_bp.route('/', methods=['POST'])
def create_candidate():
    """Crear un nuevo candidato"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['nombre_completo', 'cedula', 'numero_tarjeton', 
                          'cargo_aspirado', 'election_type_id', 'circunscripcion']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear objeto de datos del candidato
        candidate_data = CandidateData(
            nombre_completo=data['nombre_completo'],
            cedula=data['cedula'],
            numero_tarjeton=int(data['numero_tarjeton']),
            cargo_aspirado=data['cargo_aspirado'],
            election_type_id=int(data['election_type_id']),
            circunscripcion=data['circunscripcion'],
            party_id=data.get('party_id'),
            coalition_id=data.get('coalition_id'),
            es_independiente=data.get('es_independiente', False),
            foto_url=data.get('foto_url'),
            biografia=data.get('biografia'),
            propuestas=data.get('propuestas'),
            experiencia=data.get('experiencia'),
            activo=data.get('activo', True),
            habilitado_oficialmente=data.get('habilitado_oficialmente', True)
        )
        
        # Obtener usuario actual (simulado por ahora)
        created_by = data.get('created_by', 1)  # TODO: Obtener del token de sesión
        
        result = candidate_service.create_candidate(candidate_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando candidato: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE BÚSQUEDA Y REPORTES ====================

@candidate_bp.route('/search', methods=['GET'])
def search_candidates():
    """Búsqueda avanzada de candidatos"""
    try:
        search_params = {
            'nombre': request.args.get('nombre'),
            'cedula': request.args.get('cedula'),
            'cargo': request.args.get('cargo'),
            'election_type_id': request.args.get('election_type_id', type=int),
            'party_id': request.args.get('party_id', type=int),
            'coalition_id': request.args.get('coalition_id', type=int),
            'independientes_only': request.args.get('independientes_only', 'false').lower() == 'true',
            'circunscripcion': request.args.get('circunscripcion'),
            'habilitado': request.args.get('habilitado', type=bool),
            'limit': request.args.get('limit', type=int)
        }
        
        # Filtrar parámetros None
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        candidates = candidate_service.search_candidates(search_params)
        
        return jsonify({
            'success': True,
            'data': candidates,
            'total': len(candidates),
            'search_params': search_params
        })
        
    except Exception as e:
        logger.error(f"Error en búsqueda de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_bp.route('/stats', methods=['GET'])
def get_candidate_stats():
    """Obtener estadísticas generales de candidatos"""
    try:
        # Obtener todos los candidatos activos
        all_candidates = candidate_service.get_candidates(active_only=True)
        
        # Calcular estadísticas
        stats = {
            'total_candidates': len(all_candidates),
            'by_election_type': {},
            'by_party': {},
            'by_coalition': {},
            'independents': 0,
            'enabled': 0,
            'disabled': 0
        }
        
        for candidate in all_candidates:
            # Por tipo de elección
            election_type = candidate.get('election_type_name', 'Sin tipo')
            stats['by_election_type'][election_type] = stats['by_election_type'].get(election_type, 0) + 1
            
            # Por partido
            if candidate.get('party_name'):
                party_name = candidate['party_name']
                stats['by_party'][party_name] = stats['by_party'].get(party_name, 0) + 1
            
            # Por coalición
            if candidate.get('coalition_name'):
                coalition_name = candidate['coalition_name']
                stats['by_coalition'][coalition_name] = stats['by_coalition'].get(coalition_name, 0) + 1
            
            # Independientes
            if candidate.get('es_independiente'):
                stats['independents'] += 1
            
            # Habilitados/Deshabilitados
            if candidate.get('habilitado_oficialmente'):
                stats['enabled'] += 1
            else:
                stats['disabled'] += 1
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@candidate_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@candidate_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@candidate_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500