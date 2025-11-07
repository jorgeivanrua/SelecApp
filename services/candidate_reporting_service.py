"""
Servicio de Reportes y Análisis de Candidatos
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import json
import logging
import statistics
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CandidateResult:
    """Clase para resultado de candidato"""
    candidate_id: int
    nombre_completo: str
    cedula: str
    numero_tarjeton: int
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    party_name: Optional[str] = None
    coalition_name: Optional[str] = None

@dataclass
class PartyResult:
    """Clase para resultado de partido"""
    party_id: int
    party_name: str
    siglas: str
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    total_candidatos: int
    mejor_candidato: Optional[CandidateResult] = None

@dataclass
class CoalitionResult:
    """Clase para resultado de coalición"""
    coalition_id: int
    coalition_name: str
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    total_candidatos: int
    partidos_participantes: List[str] = None

class CandidateReportingService:
    """Servicio para cálculo de resultados y reportes de candidatos"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logger
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== CÁLCULO DE RESULTADOS POR CANDIDATO ====================
    
    def calculate_candidate_results(self, election_type_id: int, 
                                  calculated_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcular resultados por candidato individual
        
        Args:
            election_type_id: ID del tipo de elección
            calculated_by: ID del usuario que realiza el cálculo
            
        Returns:
            Dict con resultados calculados
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener votos por candidato desde formularios E-14
            # TODO: Esta consulta debe adaptarse cuando se implementen los formularios E-14
            # Por ahora simulamos con datos de ejemplo
            
            # Obtener candidatos del tipo de elección
            cursor.execute('''
            SELECT c.*, pp.nombre_oficial as party_name, pp.siglas as party_siglas,
                   co.nombre_coalicion as coalition_name
            FROM candidates c
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            WHERE c.election_type_id = ? AND c.activo = 1
            ORDER BY c.numero_tarjeton
            ''', (election_type_id,))
            
            candidates = [dict(row) for row in cursor.fetchall()]
            
            if not candidates:
                return {
                    'success': False,
                    'error': 'No se encontraron candidatos para este tipo de elección'
                }
            
            # Simular votos por candidato (en producción esto vendría de formularios E-14)
            candidate_votes = self._simulate_candidate_votes(candidates)
            
            # Calcular totales y porcentajes
            total_votos_validos = sum(candidate_votes.values())
            
            results = []
            for candidate in candidates:
                candidate_id = candidate['id']
                votos = candidate_votes.get(candidate_id, 0)
                porcentaje = (votos / total_votos_validos * 100) if total_votos_validos > 0 else 0
                
                result = CandidateResult(
                    candidate_id=candidate_id,
                    nombre_completo=candidate['nombre_completo'],
                    cedula=candidate['cedula'],
                    numero_tarjeton=candidate['numero_tarjeton'],
                    total_votos=votos,
                    porcentaje_votacion=round(porcentaje, 2),
                    posicion_ranking=0,  # Se calculará después
                    party_name=candidate.get('party_name'),
                    coalition_name=candidate.get('coalition_name')
                )
                results.append(result)
            
            # Ordenar por votos y asignar ranking
            results.sort(key=lambda x: x.total_votos, reverse=True)
            for i, result in enumerate(results, 1):
                result.posicion_ranking = i
            
            # Guardar resultados en la base de datos
            self._save_candidate_results(results, election_type_id, calculated_by)
            
            # Calcular estadísticas adicionales
            statistics_data = self._calculate_candidate_statistics(results, election_type_id)
            
            conn.close()
            
            self.logger.info(f"Resultados calculados para {len(results)} candidatos")
            
            return {
                'success': True,
                'data': {
                    'candidates': [result.__dict__ for result in results],
                    'statistics': statistics_data,
                    'total_votos_validos': total_votos_validos,
                    'total_candidatos': len(results),
                    'fecha_calculo': datetime.now().isoformat()
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error calculando resultados de candidatos: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _simulate_candidate_votes(self, candidates: List[Dict]) -> Dict[int, int]:
        """Simular votos por candidato (temporal hasta implementar formularios E-14)"""
        import random
        
        candidate_votes = {}
        for candidate in candidates:
            # Simular votos aleatorios entre 50 y 5000
            candidate_votes[candidate['id']] = random.randint(50, 5000)
        
        return candidate_votes
    
    def _save_candidate_results(self, results: List[CandidateResult], 
                               election_type_id: int, calculated_by: Optional[int]):
        """Guardar resultados de candidatos en la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Limpiar resultados anteriores
            cursor.execute('''
            DELETE FROM candidate_results 
            WHERE election_type_id = ?
            ''', (election_type_id,))
            
            # Insertar nuevos resultados
            for result in results:
                cursor.execute('''
                INSERT INTO candidate_results 
                (candidate_id, election_type_id, total_votos, porcentaje_votacion, 
                 posicion_ranking, fecha_calculo, calculado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.candidate_id,
                    election_type_id,
                    result.total_votos,
                    result.porcentaje_votacion,
                    result.posicion_ranking,
                    datetime.now(),
                    calculated_by
                ))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            self.logger.error(f"Error guardando resultados de candidatos: {e}")
    
    def _calculate_candidate_statistics(self, results: List[CandidateResult], 
                                      election_type_id: int) -> Dict[str, Any]:
        """Calcular estadísticas de candidatos"""
        if not results:
            return {}
        
        votos = [result.total_votos for result in results]
        
        return {
            'promedio_votos': round(statistics.mean(votos), 2),
            'mediana_votos': statistics.median(votos),
            'desviacion_estandar': round(statistics.stdev(votos) if len(votos) > 1 else 0, 2),
            'votos_maximo': max(votos),
            'votos_minimo': min(votos),
            'rango_votos': max(votos) - min(votos),
            'candidato_ganador': results[0].nombre_completo if results else None,
            'margen_victoria': results[0].total_votos - results[1].total_votos if len(results) > 1 else 0
        }
    
    # ==================== CÁLCULO DE RESULTADOS POR PARTIDO ====================
    
    def calculate_party_results(self, election_type_id: int, 
                               calculated_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcular totales automáticos por partido político
        
        Args:
            election_type_id: ID del tipo de elección
            calculated_by: ID del usuario que realiza el cálculo
            
        Returns:
            Dict con resultados por partido
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener resultados de candidatos por partido
            cursor.execute('''
            SELECT pp.id as party_id, pp.nombre_oficial as party_name, pp.siglas,
                   SUM(cr.total_votos) as total_votos_partido,
                   COUNT(c.id) as total_candidatos,
                   MAX(cr.total_votos) as mejor_candidato_votos,
                   c.nombre_completo as mejor_candidato_nombre
            FROM political_parties pp
            JOIN candidates c ON pp.id = c.party_id
            JOIN candidate_results cr ON c.id = cr.candidate_id
            WHERE c.election_type_id = ? AND c.activo = 1
            GROUP BY pp.id, pp.nombre_oficial, pp.siglas
            ORDER BY total_votos_partido DESC
            ''', (election_type_id,))
            
            party_data = [dict(row) for row in cursor.fetchall()]
            
            if not party_data:
                return {
                    'success': False,
                    'error': 'No se encontraron resultados de partidos para este tipo de elección'
                }
            
            # Calcular porcentajes y rankings
            total_votos_todos_partidos = sum(party['total_votos_partido'] for party in party_data)
            
            results = []
            for i, party in enumerate(party_data, 1):
                porcentaje = (party['total_votos_partido'] / total_votos_todos_partidos * 100) if total_votos_todos_partidos > 0 else 0
                
                result = PartyResult(
                    party_id=party['party_id'],
                    party_name=party['party_name'],
                    siglas=party['siglas'],
                    total_votos=party['total_votos_partido'],
                    porcentaje_votacion=round(porcentaje, 2),
                    posicion_ranking=i,
                    total_candidatos=party['total_candidatos']
                )
                results.append(result)
            
            # Guardar resultados en la base de datos
            self._save_party_results(results, election_type_id, calculated_by)
            
            conn.close()
            
            self.logger.info(f"Resultados calculados para {len(results)} partidos")
            
            return {
                'success': True,
                'data': {
                    'parties': [result.__dict__ for result in results],
                    'total_votos_partidos': total_votos_todos_partidos,
                    'total_partidos': len(results),
                    'fecha_calculo': datetime.now().isoformat()
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error calculando resultados de partidos: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _save_party_results(self, results: List[PartyResult], 
                           election_type_id: int, calculated_by: Optional[int]):
        """Guardar resultados de partidos en la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Limpiar resultados anteriores
            cursor.execute('''
            DELETE FROM party_results 
            WHERE election_type_id = ?
            ''', (election_type_id,))
            
            # Insertar nuevos resultados
            for result in results:
                cursor.execute('''
                INSERT INTO party_results 
                (party_id, election_type_id, total_votos_partido, porcentaje_votacion_partido,
                 posicion_ranking_partido, total_candidatos, fecha_calculo, calculado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.party_id,
                    election_type_id,
                    result.total_votos,
                    result.porcentaje_votacion,
                    result.posicion_ranking,
                    result.total_candidatos,
                    datetime.now(),
                    calculated_by
                ))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            self.logger.error(f"Error guardando resultados de partidos: {e}")
    
    # ==================== CÁLCULO DE RESULTADOS POR COALICIÓN ====================
    
    def calculate_coalition_results(self, election_type_id: int, 
                                   calculated_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcular totales automáticos por coalición
        
        Args:
            election_type_id: ID del tipo de elección
            calculated_by: ID del usuario que realiza el cálculo
            
        Returns:
            Dict con resultados por coalición
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener resultados de candidatos por coalición
            cursor.execute('''
            SELECT co.id as coalition_id, co.nombre_coalicion,
                   SUM(cr.total_votos) as total_votos_coalicion,
                   COUNT(c.id) as total_candidatos,
                   GROUP_CONCAT(DISTINCT pp.nombre_oficial) as partidos_participantes
            FROM coalitions co
            JOIN candidates c ON co.id = c.coalition_id
            JOIN candidate_results cr ON c.id = cr.candidate_id
            LEFT JOIN coalition_parties cp ON co.id = cp.coalition_id
            LEFT JOIN political_parties pp ON cp.party_id = pp.id
            WHERE c.election_type_id = ? AND c.activo = 1
            GROUP BY co.id, co.nombre_coalicion
            ORDER BY total_votos_coalicion DESC
            ''', (election_type_id,))
            
            coalition_data = [dict(row) for row in cursor.fetchall()]
            
            if not coalition_data:
                return {
                    'success': True,
                    'data': {
                        'coalitions': [],
                        'total_votos_coaliciones': 0,
                        'total_coaliciones': 0,
                        'message': 'No se encontraron coaliciones con candidatos para este tipo de elección'
                    }
                }
            
            # Calcular porcentajes y rankings
            total_votos_todas_coaliciones = sum(coalition['total_votos_coalicion'] for coalition in coalition_data)
            
            results = []
            for i, coalition in enumerate(coalition_data, 1):
                porcentaje = (coalition['total_votos_coalicion'] / total_votos_todas_coaliciones * 100) if total_votos_todas_coaliciones > 0 else 0
                
                partidos_list = coalition['partidos_participantes'].split(',') if coalition['partidos_participantes'] else []
                
                result = CoalitionResult(
                    coalition_id=coalition['coalition_id'],
                    coalition_name=coalition['nombre_coalicion'],
                    total_votos=coalition['total_votos_coalicion'],
                    porcentaje_votacion=round(porcentaje, 2),
                    posicion_ranking=i,
                    total_candidatos=coalition['total_candidatos'],
                    partidos_participantes=partidos_list
                )
                results.append(result)
            
            # Guardar resultados en la base de datos
            self._save_coalition_results(results, election_type_id, calculated_by)
            
            conn.close()
            
            self.logger.info(f"Resultados calculados para {len(results)} coaliciones")
            
            return {
                'success': True,
                'data': {
                    'coalitions': [result.__dict__ for result in results],
                    'total_votos_coaliciones': total_votos_todas_coaliciones,
                    'total_coaliciones': len(results),
                    'fecha_calculo': datetime.now().isoformat()
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error calculando resultados de coaliciones: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _save_coalition_results(self, results: List[CoalitionResult], 
                               election_type_id: int, calculated_by: Optional[int]):
        """Guardar resultados de coaliciones en la base de datos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Limpiar resultados anteriores
            cursor.execute('''
            DELETE FROM coalition_results 
            WHERE election_type_id = ?
            ''', (election_type_id,))
            
            # Insertar nuevos resultados
            for result in results:
                partidos_json = json.dumps(result.partidos_participantes) if result.partidos_participantes else None
                
                cursor.execute('''
                INSERT INTO coalition_results 
                (coalition_id, election_type_id, total_votos_coalicion, porcentaje_votacion_coalicion,
                 posicion_ranking_coalicion, total_candidatos_coalicion, partidos_resultados, 
                 fecha_calculo, calculado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.coalition_id,
                    election_type_id,
                    result.total_votos,
                    result.porcentaje_votacion,
                    result.posicion_ranking,
                    result.total_candidatos,
                    partidos_json,
                    datetime.now(),
                    calculated_by
                ))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            self.logger.error(f"Error guardando resultados de coaliciones: {e}")
    
    # ==================== GENERACIÓN DE RANKINGS ====================
    
    def generate_candidate_rankings(self, election_type_id: int) -> Dict[str, Any]:
        """
        Generar rankings de candidatos por votación
        
        Args:
            election_type_id: ID del tipo de elección
            
        Returns:
            Dict con rankings de candidatos
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener candidatos ordenados por votos
            cursor.execute('''
            SELECT c.nombre_completo, c.cedula, c.numero_tarjeton,
                   cr.total_votos, cr.porcentaje_votacion, cr.posicion_ranking,
                   pp.nombre_oficial as party_name, pp.siglas as party_siglas,
                   co.nombre_coalicion as coalition_name
            FROM candidates c
            JOIN candidate_results cr ON c.id = cr.candidate_id
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            WHERE c.election_type_id = ? AND c.activo = 1
            ORDER BY cr.posicion_ranking
            ''', (election_type_id,))
            
            candidates_ranking = [dict(row) for row in cursor.fetchall()]
            
            # Generar rankings por categorías
            rankings = {
                'general': candidates_ranking,
                'top_10': candidates_ranking[:10],
                'por_partido': self._generate_party_rankings(election_type_id),
                'por_coalicion': self._generate_coalition_rankings(election_type_id)
            }
            
            conn.close()
            
            return {
                'success': True,
                'data': rankings
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error generando rankings: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _generate_party_rankings(self, election_type_id: int) -> List[Dict[str, Any]]:
        """Generar ranking de partidos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT pp.nombre_oficial, pp.siglas,
                   pr.total_votos_partido, pr.porcentaje_votacion_partido,
                   pr.posicion_ranking_partido, pr.total_candidatos
            FROM political_parties pp
            JOIN party_results pr ON pp.id = pr.party_id
            WHERE pr.election_type_id = ?
            ORDER BY pr.posicion_ranking_partido
            ''', (election_type_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error:
            return []
    
    def _generate_coalition_rankings(self, election_type_id: int) -> List[Dict[str, Any]]:
        """Generar ranking de coaliciones"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT co.nombre_coalicion,
                   cor.total_votos_coalicion, cor.porcentaje_votacion_coalicion,
                   cor.posicion_ranking_coalicion, cor.total_candidatos_coalicion
            FROM coalitions co
            JOIN coalition_results cor ON co.id = cor.coalition_id
            WHERE cor.election_type_id = ?
            ORDER BY cor.posicion_ranking_coalicion
            ''', (election_type_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error:
            return []
    
    # ==================== REPORTES DETALLADOS ====================
    
    def generate_detailed_candidate_report(self, candidate_id: int) -> Dict[str, Any]:
        """
        Generar reporte detallado con análisis estadístico por candidato
        
        Args:
            candidate_id: ID del candidato
            
        Returns:
            Dict con reporte detallado del candidato
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información del candidato
            cursor.execute('''
            SELECT c.*, cr.total_votos, cr.porcentaje_votacion, cr.posicion_ranking,
                   pp.nombre_oficial as party_name, pp.siglas as party_siglas,
                   co.nombre_coalicion as coalition_name,
                   et.nombre as election_type_name
            FROM candidates c
            LEFT JOIN candidate_results cr ON c.id = cr.candidate_id
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            LEFT JOIN election_types et ON c.election_type_id = et.id
            WHERE c.id = ?
            ''', (candidate_id,))
            
            candidate_data = cursor.fetchone()
            if not candidate_data:
                return {
                    'success': False,
                    'error': 'Candidato no encontrado'
                }
            
            candidate_dict = dict(candidate_data)
            
            # Obtener estadísticas comparativas
            cursor.execute('''
            SELECT AVG(total_votos) as promedio_votos,
                   MAX(total_votos) as maximo_votos,
                   MIN(total_votos) as minimo_votos,
                   COUNT(*) as total_candidatos
            FROM candidate_results cr
            JOIN candidates c ON cr.candidate_id = c.id
            WHERE c.election_type_id = ?
            ''', (candidate_dict['election_type_id'],))
            
            stats = dict(cursor.fetchone())
            
            # Calcular análisis estadístico
            analysis = {
                'rendimiento_vs_promedio': 'superior' if candidate_dict['total_votos'] > stats['promedio_votos'] else 'inferior',
                'diferencia_vs_promedio': candidate_dict['total_votos'] - stats['promedio_votos'] if stats['promedio_votos'] else 0,
                'percentil': self._calculate_percentile(candidate_dict['total_votos'], candidate_dict['election_type_id']),
                'distancia_al_ganador': self._calculate_distance_to_winner(candidate_id, candidate_dict['election_type_id'])
            }
            
            # TODO: Agregar análisis geográfico cuando se implementen los formularios E-14
            geographic_analysis = {
                'mejor_municipio': 'Por implementar',
                'peor_municipio': 'Por implementar',
                'distribucion_geografica': 'Por implementar'
            }
            
            conn.close()
            
            return {
                'success': True,
                'data': {
                    'candidate_info': candidate_dict,
                    'comparative_stats': stats,
                    'statistical_analysis': analysis,
                    'geographic_analysis': geographic_analysis,
                    'fecha_reporte': datetime.now().isoformat()
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error generando reporte detallado: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _calculate_percentile(self, candidate_votes: int, election_type_id: int) -> float:
        """Calcular percentil del candidato"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT total_votos FROM candidate_results cr
            JOIN candidates c ON cr.candidate_id = c.id
            WHERE c.election_type_id = ?
            ORDER BY total_votos
            ''', (election_type_id,))
            
            all_votes = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not all_votes:
                return 0
            
            position = sum(1 for vote in all_votes if vote < candidate_votes)
            return (position / len(all_votes)) * 100
            
        except sqlite3.Error:
            return 0
    
    def _calculate_distance_to_winner(self, candidate_id: int, election_type_id: int) -> int:
        """Calcular distancia en votos al ganador"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener votos del ganador
            cursor.execute('''
            SELECT MAX(cr.total_votos) as max_votos
            FROM candidate_results cr
            JOIN candidates c ON cr.candidate_id = c.id
            WHERE c.election_type_id = ?
            ''', (election_type_id,))
            
            max_votes = cursor.fetchone()[0] or 0
            
            # Obtener votos del candidato
            cursor.execute('''
            SELECT cr.total_votos
            FROM candidate_results cr
            WHERE cr.candidate_id = ?
            ''', (candidate_id,))
            
            candidate_votes = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return max_votes - candidate_votes
            
        except sqlite3.Error:
            return 0
    
    # ==================== REPORTES COMPARATIVOS ====================
    
    def generate_comparative_report(self, election_type_id: int) -> Dict[str, Any]:
        """
        Generar reportes comparativos entre partidos y coaliciones
        
        Args:
            election_type_id: ID del tipo de elección
            
        Returns:
            Dict con reportes comparativos
        """
        try:
            # Obtener resultados de candidatos, partidos y coaliciones
            candidate_results = self.calculate_candidate_results(election_type_id)
            party_results = self.calculate_party_results(election_type_id)
            coalition_results = self.calculate_coalition_results(election_type_id)
            
            if not candidate_results['success']:
                return candidate_results
            
            # Generar comparaciones
            comparative_data = {
                'resumen_general': {
                    'total_candidatos': len(candidate_results['data']['candidates']),
                    'total_partidos': len(party_results['data']['parties']) if party_results['success'] else 0,
                    'total_coaliciones': len(coalition_results['data']['coalitions']) if coalition_results['success'] else 0,
                    'total_votos_validos': candidate_results['data']['total_votos_validos']
                },
                'top_candidatos': candidate_results['data']['candidates'][:10],
                'ranking_partidos': party_results['data']['parties'] if party_results['success'] else [],
                'ranking_coaliciones': coalition_results['data']['coalitions'] if coalition_results['success'] else [],
                'analisis_competitividad': self._analyze_competitiveness(candidate_results['data']['candidates']),
                'distribucion_votos': self._analyze_vote_distribution(candidate_results['data']['candidates'])
            }
            
            return {
                'success': True,
                'data': comparative_data
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte comparativo: {e}")
            return {
                'success': False,
                'error': f'Error generando reporte: {str(e)}'
            }
    
    def _analyze_competitiveness(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Analizar competitividad de la elección"""
        if len(candidates) < 2:
            return {'competitividad': 'baja', 'margen_victoria': 0}
        
        winner_votes = candidates[0]['total_votos']
        runner_up_votes = candidates[1]['total_votos']
        margin = winner_votes - runner_up_votes
        
        total_votes = sum(c['total_votos'] for c in candidates)
        margin_percentage = (margin / total_votes * 100) if total_votes > 0 else 0
        
        if margin_percentage < 5:
            competitiveness = 'muy_alta'
        elif margin_percentage < 15:
            competitiveness = 'alta'
        elif margin_percentage < 30:
            competitiveness = 'media'
        else:
            competitiveness = 'baja'
        
        return {
            'competitividad': competitiveness,
            'margen_victoria': margin,
            'margen_porcentaje': round(margin_percentage, 2),
            'candidatos_competitivos': len([c for c in candidates if c['porcentaje_votacion'] > 5])
        }
    
    def _analyze_vote_distribution(self, candidates: List[Dict]) -> Dict[str, Any]:
        """Analizar distribución de votos"""
        if not candidates:
            return {}
        
        votes = [c['total_votos'] for c in candidates]
        
        return {
            'concentracion_top_3': sum(votes[:3]) / sum(votes) * 100 if sum(votes) > 0 else 0,
            'concentracion_top_5': sum(votes[:5]) / sum(votes) * 100 if sum(votes) > 0 else 0,
            'candidatos_con_menos_1_pct': len([c for c in candidates if c['porcentaje_votacion'] < 1]),
            'indice_fragmentacion': len([c for c in candidates if c['porcentaje_votacion'] > 5])
        }

if __name__ == "__main__":
    print("🗳️  Servicio de Reportes y Análisis de Candidatos")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    
    # Ejemplo de uso
    service = CandidateReportingService()
    
    # Simular cálculo de resultados
    print("Funcionalidades disponibles:")
    print("- Cálculo de resultados por candidato")
    print("- Cálculo de totales por partido")
    print("- Cálculo de totales por coalición")
    print("- Generación de rankings")
    print("- Reportes detallados por candidato")
    print("- Reportes comparativos")
    print("- Análisis estadístico y geográfico")