"""
Módulo Dashboard - Rutas y Endpoints
Dashboard principal y widgets del sistema
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import DashboardService
from core.permissions import Permission

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Obtener vista general del dashboard"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        overview = service.get_dashboard_overview(user_id)
        
        return jsonify({'success': True, 'data': overview})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/electoral-progress', methods=['GET'])
@jwt_required()
def get_electoral_progress_widget():
    """Widget de progreso electoral"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        process_id = request.args.get('process_id', type=int)
        widget_data = service.get_electoral_progress_widget(process_id)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/candidate-ranking', methods=['GET'])
@jwt_required()
def get_candidate_ranking_widget():
    """Widget de ranking de candidatos"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        limit = request.args.get('limit', 5, type=int)
        
        widget_data = service.get_candidate_ranking_widget(election_type_id, limit)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/party-distribution', methods=['GET'])
@jwt_required()
def get_party_distribution_widget():
    """Widget de distribución por partido"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        widget_data = service.get_party_distribution_widget(election_type_id)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/geographic-map', methods=['GET'])
@jwt_required()
def get_geographic_map_widget():
    """Widget de mapa geográfico"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        election_type_id = request.args.get('election_type_id', type=int)
        metric = request.args.get('metric', 'participation')  # participation, votes, etc.
        
        widget_data = service.get_geographic_map_widget(election_type_id, metric)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/real-time-stats', methods=['GET'])
@jwt_required()
def get_real_time_stats_widget():
    """Widget de estadísticas en tiempo real"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        widget_data = service.get_real_time_stats_widget()
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/user-activity', methods=['GET'])
@jwt_required()
def get_user_activity_widget():
    """Widget de actividad de usuarios"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        time_range = request.args.get('time_range', '24h')  # 24h, 7d, 30d
        widget_data = service.get_user_activity_widget(time_range)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/alerts', methods=['GET'])
@jwt_required()
def get_alerts_widget():
    """Widget de alertas del sistema"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        
        severity = request.args.get('severity', 'all')  # all, high, medium, low
        limit = request.args.get('limit', 10, type=int)
        
        widget_data = service.get_alerts_widget(severity, limit)
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/widgets/performance-metrics', methods=['GET'])
@jwt_required()
def get_performance_metrics_widget():
    """Widget de métricas de rendimiento"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        service = DashboardService(current_app.db_manager)
        widget_data = service.get_performance_metrics_widget()
        
        return jsonify({'success': True, 'data': widget_data})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/config', methods=['GET'])
@jwt_required()
def get_dashboard_config():
    """Obtener configuración del dashboard del usuario"""
    try:
        user_id = get_jwt_identity()
        service = DashboardService(current_app.db_manager)
        
        config = service.get_user_dashboard_config(user_id)
        return jsonify({'success': True, 'data': config})
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/config', methods=['POST'])
@jwt_required()
def save_dashboard_config():
    """Guardar configuración del dashboard del usuario"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        service = DashboardService(current_app.db_manager)
        success = service.save_user_dashboard_config(user_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Dashboard configuration saved successfully'
            })
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)

@dashboard_bp.route('/export', methods=['POST'])
@jwt_required()
def export_dashboard():
    """Exportar dashboard como imagen o PDF"""
    try:
        # Verificar permisos
        user_id = get_jwt_identity()
        if not current_app.permission_manager.has_permission(user_id, Permission.DASHBOARD_VIEW.value):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        if not data or 'format' not in data:
            return jsonify({'error': 'Export format required'}), 400
        
        service = DashboardService(current_app.db_manager)
        
        export_file = service.export_dashboard(
            user_id,
            data['format'],  # 'png', 'pdf'
            data.get('widgets', []),
            data.get('options', {})
        )
        
        if export_file:
            return jsonify({
                'success': True,
                'message': 'Dashboard exported successfully',
                'download_url': f'/api/dashboard/download/{export_file}'
            })
        else:
            return jsonify({'error': 'Failed to export dashboard'}), 500
        
    except Exception as e:
        return current_app.api_manager.handle_api_error(e)