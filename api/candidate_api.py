"""
API para Gestión de Candidatos, Partidos Políticos y Coaliciones
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Importar el servicio
from services.candidate_management_service import (
    CandidateManagementService, 
    PoliticalPartyData, 
    CoalitionData, 
    CandidateData
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
candidate_api = Blueprint('candidate_api', __name__, url_prefix='/api/candidates')

# Instancia del servicio
candidate_service = CandidateManagementService()

# ==================== ENDPOINTS DE PARTIDOS POLÍTICOS ====================

@candidate_api.route('/parties', methods=['GET'])
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

@candidate_api.route('/parties', methods=['POST'])
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

# ==================== ENDPOINTS DE COALICIONES ====================

@candidate_api.route('/coalitions', methods=['GET'])
def get_coalitions():
    """Obtener lista de coaliciones"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        coalitions = candidate_service.get_coalitions(active_only=active_only)
        
        return jsonify({
            'success': True,
            'data': coalitions,
            'total': len(coalitions)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo coaliciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_api.route('/coalitions', methods=['POST'])
def create_coalition():
    """Crear una nueva coalición"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        if not data.get('nombre_coalicion'):
            return jsonify({
                'success': False,
                'error': 'Campo requerido: nombre_coalicion'
            }), 400
        
        # Crear objeto de datos de la coalición
        coalition_data = CoalitionData(
            nombre_coalicion=data['nombre_coalicion'],
            descripcion=data.get('descripcion'),
            fecha_formacion=datetime.fromisoformat(data['fecha_formacion']) if data.get('fecha_formacion') else None,
            partidos_ids=data.get('partidos_ids', []),
            activo=data.get('activo', True)
        )
        
        # Obtener usuario actual (simulado por ahora)
        created_by = data.get('created_by', 1)  # TODO: Obtener del token de sesión
        
        result = candidate_service.create_coalition(coalition_data, created_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creando coalición: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_api.route('/coalitions/<int:coalition_id>/parties', methods=['POST'])
def add_party_to_coalition(coalition_id):
    """Agregar un partido a una coalición"""
    try:
        data = request.get_json()
        
        if not data or not data.get('party_id'):
            return jsonify({
                'success': False,
                'error': 'party_id es requerido'
            }), 400
        
        result = candidate_service.add_party_to_coalition(
            coalition_id=coalition_id,
            party_id=data['party_id'],
            es_principal=data.get('es_principal', False),
            porcentaje_participacion=data.get('porcentaje_participacion')
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error agregando partido a coalición: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE CANDIDATOS ====================

@candidate_api.route('/', methods=['GET'])
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

@candidate_api.route('/', methods=['POST'])
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

@candidate_api.route('/search', methods=['GET'])
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

@candidate_api.route('/by-party/<int:party_id>', methods=['GET'])
def get_candidates_by_party(party_id):
    """Obtener candidatos por partido"""
    try:
        candidates = candidate_service.get_candidates(party_id=party_id)
        
        return jsonify({
            'success': True,
            'data': candidates,
            'total': len(candidates),
            'party_id': party_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo candidatos por partido: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@candidate_api.route('/by-coalition/<int:coalition_id>', methods=['GET'])
def get_candidates_by_coalition(coalition_id):
    """Obtener candidatos por coalición"""
    try:
        candidates = candidate_service.get_candidates(coalition_id=coalition_id)
        
        return jsonify({
            'success': True,
            'data': candidates,
            'total': len(candidates),
            'coalition_id': coalition_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo candidatos por coalición: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== CARGA MASIVA ====================

@candidate_api.route('/upload-csv', methods=['POST'])
def upload_candidates_csv():
    """Carga masiva de candidatos desde archivo CSV"""
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo CSV'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo'
            }), 400
        
        # Verificar extensión
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Solo se permiten archivos CSV'
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
            # Procesar archivo CSV
            created_by = request.form.get('created_by', 1, type=int)  # TODO: Obtener del token
            result = candidate_service.load_candidates_from_csv(temp_path, election_type_id, created_by)
            
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
        logger.error(f"Error en carga masiva de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error procesando archivo CSV'
        }), 500

# ==================== VALIDACIÓN CON TARJETONES ====================

@candidate_api.route('/validate-ballot', methods=['POST'])
def validate_candidates_with_ballot():
    """Validar candidatos contra tarjetón oficial"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        election_type_id = data.get('election_type_id')
        official_ballot_data = data.get('official_ballot_data')
        
        if not election_type_id or not official_ballot_data:
            return jsonify({
                'success': False,
                'error': 'election_type_id y official_ballot_data son requeridos'
            }), 400
        
        result = candidate_service.validate_candidates_with_ballot(
            election_type_id, official_ballot_data
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error validando candidatos con tarjetón: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== LISTAS ORGANIZADAS ====================

@candidate_api.route('/candidate-lists/<int:election_type_id>', methods=['GET'])
def get_candidate_lists(election_type_id):
    """Obtener listas organizadas de candidatos por partido/coalición"""
    try:
        result = candidate_service.generate_candidate_lists(election_type_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error generando listas de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE UTILIDAD ====================

@candidate_api.route('/stats', methods=['GET'])
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
            'by_gender': {'male': 0, 'female': 0, 'other': 0},  # TODO: Agregar campo género
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

@candidate_api.route('/export-template', methods=['GET'])
def export_csv_template():
    """Exportar plantilla CSV para carga masiva"""
    try:
        template_data = {
            'headers': [
                'nombre_completo',
                'cedula',
                'numero_tarjeton',
                'cargo_aspirado',
                'circunscripcion',
                'party_siglas',
                'coalition_name',
                'foto_url',
                'biografia',
                'propuestas',
                'experiencia'
            ],
            'example_row': [
                'Juan Pérez García',
                '12345678',
                '1',
                'Senador',
                'Nacional',
                'PLC',
                '',
                'https://example.com/foto.jpg',
                'Abogado con 20 años de experiencia',
                'Educación y salud para todos',
                'Alcalde de Bogotá 2016-2020'
            ],
            'instructions': {
                'nombre_completo': 'Nombre completo del candidato (requerido)',
                'cedula': 'Número de cédula sin puntos ni espacios (requerido)',
                'numero_tarjeton': 'Número en el tarjetón electoral (requerido)',
                'cargo_aspirado': 'Cargo al que aspira (requerido)',
                'circunscripcion': 'Circunscripción electoral (requerido)',
                'party_siglas': 'Siglas del partido político (opcional, usar solo si no es coalición)',
                'coalition_name': 'Nombre de la coalición (opcional, usar solo si no es partido)',
                'foto_url': 'URL de la foto del candidato (opcional)',
                'biografia': 'Biografía del candidato (opcional)',
                'propuestas': 'Propuestas principales (opcional)',
                'experiencia': 'Experiencia relevante (opcional)'
            }
        }
        
        return jsonify({
            'success': True,
            'data': template_data
        })
        
    except Exception as e:
        logger.error(f"Error exportando plantilla: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@candidate_api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@candidate_api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@candidate_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500

if __name__ == "__main__":
    print("🗳️  API de Gestión de Candidatos, Partidos y Coaliciones")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    print("Endpoints disponibles:")
    print("  GET    /api/candidates/parties - Obtener partidos políticos")
    print("  POST   /api/candidates/parties - Crear partido político")
    print("  GET    /api/candidates/coalitions - Obtener coaliciones")
    print("  POST   /api/candidates/coalitions - Crear coalición")
    print("  GET    /api/candidates/ - Obtener candidatos")
    print("  POST   /api/candidates/ - Crear candidato")
    print("  GET    /api/candidates/search - Búsqueda avanzada")
    print("  POST   /api/candidates/upload-csv - Carga masiva CSV")
    print("  POST   /api/candidates/validate-ballot - Validar con tarjetón")
    print("  GET    /api/candidates/candidate-lists/<id> - Listas organizadas")
    print("  GET    /api/candidates/stats - Estadísticas generales")