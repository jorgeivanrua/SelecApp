"""
Rutas del módulo de reportes
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime

from .services import ReportService, ExportService
from .models import ReportFilter

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

# Instancias de servicios
report_service = ReportService()
export_service = ExportService()

# ==================== ENDPOINTS DE REPORTES PRINCIPALES ====================

@reports_bp.route('/electoral-summary', methods=['GET'])
def get_electoral_summary():
    """Obtener resumen electoral"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            process_id=request.args.get('process_id', type=int),
            election_type_id=request.args.get('election_type_id', type=int),
            top_n=request.args.get('top_n', 10, type=int)
        )
        
        summary = report_service.generate_electoral_summary(filters)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen electoral: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/candidate-results', methods=['GET'])
def get_candidate_results_report():
    """Obtener reporte de resultados de candidatos"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            election_type_id=request.args.get('election_type_id', type=int),
            party_id=request.args.get('party_id', type=int),
            top_n=request.args.get('top_n', 10, type=int)
        )
        
        report = report_service.generate_candidate_results_report(filters)
        
        return jsonify({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reporte de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/party-performance', methods=['GET'])
def get_party_performance():
    """Obtener reporte de desempeño por partido"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            election_type_id=request.args.get('election_type_id', type=int)
        )
        
        report = report_service.generate_party_performance_report(filters)
        
        return jsonify({
            'success': True,
            'data': report
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reporte de partidos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/geographic-analysis', methods=['GET'])
def get_geographic_analysis():
    """Obtener análisis geográfico de resultados"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            election_type_id=request.args.get('election_type_id', type=int),
            candidate_id=request.args.get('candidate_id', type=int),
            municipality_id=request.args.get('municipality_id', type=int)
        )
        
        analysis = report_service.generate_geographic_analysis(filters)
        
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo análisis geográfico: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/participation-stats', methods=['GET'])
def get_participation_stats():
    """Obtener estadísticas de participación"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            process_id=request.args.get('process_id', type=int)
        )
        
        stats = report_service.generate_participation_stats(filters)
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de participación: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/system-audit', methods=['GET'])
def get_system_audit():
    """Obtener reporte de auditoría del sistema"""
    try:
        # Crear filtros desde parámetros de consulta
        filters = ReportFilter(
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date')
        )
        
        audit = report_service.generate_system_audit_report(filters)
        
        return jsonify({
            'success': True,
            'data': audit
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reporte de auditoría: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE EXPORTACIÓN ====================

@reports_bp.route('/export', methods=['POST'])
def export_report():
    """Exportar reporte en formato especificado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['report_type', 'format']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        report_type = data['report_type']
        export_format = data['format']
        filters_data = data.get('filters', {})
        user_id = data.get('user_id', 1)  # TODO: Obtener del token de sesión
        
        # Crear filtros
        filters = ReportFilter(
            process_id=filters_data.get('process_id'),
            election_type_id=filters_data.get('election_type_id'),
            party_id=filters_data.get('party_id'),
            candidate_id=filters_data.get('candidate_id'),
            municipality_id=filters_data.get('municipality_id'),
            start_date=filters_data.get('start_date'),
            end_date=filters_data.get('end_date'),
            top_n=filters_data.get('top_n', 10)
        )
        
        # Generar datos del reporte
        report_data = None
        if report_type == 'electoral_summary':
            report_data = report_service.generate_electoral_summary(filters)
        elif report_type == 'candidate_results':
            report_data = report_service.generate_candidate_results_report(filters)
        elif report_type == 'party_performance':
            report_data = report_service.generate_party_performance_report(filters)
        elif report_type == 'geographic_analysis':
            report_data = report_service.generate_geographic_analysis(filters)
        elif report_type == 'participation_stats':
            report_data = report_service.generate_participation_stats(filters)
        elif report_type == 'system_audit':
            report_data = report_service.generate_system_audit_report(filters)
        else:
            return jsonify({
                'success': False,
                'error': f'Tipo de reporte no soportado: {report_type}'
            }), 400
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': 'Error generando datos del reporte'
            }), 500
        
        # Exportar según el formato
        exported_file = None
        mime_type = 'application/octet-stream'
        file_extension = '.txt'
        
        if export_format == 'csv':
            # Para CSV, extraer datos tabulares
            if 'candidates' in report_data:
                exported_file = export_service.export_to_csv(report_data['candidates'])
            elif 'parties' in report_data:
                exported_file = export_service.export_to_csv(report_data['parties'])
            elif 'municipalities' in report_data:
                exported_file = export_service.export_to_csv(report_data['municipalities'])
            else:
                exported_file = export_service.export_to_csv([report_data])
            mime_type = 'text/csv'
            file_extension = '.csv'
            
        elif export_format == 'json':
            exported_file = export_service.export_to_json(report_data)
            mime_type = 'application/json'
            file_extension = '.json'
            
        elif export_format == 'excel':
            exported_file = export_service.export_to_excel(report_data, report_type)
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_extension = '.xlsx'
            
        elif export_format == 'pdf':
            exported_file = export_service.export_to_pdf(report_data, report_type)
            mime_type = 'application/pdf'
            file_extension = '.pdf'
        
        else:
            return jsonify({
                'success': False,
                'error': f'Formato de exportación no soportado: {export_format}'
            }), 400
        
        if not exported_file:
            export_service.log_export(user_id, report_type, export_format, False)
            return jsonify({
                'success': False,
                'error': 'Error generando archivo de exportación'
            }), 500
        
        # Registrar exportación exitosa
        export_service.log_export(user_id, report_type, export_format, True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_{report_type}_{timestamp}{file_extension}"
        
        return send_file(
            exported_file,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )
        
    except Exception as e:
        logger.error(f"Error exportando reporte: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE REPORTES PROGRAMADOS ====================

@reports_bp.route('/scheduled', methods=['GET'])
def get_scheduled_reports():
    """Obtener reportes programados"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: Obtener del token
        
        scheduled = report_service.get_scheduled_reports(user_id)
        
        return jsonify({
            'success': True,
            'data': scheduled,
            'total': len(scheduled)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reportes programados: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/scheduled', methods=['POST'])
def create_scheduled_report():
    """Crear reporte programado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['name', 'report_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        user_id = data.get('user_id', 1)  # TODO: Obtener del token
        
        schedule_id = report_service.create_scheduled_report(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Reporte programado creado exitosamente',
            'schedule_id': schedule_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando reporte programado: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE INFORMACIÓN ====================

@reports_bp.route('/templates', methods=['GET'])
def get_report_templates():
    """Obtener plantillas de reportes disponibles"""
    try:
        templates = report_service.get_report_templates()
        
        return jsonify({
            'success': True,
            'data': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo plantillas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/export-formats', methods=['GET'])
def get_export_formats():
    """Obtener formatos de exportación disponibles"""
    try:
        formats = export_service.get_export_formats()
        
        return jsonify({
            'success': True,
            'data': formats,
            'total': len(formats)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo formatos de exportación: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@reports_bp.route('/export-history', methods=['GET'])
def get_export_history():
    """Obtener historial de exportaciones"""
    try:
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        history = export_service.get_export_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': history,
            'total': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de exportaciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@reports_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@reports_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@reports_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500