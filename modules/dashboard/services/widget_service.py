"""
Servicio de Widgets para Dashboard
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

class WidgetService:
    """Servicio especializado para widgets del dashboard"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def get_widget_data(self, widget_type: str, user_id: int, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtener datos para un widget específico"""
        try:
            if params is None:
                params = {}
            
            # Importar el servicio principal para reutilizar métodos
            from .dashboard_service import DashboardService
            dashboard_service = DashboardService(self.db_path)
            
            if widget_type == 'electoral_progress':
                return dashboard_service.get_electoral_progress_widget(
                    process_id=params.get('process_id')
                )
            
            elif widget_type == 'candidate_ranking':
                return dashboard_service.get_candidate_ranking_widget(
                    election_type_id=params.get('election_type_id'),
                    limit=params.get('limit', 5)
                )
            
            elif widget_type == 'party_distribution':
                return dashboard_service.get_party_distribution_widget(
                    election_type_id=params.get('election_type_id')
                )
            
            elif widget_type == 'geographic_map':
                return dashboard_service.get_geographic_map_widget(
                    election_type_id=params.get('election_type_id'),
                    metric=params.get('metric', 'participation')
                )
            
            elif widget_type == 'real_time_stats':
                return dashboard_service.get_real_time_stats_widget()
            
            elif widget_type == 'user_activity':
                return dashboard_service.get_user_activity_widget(
                    time_range=params.get('time_range', '24h')
                )
            
            elif widget_type == 'alerts':
                return dashboard_service.get_alerts_widget(
                    severity=params.get('severity', 'all'),
                    limit=params.get('limit', 10)
                )
            
            elif widget_type == 'performance_metrics':
                return dashboard_service.get_performance_metrics_widget()
            
            else:
                return {
                    'error': f'Tipo de widget no soportado: {widget_type}',
                    'available_widgets': self.get_available_widgets()
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo datos del widget {widget_type}: {e}")
            return {
                'error': f'Error obteniendo datos del widget: {str(e)}',
                'widget_type': widget_type
            }
    
    def get_available_widgets(self) -> List[Dict[str, Any]]:
        """Obtener lista de widgets disponibles"""
        return [
            {
                'type': 'electoral_progress',
                'name': 'Progreso Electoral',
                'description': 'Muestra el progreso de recolección de datos electorales',
                'category': 'electoral',
                'parameters': ['process_id']
            },
            {
                'type': 'candidate_ranking',
                'name': 'Ranking de Candidatos',
                'description': 'Top candidatos por número de votos',
                'category': 'electoral',
                'parameters': ['election_type_id', 'limit']
            },
            {
                'type': 'party_distribution',
                'name': 'Distribución por Partido',
                'description': 'Distribución de votos por partido político',
                'category': 'electoral',
                'parameters': ['election_type_id']
            },
            {
                'type': 'geographic_map',
                'name': 'Mapa Geográfico',
                'description': 'Visualización geográfica de resultados',
                'category': 'geographic',
                'parameters': ['election_type_id', 'metric']
            },
            {
                'type': 'real_time_stats',
                'name': 'Estadísticas en Tiempo Real',
                'description': 'Métricas del sistema en tiempo real',
                'category': 'system',
                'parameters': []
            },
            {
                'type': 'user_activity',
                'name': 'Actividad de Usuarios',
                'description': 'Actividad y uso del sistema por usuarios',
                'category': 'system',
                'parameters': ['time_range']
            },
            {
                'type': 'alerts',
                'name': 'Alertas del Sistema',
                'description': 'Alertas y notificaciones importantes',
                'category': 'system',
                'parameters': ['severity', 'limit']
            },
            {
                'type': 'performance_metrics',
                'name': 'Métricas de Rendimiento',
                'description': 'Métricas de rendimiento del sistema',
                'category': 'system',
                'parameters': []
            }
        ]
    
    def get_widget_categories(self) -> List[Dict[str, Any]]:
        """Obtener categorías de widgets"""
        return [
            {
                'category': 'electoral',
                'name': 'Electoral',
                'description': 'Widgets relacionados con datos electorales',
                'icon': 'ballot'
            },
            {
                'category': 'geographic',
                'name': 'Geográfico',
                'description': 'Widgets con visualización geográfica',
                'icon': 'map'
            },
            {
                'category': 'system',
                'name': 'Sistema',
                'description': 'Widgets de monitoreo del sistema',
                'icon': 'monitor'
            }
        ]
    
    def validate_widget_params(self, widget_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validar parámetros de widget"""
        try:
            widgets = {w['type']: w for w in self.get_available_widgets()}
            
            if widget_type not in widgets:
                return {
                    'valid': False,
                    'error': f'Tipo de widget no válido: {widget_type}'
                }
            
            widget_info = widgets[widget_type]
            required_params = widget_info.get('parameters', [])
            
            # Por ahora, todos los parámetros son opcionales
            # En el futuro se pueden agregar validaciones más específicas
            
            return {
                'valid': True,
                'widget_type': widget_type,
                'validated_params': params
            }
            
        except Exception as e:
            self.logger.error(f"Error validando parámetros del widget: {e}")
            return {
                'valid': False,
                'error': f'Error validando parámetros: {str(e)}'
            }
    
    def get_widget_refresh_intervals(self) -> Dict[str, int]:
        """Obtener intervalos de actualización recomendados por widget (en segundos)"""
        return {
            'electoral_progress': 60,      # 1 minuto
            'candidate_ranking': 120,      # 2 minutos
            'party_distribution': 300,     # 5 minutos
            'geographic_map': 300,         # 5 minutos
            'real_time_stats': 30,         # 30 segundos
            'user_activity': 60,           # 1 minuto
            'alerts': 30,                  # 30 segundos
            'performance_metrics': 60      # 1 minuto
        }
    
    def get_widget_size_recommendations(self) -> Dict[str, Dict[str, int]]:
        """Obtener recomendaciones de tamaño por widget"""
        return {
            'electoral_progress': {'min_w': 6, 'min_h': 4, 'default_w': 8, 'default_h': 4},
            'candidate_ranking': {'min_w': 4, 'min_h': 4, 'default_w': 6, 'default_h': 4},
            'party_distribution': {'min_w': 4, 'min_h': 4, 'default_w': 6, 'default_h': 4},
            'geographic_map': {'min_w': 6, 'min_h': 6, 'default_w': 8, 'default_h': 6},
            'real_time_stats': {'min_w': 4, 'min_h': 3, 'default_w': 6, 'default_h': 3},
            'user_activity': {'min_w': 4, 'min_h': 4, 'default_w': 6, 'default_h': 4},
            'alerts': {'min_w': 4, 'min_h': 3, 'default_w': 6, 'default_h': 4},
            'performance_metrics': {'min_w': 6, 'min_h': 4, 'default_w': 8, 'default_h': 4}
        }