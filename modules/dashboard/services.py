"""
Módulo Dashboard - Servicios
Lógica de negocio para dashboard y widgets
"""

import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class DashboardService:
    """Servicio para dashboard y widgets"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_dashboard_overview(self, user_id):
        """Obtener vista general del dashboard"""
        try:
            # Obtener rol del usuario para personalizar dashboard
            user_role = self._get_user_role(user_id)
            
            overview = {
                'user_role': user_role,
                'last_updated': datetime.utcnow().isoformat(),
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
            logger.error(f"Get dashboard overview error: {e}")
            raise
    
    def get_electoral_progress_widget(self, process_id=None):
        """Widget de progreso electoral"""
        try:
            # Estadísticas de progreso
            progress_query = """
                SELECT 
                    estado_recoleccion,
                    COUNT(*) as count
                FROM mesas_electorales
                GROUP BY estado_recoleccion
            """
            
            progress_result = self.db.execute_query(progress_query)
            
            progress_data = {}
            total_mesas = 0
            
            for row in progress_result:
                progress_data[row[0]] = row[1]
                total_mesas += row[1]
            
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
            
            return {
                'total_mesas': total_mesas,
                'progress_by_status': progress_data,
                'progress_percentages': progress_percentages,
                'municipality_progress': municipality_progress,
                'time_series': time_series,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get electoral progress widget error: {e}")
            raise
    
    def get_candidate_ranking_widget(self, election_type_id=None, limit=5):
        """Widget de ranking de candidatos"""
        try:
            base_query = """
                SELECT 
                    c.nombre_completo,
                    c.numero_tarjeton,
                    p.siglas as partido_siglas,
                    p.color_representativo,
                    COALESCE(cr.total_votos, 0) as total_votos,
                    COALESCE(cr.porcentaje_votacion, 0) as porcentaje_votacion,
                    COALESCE(cr.posicion_ranking, 999) as posicion_ranking
                FROM candidates c
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
                WHERE c.activo = 1
            """
            
            params = {}
            
            if election_type_id:
                base_query += " AND c.election_type_id = :election_type_id"
                params['election_type_id'] = election_type_id
            
            base_query += f" ORDER BY total_votos DESC LIMIT {limit}"
            
            result = self.db.execute_query(base_query, params)
            
            candidates = [
                {
                    'nombre': row[0],
                    'numero_tarjeton': row[1],
                    'partido_siglas': row[2],
                    'color_partido': row[3] or '#666666',
                    'total_votos': row[4],
                    'porcentaje_votacion': row[5],
                    'posicion': row[6] if row[6] != 999 else len(result) + 1
                }
                for row in result
            ]
            
            # Estadísticas adicionales
            total_votos = sum(c['total_votos'] for c in candidates)
            
            return {
                'candidates': candidates,
                'total_votos_top': total_votos,
                'election_type_id': election_type_id,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get candidate ranking widget error: {e}")
            raise
    
    def get_party_distribution_widget(self, election_type_id=None):
        """Widget de distribución por partido"""
        try:
            query = """
                SELECT 
                    p.siglas,
                    p.nombre_oficial,
                    p.color_representativo,
                    COUNT(c.id) as total_candidatos,
                    SUM(COALESCE(cr.total_votos, 0)) as total_votos,
                    AVG(COALESCE(cr.porcentaje_votacion, 0)) as promedio_porcentaje
                FROM political_parties p
                LEFT JOIN candidates c ON p.id = c.party_id AND c.activo = 1
                LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
            """
            
            params = {}
            
            if election_type_id:
                query += " AND c.election_type_id = :election_type_id"
                params['election_type_id'] = election_type_id
            
            query += """
                WHERE p.activo = 1
                GROUP BY p.id, p.siglas, p.nombre_oficial, p.color_representativo
                HAVING total_candidatos > 0
                ORDER BY total_votos DESC
            """
            
            result = self.db.execute_query(query, params)
            
            parties = [
                {
                    'siglas': row[0],
                    'nombre_oficial': row[1],
                    'color': row[2] or '#666666',
                    'total_candidatos': row[3],
                    'total_votos': row[4],
                    'promedio_porcentaje': round(row[5], 2)
                }
                for row in result
            ]
            
            # Calcular porcentajes de distribución
            total_votos_all = sum(p['total_votos'] for p in parties)
            
            for party in parties:
                party['porcentaje_distribucion'] = round(
                    (party['total_votos'] / total_votos_all * 100) if total_votos_all > 0 else 0, 2
                )
            
            return {
                'parties': parties,
                'total_votos_all': total_votos_all,
                'total_parties': len(parties),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get party distribution widget error: {e}")
            raise
    
    def get_geographic_map_widget(self, election_type_id=None, metric='participation'):
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
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get geographic map widget error: {e}")
            raise
    
    def get_real_time_stats_widget(self):
        """Widget de estadísticas en tiempo real"""
        try:
            # Simular estadísticas en tiempo real
            current_time = datetime.utcnow()
            
            stats = {
                'current_time': current_time.isoformat(),
                'active_users': self._get_active_users_count(),
                'mesas_being_processed': self._get_processing_mesas_count(),
                'votes_per_minute': self._get_votes_per_minute_simulation(),
                'system_load': {
                    'cpu_usage': 45.2,
                    'memory_usage': 62.8,
                    'disk_usage': 34.1,
                    'network_io': 1.2
                },
                'recent_activities': self._get_recent_system_activities()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Get real time stats widget error: {e}")
            raise
    
    def get_user_activity_widget(self, time_range='24h'):
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
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get user activity widget error: {e}")
            raise
    
    def get_alerts_widget(self, severity='all', limit=10):
        """Widget de alertas del sistema"""
        try:
            # Generar alertas simuladas basadas en datos reales
            alerts = []
            
            # Verificar mesas sin testigo
            unassigned_mesas = self.db.execute_query("""
                SELECT COUNT(*) FROM mesas_electorales 
                WHERE testigo_asignado_id IS NULL
            """)
            
            if unassigned_mesas and unassigned_mesas[0][0] > 0:
                alerts.append({
                    'id': 1,
                    'type': 'warning',
                    'severity': 'medium',
                    'title': 'Mesas sin testigo asignado',
                    'message': f'{unassigned_mesas[0][0]} mesas electorales no tienen testigo asignado',
                    'timestamp': datetime.utcnow().isoformat(),
                    'action_required': True
                })
            
            # Verificar candidatos sin partido
            orphan_candidates = self.db.execute_query("""
                SELECT COUNT(*) FROM candidates 
                WHERE party_id IS NULL AND coalition_id IS NULL AND es_independiente = 0
            """)
            
            if orphan_candidates and orphan_candidates[0][0] > 0:
                alerts.append({
                    'id': 2,
                    'type': 'info',
                    'severity': 'low',
                    'title': 'Candidatos sin afiliación',
                    'message': f'{orphan_candidates[0][0]} candidatos sin partido o coalición',
                    'timestamp': datetime.utcnow().isoformat(),
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
                    'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    'action_required': False
                },
                {
                    'id': 4,
                    'type': 'error',
                    'severity': 'high',
                    'title': 'Error de conectividad',
                    'message': 'Problemas de conexión detectados en 3 puestos electorales',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                    'action_required': True
                }
            ])
            
            # Filtrar por severidad si se especifica
            if severity != 'all':
                alerts = [a for a in alerts if a['severity'] == severity]
            
            # Limitar resultados
            alerts = alerts[:limit]
            
            return {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'severity_filter': severity,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get alerts widget error: {e}")
            raise
    
    def get_performance_metrics_widget(self):
        """Widget de métricas de rendimiento"""
        try:
            # Métricas simuladas del sistema
            metrics = {
                'database': {
                    'query_time_avg': 125.5,  # ms
                    'connections_active': 15,
                    'connections_max': 100,
                    'size_mb': 245.8
                },
                'api': {
                    'requests_per_minute': 450,
                    'response_time_avg': 89.2,  # ms
                    'error_rate': 0.8,  # %
                    'uptime': 99.95  # %
                },
                'system': {
                    'cpu_usage': 45.2,  # %
                    'memory_usage': 62.8,  # %
                    'disk_usage': 34.1,  # %
                    'network_io': 1.2  # MB/s
                },
                'electoral': {
                    'mesas_processed_per_hour': 25,
                    'average_processing_time': 8.5,  # minutes
                    'data_quality_score': 94.2,  # %
                    'completion_rate': 78.5  # %
                }
            }
            
            # Tendencias (simuladas)
            trends = {
                'database_performance': [120, 125, 130, 125, 122, 125],  # últimas 6 horas
                'api_response_time': [85, 89, 92, 89, 87, 89],
                'system_cpu': [42, 45, 48, 45, 43, 45],
                'processing_rate': [22, 25, 28, 25, 23, 25]
            }
            
            return {
                'metrics': metrics,
                'trends': trends,
                'status': 'healthy',
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get performance metrics widget error: {e}")
            raise
    
    def get_user_dashboard_config(self, user_id):
        """Obtener configuración del dashboard del usuario"""
        try:
            # En un sistema real, esto se almacenaría en una tabla de configuraciones
            # Por ahora retornamos configuración por defecto
            
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
                'testigo_mesa': {
                    'layout': 'simple',
                    'widgets': [
                        {'type': 'electoral_progress', 'position': {'x': 0, 'y': 0, 'w': 12, 'h': 4}},
                        {'type': 'real_time_stats', 'position': {'x': 0, 'y': 4, 'w': 12, 'h': 3}}
                    ],
                    'refresh_interval': 60,
                    'theme': 'light'
                }
            }
            
            return default_configs.get(user_role, default_configs['testigo_mesa'])
            
        except Exception as e:
            logger.error(f"Get user dashboard config error: {e}")
            raise
    
    def save_user_dashboard_config(self, user_id, config):
        """Guardar configuración del dashboard del usuario"""
        try:
            # En un sistema real, esto se almacenaría en una tabla de configuraciones
            # Por ahora simulamos el guardado
            
            logger.info(f"Dashboard config saved for user {user_id}: {json.dumps(config)}")
            return True
            
        except Exception as e:
            logger.error(f"Save user dashboard config error: {e}")
            return False
    
    def export_dashboard(self, user_id, format_type, widgets, options):
        """Exportar dashboard"""
        try:
            # En un sistema real, esto generaría una imagen o PDF del dashboard
            # Por ahora simulamos la exportación
            
            export_filename = f"dashboard_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            
            logger.info(f"Dashboard exported: {export_filename} for user {user_id}")
            
            return export_filename
            
        except Exception as e:
            logger.error(f"Export dashboard error: {e}")
            return None
    
    # Métodos auxiliares privados
    
    def _get_user_role(self, user_id):
        """Obtener rol del usuario"""
        try:
            query = "SELECT rol FROM users WHERE id = :user_id"
            result = self.db.execute_query(query, {'user_id': user_id})
            return result[0][0] if result else 'observador'
        except:
            return 'observador'
    
    def _get_quick_stats(self):
        """Obtener estadísticas rápidas"""
        try:
            stats = {}
            
            # Total de candidatos
            candidate_result = self.db.execute_query("SELECT COUNT(*) FROM candidates WHERE activo = 1")
            stats['total_candidates'] = candidate_result[0][0] if candidate_result else 0
            
            # Total de mesas
            mesa_result = self.db.execute_query("SELECT COUNT(*) FROM mesas_electorales")
            stats['total_mesas'] = mesa_result[0][0] if mesa_result else 0
            
            # Mesas completadas
            completed_result = self.db.execute_query(
                "SELECT COUNT(*) FROM mesas_electorales WHERE estado_recoleccion = 'completada'"
            )
            stats['mesas_completed'] = completed_result[0][0] if completed_result else 0
            
            # Usuarios activos
            active_users_result = self.db.execute_query("SELECT COUNT(*) FROM users WHERE activo = 1")
            stats['active_users'] = active_users_result[0][0] if active_users_result else 0
            
            return stats
        except:
            return {}
    
    def _get_recent_activity(self, user_id):
        """Obtener actividad reciente"""
        try:
            # En un sistema real, esto vendría de una tabla de logs
            return [
                {
                    'type': 'mesa_completed',
                    'message': 'Mesa 001-FLORENCIA completada',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat()
                },
                {
                    'type': 'user_login',
                    'message': 'Usuario testigo_001 inició sesión',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=15)).isoformat()
                }
            ]
        except:
            return []
    
    def _get_system_status(self):
        """Obtener estado del sistema"""
        try:
            return {
                'database': 'healthy',
                'api': 'healthy',
                'storage': 'healthy',
                'network': 'warning'
            }
        except:
            return {}
    
    def _get_user_dashboard_permissions(self, user_id):
        """Obtener permisos de dashboard del usuario"""
        try:
            # Esto se integraría con el PermissionManager
            return ['view', 'export']
        except:
            return ['view']
    
    def _get_admin_widgets(self):
        """Obtener widgets específicos para administradores"""
        return ['user_management', 'system_monitoring', 'audit_logs']
    
    def _get_operational_widgets(self, user_id):
        """Obtener widgets operacionales"""
        return ['assigned_mesas', 'task_queue', 'quick_actions']
    
    def _get_municipality_progress(self):
        """Obtener progreso por municipio"""
        try:
            query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas
                FROM locations l
                JOIN locations lp ON l.id = lp.parent_id
                JOIN mesas_electorales me ON lp.id = me.puesto_id
                WHERE l.tipo = 'MUNICIPIO'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY completadas DESC
                LIMIT 10
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'municipio': row[0],
                    'total': row[1],
                    'completadas': row[2],
                    'porcentaje': round((row[2] / row[1] * 100) if row[1] > 0 else 0, 1)
                }
                for row in result
            ]
        except:
            return []
    
    def _get_progress_time_series(self):
        """Obtener serie temporal de progreso (simulada)"""
        try:
            # Simular progreso por hora en las últimas 12 horas
            series = []
            base_time = datetime.utcnow() - timedelta(hours=12)
            
            for i in range(13):  # 0 a 12 horas
                timestamp = base_time + timedelta(hours=i)
                completed = min(i * 8 + 10, 148)  # Progreso simulado
                
                series.append({
                    'timestamp': timestamp.isoformat(),
                    'completed_mesas': completed,
                    'percentage': round((completed / 148 * 100), 1)
                })
            
            return series
        except:
            return []
    
    def _get_participation_by_municipality(self):
        """Obtener participación por municipio"""
        try:
            query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total_mesas,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas,
                    SUM(me.total_votantes_habilitados) as total_votantes
                FROM locations l
                JOIN locations lp ON l.id = lp.parent_id
                JOIN mesas_electorales me ON lp.id = me.puesto_id
                WHERE l.tipo = 'MUNICIPIO'
                GROUP BY l.id, l.nombre_municipio
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'municipio': row[0],
                    'total_mesas': row[1],
                    'completadas': row[2],
                    'total_votantes': row[3],
                    'porcentaje_completado': round((row[2] / row[1] * 100) if row[1] > 0 else 0, 1)
                }
                for row in result
            ]
        except:
            return []
    
    def _get_votes_by_municipality(self, election_type_id):
        """Obtener votos por municipio"""
        # Esta función requeriría datos más detallados de resultados
        return []
    
    def _get_municipality_coordinates(self, municipality_name):
        """Obtener coordenadas de municipio (simuladas)"""
        # Coordenadas aproximadas de algunos municipios de Caquetá
        coordinates = {
            'FLORENCIA': {'lat': 1.6143, 'lng': -75.6062},
            'ALBANIA': {'lat': 2.0167, 'lng': -76.2833},
            'CARTAGENA DEL CHAIRA': {'lat': 1.3333, 'lng': -74.8667},
            'BELEN DE LOS ANDAQUIES': {'lat': 1.4167, 'lng': -75.8500},
            'EL DONCELLO': {'lat': 1.6500, 'lng': -75.2833},
            'EL PAUJIL': {'lat': 1.5167, 'lng': -75.1000}
        }
        
        return coordinates.get(municipality_name, {'lat': 1.6143, 'lng': -75.6062})
    
    def _get_active_users_count(self):
        """Obtener conteo de usuarios activos"""
        try:
            # En un sistema real, esto verificaría sesiones activas
            return 45  # Simulado
        except:
            return 0
    
    def _get_processing_mesas_count(self):
        """Obtener conteo de mesas en proceso"""
        try:
            result = self.db.execute_query(
                "SELECT COUNT(*) FROM mesas_electorales WHERE estado_recoleccion = 'en_proceso'"
            )
            return result[0][0] if result else 0
        except:
            return 0
    
    def _get_votes_per_minute_simulation(self):
        """Simular votos por minuto"""
        import random
        return random.randint(50, 150)
    
    def _get_recent_system_activities(self):
        """Obtener actividades recientes del sistema"""
        return [
            {'activity': 'Mesa completada', 'count': 3, 'last_occurrence': '2 min ago'},
            {'activity': 'Usuario conectado', 'count': 8, 'last_occurrence': '5 min ago'},
            {'activity': 'Reporte generado', 'count': 1, 'last_occurrence': '10 min ago'}
        ]
    
    def _get_activity_by_role(self, hours):
        """Obtener actividad por rol"""
        try:
            query = """
                SELECT rol, COUNT(*) as count
                FROM users
                WHERE activo = 1
                GROUP BY rol
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'role': row[0],
                    'count': row[1]
                }
                for row in result
            ]
        except:
            return []
    
    def _get_top_active_users(self, hours, limit=5):
        """Obtener usuarios más activos"""
        try:
            query = """
                SELECT nombre_completo, rol, ultimo_acceso
                FROM users
                WHERE activo = 1 AND ultimo_acceso IS NOT NULL
                ORDER BY ultimo_acceso DESC
                LIMIT :limit
            """
            
            result = self.db.execute_query(query, {'limit': limit})
            
            return [
                {
                    'nombre': row[0],
                    'rol': row[1],
                    'ultimo_acceso': row[2]
                }
                for row in result
            ]
        except:
            return []
    
    def _get_hourly_activity_simulation(self):
        """Simular actividad por hora"""
        import random
        
        activities = []
        base_time = datetime.utcnow() - timedelta(hours=24)
        
        for i in range(24):
            hour_time = base_time + timedelta(hours=i)
            activity_count = random.randint(10, 100)
            
            activities.append({
                'hour': hour_time.strftime('%H:00'),
                'activity_count': activity_count
            })
        
        return activities