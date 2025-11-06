"""
Módulo Reportes - Rutas y Endpoints
Generación y exportación de reportes del sistema
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import ReportService
from core.permissions import Permission
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/electoral-summary', methods=['GET'])
@jwt_required()
def get_electoral_summary():
    """Obtener resumen electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        process_id = request.args.get('process_id', type=int)
        election_type_id = request.args.get('election_type_id', type=int)
        
        summary = service.generate_electoral_summary(process_id, election_type_id)
        return jsonify({'success': True, 'data': summary})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/candidate-results', methods=['GET'])
@jwt_required()
def get_candidate_results_report():
    """Obtener reporte de resultados de candidatos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        party_id = request.args.get('party_id', type=int)
        top_n = request.args.get('top_n', 10, type=int)
        
        report = service.generate_candidate_results_report(election_type_id, party_id, top_n)
        return jsonify({'success': True, 'data': report})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/party-performance', methods=['GET'])
@jwt_required()
def get_party_performance():
    """Obtener reporte de desempeño por partido"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        
        report = service.generate_party_performance_report(election_type_id)
        return jsonify({'success': True, 'data': report})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/geographic-analysis', methods=['GET'])
@jwt_required()
def get_geographic_analysis():
    """Obtener análisis geográfico de resultados"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        candidate_id = request.args.get('candidate_id', type=int)
        
        analysis = service.generate_geographic_analysis(election_type_id, candidate_id)
        return jsonify({'success': True, 'data': analysis})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/participation-stats', methods=['GET'])
@jwt_required()
def get_participation_stats():
    """Obtener estadísticas de participación"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        process_id = request.args.get('process_id', type=int)
        
        stats = service.generate_participation_stats(process_id)
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/system-audit', methods=['GET'])
@jwt_required()
def get_system_audit():
    """Obtener reporte de auditoría del sistema"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        audit = service.generate_system_audit_report(start_date, end_date)
        return jsonify({'success': True, 'data': audit})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/export/excel', methods=['POST'])
@jwt_required()
def export_to_excel():
    """Exportar reporte a Excel"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_EXPORT.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data or 'report_type' not in data:
            return jsonify({'error': 'Report type required'}), 400
        
        service = ReportService(current_app.db_manager)
        
        excel_file = service.export_report_to_excel(
            data['report_type'],
            data.get('filters', {}),
            user_id
        )
        
        if not excel_file:
            return jsonify({'error': 'Failed to generate Excel file'}), 500
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=f"reporte_{data['report_type']}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/export/pdf', methods=['POST'])
@jwt_required()
def export_to_pdf():
    """Exportar reporte a PDF"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_EXPORT.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data or 'report_type' not in data:
            return jsonify({'error': 'Report type required'}), 400
        
        service = ReportService(current_app.db_manager)
        
        pdf_file = service.export_report_to_pdf(
            data['report_type'],
            data.get('filters', {}),
            user_id
        )
        
        if not pdf_file:
            return jsonify({'error': 'Failed to generate PDF file'}), 500
        
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=f"reporte_{data['report_type']}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/scheduled', methods=['GET'])
@jwt_required()
def get_scheduled_reports():
    """Obtener reportes programados"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        scheduled = service.get_scheduled_reports(user_id)
        
        return jsonify({'success': True, 'data': scheduled})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/scheduled', methods=['POST'])
@jwt_required()
def create_scheduled_report():
    """Crear reporte programado"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_GENERATE.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        service = ReportService(current_app.db_manager)
        schedule_id = service.create_scheduled_report(data, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Scheduled report created successfully',
            'schedule_id': schedule_id
        }), 201
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@reports_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Obtener plantillas de reportes disponibles"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.REPORTS_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = ReportService(current_app.db_manager)
        templates = service.get_report_templates()
        
        return jsonify({'success': True, 'data': templates})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)