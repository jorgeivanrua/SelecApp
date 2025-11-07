#!/usr/bin/env python3
"""
APIs para Coordinación Municipal
Endpoints para consolidación E-14 a E-24, verificación y gestión de reclamaciones
"""

from flask import Blueprint, request, jsonify, current_app
from services.municipal_coordination_service import MunicipalCoordinationService
import logging
from datetime import datetime
import os

municipal_api = Blueprint('municipal_api', __name__)
logger = logging.getLogger(__name__)

def get_municipal_service():
    """Obtener instancia del servicio de coordinación municipal"""
    return MunicipalCoordinationService()

# ==================== ENDPOINTS DE CONSOLIDACIÓN ====================

@municipal_api.route('/consolidacion/<int:municipio_id>/estado', methods=['GET'])
def get_consolidation_status(municipio_id):
    """Obtener estado de consolidación municipal"""
    try:
        service = get_municipal_service()
        status = service.get_consolidation_status(municipio_id)
        
        return jsonify({
            'success': True,
            'data': status,
            'municipio_id': municipio_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de consolidación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/consolidacion/<int:municipio_id>/lista', methods=['GET'])
def get_municipal_consolidations(municipio_id):
    """Obtener lista de consolidaciones municipales"""
    try:
        service = get_municipal_service()
        proceso_id = request.args.get('proceso_id', type=int)
        
        consolidations = service.get_municipal_consolidations(municipio_id, proceso_id)
        
        return jsonify({
            'success': True,
            'data': consolidations,
            'total': len(consolidations),
            'municipio_id': municipio_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo consolidaciones: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/consolidacion/iniciar', methods=['POST'])
def start_consolidation():
    """Iniciar proceso de consolidación"""
    try:
        service = get_municipal_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['municipio_id', 'proceso_id', 'tipo_eleccion']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = data.get('usuario_id', 1)  # Placeholder
        
        consolidation_id = service.start_consolidation(
            data['municipio_id'],
            data['proceso_id'],
            data['tipo_eleccion'],
            usuario_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Consolidación iniciada exitosamente',
            'consolidation_id': consolidation_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error iniciando consolidación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/consolidacion/<int:consolidation_id>/procesar', methods=['POST'])
def process_consolidation(consolidation_id):
    """Procesar E-14s para consolidación"""
    try:
        service = get_municipal_service()
        data = request.get_json() or {}
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = data.get('usuario_id', 1)  # Placeholder
        
        result = service.process_e14_to_consolidation(consolidation_id, usuario_id)
        
        return jsonify({
            'success': True,
            'message': 'E-14s procesados exitosamente',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error procesando consolidación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/consolidacion/<int:consolidation_id>/generar-e24', methods=['POST'])
def generate_e24(consolidation_id):
    """Generar imagen E-24 desde consolidación"""
    try:
        service = get_municipal_service()
        data = request.get_json() or {}
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = data.get('usuario_id', 1)  # Placeholder
        
        filepath = service.generate_e24_image(consolidation_id, usuario_id)
        
        return jsonify({
            'success': True,
            'message': 'E-24 generado exitosamente',
            'filepath': filepath,
            'consolidation_id': consolidation_id
        })
        
    except Exception as e:
        logger.error(f"Error generando E-24: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE VERIFICACIÓN E-24 ====================

@municipal_api.route('/e24/<int:consolidation_id>/subir-oficial', methods=['POST'])
def upload_official_e24(consolidation_id):
    """Subir imagen oficial E-24 de Registraduría"""
    try:
        service = get_municipal_service()
        
        # Verificar si se envió un archivo
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"E24_oficial_{consolidation_id}_{timestamp}_{file.filename}"
        filepath = f"static/official_e24/{filename}"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = request.form.get('usuario_id', 1, type=int)  # Placeholder
        
        success = service.upload_official_e24(consolidation_id, filepath, usuario_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'E-24 oficial subido exitosamente',
                'filepath': filepath
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo subir el archivo'}), 400
        
    except Exception as e:
        logger.error(f"Error subiendo E-24 oficial: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/e24/<int:consolidation_id>/verificar', methods=['POST'])
def verify_e24(consolidation_id):
    """Verificar y comparar E-24 generado vs oficial"""
    try:
        service = get_municipal_service()
        data = request.get_json() or {}
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = data.get('usuario_id', 1)  # Placeholder
        
        result = service.verify_e24_comparison(consolidation_id, usuario_id)
        
        return jsonify({
            'success': True,
            'message': 'Verificación completada',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error verificando E-24: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/e24/<int:consolidation_id>/discrepancias', methods=['GET'])
def get_discrepancies(consolidation_id):
    """Obtener discrepancias de una consolidación"""
    try:
        service = get_municipal_service()
        discrepancies = service.get_discrepancies(consolidation_id)
        
        return jsonify({
            'success': True,
            'data': discrepancies,
            'total': len(discrepancies),
            'consolidation_id': consolidation_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo discrepancias: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE RECLAMACIONES ====================

@municipal_api.route('/reclamaciones', methods=['POST'])
def generate_claim():
    """Generar reclamación por discrepancias"""
    try:
        service = get_municipal_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['consolidation_id', 'tipo_reclamacion', 'descripcion']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = data.get('usuario_id', 1)  # Placeholder
        
        claim_id = service.generate_claim(
            data['consolidation_id'],
            data['tipo_reclamacion'],
            data['descripcion'],
            usuario_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Reclamación generada exitosamente',
            'claim_id': claim_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error generando reclamación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/reclamaciones', methods=['GET'])
def get_claims():
    """Obtener reclamaciones"""
    try:
        service = get_municipal_service()
        consolidation_id = request.args.get('consolidation_id', type=int)
        municipio_id = request.args.get('municipio_id', type=int)
        
        claims = service.get_claims(consolidation_id, municipio_id)
        
        return jsonify({
            'success': True,
            'data': claims,
            'total': len(claims)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reclamaciones: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE DASHBOARD MUNICIPAL ====================

@municipal_api.route('/dashboard/<int:municipio_id>', methods=['GET'])
def get_municipal_dashboard(municipio_id):
    """Obtener datos para dashboard municipal"""
    try:
        service = get_municipal_service()
        
        # TODO: Obtener user_id de la sesión/token
        usuario_id = request.args.get('usuario_id', 1, type=int)  # Placeholder
        
        dashboard_data = service.get_municipal_dashboard_data(municipio_id, usuario_id)
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'municipio_id': municipio_id,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard municipal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE UTILIDADES ====================

@municipal_api.route('/tipos-eleccion', methods=['GET'])
def get_election_types():
    """Obtener tipos de elección disponibles"""
    try:
        # Tipos de elección comunes para municipios
        election_types = [
            {'id': 'alcalde', 'nombre': 'Alcalde Municipal', 'descripcion': 'Elección de Alcalde'},
            {'id': 'concejo', 'nombre': 'Concejo Municipal', 'descripcion': 'Elección de Concejales'},
            {'id': 'senado', 'nombre': 'Senado', 'descripcion': 'Elección de Senadores'},
            {'id': 'camara', 'nombre': 'Cámara de Representantes', 'descripcion': 'Elección de Representantes'},
            {'id': 'gobernador', 'nombre': 'Gobernador', 'descripcion': 'Elección de Gobernador'},
            {'id': 'asamblea', 'nombre': 'Asamblea Departamental', 'descripcion': 'Elección de Diputados'}
        ]
        
        return jsonify({
            'success': True,
            'data': election_types,
            'total': len(election_types)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de elección: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@municipal_api.route('/estados-consolidacion', methods=['GET'])
def get_consolidation_states():
    """Obtener estados de consolidación disponibles"""
    try:
        states = [
            {'id': 'pendiente', 'nombre': 'Pendiente', 'descripcion': 'No iniciada', 'color': '#6c757d'},
            {'id': 'consolidando', 'nombre': 'En Proceso', 'descripcion': 'Consolidando E-14s', 'color': '#ffc107'},
            {'id': 'completado', 'nombre': 'Completado', 'descripcion': 'Consolidación terminada', 'color': '#28a745'},
            {'id': 'verificado', 'nombre': 'Verificado', 'descripcion': 'E-24 verificado', 'color': '#007bff'}
        ]
        
        return jsonify({
            'success': True,
            'data': states,
            'total': len(states)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estados: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MANEJO DE ERRORES ====================

@municipal_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@municipal_api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Método no permitido'}), 405

@municipal_api.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno del servidor: {error}")
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500