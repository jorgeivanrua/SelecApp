"""
Rutas del módulo de dashboard
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime

from .services import DashboardService, WidgetService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# Instancias de servicios
dashboard_service = DashboardService()
widget_service = WidgetService()

# ==================== ENDPOINTS PRINCIPALES ====================

@dashboard_bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """Obtener vista general del dashboard"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: Obtener del token
        
        overview = dashboard_service.get_dashboard_overview(user_id)
        
        return jsonify({
            'success': True,
            'data': overview
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo vista general del dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE WIDGETS ====================

@dashboard_bp.route('/widgets/electoral-progress', methods=['GET'])
def get_electoral_progress_widget():
    """Widget de progreso electoral"""
    try:
        process_id = request.args.get('process_id', type=int)
        
        widget_data = dashboard_service.get_electoral_progress_widget(process_id)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de progreso electoral: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/candidate-ranking', methods=['GET'])
def get_candidate_ranking_widget():
    """Widget de ranking de candidatos"""
    try:
        election_type_id = request.args.get('election_type_id', type=int)
        limit = request.args.get('limit', 5, type=int)
        
        widget_data = dashboard_service.get_candidate_ranking_widget(election_type_id, limit)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de ranking de candidatos: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/party-distribution', methods=['GET'])
def get_party_distribution_widget():
    """Widget de distribución por partido"""
    try:
        election_type_id = request.args.get('election_type_id', type=int)
        
        widget_data = dashboard_service.get_party_distribution_widget(election_type_id)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de distribución por partido: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/geographic-map', methods=['GET'])
def get_geographic_map_widget():
    """Widget de mapa geográfico"""
    try:
        election_type_id = request.args.get('election_type_id', type=int)
        metric = request.args.get('metric', 'participation')
        
        widget_data = dashboard_service.get_geographic_map_widget(election_type_id, metric)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de mapa geográfico: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/real-time-stats', methods=['GET'])
def get_real_time_stats_widget():
    """Widget de estadísticas en tiempo real"""
    try:
        widget_data = dashboard_service.get_real_time_stats_widget()
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de estadísticas en tiempo real: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/user-activity', methods=['GET'])
def get_user_activity_widget():
    """Widget de actividad de usuarios"""
    try:
        time_range = request.args.get('time_range', '24h')
        
        widget_data = dashboard_service.get_user_activity_widget(time_range)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de actividad de usuarios: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/alerts', methods=['GET'])
def get_alerts_widget():
    """Widget de alertas del sistema"""
    try:
        severity = request.args.get('severity', 'all')
        limit = request.args.get('limit', 10, type=int)
        
        widget_data = dashboard_service.get_alerts_widget(severity, limit)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de alertas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/performance-metrics', methods=['GET'])
def get_performance_metrics_widget():
    """Widget de métricas de rendimiento"""
    try:
        widget_data = dashboard_service.get_performance_metrics_widget()
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widget de métricas de rendimiento: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINT GENÉRICO DE WIDGETS ====================

@dashboard_bp.route('/widgets/<widget_type>', methods=['GET'])
def get_widget_data(widget_type):
    """Endpoint genérico para obtener datos de cualquier widget"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        # Obtener parámetros de la query string
        params = {}
        for key, value in request.args.items():
            if key != 'user_id':
                # Intentar convertir a int si es posible
                try:
                    params[key] = int(value)
                except ValueError:
                    params[key] = value
        
        widget_data = widget_service.get_widget_data(widget_type, user_id, params)
        
        return jsonify({
            'success': True,
            'data': widget_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos del widget {widget_type}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE CONFIGURACIÓN ====================

@dashboard_bp.route('/config', methods=['GET'])
def get_dashboard_config():
    """Obtener configuración del dashboard del usuario"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # TODO: Obtener del token
        
        config = dashboard_service.get_user_dashboard_config(user_id)
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración del dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/config', methods=['POST'])
def save_dashboard_config():
    """Guardar configuración del dashboard del usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        user_id = data.get('user_id', 1)  # TODO: Obtener del token
        config = data.get('config', {})
        
        success = dashboard_service.save_user_dashboard_config(user_id, config)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Configuración del dashboard guardada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error guardando configuración'
            }), 500
        
    except Exception as e:
        logger.error(f"Error guardando configuración del dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE INFORMACIÓN ====================

@dashboard_bp.route('/widgets/available', methods=['GET'])
def get_available_widgets():
    """Obtener lista de widgets disponibles"""
    try:
        widgets = widget_service.get_available_widgets()
        
        return jsonify({
            'success': True,
            'data': widgets,
            'total': len(widgets)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo widgets disponibles: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/categories', methods=['GET'])
def get_widget_categories():
    """Obtener categorías de widgets"""
    try:
        categories = widget_service.get_widget_categories()
        
        return jsonify({
            'success': True,
            'data': categories,
            'total': len(categories)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías de widgets: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@dashboard_bp.route('/widgets/refresh-intervals', methods=['GET'])
def get_widget_refresh_intervals():
    """Obtener intervalos de actualización recomendados"""
    try:
        intervals = widget_service.get_widget_refresh_intervals()
        
        return jsonify({
            'success': True,
            'data': intervals
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo intervalos de actualización: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== ENDPOINTS DE EXPORTACIÓN ====================

@dashboard_bp.route('/export', methods=['POST'])
def export_dashboard():
    """Exportar dashboard como imagen o PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        user_id = data.get('user_id', 1)  # TODO: Obtener del token
        format_type = data.get('format', 'png')
        widgets = data.get('widgets', [])
        options = data.get('options', {})
        
        export_filename = dashboard_service.export_dashboard(user_id, format_type, widgets, options)
        
        if export_filename:
            return jsonify({
                'success': True,
                'message': 'Dashboard exportado exitosamente',
                'filename': export_filename,
                'download_url': f'/api/dashboard/download/{export_filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error exportando dashboard'
            }), 500
        
    except Exception as e:
        logger.error(f"Error exportando dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

# ==================== MANEJO DE ERRORES ====================

@dashboard_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@dashboard_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Método no permitido'
    }), 405

@dashboard_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500