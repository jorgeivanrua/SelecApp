"""
Módulo Reportes - Servicios
Lógica de negocio para generación de reportes
"""

import logging
from datetime import datetime, timedelta
import io
import json

logger = logging.getLogger(__name__)

class ReportService:
    """Servicio para generación de reportes"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def generate_electoral_summary(self, process_id=None, election_type_id=None):
        """Generar resumen electoral general"""
        try:
            summary = {}
            
            # Estadísticas generales
            general_stats = self._get_general_electoral_stats(process_id, election_type_id)
            summary['general_stats'] = general_stats
            
            # Progreso de recolección
            collection_progress = self._get_collection_progress(process_id)
            summary['collection_progress'] = collection_progress
            
            # Top candidatos
            top_candidates = self._get_top_candidates(election_type_id, limit=10)
            summary['top_candidates'] = top_candidates
            
            # Participación por municipio
            participation_by_municipality = self._get_participation_by_municipality(process_id)
            summary['participation_by_municipality'] = participation_by_municipality
            
            return summary
            
        except Exception as e:
            logger.error(f"Generate electoral summary error: {e}")
            raise
    
    def generate_candidate_results_report(self, election_type_id=None, party_id=None, top_n=10):
        """Generar reporte de resultados de candidatos"""
        try:
            base_query = """
                SELECT 
                    c.id,
                    c.nombre_completo,
                    c.cargo_aspirado,
                    c.numero_tarjeton,
                    p.siglas as partido_siglas,
                    p.nombre_oficial as partido_nombre,
                    et.nombre as tipo_eleccion,
                    COALESCE(cr.total_votos, 0) as total_votos,
                    COALESCE(cr.porcentaje_votacion, 0) as porcentaje_votacion,
                    COALESCE(cr.posicion_ranking, 999) as posicion_ranking
                FROM candidates c
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN election_types et ON c.election_type_id = et.id
                LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
            """
            
            conditions = []
            params = {}
            
            if election_type_id:
                conditions.append("c.election_type_id = :election_type_id")
                params['election_type_id'] = election_type_id
            
            if party_id:
                conditions.append("c.party_id = :party_id")
                params['party_id'] = party_id
            
            conditions.append("c.activo = 1")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += f" ORDER BY total_votos DESC LIMIT {top_n}"
            
            result = self.db.execute_query(base_query, params)
            
            candidates = [
                {
                    'id': row[0],
                    'nombre_completo': row[1],
                    'cargo_aspirado': row[2],
                    'numero_tarjeton': row[3],
                    'partido_siglas': row[4],
                    'partido_nombre': row[5],
                    'tipo_eleccion': row[6],
                    'total_votos': row[7],
                    'porcentaje_votacion': row[8],
                    'posicion_ranking': row[9]
                }
                for row in result
            ]
            
            # Agregar estadísticas adicionales
            stats = self._get_candidate_results_stats(election_type_id, party_id)
            
            return {
                'candidates': candidates,
                'statistics': stats,
                'generated_at': datetime.utcnow().isoformat(),
                'filters': {
                    'election_type_id': election_type_id,
                    'party_id': party_id,
                    'top_n': top_n
                }
            }
            
        except Exception as e:
            logger.error(f"Generate candidate results report error: {e}")
            raise
    
    def generate_party_performance_report(self, election_type_id=None):
        """Generar reporte de desempeño por partido"""
        try:
            query = """
                SELECT 
                    p.id,
                    p.nombre_oficial,
                    p.siglas,
                    COUNT(c.id) as total_candidatos,
                    SUM(COALESCE(cr.total_votos, 0)) as total_votos_partido,
                    AVG(COALESCE(cr.porcentaje_votacion, 0)) as promedio_porcentaje,
                    MAX(COALESCE(cr.total_votos, 0)) as mejor_candidato_votos,
                    MIN(COALESCE(cr.total_votos, 0)) as peor_candidato_votos
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
                GROUP BY p.id, p.nombre_oficial, p.siglas
                HAVING total_candidatos > 0
                ORDER BY total_votos_partido DESC
            """
            
            result = self.db.execute_query(query, params)
            
            parties = [
                {
                    'id': row[0],
                    'nombre_oficial': row[1],
                    'siglas': row[2],
                    'total_candidatos': row[3],
                    'total_votos_partido': row[4],
                    'promedio_porcentaje': round(row[5], 2),
                    'mejor_candidato_votos': row[6],
                    'peor_candidato_votos': row[7]
                }
                for row in result
            ]
            
            return {
                'parties': parties,
                'generated_at': datetime.utcnow().isoformat(),
                'filters': {
                    'election_type_id': election_type_id
                }
            }
            
        except Exception as e:
            logger.error(f"Generate party performance report error: {e}")
            raise
    
    def generate_geographic_analysis(self, election_type_id=None, candidate_id=None):
        """Generar análisis geográfico de resultados"""
        try:
            # Análisis por municipio
            municipality_query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total_mesas,
                    SUM(me.total_votantes_habilitados) as total_votantes,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as mesas_completadas
                FROM locations l
                JOIN locations lp ON l.id = lp.parent_id
                JOIN mesas_electorales me ON lp.id = me.puesto_id
                WHERE l.tipo = 'MUNICIPIO'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY total_votantes DESC
            """
            
            municipality_result = self.db.execute_query(municipality_query)
            
            municipalities = [
                {
                    'nombre_municipio': row[0],
                    'total_mesas': row[1],
                    'total_votantes': row[2],
                    'mesas_completadas': row[3],
                    'porcentaje_completado': round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in municipality_result
            ]
            
            # Si se especifica un candidato, obtener su desempeño geográfico
            candidate_performance = None
            if candidate_id:
                candidate_performance = self._get_candidate_geographic_performance(candidate_id)
            
            return {
                'municipalities': municipalities,
                'candidate_performance': candidate_performance,
                'generated_at': datetime.utcnow().isoformat(),
                'filters': {
                    'election_type_id': election_type_id,
                    'candidate_id': candidate_id
                }
            }
            
        except Exception as e:
            logger.error(f"Generate geographic analysis error: {e}")
            raise
    
    def generate_participation_stats(self, process_id=None):
        """Generar estadísticas de participación"""
        try:
            # Estadísticas generales de participación
            general_query = """
                SELECT 
                    COUNT(*) as total_mesas,
                    SUM(total_votantes_habilitados) as total_votantes_habilitados,
                    COUNT(CASE WHEN estado_recoleccion = 'completada' THEN 1 END) as mesas_completadas,
                    COUNT(CASE WHEN estado_recoleccion = 'en_proceso' THEN 1 END) as mesas_en_proceso,
                    COUNT(CASE WHEN estado_recoleccion = 'pendiente' THEN 1 END) as mesas_pendientes
                FROM mesas_electorales
            """
            
            general_result = self.db.execute_query(general_query)
            general_stats = general_result[0] if general_result else (0, 0, 0, 0, 0)
            
            # Participación por hora (simulada)
            hourly_participation = self._get_hourly_participation_simulation()
            
            # Participación por tipo de elección
            election_type_query = """
                SELECT 
                    et.nombre,
                    COUNT(c.id) as total_candidatos,
                    SUM(COALESCE(cr.total_votos, 0)) as total_votos
                FROM election_types et
                LEFT JOIN candidates c ON et.id = c.election_type_id AND c.activo = 1
                LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
                WHERE et.activo = 1
                GROUP BY et.id, et.nombre
                ORDER BY total_votos DESC
            """
            
            election_type_result = self.db.execute_query(election_type_query)
            
            participation_by_election = [
                {
                    'tipo_eleccion': row[0],
                    'total_candidatos': row[1],
                    'total_votos': row[2]
                }
                for row in election_type_result
            ]
            
            return {
                'general_stats': {
                    'total_mesas': general_stats[0],
                    'total_votantes_habilitados': general_stats[1],
                    'mesas_completadas': general_stats[2],
                    'mesas_en_proceso': general_stats[3],
                    'mesas_pendientes': general_stats[4],
                    'porcentaje_completado': round((general_stats[2] / general_stats[0] * 100) if general_stats[0] > 0 else 0, 2)
                },
                'hourly_participation': hourly_participation,
                'participation_by_election': participation_by_election,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generate participation stats error: {e}")
            raise
    
    def generate_system_audit_report(self, start_date=None, end_date=None):
        """Generar reporte de auditoría del sistema"""
        try:
            # Estadísticas de usuarios
            user_stats = self._get_user_audit_stats(start_date, end_date)
            
            # Actividad del sistema
            system_activity = self._get_system_activity_stats(start_date, end_date)
            
            # Integridad de datos
            data_integrity = self._check_data_integrity()
            
            return {
                'user_stats': user_stats,
                'system_activity': system_activity,
                'data_integrity': data_integrity,
                'audit_period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generate system audit report error: {e}")
            raise
    
    def export_report_to_excel(self, report_type, filters, user_id):
        """Exportar reporte a Excel"""
        try:
            # Esta es una implementación básica
            # En producción se usaría una librería como openpyxl o xlsxwriter
            
            # Generar datos del reporte
            report_data = self._get_report_data(report_type, filters)
            
            # Crear archivo Excel en memoria (simulado)
            excel_buffer = io.BytesIO()
            
            # Aquí iría la lógica real de creación del Excel
            # Por ahora retornamos un buffer vacío como ejemplo
            excel_buffer.write(b"Excel file content would go here")
            excel_buffer.seek(0)
            
            return excel_buffer
            
        except Exception as e:
            logger.error(f"Export to Excel error: {e}")
            return None
    
    def export_report_to_pdf(self, report_type, filters, user_id):
        """Exportar reporte a PDF"""
        try:
            # Esta es una implementación básica
            # En producción se usaría una librería como reportlab o weasyprint
            
            # Generar datos del reporte
            report_data = self._get_report_data(report_type, filters)
            
            # Crear archivo PDF en memoria (simulado)
            pdf_buffer = io.BytesIO()
            
            # Aquí iría la lógica real de creación del PDF
            # Por ahora retornamos un buffer vacío como ejemplo
            pdf_buffer.write(b"PDF file content would go here")
            pdf_buffer.seek(0)
            
            return pdf_buffer
            
        except Exception as e:
            logger.error(f"Export to PDF error: {e}")
            return None
    
    def get_scheduled_reports(self, user_id):
        """Obtener reportes programados del usuario"""
        try:
            # Esta funcionalidad requeriría una tabla de reportes programados
            # Por ahora retornamos datos de ejemplo
            
            return [
                {
                    'id': 1,
                    'name': 'Reporte Semanal de Resultados',
                    'type': 'candidate_results',
                    'schedule': 'weekly',
                    'next_run': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    'active': True
                },
                {
                    'id': 2,
                    'name': 'Resumen Diario de Participación',
                    'type': 'participation_stats',
                    'schedule': 'daily',
                    'next_run': (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    'active': True
                }
            ]
            
        except Exception as e:
            logger.error(f"Get scheduled reports error: {e}")
            raise
    
    def create_scheduled_report(self, data, user_id):
        """Crear reporte programado"""
        try:
            # Esta funcionalidad requeriría una tabla de reportes programados
            # Por ahora simulamos la creación
            
            schedule_id = 123  # ID simulado
            
            logger.info(f"Scheduled report created: {data['name']} by user {user_id}")
            
            return schedule_id
            
        except Exception as e:
            logger.error(f"Create scheduled report error: {e}")
            raise
    
    def get_report_templates(self):
        """Obtener plantillas de reportes disponibles"""
        try:
            templates = [
                {
                    'id': 'electoral_summary',
                    'name': 'Resumen Electoral',
                    'description': 'Resumen general del proceso electoral',
                    'parameters': ['process_id', 'election_type_id']
                },
                {
                    'id': 'candidate_results',
                    'name': 'Resultados de Candidatos',
                    'description': 'Resultados detallados por candidato',
                    'parameters': ['election_type_id', 'party_id', 'top_n']
                },
                {
                    'id': 'party_performance',
                    'name': 'Desempeño por Partido',
                    'description': 'Análisis de desempeño de partidos políticos',
                    'parameters': ['election_type_id']
                },
                {
                    'id': 'geographic_analysis',
                    'name': 'Análisis Geográfico',
                    'description': 'Análisis de resultados por ubicación geográfica',
                    'parameters': ['election_type_id', 'candidate_id']
                },
                {
                    'id': 'participation_stats',
                    'name': 'Estadísticas de Participación',
                    'description': 'Estadísticas de participación electoral',
                    'parameters': ['process_id']
                }
            ]
            
            return templates
            
        except Exception as e:
            logger.error(f"Get report templates error: {e}")
            raise
    
    # Métodos auxiliares privados
    
    def _get_general_electoral_stats(self, process_id=None, election_type_id=None):
        """Obtener estadísticas generales electorales"""
        try:
            stats = {}
            
            # Total de candidatos
            candidate_query = "SELECT COUNT(*) FROM candidates WHERE activo = 1"
            candidate_result = self.db.execute_query(candidate_query)
            stats['total_candidates'] = candidate_result[0][0] if candidate_result else 0
            
            # Total de partidos
            party_query = "SELECT COUNT(*) FROM political_parties WHERE activo = 1"
            party_result = self.db.execute_query(party_query)
            stats['total_parties'] = party_result[0][0] if party_result else 0
            
            # Total de mesas
            mesa_query = "SELECT COUNT(*) FROM mesas_electorales"
            mesa_result = self.db.execute_query(mesa_query)
            stats['total_mesas'] = mesa_result[0][0] if mesa_result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Get general electoral stats error: {e}")
            return {}
    
    def _get_collection_progress(self, process_id=None):
        """Obtener progreso de recolección"""
        try:
            query = """
                SELECT 
                    estado_recoleccion,
                    COUNT(*) as count
                FROM mesas_electorales
                GROUP BY estado_recoleccion
            """
            
            result = self.db.execute_query(query)
            
            progress = {}
            total = 0
            
            for row in result:
                progress[row[0]] = row[1]
                total += row[1]
            
            # Calcular porcentajes
            for estado in progress:
                progress[f"{estado}_percentage"] = round((progress[estado] / total * 100) if total > 0 else 0, 2)
            
            progress['total'] = total
            
            return progress
            
        except Exception as e:
            logger.error(f"Get collection progress error: {e}")
            return {}
    
    def _get_top_candidates(self, election_type_id=None, limit=10):
        """Obtener top candidatos"""
        try:
            query = """
                SELECT 
                    c.nombre_completo,
                    p.siglas,
                    COALESCE(cr.total_votos, 0) as votos
                FROM candidates c
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
                WHERE c.activo = 1
            """
            
            if election_type_id:
                query += f" AND c.election_type_id = {election_type_id}"
            
            query += f" ORDER BY votos DESC LIMIT {limit}"
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'nombre': row[0],
                    'partido': row[1],
                    'votos': row[2]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get top candidates error: {e}")
            return []
    
    def _get_participation_by_municipality(self, process_id=None):
        """Obtener participación por municipio"""
        try:
            query = """
                SELECT 
                    l.nombre_municipio,
                    COUNT(me.id) as total_mesas,
                    COUNT(CASE WHEN me.estado_recoleccion = 'completada' THEN 1 END) as completadas
                FROM locations l
                JOIN locations lp ON l.id = lp.parent_id
                JOIN mesas_electorales me ON lp.id = me.puesto_id
                WHERE l.tipo = 'MUNICIPIO'
                GROUP BY l.id, l.nombre_municipio
                ORDER BY completadas DESC
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'municipio': row[0],
                    'total_mesas': row[1],
                    'completadas': row[2],
                    'porcentaje': round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get participation by municipality error: {e}")
            return []
    
    def _get_candidate_results_stats(self, election_type_id=None, party_id=None):
        """Obtener estadísticas de resultados de candidatos"""
        try:
            # Implementación básica de estadísticas
            return {
                'total_votes_cast': 0,
                'average_votes_per_candidate': 0,
                'highest_vote_count': 0,
                'lowest_vote_count': 0
            }
            
        except Exception as e:
            logger.error(f"Get candidate results stats error: {e}")
            return {}
    
    def _get_candidate_geographic_performance(self, candidate_id):
        """Obtener desempeño geográfico de un candidato"""
        try:
            # Esta funcionalidad requeriría datos más detallados
            # Por ahora retornamos datos de ejemplo
            return {
                'best_municipality': 'FLORENCIA',
                'worst_municipality': 'SOLITA',
                'vote_distribution': {}
            }
            
        except Exception as e:
            logger.error(f"Get candidate geographic performance error: {e}")
            return {}
    
    def _get_hourly_participation_simulation(self):
        """Simular participación por hora"""
        try:
            # Datos simulados de participación por hora
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
            logger.error(f"Get hourly participation simulation error: {e}")
            return []
    
    def _get_user_audit_stats(self, start_date=None, end_date=None):
        """Obtener estadísticas de auditoría de usuarios"""
        try:
            return {
                'total_users': 467,
                'active_users': 450,
                'new_users_period': 15,
                'login_attempts': 1250,
                'failed_logins': 23
            }
            
        except Exception as e:
            logger.error(f"Get user audit stats error: {e}")
            return {}
    
    def _get_system_activity_stats(self, start_date=None, end_date=None):
        """Obtener estadísticas de actividad del sistema"""
        try:
            return {
                'total_api_calls': 15000,
                'successful_operations': 14850,
                'failed_operations': 150,
                'average_response_time': 250,
                'peak_usage_hour': '14:00'
            }
            
        except Exception as e:
            logger.error(f"Get system activity stats error: {e}")
            return {}
    
    def _check_data_integrity(self):
        """Verificar integridad de datos"""
        try:
            issues = []
            
            # Verificar candidatos sin partido ni coalición
            orphan_candidates = self.db.execute_query("""
                SELECT COUNT(*) FROM candidates 
                WHERE party_id IS NULL AND coalition_id IS NULL AND es_independiente = 0
            """)
            
            if orphan_candidates and orphan_candidates[0][0] > 0:
                issues.append(f"{orphan_candidates[0][0]} candidates without party affiliation")
            
            # Verificar mesas sin testigo
            unassigned_mesas = self.db.execute_query("""
                SELECT COUNT(*) FROM mesas_electorales 
                WHERE testigo_asignado_id IS NULL
            """)
            
            if unassigned_mesas and unassigned_mesas[0][0] > 0:
                issues.append(f"{unassigned_mesas[0][0]} mesas without assigned witness")
            
            return {
                'status': 'OK' if not issues else 'WARNING',
                'issues': issues,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Check data integrity error: {e}")
            return {'status': 'ERROR', 'issues': ['Failed to check data integrity']}
    
    def _get_report_data(self, report_type, filters):
        """Obtener datos para reporte específico"""
        try:
            if report_type == 'electoral_summary':
                return self.generate_electoral_summary(
                    filters.get('process_id'),
                    filters.get('election_type_id')
                )
            elif report_type == 'candidate_results':
                return self.generate_candidate_results_report(
                    filters.get('election_type_id'),
                    filters.get('party_id'),
                    filters.get('top_n', 10)
                )
            # Agregar más tipos de reporte según sea necesario
            
            return {}
            
        except Exception as e:
            logger.error(f"Get report data error: {e}")
            return {}