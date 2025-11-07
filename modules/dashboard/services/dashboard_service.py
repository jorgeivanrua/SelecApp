"""
Servicio Principal de Dashboard
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ..models import (
    DashboardOverview, QuickStats, SystemStatus, RecentActivity,
    DashboardConfig, SystemAlert
)

class DashboardService:
    """Servicio principal para dashboard y widgets"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== DASHBOARD PRINCIPAL ====================
    
    def get_dashboard_overview(self, user_id: int) -> Dict[str, Any]:
        """Obtener vista general del dashboard"""
        try:
            # Obtener rol del usuario para personalizar dashboard
            user_role = self._get_user_role(user_id)
            
            overview = {
                'user_role': user_role,
                'last_updated': datetime.now().isoformat(),
                'quick_stats': self._get_quick_stats(),
                'recent_activity': self._get_recent_activity(user_id),
                'system_status': self._get_system_status(),
                'user_permissions': self._get_user_dashboard_permissions(user_id)
            }
            
            # Personalizar según el rol
            if user_role in ['super_admin', 'admin_departamental']:
                overview['admin_widgets'] = self._get_admin_widgets()
            elif user_role in ['testigo_mesa', 'digitador']:
                overview['operational_widgets'] = self._get_operational_widgets(user_id)
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vista general del dashboard: {e}")
            raise
    
    # ==================== WIDGETS PRINCIPALES ====================
    
    def get_electoral_progress_widget(self, process_id: Optional[int] = None) -> Dict[str, Any]:
        """Widget de progreso electoral"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Estadísticas de progreso
            cursor.execute("""
                SELECT 
                    estado_recoleccion,
                    COUNT(*) as count
                FROM mesas_electorales
                GROUP BY estado_recoleccion
            """)
            
            progress_result = cursor.fetchall()
            
            progress_data = {}
            total_mesas = 0
            
            for row in progress_result:
                estado = row['estado_recoleccion'] or 'sin_estado'
                count = row['count']
                progress_data[estado] = count
                total_mesas += count
            
            # Calcular porcentajes
            progress_percentages = {}
            for estado in progress_data:
                progress_percentages[estado] = round(
                    (progress_data[estado] / total_mesas * 100) if total_mesas > 0 else 0, 2
                )
            
            # Progreso por municipio
            municipality_progress = self._get_municipality_progress()
            
            # Tendencia temporal (simulada)
            time_series = self._get_progress_time_series()
            
            conn.close()
            
            return {
                'total_mesas': total_mesas,
                'progress_by_status': progress_data,
                'progress_percentages': progress_percentages,
                'municipality_progress': municipality_progress,
                'time_series': time_series,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de progreso electoral: {e}")
            raise
    
    def get_candidate_ranking_widget(self, election_type_id: Optional[int] = None, limit: int = 5) -> Dict[str, Any]:
        """Widget de ranking de candidatos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    c.nombre_completo,
                    c.numero_tarjeton,
                    c.party_siglas,
                    COALESCE(v.votos, 0) as total_votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1
            """
            
            params = []
            
            if election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(election_type_id)
            
            query += f" ORDER BY total_votos DESC LIMIT {limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            candidates = []
            for i, row in enumerate(results, 1):
                candidates.append({
                    'nombre': row['nombre_completo'],
                    'numero_tarjeton': row['numero_tarjeton'],
                    'partido_siglas': row['party_siglas'],
                    'total_votos': row['total_votos'],
                    'posicion': i
                })
            
            # Estadísticas adicionales
            total_votos = sum(c['total_votos'] for c in candidates)
            
            conn.close()
            
            return {
                'candidates': candidates,
                'total_votos_top': total_votos,
                'election_type_id': election_type_id,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de ranking de candidatos: {e}")
            raise
    
    def get_party_distribution_widget(self, election_type_id: Optional[int] = None) -> Dict[str, Any]:
        """Widget de distribución por partido"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    c.party_siglas,
                    COUNT(c.id) as total_candidatos,
                    COALESCE(SUM(v.votos), 0) as total_votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1 AND c.party_siglas IS NOT NULL
            """
            
            params = []
            
            if election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(election_type_id)
            
            query += """
                GROUP BY c.party_siglas
                HAVING total_candidatos > 0
                ORDER BY total_votos DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            parties = []
            for row in results:
                parties.append({
                    'siglas': row['party_siglas'],
                    'total_candidatos': row['total_candidatos'],
                    'total_votos': row['total_votos']
                })
            
            # Calcular porcentajes de distribución
            total_votos_all = sum(p['total_votos'] for p in parties)
            
            for party in parties:
                party['porcentaje_distribucion'] = round(
                    (party['total_votos'] / total_votos_all * 100) if total_votos_all > 0 else 0, 2
                )
            
            conn.close()
            
            return {
                'parties': parties,
                'total_votos_all': total_votos_all,
                'total_parties': len(parties),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de distribución por partido: {e}")
            raise
    
    def get_geographic_map_widget(self, election_type_id: Optional[int] = None, metric: str = 'participation') -> Dict[str, Any]:
        """Widget de mapa geográfico"""
        try:
            if metric == 'participation':
                data = self._get_participation_by_municipality()
            elif metric == 'votes':
                data = self._get_votes_by_municipality(election_type_id)
            else:
                data = []
            
            # Agregar coordenadas simuladas para el mapa
            for item in data:
                item['coordinates'] = self._get_municipality_coordinates(item['municipio'])
            
            return {
                'metric': metric,
                'data': data,
                'map_center': {'lat': 1.6143, 'lng': -75.6062},  # Centro de Caquetá
                'zoom_level': 8,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de mapa geográfico: {e}")
            raise
    
    def get_real_time_stats_widget(self) -> Dict[str, Any]:
        """Widget de estadísticas en tiempo real"""
        try:
            current_time = datetime.now()
            
            stats = {
                'current_time': current_time.isoformat(),
                'active_users': self._get_active_users_count(),
                'mesas_being_processed': self._get_processing_mesas_count(),
                'votes_per_minute': self._get_votes_per_minute_simulation(),
                'system_load': {
                    'cpu_usage': round(random.uniform(30, 70), 1),
                    'memory_usage': round(random.uniform(40, 80), 1),
                    'disk_usage': round(random.uniform(20, 50), 1),
                    'network_io': round(random.uniform(0.5, 2.0), 1)
                },
                'recent_activities': self._get_recent_system_activities()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de estadísticas en tiempo real: {e}")
            raise
    
    def get_user_activity_widget(self, time_range: str = '24h') -> Dict[str, Any]:
        """Widget de actividad de usuarios"""
        try:
            # Convertir time_range a horas
            hours_map = {'24h': 24, '7d': 168, '30d': 720}
            hours = hours_map.get(time_range, 24)
            
            # Actividad por rol
            role_activity = self._get_activity_by_role(hours)
            
            # Usuarios más activos
            top_users = self._get_top_active_users(hours, limit=5)
            
            # Actividad por hora (últimas 24 horas)
            hourly_activity = self._get_hourly_activity_simulation()
            
            return {
                'time_range': time_range,
                'role_activity': role_activity,
                'top_users': top_users,
                'hourly_activity': hourly_activity,
                'total_active_users': sum(ra['count'] for ra in role_activity),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de actividad de usuarios: {e}")
            raise
    
    def get_alerts_widget(self, severity: str = 'all', limit: int = 10) -> Dict[str, Any]:
        """Widget de alertas del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            alerts = []
            
            # Verificar mesas sin testigo
            cursor.execute("""
                SELECT COUNT(*) FROM mesas_electorales 
                WHERE testigo_asignado_id IS NULL
            """)
            
            unassigned_result = cursor.fetchone()
            unassigned_count = unassigned_result[0] if unassigned_result else 0
            
            if unassigned_count > 0:
                alerts.append({
                    'id': 1,
                    'type': 'warning',
                    'severity': 'medium',
                    'title': 'Mesas sin testigo asignado',
                    'message': f'{unassigned_count} mesas electorales no tienen testigo asignado',
                    'timestamp': datetime.now().isoformat(),
                    'action_required': True
                })
            
            # Verificar candidatos sin partido
            cursor.execute("""
                SELECT COUNT(*) FROM candidates 
                WHERE party_siglas IS NULL AND activo = 1
            """)
            
            orphan_result = cursor.fetchone()
            orphan_count = orphan_result[0] if orphan_result else 0
            
            if orphan_count > 0:
                alerts.append({
                    'id': 2,
                    'type': 'info',
                    'severity': 'low',
                    'title': 'Candidatos sin partido',
                    'message': f'{orphan_count} candidatos sin partido asignado',
                    'timestamp': datetime.now().isoformat(),
                    'action_required': False
                })
            
            # Agregar alertas simuladas adicionales
            alerts.extend([
                {
                    'id': 3,
                    'type': 'success',
                    'severity': 'low',
                    'title': 'Backup completado',
                    'message': 'Respaldo de base de datos completado exitosamente',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'action_required': False
                },
                {
                    'id': 4,
                    'type': 'error',
                    'severity': 'high',
                    'title': 'Error de conectividad',
                    'message': 'Problemas de conexión detectados en 3 puestos electorales',
                    'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'action_required': True
                }
            ])
            
            # Filtrar por severidad si se especifica
            if severity != 'all':
                alerts = [a for a in alerts if a['severity'] == severity]
            
            # Limitar resultados
            alerts = alerts[:limit]
            
            conn.close()
            
            return {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'severity_filter': severity,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de alertas: {e}")
            raise
    
    def get_performance_metrics_widget(self) -> Dict[str, Any]:
        """Widget de métricas de rendimiento"""
        try:
            # Métricas simuladas del sistema
            metrics = {
                'database': {
                    'query_time_avg': round(random.uniform(100, 200), 1),
                    'connections_active': random.randint(10, 25),
                    'connections_max': 100,
                    'size_mb': round(random.uniform(200, 300), 1)
                },
                'api': {
                    'requests_per_minute': random.randint(300, 600),
                    'response_time_avg': round(random.uniform(50, 150), 1),
                    'error_rate': round(random.uniform(0.1, 2.0), 1),
                    'uptime': round(random.uniform(99.0, 99.99), 2)
                },
                'system': {
                    'cpu_usage': round(random.uniform(30, 70), 1),
                    'memory_usage': round(random.uniform(40, 80), 1),
                    'disk_usage': round(random.uniform(20, 50), 1),
                    'network_io': round(random.uniform(0.5, 2.0), 1)
                },
                'electoral': {
                    'mesas_processed_per_hour': random.randint(15, 35),
                    'average_processing_time': round(random.uniform(5, 15), 1),
                    'data_quality_score': round(random.uniform(90, 98), 1),
                    'completion_rate': round(random.uniform(70, 90), 1)
                }
            }
            
            # Tendencias (simuladas)
            trends = {
                'database_performance': [random.randint(100, 200) for _ in range(6)],
                'api_response_time': [random.randint(50, 150) for _ in range(6)],
                'system_cpu': [random.randint(30, 70) for _ in range(6)],
                'processing_rate': [random.randint(15, 35) for _ in range(6)]
            }
            
            return {
                'metrics': metrics,
                'trends': trends,
                'status': 'healthy',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo widget de métricas de rendimiento: {e}")
            raise    

    # ==================== CONFIGURACIÓN DE DASHBOARD ====================
    
    def get_user_dashboard_config(self, user_id: int) -> Dict[str, Any]:
        """Obtener configuración del dashboard del usuario"""
        try:
            user_role = self._get_user_role(user_id)
            
            default_configs = {
                'super_admin': {
                    'layout': 'grid',
                    'widgets': [
                        {'type': 'electoral_progress', 'position': {'x': 0, 'y': 0, 'w': 6, 'h': 4}},
                        {'type': 'candidate_ranking', 'position': {'x': 6, 'y': 0, 'w': 6, 'h': 4}},
                        {'type': 'party_distribution', 'position': {'x': 0, 'y': 4, 'w': 4, 'h': 4}},
                        {'type': 'geographic_map', 'position': {'x': 4, 'y': 4, 'w': 8, 'h': 4}},
                        {'type': 'real_time_stats', 'position': {'x': 0, 'y': 8, 'w': 6, 'h': 3}},
                        {'type': 'alerts', 'position': {'x': 6, 'y': 8, 'w': 6, 'h': 3}}
                    ],
                    'refresh_interval': 30,
                    'theme': 'light'
                },
                'admin_departamental': {
                    'layout': 'grid',
                    'widgets': [
                        {'type': 'electoral_progress', 'position': {'x': 0, 'y': 0, 'w': 8, 'h': 4}},
                        {'type': 'candidate_ranking', 'position': {'x': 8, 'y': 0, 'w': 4, 'h': 4}},
                        {'type': 'party_distribution', 'position': {'x': 0, 'y': 4, 'w': 6, 'h': 4}},
                        {'type': 'alerts', 'position': {'x': 6, 'y': 4, 'w': 6, 'h': 4}}
                    ],
                    'refresh_interval': 60,
                    'theme': 'light'
                },
                'coordinador_municipal': {
                    'layout': 'simple',
                    'widgets': [
                        {'type': 'electoral_progress', 'position': {'x': 0, 'y': 0, 'w': 12, 'h': 4}},
                        {'type': 'geographic_map', 'position': {'x': 0, 'y': 4, 'w': 12, 'h': 4}},
                        {'type': 'alerts', 'position': {'x': 0, 'y': 8, 'w': 12, 'h': 3}}
                    ],
                    'refresh_interval': 60,
                    'theme': 'light'
                },
                'testigo_electoral': {
                    'layout': 'simple',
                    'widgets': [
                        {'type': 'electoral_progress', 'position': {'x': 0, 'y': 0, 'w': 12, 'h': 4}},
                        {'type': 'real_time_stats', 'position': {'x': 0, 'y': 4, 'w': 12, 'h': 3}}
                    ],
                    'refresh_interval': 120,
                    'theme': 'light'
                }
            }
            
            return default_configs.get(user_role, default_configs['testigo_electoral'])
            
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración de dashboard: {e}")
            raise
    
    def save_user_dashboard_config(self, user_id: int, config: Dict[str, Any]) -> bool:
        """Guardar configuración del dashboard del usuario"""
        try:
            # En un sistema real, esto se almacenaría en una tabla de configuraciones
            # Por ahora simulamos el guardado
            
            self.logger.info(f"Configuración de dashboard guardada para usuario {user_id}: {json.dumps(config)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando configuración de dashboard: {e}")
            return False
    
    def export_dashboard(self, user_id: int, format_type: str, widgets: List[str], options: Dict[str, Any]) -> Optional[str]:
        """Exportar dashboard"""
        try:
            # En un sistema real, esto generaría una imagen o PDF del dashboard
            # Por ahora simulamos la exportación
            
            export_filename = f"dashboard_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            
            self.logger.info(f"Dashboard exportado: {export_filename} para usuario {user_id}")
            
            return export_filename
            
        except Exception as e:
            self.logger.error(f"Error exportando dashboard: {e}")
            return None
    
    # ==================== MÉTODOS AUXILIARES PRIVADOS ====================
    
    def _get_user_role(self, user_id: int) -> str:
        """Obtener rol del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT rol FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result['rol'] if result else 'observador'
            
        except Exception as e:
            self.logger.error(f"Error obteniendo rol de usuario: {e}")
            return 'observador'
    
    def _get_quick_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas rápidas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de candidatos
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE activo = 1")
            result = cursor.fetchone()
            stats['total_candidates'] = result[0] if result else 0
            
            # Total de mesas
            cursor.execute("SELECT COUNT(*) FROM mesas_electorales")
            result = cursor.fetchone()
            stats['total_mesas'] = result[0] if result else 0
            
            # Mesas completadas
            cursor.execute("SELECT COUNT(*) FROM mesas_electorales WHERE estado_recoleccion = 'completada'")
            result = cursor.fetchone()
            stats['mesas_completed'] = result[0] if result else 0
            
            # Usuarios activos
            cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
            result = cursor.fetchone()
            stats['active_users'] = result[0] if result else 0
            
            # Calcular porcentaje de completado
            if stats['total_mesas'] > 0:
                stats['completion_percentage'] = round((stats['mesas_completed'] / stats['total_mesas']) * 100, 1)
            else:
                stats['completion_percentage'] = 0.0
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas rápidas: {e}")
            return {}
    
    def _get_recent_activity(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtener actividad reciente"""
        try:
            # En un sistema real, esto vendría de una tabla de logs
            return [
                {
                    'type': 'mesa_completed',
                    'message': 'Mesa 001-FLORENCIA completada',
                    'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                    'user_id': user_id
                },
                {
                    'type': 'user_login',
                    'message': 'Usuario testigo_001 inició sesión',
                    'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                    'user_id': None
                },
                {
                    'type': 'report_generated',
                    'message': 'Reporte de candidatos generado',
                    'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'user_id': user_id
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error obteniendo actividad reciente: {e}")
            return []
    
    def _get_system_status(self) -> Dict[str, str]:
        """Obtener estado del sistema"""
        try:
            # En un sistema real, esto verificaría servicios reales
            return {
                'database': 'healthy',
                'api': 'healthy',
                'storage': 'healthy',
                'network': random.choice(['healthy', 'warning']),
                'overall': 'healthy'
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del sistema: {e}")
            return {'overall': 'error'}
    
    def _get_user_dashboard_permissions(self, user_id: int) -> List[str]:
        """Obtener permisos de dashboard del usuario"""
        try:
            user_role = self._get_user_role(user_id)
            
            role_permissions = {
                'super_admin': ['view', 'export', 'configure', 'admin'],
                'admin_departamental': ['view', 'export', 'configure'],
                'coordinador_municipal': ['view', 'export'],
                'testigo_electoral': ['view']
            }
            
            return role_permissions.get(user_role, ['view'])
            
        except Exception as e:
            self.logger.error(f"Error obteniendo permisos de dashboard: {e}")
            return ['view']
    
    def _get_admin_widgets(self) -> List[str]:
        """Obtener widgets específicos para administradores"""
        return ['user_management', 'system_monitoring', 'audit_logs', 'performance_metrics']
    
    def _get_operational_widgets(self, user_id: int) -> List[str]:
        """Obtener widgets operacionales"""
        return ['assigned_mesas', 'task_queue', 'quick_actions']
    
    def _get_municipality_progress(self) -> List[Dict[str, Any]]:
        """Obtener progreso por municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.municipio_id
                WHERE l.tipo = 'municipio'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY completadas DESC
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            
            municipalities = []
            for row in results:
                total = row['total'] or 0
                completadas = row['completadas'] or 0
                porcentaje = round((completadas / total * 100) if total > 0 else 0, 1)
                
                municipalities.append({
                    'municipio': row['nombre_municipio'],
                    'total': total,
                    'completadas': completadas,
                    'porcentaje': porcentaje
                })
            
            conn.close()
            return municipalities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo progreso por municipio: {e}")
            return []
    
    def _get_progress_time_series(self) -> List[Dict[str, Any]]:
        """Obtener serie temporal de progreso (simulada)"""
        try:
            # Simular progreso por hora en las últimas 12 horas
            series = []
            base_time = datetime.now() - timedelta(hours=12)
            
            for i in range(13):  # 0 a 12 horas
                timestamp = base_time + timedelta(hours=i)
                completed = min(i * 8 + 10, 148)  # Progreso simulado
                
                series.append({
                    'timestamp': timestamp.isoformat(),
                    'completed_mesas': completed,
                    'percentage': round((completed / 148 * 100), 1)
                })
            
            return series
            
        except Exception as e:
            self.logger.error(f"Error obteniendo serie temporal de progreso: {e}")
            return []
    
    def _get_participation_by_municipality(self) -> List[Dict[str, Any]]:
        """Obtener participación por municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total_mesas,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas,
                    COALESCE(SUM(me.total_votantes_habilitados), 0) as total_votantes
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.municipio_id
                WHERE l.tipo = 'municipio'
                GROUP BY l.id, l.nombre_municipio
            """)
            
            results = cursor.fetchall()
            
            municipalities = []
            for row in results:
                total_mesas = row['total_mesas'] or 0
                completadas = row['completadas'] or 0
                porcentaje = round((completadas / total_mesas * 100) if total_mesas > 0 else 0, 1)
                
                municipalities.append({
                    'municipio': row['nombre_municipio'],
                    'total_mesas': total_mesas,
                    'completadas': completadas,
                    'total_votantes': row['total_votantes'],
                    'porcentaje_completado': porcentaje
                })
            
            conn.close()
            return municipalities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo participación por municipio: {e}")
            return []
    
    def _get_votes_by_municipality(self, election_type_id: Optional[int]) -> List[Dict[str, Any]]:
        """Obtener votos por municipio"""
        # Esta función requeriría datos más detallados de resultados
        # Por ahora retornamos datos simulados
        return [
            {'municipio': 'FLORENCIA', 'total_votos': 15000},
            {'municipio': 'ALBANIA', 'total_votos': 8500},
            {'municipio': 'EL DONCELLO', 'total_votos': 6200}
        ]
    
    def _get_municipality_coordinates(self, municipality_name: str) -> Dict[str, float]:
        """Obtener coordenadas de municipio (simuladas)"""
        # Coordenadas aproximadas de algunos municipios de Caquetá
        coordinates = {
            'FLORENCIA': {'lat': 1.6143, 'lng': -75.6062},
            'ALBANIA': {'lat': 2.0167, 'lng': -76.2833},
            'CARTAGENA DEL CHAIRA': {'lat': 1.3333, 'lng': -74.8667},
            'BELEN DE LOS ANDAQUIES': {'lat': 1.4167, 'lng': -75.8500},
            'EL DONCELLO': {'lat': 1.6500, 'lng': -75.2833},
            'EL PAUJIL': {'lat': 1.5167, 'lng': -75.1000},
            'LA MONTAÑITA': {'lat': 1.5500, 'lng': -75.4167},
            'MILAN': {'lat': 1.2833, 'lng': -75.9167},
            'MORELIA': {'lat': 1.4833, 'lng': -75.7833},
            'PUERTO RICO': {'lat': 1.9167, 'lng': -75.1500},
            'SAN JOSE DEL FRAGUA': {'lat': 1.2833, 'lng': -76.0833},
            'SAN VICENTE DEL CAGUAN': {'lat': 2.1167, 'lng': -74.7667},
            'SOLANO': {'lat': 1.5833, 'lng': -74.7833},
            'SOLITA': {'lat': 1.2167, 'lng': -75.6833},
            'VALPARAISO': {'lat': 1.2500, 'lng': -75.4167},
            'CURILLO': {'lat': 1.2833, 'lng': -76.1000}
        }
        
        return coordinates.get(municipality_name, {'lat': 1.6143, 'lng': -75.6062})
    
    def _get_active_users_count(self) -> int:
        """Obtener conteo de usuarios activos"""
        try:
            # En un sistema real, esto verificaría sesiones activas
            return random.randint(35, 65)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conteo de usuarios activos: {e}")
            return 0
    
    def _get_processing_mesas_count(self) -> int:
        """Obtener conteo de mesas en proceso"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM mesas_electorales WHERE estado_recoleccion = 'en_proceso'")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conteo de mesas en proceso: {e}")
            return 0
    
    def _get_votes_per_minute_simulation(self) -> int:
        """Simular votos por minuto"""
        return random.randint(50, 150)
    
    def _get_recent_system_activities(self) -> List[Dict[str, Any]]:
        """Obtener actividades recientes del sistema"""
        return [
            {'activity': 'Mesa completada', 'count': random.randint(1, 5), 'last_occurrence': '2 min ago'},
            {'activity': 'Usuario conectado', 'count': random.randint(3, 10), 'last_occurrence': '5 min ago'},
            {'activity': 'Reporte generado', 'count': random.randint(1, 3), 'last_occurrence': '10 min ago'},
            {'activity': 'Datos importados', 'count': random.randint(0, 2), 'last_occurrence': '15 min ago'}
        ]
    
    def _get_activity_by_role(self, hours: int) -> List[Dict[str, Any]]:
        """Obtener actividad por rol"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rol, COUNT(*) as count
                FROM users
                WHERE activo = 1
                GROUP BY rol
            """)
            
            results = cursor.fetchall()
            
            activity = []
            for row in results:
                activity.append({
                    'role': row['rol'],
                    'count': row['count']
                })
            
            conn.close()
            return activity
            
        except Exception as e:
            self.logger.error(f"Error obteniendo actividad por rol: {e}")
            return []
    
    def _get_top_active_users(self, hours: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener usuarios más activos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT nombre_completo, rol, ultimo_login
                FROM users
                WHERE activo = 1 AND ultimo_login IS NOT NULL
                ORDER BY ultimo_login DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            
            users = []
            for row in results:
                users.append({
                    'nombre': row['nombre_completo'],
                    'rol': row['rol'],
                    'ultimo_acceso': row['ultimo_login']
                })
            
            conn.close()
            return users
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios más activos: {e}")
            return []
    
    def _get_hourly_activity_simulation(self) -> List[Dict[str, Any]]:
        """Simular actividad por hora"""
        activities = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(24):
            hour_time = base_time + timedelta(hours=i)
            activity_count = random.randint(10, 100)
            
            activities.append({
                'hour': hour_time.strftime('%H:00'),
                'activity_count': activity_count
            })
        
        return activities