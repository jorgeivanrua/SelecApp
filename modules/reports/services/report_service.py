"""
Servicio de Generación de Reportes
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ..models import (
    ReportFilter, ElectoralSummary, CandidateResultsReport, 
    PartyPerformanceReport, GeographicAnalysis, ParticipationStats,
    SystemAuditReport, ScheduledReport, ReportTemplate
)

class ReportService:
    """Servicio para generación de reportes electorales"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== REPORTES PRINCIPALES ====================
    
    def generate_electoral_summary(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar resumen electoral general"""
        try:
            # Estadísticas generales
            general_stats = self._get_general_electoral_stats(filters)
            
            # Progreso de recolección
            collection_progress = self._get_collection_progress(filters)
            
            # Top candidatos
            top_candidates = self._get_top_candidates(filters)
            
            # Participación por municipio
            participation_by_municipality = self._get_participation_by_municipality(filters)
            
            return {
                'general_stats': general_stats,
                'collection_progress': collection_progress,
                'top_candidates': top_candidates,
                'participation_by_municipality': participation_by_municipality,
                'generated_at': datetime.now().isoformat(),
                'filters': filters.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Error generando resumen electoral: {e}")
            raise
    
    def generate_candidate_results_report(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar reporte de resultados de candidatos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query base para candidatos
            query = """
                SELECT 
                    c.id,
                    c.nombre_completo,
                    c.cargo_aspirado,
                    c.numero_tarjeton,
                    c.party_siglas,
                    c.election_type_id,
                    COALESCE(SUM(v.votos), 0) as total_votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1
            """
            
            params = []
            
            if filters.election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(filters.election_type_id)
            
            if filters.party_id:
                query += " AND c.party_id = ?"
                params.append(filters.party_id)
            
            query += f"""
                GROUP BY c.id, c.nombre_completo, c.cargo_aspirado, 
                         c.numero_tarjeton, c.party_siglas, c.election_type_id
                ORDER BY total_votos DESC 
                LIMIT {filters.top_n}
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            candidates = []
            for row in results:
                candidates.append({
                    'id': row['id'],
                    'nombre_completo': row['nombre_completo'],
                    'cargo_aspirado': row['cargo_aspirado'],
                    'numero_tarjeton': row['numero_tarjeton'],
                    'partido_siglas': row['party_siglas'],
                    'total_votos': row['total_votos'],
                    'porcentaje_votacion': 0.0,  # Calcular si es necesario
                    'posicion_ranking': 0  # Calcular si es necesario
                })
            
            # Estadísticas adicionales
            statistics = self._calculate_candidate_statistics(candidates)
            
            conn.close()
            
            return {
                'candidates': candidates,
                'statistics': statistics,
                'generated_at': datetime.now().isoformat(),
                'filters': filters.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de candidatos: {e}")
            raise
    
    def generate_party_performance_report(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar reporte de desempeño por partido"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    c.party_siglas,
                    COUNT(c.id) as total_candidatos,
                    COALESCE(SUM(v.votos), 0) as total_votos_partido,
                    COALESCE(AVG(v.votos), 0) as promedio_votos,
                    COALESCE(MAX(v.votos), 0) as mejor_candidato_votos,
                    COALESCE(MIN(v.votos), 0) as peor_candidato_votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1 AND c.party_siglas IS NOT NULL
            """
            
            params = []
            
            if filters.election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(filters.election_type_id)
            
            query += """
                GROUP BY c.party_siglas
                HAVING total_candidatos > 0
                ORDER BY total_votos_partido DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            parties = []
            for row in results:
                parties.append({
                    'siglas': row['party_siglas'],
                    'total_candidatos': row['total_candidatos'],
                    'total_votos_partido': row['total_votos_partido'],
                    'promedio_votos': round(row['promedio_votos'], 2),
                    'mejor_candidato_votos': row['mejor_candidato_votos'],
                    'peor_candidato_votos': row['peor_candidato_votos']
                })
            
            conn.close()
            
            return {
                'parties': parties,
                'generated_at': datetime.now().isoformat(),
                'filters': filters.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de partidos: {e}")
            raise
    
    def generate_geographic_analysis(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar análisis geográfico de resultados"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Análisis por municipio
            query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(DISTINCT me.id) as total_mesas,
                    COALESCE(SUM(me.total_votantes_habilitados), 0) as total_votantes,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as mesas_completadas
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.municipio_id
                WHERE l.tipo = 'municipio'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY total_votantes DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            municipalities = []
            for row in results:
                total_mesas = row['total_mesas'] or 0
                completadas = row['mesas_completadas'] or 0
                porcentaje = round((completadas / total_mesas * 100) if total_mesas > 0 else 0, 2)
                
                municipalities.append({
                    'nombre_municipio': row['nombre_municipio'],
                    'total_mesas': total_mesas,
                    'total_votantes': row['total_votantes'],
                    'mesas_completadas': completadas,
                    'porcentaje_completado': porcentaje
                })
            
            # Desempeño de candidato específico si se solicita
            candidate_performance = None
            if filters.candidate_id:
                candidate_performance = self._get_candidate_geographic_performance(filters.candidate_id)
            
            conn.close()
            
            return {
                'municipalities': municipalities,
                'candidate_performance': candidate_performance,
                'generated_at': datetime.now().isoformat(),
                'filters': filters.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Error generando análisis geográfico: {e}")
            raise
    
    def generate_participation_stats(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar estadísticas de participación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_mesas,
                    COALESCE(SUM(total_votantes_habilitados), 0) as total_votantes_habilitados,
                    COUNT(CASE WHEN estado_recoleccion = 'completada' THEN 1 END) as mesas_completadas,
                    COUNT(CASE WHEN estado_recoleccion = 'en_proceso' THEN 1 END) as mesas_en_proceso,
                    COUNT(CASE WHEN estado_recoleccion = 'pendiente' THEN 1 END) as mesas_pendientes
                FROM mesas_electorales
            """)
            
            general_result = cursor.fetchone()
            
            general_stats = {
                'total_mesas': general_result['total_mesas'] or 0,
                'total_votantes_habilitados': general_result['total_votantes_habilitados'] or 0,
                'mesas_completadas': general_result['mesas_completadas'] or 0,
                'mesas_en_proceso': general_result['mesas_en_proceso'] or 0,
                'mesas_pendientes': general_result['mesas_pendientes'] or 0
            }
            
            # Calcular porcentaje de completado
            total_mesas = general_stats['total_mesas']
            completadas = general_stats['mesas_completadas']
            general_stats['porcentaje_completado'] = round((completadas / total_mesas * 100) if total_mesas > 0 else 0, 2)
            
            # Participación por hora (simulada por ahora)
            hourly_participation = self._generate_hourly_participation()
            
            # Participación por tipo de elección
            cursor.execute("""
                SELECT 
                    c.election_type_id,
                    COUNT(c.id) as total_candidatos,
                    COALESCE(SUM(v.votos), 0) as total_votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1
                GROUP BY c.election_type_id
                ORDER BY total_votos DESC
            """)
            
            election_results = cursor.fetchall()
            
            participation_by_election = []
            for row in election_results:
                participation_by_election.append({
                    'election_type_id': row['election_type_id'],
                    'total_candidatos': row['total_candidatos'],
                    'total_votos': row['total_votos']
                })
            
            conn.close()
            
            return {
                'general_stats': general_stats,
                'hourly_participation': hourly_participation,
                'participation_by_election': participation_by_election,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando estadísticas de participación: {e}")
            raise
    
    def generate_system_audit_report(self, filters: ReportFilter) -> Dict[str, Any]:
        """Generar reporte de auditoría del sistema"""
        try:
            # Estadísticas de usuarios
            user_stats = self._get_user_audit_stats(filters)
            
            # Actividad del sistema
            system_activity = self._get_system_activity_stats(filters)
            
            # Integridad de datos
            data_integrity = self._check_data_integrity()
            
            return {
                'user_stats': user_stats,
                'system_activity': system_activity,
                'data_integrity': data_integrity,
                'audit_period': {
                    'start_date': filters.start_date,
                    'end_date': filters.end_date
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de auditoría: {e}")
            raise
    
    # ==================== GESTIÓN DE REPORTES PROGRAMADOS ====================
    
    def get_scheduled_reports(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtener reportes programados del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    report_type VARCHAR(100) NOT NULL,
                    schedule_type VARCHAR(50) NOT NULL,
                    filters TEXT,
                    user_id INTEGER NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    next_run DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                SELECT * FROM scheduled_reports 
                WHERE user_id = ? AND active = 1
                ORDER BY next_run ASC
            """, (user_id,))
            
            results = cursor.fetchall()
            
            scheduled_reports = []
            for row in results:
                scheduled_reports.append({
                    'id': row['id'],
                    'name': row['name'],
                    'report_type': row['report_type'],
                    'schedule_type': row['schedule_type'],
                    'next_run': row['next_run'],
                    'active': bool(row['active']),
                    'created_at': row['created_at']
                })
            
            conn.close()
            return scheduled_reports
            
        except Exception as e:
            self.logger.error(f"Error obteniendo reportes programados: {e}")
            return []
    
    def create_scheduled_report(self, data: Dict[str, Any], user_id: int) -> int:
        """Crear reporte programado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Calcular próxima ejecución
            next_run = self._calculate_next_run(data.get('schedule_type', 'daily'))
            
            cursor.execute("""
                INSERT INTO scheduled_reports 
                (name, report_type, schedule_type, filters, user_id, next_run)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data['name'],
                data['report_type'],
                data.get('schedule_type', 'daily'),
                str(data.get('filters', {})),
                user_id,
                next_run
            ))
            
            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Reporte programado creado: {data['name']} por usuario {user_id}")
            
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Error creando reporte programado: {e}")
            raise
    
    def get_report_templates(self) -> List[Dict[str, Any]]:
        """Obtener plantillas de reportes disponibles"""
        try:
            templates = [
                {
                    'id': 'electoral_summary',
                    'name': 'Resumen Electoral',
                    'description': 'Resumen general del proceso electoral con estadísticas principales',
                    'category': 'General',
                    'parameters': ['process_id', 'election_type_id']
                },
                {
                    'id': 'candidate_results',
                    'name': 'Resultados de Candidatos',
                    'description': 'Resultados detallados por candidato con ranking y estadísticas',
                    'category': 'Candidatos',
                    'parameters': ['election_type_id', 'party_id', 'top_n']
                },
                {
                    'id': 'party_performance',
                    'name': 'Desempeño por Partido',
                    'description': 'Análisis comparativo de desempeño de partidos políticos',
                    'category': 'Partidos',
                    'parameters': ['election_type_id']
                },
                {
                    'id': 'geographic_analysis',
                    'name': 'Análisis Geográfico',
                    'description': 'Análisis de resultados por ubicación geográfica y distribución territorial',
                    'category': 'Geografía',
                    'parameters': ['election_type_id', 'candidate_id', 'municipality_id']
                },
                {
                    'id': 'participation_stats',
                    'name': 'Estadísticas de Participación',
                    'description': 'Estadísticas detalladas de participación electoral y cobertura',
                    'category': 'Participación',
                    'parameters': ['process_id']
                },
                {
                    'id': 'system_audit',
                    'name': 'Auditoría del Sistema',
                    'description': 'Reporte de auditoría con actividad del sistema e integridad de datos',
                    'category': 'Administración',
                    'parameters': ['start_date', 'end_date']
                }
            ]
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Error obteniendo plantillas de reportes: {e}")
            return []   
 
    # ==================== MÉTODOS AUXILIARES PRIVADOS ====================
    
    def _get_general_electoral_stats(self, filters: ReportFilter) -> Dict[str, Any]:
        """Obtener estadísticas generales electorales"""
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
            
            # Total de votantes habilitados
            cursor.execute("SELECT COALESCE(SUM(total_votantes_habilitados), 0) FROM mesas_electorales")
            result = cursor.fetchone()
            stats['total_votantes_habilitados'] = result[0] if result else 0
            
            # Total de votos registrados
            cursor.execute("SELECT COUNT(*) FROM votes")
            result = cursor.fetchone()
            stats['total_votos_registrados'] = result[0] if result else 0
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas generales: {e}")
            return {}
    
    def _get_collection_progress(self, filters: ReportFilter) -> Dict[str, Any]:
        """Obtener progreso de recolección"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    estado_recoleccion,
                    COUNT(*) as count
                FROM mesas_electorales
                GROUP BY estado_recoleccion
            """)
            
            results = cursor.fetchall()
            
            progress = {}
            total = 0
            
            for row in results:
                estado = row['estado_recoleccion'] or 'sin_estado'
                count = row['count']
                progress[estado] = count
                total += count
            
            # Calcular porcentajes
            for estado in progress:
                progress[f"{estado}_percentage"] = round((progress[estado] / total * 100) if total > 0 else 0, 2)
            
            progress['total'] = total
            
            conn.close()
            return progress
            
        except Exception as e:
            self.logger.error(f"Error obteniendo progreso de recolección: {e}")
            return {}
    
    def _get_top_candidates(self, filters: ReportFilter) -> List[Dict[str, Any]]:
        """Obtener top candidatos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    c.nombre_completo,
                    c.party_siglas,
                    COALESCE(v.votos, 0) as votos
                FROM candidates c
                LEFT JOIN (
                    SELECT candidate_id, COUNT(*) as votos
                    FROM votes 
                    GROUP BY candidate_id
                ) v ON c.id = v.candidate_id
                WHERE c.activo = 1
            """
            
            params = []
            
            if filters.election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(filters.election_type_id)
            
            query += f" ORDER BY votos DESC LIMIT {filters.top_n}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            candidates = []
            for row in results:
                candidates.append({
                    'nombre': row['nombre_completo'],
                    'partido': row['party_siglas'],
                    'votos': row['votos']
                })
            
            conn.close()
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error obteniendo top candidatos: {e}")
            return []
    
    def _get_participation_by_municipality(self, filters: ReportFilter) -> List[Dict[str, Any]]:
        """Obtener participación por municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total_mesas,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.municipio_id
                WHERE l.tipo = 'municipio'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY completadas DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            municipalities = []
            for row in results:
                total_mesas = row['total_mesas'] or 0
                completadas = row['completadas'] or 0
                porcentaje = round((completadas / total_mesas * 100) if total_mesas > 0 else 0, 2)
                
                municipalities.append({
                    'municipio': row['nombre_municipio'],
                    'total_mesas': total_mesas,
                    'completadas': completadas,
                    'porcentaje': porcentaje
                })
            
            conn.close()
            return municipalities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo participación por municipio: {e}")
            return []
    
    def _calculate_candidate_statistics(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular estadísticas de candidatos"""
        try:
            if not candidates:
                return {
                    'total_votes_cast': 0,
                    'average_votes_per_candidate': 0,
                    'highest_vote_count': 0,
                    'lowest_vote_count': 0
                }
            
            votos = [c['total_votos'] for c in candidates]
            
            return {
                'total_votes_cast': sum(votos),
                'average_votes_per_candidate': round(sum(votos) / len(votos), 2),
                'highest_vote_count': max(votos),
                'lowest_vote_count': min(votos)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas de candidatos: {e}")
            return {}
    
    def _get_candidate_geographic_performance(self, candidate_id: int) -> Dict[str, Any]:
        """Obtener desempeño geográfico de un candidato"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Por ahora retornamos datos básicos
            # En una implementación completa se analizarían los votos por ubicación
            
            cursor.execute("""
                SELECT nombre_completo FROM candidates WHERE id = ?
            """, (candidate_id,))
            
            result = cursor.fetchone()
            candidate_name = result['nombre_completo'] if result else 'Desconocido'
            
            conn.close()
            
            return {
                'candidate_id': candidate_id,
                'candidate_name': candidate_name,
                'best_municipality': 'FLORENCIA',  # Datos simulados
                'worst_municipality': 'SOLITA',
                'vote_distribution': {}
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo desempeño geográfico del candidato: {e}")
            return {}
    
    def _generate_hourly_participation(self) -> List[Dict[str, Any]]:
        """Generar datos simulados de participación por hora"""
        try:
            hours = []
            for hour in range(8, 17):  # 8 AM a 4 PM
                participation = {
                    'hour': f"{hour:02d}:00",
                    'votes_cast': hour * 1000 + (hour - 8) * 500,
                    'cumulative_percentage': min(((hour - 7) / 9) * 100, 100)
                }
                hours.append(participation)
            
            return hours
            
        except Exception as e:
            self.logger.error(f"Error generando participación por hora: {e}")
            return []
    
    def _get_user_audit_stats(self, filters: ReportFilter) -> Dict[str, Any]:
        """Obtener estadísticas de auditoría de usuarios"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Usuarios activos
            cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
            active_users = cursor.fetchone()[0]
            
            # Usuarios creados en el período (si se especifica)
            new_users_period = 0
            if filters.start_date and filters.end_date:
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE fecha_creacion BETWEEN ? AND ?
                """, (filters.start_date, filters.end_date))
                result = cursor.fetchone()
                new_users_period = result[0] if result else 0
            
            conn.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'new_users_period': new_users_period,
                'login_attempts': 0,  # Requiere tabla de logs
                'failed_logins': 0    # Requiere tabla de logs
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de usuarios: {e}")
            return {}
    
    def _get_system_activity_stats(self, filters: ReportFilter) -> Dict[str, Any]:
        """Obtener estadísticas de actividad del sistema"""
        try:
            # Por ahora retornamos datos simulados
            # En una implementación completa se analizarían logs del sistema
            
            return {
                'total_api_calls': 15000,
                'successful_operations': 14850,
                'failed_operations': 150,
                'average_response_time': 250,
                'peak_usage_hour': '14:00',
                'database_queries': 8500,
                'cache_hit_rate': 85.5
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de actividad: {e}")
            return {}
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """Verificar integridad de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            issues = []
            
            # Verificar candidatos sin información completa
            cursor.execute("""
                SELECT COUNT(*) FROM candidates 
                WHERE nombre_completo IS NULL OR nombre_completo = ''
            """)
            result = cursor.fetchone()
            if result and result[0] > 0:
                issues.append(f"{result[0]} candidatos sin nombre completo")
            
            # Verificar mesas sin información de votantes
            cursor.execute("""
                SELECT COUNT(*) FROM mesas_electorales 
                WHERE total_votantes_habilitados IS NULL OR total_votantes_habilitados = 0
            """)
            result = cursor.fetchone()
            if result and result[0] > 0:
                issues.append(f"{result[0]} mesas sin información de votantes habilitados")
            
            # Verificar ubicaciones sin nombre
            cursor.execute("""
                SELECT COUNT(*) FROM locations 
                WHERE (nombre_municipio IS NULL OR nombre_municipio = '') 
                AND (nombre_puesto IS NULL OR nombre_puesto = '')
            """)
            result = cursor.fetchone()
            if result and result[0] > 0:
                issues.append(f"{result[0]} ubicaciones sin nombre")
            
            conn.close()
            
            return {
                'status': 'OK' if not issues else 'WARNING',
                'issues': issues,
                'total_issues': len(issues),
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error verificando integridad de datos: {e}")
            return {
                'status': 'ERROR',
                'issues': ['Error al verificar integridad de datos'],
                'total_issues': 1,
                'checked_at': datetime.now().isoformat()
            }
    
    def _calculate_next_run(self, schedule_type: str) -> str:
        """Calcular próxima ejecución de reporte programado"""
        try:
            now = datetime.now()
            
            if schedule_type == 'daily':
                next_run = now + timedelta(days=1)
            elif schedule_type == 'weekly':
                next_run = now + timedelta(weeks=1)
            elif schedule_type == 'monthly':
                next_run = now + timedelta(days=30)
            else:
                next_run = now + timedelta(days=1)  # Default a diario
            
            return next_run.isoformat()
            
        except Exception as e:
            self.logger.error(f"Error calculando próxima ejecución: {e}")
            return (datetime.now() + timedelta(days=1)).isoformat()