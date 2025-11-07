#!/usr/bin/env python3
"""
APIs Administrativas Extendidas
Endpoints para gestión completa de candidatos, partidos, coaliciones y configuración
"""

from flask import Blueprint, request, jsonify, current_app
from services.admin_panel_service import AdminPanelService
import logging
from datetime import datetime
import os

admin_api = Blueprint('admin_api', __name__)
logger = logging.getLogger(__name__)

def get_admin_service():
    """Obtener instancia del servicio administrativo"""
    return AdminPanelService()

# ==================== ENDPOINTS DE CANDIDATOS ====================

@admin_api.route('/candidatos', methods=['GET'])
def get_all_candidates():
    """Obtener todos los candidatos con filtros"""
    try:
        service = get_admin_service()
        
        # Obtener filtros de query parameters
        filters = {}
        if request.args.get('partido_id'):
            filters['partido_id'] = int(request.args.get('partido_id'))
        if request.args.get('cargo_id'):
            filters['cargo_id'] = int(request.args.get('cargo_id'))
        if request.args.get('municipio_id'):
            filters['municipio_id'] = int(request.args.get('municipio_id'))
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        candidates = service.get_all_candidates(filters if filters else None)
        
        return jsonify({
            'success': True,
            'data': candidates,
            'total': len(candidates),
            'filters_applied': filters
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo candidatos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/candidatos', methods=['POST'])
def create_candidate():
    """Crear nuevo candidato"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        candidate_id = service.create_candidate(data)
        
        return jsonify({
            'success': True,
            'message': 'Candidato creado exitosamente',
            'candidate_id': candidate_id,
            'data': data
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando candidato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/candidatos/<int:candidate_id>', methods=['PUT'])
def update_candidate(candidate_id):
    """Actualizar candidato existente"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        success = service.update_candidate(candidate_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Candidato actualizado exitosamente',
                'candidate_id': candidate_id
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el candidato'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando candidato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/candidatos/<int:candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    """Eliminar candidato"""
    try:
        service = get_admin_service()
        success = service.delete_candidate(candidate_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Candidato eliminado exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo eliminar el candidato'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error eliminando candidato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/candidatos/bulk-import', methods=['POST'])
def bulk_import_candidates():
    """Importar candidatos desde CSV"""
    try:
        service = get_admin_service()
        
        # Verificar si se envió un archivo
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'El archivo debe ser CSV'}), 400
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/candidates_import_{datetime.now().timestamp()}.csv"
        file.save(temp_path)
        
        # Verificar si es solo validación
        validate_only = request.form.get('validate_only', 'false').lower() == 'true'
        
        try:
            results = service.bulk_import_candidates(temp_path, validate_only)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'message': 'Importación completada' if not validate_only else 'Validación completada',
                'results': results
            })
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error en importación masiva: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE PARTIDOS ====================

@admin_api.route('/partidos', methods=['GET'])
def get_all_parties():
    """Obtener todos los partidos políticos"""
    try:
        service = get_admin_service()
        parties = service.get_all_parties()
        
        return jsonify({
            'success': True,
            'data': parties,
            'total': len(parties)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo partidos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/partidos', methods=['POST'])
def create_party():
    """Crear nuevo partido político"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        party_id = service.create_party(data)
        
        return jsonify({
            'success': True,
            'message': 'Partido creado exitosamente',
            'party_id': party_id,
            'data': data
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando partido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE COALICIONES ====================

@admin_api.route('/coaliciones', methods=['GET'])
def get_all_coalitions():
    """Obtener todas las coaliciones"""
    try:
        service = get_admin_service()
        coalitions = service.get_all_coalitions()
        
        return jsonify({
            'success': True,
            'data': coalitions,
            'total': len(coalitions)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo coaliciones: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/coaliciones', methods=['POST'])
def create_coalition():
    """Crear nueva coalición"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        party_ids = data.pop('party_ids', [])
        coalition_id = service.create_coalition(data, party_ids)
        
        return jsonify({
            'success': True,
            'message': 'Coalición creada exitosamente',
            'coalition_id': coalition_id,
            'data': data
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando coalición: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE JORNADAS ELECTORALES ====================

@admin_api.route('/jornadas-electorales', methods=['POST'])
def create_electoral_journey():
    """Crear jornada electoral con múltiples elecciones"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        election_types = data.pop('election_types', [])
        if not election_types:
            return jsonify({'success': False, 'error': 'Debe especificar al menos un tipo de elección'}), 400
        
        journey_id = service.create_electoral_journey(data, election_types)
        
        return jsonify({
            'success': True,
            'message': 'Jornada electoral creada exitosamente',
            'journey_id': journey_id,
            'election_types_count': len(election_types)
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando jornada electoral: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE CONFIGURACIÓN ====================

@admin_api.route('/configuracion', methods=['GET'])
def get_system_configuration():
    """Obtener configuración del sistema"""
    try:
        service = get_admin_service()
        category = request.args.get('category')
        
        config = service.get_system_configuration(category)
        
        return jsonify({
            'success': True,
            'data': config,
            'category': category
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/configuracion', methods=['PUT'])
def update_system_configuration():
    """Actualizar configuración del sistema"""
    try:
        service = get_admin_service()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        # TODO: Obtener user_id de la sesión/token
        user_id = 1  # Placeholder
        
        success = service.update_system_configuration(data, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Configuración actualizada exitosamente',
                'updated_keys': list(data.keys())
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar la configuración'}), 400
        
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE ESTADÍSTICAS Y REPORTES ====================

@admin_api.route('/estadisticas', methods=['GET'])
def get_system_statistics():
    """Obtener estadísticas del sistema"""
    try:
        service = get_admin_service()
        stats = service.get_system_statistics()
        
        return jsonify({
            'success': True,
            'data': stats,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/reportes/<report_type>', methods=['GET'])
def generate_admin_report(report_type):
    """Generar reportes administrativos"""
    try:
        service = get_admin_service()
        
        # Obtener filtros de query parameters
        filters = {}
        for key, value in request.args.items():
            if key != 'format':
                filters[key] = value
        
        report = service.generate_admin_report(report_type, filters if filters else None)
        
        # Determinar formato de respuesta
        response_format = request.args.get('format', 'json')
        
        if response_format == 'json':
            return jsonify({
                'success': True,
                'report': report
            })
        else:
            return jsonify({'success': False, 'error': f'Formato no soportado: {response_format}'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE DATOS MAESTROS ====================

@admin_api.route('/cargos', methods=['GET'])
def get_electoral_positions():
    """Obtener cargos electorales"""
    try:
        service = get_admin_service()
        conn = service.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cargos_electorales WHERE activo = 1 ORDER BY nivel, nombre")
        results = cursor.fetchall()
        conn.close()
        
        positions = [dict(row) for row in results]
        
        return jsonify({
            'success': True,
            'data': positions,
            'total': len(positions)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo cargos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/municipios', methods=['GET'])
def get_municipalities():
    """Obtener municipios"""
    try:
        service = get_admin_service()
        conn = service.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM municipios WHERE activo = 1 ORDER BY nombre")
        results = cursor.fetchall()
        conn.close()
        
        municipalities = [dict(row) for row in results]
        
        return jsonify({
            'success': True,
            'data': municipalities,
            'total': len(municipalities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo municipios: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE IMPORTACIÓN EXCEL ====================

@admin_api.route('/import/excel/validate', methods=['POST'])
def validate_excel_file():
    """Validar estructura del archivo Excel antes de importar"""
    try:
        from services.excel_import_service import ExcelImportService
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'error': 'El archivo debe ser Excel (.xlsx o .xls)'}), 400
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/excel_validation_{datetime.now().timestamp()}.xlsx"
        file.save(temp_path)
        
        try:
            service = ExcelImportService()
            validation_results = service.validate_excel_structure(temp_path)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'validation': validation_results
            })
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error validando archivo Excel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/import/excel/complete', methods=['POST'])
def import_complete_excel():
    """Importar todos los datos desde archivo Excel"""
    try:
        from services.excel_import_service import ExcelImportService
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'error': 'El archivo debe ser Excel (.xlsx o .xls)'}), 400
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/excel_import_{datetime.now().timestamp()}.xlsx"
        file.save(temp_path)
        
        try:
            service = ExcelImportService()
            results = service.import_all_from_excel(temp_path)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'message': 'Importación completada',
                'results': results
            })
            
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error importando archivo Excel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/import/excel/parties', methods=['POST'])
def import_parties_excel():
    """Importar solo partidos desde Excel"""
    try:
        from services.excel_import_service import ExcelImportService
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        sheet_name = request.form.get('sheet_name', 'Partidos')
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/parties_import_{datetime.now().timestamp()}.xlsx"
        file.save(temp_path)
        
        try:
            service = ExcelImportService()
            results = service.import_parties_from_excel(temp_path, sheet_name)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'message': 'Importación de partidos completada',
                'results': results
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error importando partidos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/import/excel/candidates', methods=['POST'])
def import_candidates_excel():
    """Importar solo candidatos desde Excel"""
    try:
        from services.excel_import_service import ExcelImportService
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        sheet_name = request.form.get('sheet_name', 'Candidatos')
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/candidates_import_{datetime.now().timestamp()}.xlsx"
        file.save(temp_path)
        
        try:
            service = ExcelImportService()
            results = service.import_candidates_from_excel(temp_path, sheet_name)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'message': 'Importación de candidatos completada',
                'results': results
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error importando candidatos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE PRIORIZACIÓN ====================

@admin_api.route('/prioridades/configuraciones', methods=['GET'])
def get_priority_configurations():
    """Obtener todas las configuraciones de prioridades"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        configurations = service.get_all_configurations()
        
        return jsonify({
            'success': True,
            'data': configurations,
            'total': len(configurations)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuraciones de prioridades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/configuraciones', methods=['POST'])
def create_priority_configuration():
    """Crear nueva configuración de prioridades"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        # TODO: Obtener user_id de la sesión/token
        user_id = 1  # Placeholder
        
        config_id = service.create_configuration(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Configuración de prioridades creada exitosamente',
            'config_id': config_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando configuración de prioridades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/configuraciones/<int:config_id>/activar', methods=['POST'])
def activate_priority_configuration(config_id):
    """Activar una configuración de prioridades"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        success = service.activate_configuration(config_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Configuración activada exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo activar la configuración'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error activando configuración: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/configuracion-activa', methods=['GET'])
def get_active_priority_configuration():
    """Obtener la configuración de prioridades activa"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config = service.get_active_configuration()
        
        if config:
            return jsonify({
                'success': True,
                'data': config
            })
        else:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No hay configuración activa'
            })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración activa: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/partidos', methods=['GET'])
def get_party_priorities():
    """Obtener prioridades de partidos"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        priorities = service.get_party_priorities(config_id)
        
        return jsonify({
            'success': True,
            'data': priorities,
            'total': len(priorities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo prioridades de partidos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/partidos/establecer', methods=['POST'])
def set_party_priority():
    """Establecer prioridad de un partido"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['config_id', 'partido_id', 'prioridad']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        success = service.set_party_priority(
            data['config_id'],
            data['partido_id'],
            data['prioridad'],
            data.get('observaciones')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prioridad de partido establecida exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo establecer la prioridad'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error estableciendo prioridad de partido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/partidos/masivo', methods=['POST'])
def bulk_set_party_priorities():
    """Establecer prioridades de múltiples partidos"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data or 'config_id' not in data or 'priorities' not in data:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        results = service.bulk_set_party_priorities(data['config_id'], data['priorities'])
        
        return jsonify({
            'success': True,
            'message': 'Prioridades establecidas',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error en asignación masiva de prioridades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/candidatos', methods=['GET'])
def get_candidate_priorities():
    """Obtener prioridades de candidatos"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        # Obtener filtros
        filters = {}
        if request.args.get('partido_id'):
            filters['partido_id'] = int(request.args.get('partido_id'))
        if request.args.get('cargo_id'):
            filters['cargo_id'] = int(request.args.get('cargo_id'))
        if request.args.get('prioridad'):
            filters['prioridad'] = int(request.args.get('prioridad'))
        
        priorities = service.get_candidate_priorities(config_id, filters if filters else None)
        
        return jsonify({
            'success': True,
            'data': priorities,
            'total': len(priorities),
            'filters_applied': filters
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo prioridades de candidatos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/candidatos/establecer', methods=['POST'])
def set_candidate_priority():
    """Establecer prioridad de un candidato"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['config_id', 'candidato_id', 'prioridad']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        success = service.set_candidate_priority(
            data['config_id'],
            data['candidato_id'],
            data['prioridad'],
            data.get('observaciones')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prioridad de candidato establecida exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo establecer la prioridad'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error estableciendo prioridad de candidato: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/procesos', methods=['GET'])
def get_process_priorities():
    """Obtener prioridades de procesos electorales"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        priorities = service.get_process_priorities(config_id)
        
        return jsonify({
            'success': True,
            'data': priorities,
            'total': len(priorities)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo prioridades de procesos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/procesos/establecer', methods=['POST'])
def set_process_priority():
    """Establecer prioridad de un proceso electoral"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['config_id', 'proceso_id', 'prioridad']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        success = service.set_process_priority(
            data['config_id'],
            data['proceso_id'],
            data['prioridad'],
            data.get('observaciones')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Prioridad de proceso establecida exitosamente'
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo establecer la prioridad'}), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error estableciendo prioridad de proceso: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/metas', methods=['GET'])
def get_collection_goals():
    """Obtener metas de recolección"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        goals = service.get_collection_goals(config_id)
        
        return jsonify({
            'success': True,
            'data': goals,
            'total': len(goals)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo metas de recolección: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/metas', methods=['POST'])
def set_collection_goal():
    """Establecer meta de recolección"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se enviaron datos'}), 400
        
        required_fields = ['config_id', 'tipo_entidad', 'entidad_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
        
        goal_id = service.set_collection_goal(data['config_id'], data)
        
        return jsonify({
            'success': True,
            'message': 'Meta de recolección establecida exitosamente',
            'goal_id': goal_id
        })
        
    except Exception as e:
        logger.error(f"Error estableciendo meta de recolección: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/resumen', methods=['GET'])
def get_priority_summary():
    """Obtener resumen de prioridades"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        summary = service.get_priority_summary(config_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de prioridades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/prioridades/alta-prioridad', methods=['GET'])
def get_high_priority_entities():
    """Obtener entidades de alta prioridad"""
    try:
        from services.priority_service import PriorityService
        
        service = PriorityService()
        config_id = request.args.get('config_id', type=int)
        
        high_priority = service.get_high_priority_entities(config_id)
        
        return jsonify({
            'success': True,
            'data': high_priority
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo entidades de alta prioridad: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ENDPOINTS DE VALIDACIÓN ====================

@admin_api.route('/validar/candidato-cedula/<cedula>', methods=['GET'])
def validate_candidate_cedula(cedula):
    """Validar si una cédula ya está registrada"""
    try:
        service = get_admin_service()
        conn = service.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nombre_completo FROM candidatos WHERE cedula = ? AND activo = 1", (cedula,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'exists': True,
                'candidate': dict(result),
                'message': f'La cédula {cedula} ya está registrada'
            })
        else:
            return jsonify({
                'success': True,
                'exists': False,
                'message': f'La cédula {cedula} está disponible'
            })
        
    except Exception as e:
        logger.error(f"Error validando cédula: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api.route('/validar/partido-nombre/<nombre>', methods=['GET'])
def validate_party_name(nombre):
    """Validar si un nombre de partido ya existe"""
    try:
        service = get_admin_service()
        conn = service.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, sigla FROM partidos_politicos WHERE nombre = ? AND activo = 1", (nombre,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'exists': True,
                'party': dict(result),
                'message': f'El nombre "{nombre}" ya está registrado'
            })
        else:
            return jsonify({
                'success': True,
                'exists': False,
                'message': f'El nombre "{nombre}" está disponible'
            })
        
    except Exception as e:
        logger.error(f"Error validando nombre de partido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MANEJO DE ERRORES ====================

@admin_api.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint no encontrado'}), 404

@admin_api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Método no permitido'}), 405

@admin_api.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno del servidor: {error}")
    return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500