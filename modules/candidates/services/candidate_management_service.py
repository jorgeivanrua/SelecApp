"""
Servicio de Gestión de Candidatos, Partidos Políticos y Coaliciones
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

from ..models import PoliticalPartyData, CoalitionData, CandidateData

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandidateManagementService:
    """Servicio para gestión completa de candidatos, partidos y coaliciones"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logger
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== GESTIÓN DE PARTIDOS POLÍTICOS ====================
    
    def create_political_party(self, party_data: PoliticalPartyData, created_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Crear un nuevo partido político con validación de datos
        
        Args:
            party_data: Datos del partido político
            created_by: ID del usuario que crea el partido
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos requeridos
            if not party_data.nombre_oficial or not party_data.siglas:
                return {
                    'success': False,
                    'error': 'Nombre oficial y siglas son requeridos'
                }
            
            # Validar que las siglas no existan
            if self._party_siglas_exists(party_data.siglas):
                return {
                    'success': False,
                    'error': f'Las siglas {party_data.siglas} ya están en uso'
                }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO political_parties 
            (nombre_oficial, siglas, color_representativo, logo_url, descripcion, 
             fundacion_year, ideologia, activo, reconocido_oficialmente, creado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                party_data.nombre_oficial,
                party_data.siglas,
                party_data.color_representativo,
                party_data.logo_url,
                party_data.descripcion,
                party_data.fundacion_year,
                party_data.ideologia,
                party_data.activo,
                party_data.reconocido_oficialmente,
                created_by
            ))
            
            party_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Partido político creado: {party_data.nombre_oficial} ({party_data.siglas})")
            
            return {
                'success': True,
                'party_id': party_id,
                'message': f'Partido {party_data.nombre_oficial} creado exitosamente'
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error creando partido político: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def get_political_parties(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Obtener lista de partidos políticos
        
        Args:
            active_only: Si solo obtener partidos activos
            
        Returns:
            Lista de partidos políticos
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM political_parties"
            if active_only:
                query += " WHERE activo = 1"
            query += " ORDER BY nombre_oficial"
            
            cursor.execute(query)
            parties = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return parties
            
        except sqlite3.Error as e:
            self.logger.error(f"Error obteniendo partidos políticos: {e}")
            return []
    
    def _party_siglas_exists(self, siglas: str) -> bool:
        """Verificar si las siglas de un partido ya existen"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM political_parties WHERE siglas = ?", (siglas,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except sqlite3.Error:
            return False
    
    # ==================== GESTIÓN DE COALICIONES ====================
    
    def create_coalition(self, coalition_data: CoalitionData, created_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Crear una nueva coalición entre partidos
        
        Args:
            coalition_data: Datos de la coalición
            created_by: ID del usuario que crea la coalición
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            if not coalition_data.nombre_coalicion:
                return {
                    'success': False,
                    'error': 'Nombre de coalición es requerido'
                }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear la coalición
            cursor.execute('''
            INSERT INTO coalitions 
            (nombre_coalicion, descripcion, fecha_formacion, activo, creado_por)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                coalition_data.nombre_coalicion,
                coalition_data.descripcion,
                coalition_data.fecha_formacion,
                coalition_data.activo,
                created_by
            ))
            
            coalition_id = cursor.lastrowid
            
            # Asociar partidos si se proporcionaron
            if coalition_data.partidos_ids:
                for party_id in coalition_data.partidos_ids:
                    cursor.execute('''
                    INSERT INTO coalition_parties (coalition_id, party_id)
                    VALUES (?, ?)
                    ''', (coalition_id, party_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Coalición creada: {coalition_data.nombre_coalicion}")
            
            return {
                'success': True,
                'coalition_id': coalition_id,
                'message': f'Coalición {coalition_data.nombre_coalicion} creada exitosamente'
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error creando coalición: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def add_party_to_coalition(self, coalition_id: int, party_id: int, 
                              es_principal: bool = False, 
                              porcentaje_participacion: Optional[float] = None) -> Dict[str, Any]:
        """
        Agregar un partido a una coalición
        
        Args:
            coalition_id: ID de la coalición
            party_id: ID del partido
            es_principal: Si es el partido principal de la coalición
            porcentaje_participacion: Porcentaje de participación del partido
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que no esté ya en la coalición
            cursor.execute('''
            SELECT COUNT(*) FROM coalition_parties 
            WHERE coalition_id = ? AND party_id = ? AND fecha_retiro IS NULL
            ''', (coalition_id, party_id))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {
                    'success': False,
                    'error': 'El partido ya está en esta coalición'
                }
            
            cursor.execute('''
            INSERT INTO coalition_parties 
            (coalition_id, party_id, es_partido_principal, porcentaje_participacion)
            VALUES (?, ?, ?, ?)
            ''', (coalition_id, party_id, es_principal, porcentaje_participacion))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Partido agregado a la coalición exitosamente'
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error agregando partido a coalición: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def get_coalitions(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Obtener lista de coaliciones con sus partidos
        
        Args:
            active_only: Si solo obtener coaliciones activas
            
        Returns:
            Lista de coaliciones con partidos asociados
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener coaliciones
            query = "SELECT * FROM coalitions"
            if active_only:
                query += " WHERE activo = 1"
            query += " ORDER BY nombre_coalicion"
            
            cursor.execute(query)
            coalitions = [dict(row) for row in cursor.fetchall()]
            
            # Obtener partidos de cada coalición
            for coalition in coalitions:
                cursor.execute('''
                SELECT pp.*, cp.es_partido_principal, cp.porcentaje_participacion
                FROM political_parties pp
                JOIN coalition_parties cp ON pp.id = cp.party_id
                WHERE cp.coalition_id = ? AND cp.fecha_retiro IS NULL
                ORDER BY cp.es_partido_principal DESC, pp.nombre_oficial
                ''', (coalition['id'],))
                
                coalition['partidos'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return coalitions
            
        except sqlite3.Error as e:
            self.logger.error(f"Error obteniendo coaliciones: {e}")
            return []
    
    # ==================== GESTIÓN DE CANDIDATOS ====================
    
    def create_candidate(self, candidate_data: CandidateData, created_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Crear un nuevo candidato con validación de datos
        
        Args:
            candidate_data: Datos del candidato
            created_by: ID del usuario que crea el candidato
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos requeridos
            validation_result = self._validate_candidate_data(candidate_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Verificar duplicados
            if self._candidate_exists(candidate_data.cedula, candidate_data.election_type_id):
                return {
                    'success': False,
                    'error': f'Ya existe un candidato con cédula {candidate_data.cedula} para este tipo de elección'
                }
            
            # Verificar número de tarjetón único
            if self._tarjeton_exists(candidate_data.numero_tarjeton, candidate_data.election_type_id):
                return {
                    'success': False,
                    'error': f'El número de tarjetón {candidate_data.numero_tarjeton} ya está en uso para este tipo de elección'
                }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO candidates 
            (nombre_completo, cedula, numero_tarjeton, cargo_aspirado, election_type_id,
             circunscripcion, party_id, coalition_id, es_independiente, foto_url,
             biografia, propuestas, experiencia, activo, habilitado_oficialmente, creado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_data.nombre_completo,
                candidate_data.cedula,
                candidate_data.numero_tarjeton,
                candidate_data.cargo_aspirado,
                candidate_data.election_type_id,
                candidate_data.circunscripcion,
                candidate_data.party_id,
                candidate_data.coalition_id,
                candidate_data.es_independiente,
                candidate_data.foto_url,
                candidate_data.biografia,
                candidate_data.propuestas,
                candidate_data.experiencia,
                candidate_data.activo,
                candidate_data.habilitado_oficialmente,
                created_by
            ))
            
            candidate_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Candidato creado: {candidate_data.nombre_completo} ({candidate_data.cedula})")
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'message': f'Candidato {candidate_data.nombre_completo} creado exitosamente'
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error creando candidato: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _validate_candidate_data(self, candidate_data: CandidateData) -> Dict[str, Any]:
        """Validar datos de candidato"""
        if not candidate_data.nombre_completo:
            return {'valid': False, 'error': 'Nombre completo es requerido'}
        
        if not candidate_data.cedula:
            return {'valid': False, 'error': 'Cédula es requerida'}
        
        if not candidate_data.numero_tarjeton:
            return {'valid': False, 'error': 'Número de tarjetón es requerido'}
        
        if not candidate_data.cargo_aspirado:
            return {'valid': False, 'error': 'Cargo aspirado es requerido'}
        
        if not candidate_data.election_type_id:
            return {'valid': False, 'error': 'Tipo de elección es requerido'}
        
        if not candidate_data.circunscripcion:
            return {'valid': False, 'error': 'Circunscripción es requerida'}
        
        # Validar afiliación política (solo una puede ser válida)
        affiliations = [candidate_data.party_id, candidate_data.coalition_id, candidate_data.es_independiente]
        valid_affiliations = sum(1 for x in affiliations if x)
        
        if valid_affiliations != 1:
            return {
                'valid': False, 
                'error': 'El candidato debe tener exactamente una afiliación: partido, coalición o independiente'
            }
        
        return {'valid': True}
    
    def _candidate_exists(self, cedula: str, election_type_id: int) -> bool:
        """Verificar si un candidato ya existe para un tipo de elección"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT COUNT(*) FROM candidates 
            WHERE cedula = ? AND election_type_id = ? AND activo = 1
            ''', (cedula, election_type_id))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except sqlite3.Error:
            return False
    
    def _tarjeton_exists(self, numero_tarjeton: int, election_type_id: int) -> bool:
        """Verificar si un número de tarjetón ya existe para un tipo de elección"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT COUNT(*) FROM candidates 
            WHERE numero_tarjeton = ? AND election_type_id = ? AND activo = 1
            ''', (numero_tarjeton, election_type_id))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except sqlite3.Error:
            return False
    
    def get_candidates(self, election_type_id: Optional[int] = None, 
                      party_id: Optional[int] = None,
                      coalition_id: Optional[int] = None,
                      active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Obtener lista de candidatos con filtros opcionales
        
        Args:
            election_type_id: Filtrar por tipo de elección
            party_id: Filtrar por partido
            coalition_id: Filtrar por coalición
            active_only: Si solo obtener candidatos activos
            
        Returns:
            Lista de candidatos con información de partido/coalición
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT c.*, 
                   et.nombre as election_type_name,
                   pp.nombre_oficial as party_name,
                   pp.siglas as party_siglas,
                   co.nombre_coalicion as coalition_name
            FROM candidates c
            LEFT JOIN election_types et ON c.election_type_id = et.id
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            WHERE 1=1
            '''
            
            params = []
            
            if active_only:
                query += " AND c.activo = 1"
            
            if election_type_id:
                query += " AND c.election_type_id = ?"
                params.append(election_type_id)
            
            if party_id:
                query += " AND c.party_id = ?"
                params.append(party_id)
            
            if coalition_id:
                query += " AND c.coalition_id = ?"
                params.append(coalition_id)
            
            query += " ORDER BY c.numero_tarjeton, c.nombre_completo"
            
            cursor.execute(query, params)
            candidates = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return candidates
            
        except sqlite3.Error as e:
            self.logger.error(f"Error obteniendo candidatos: {e}")
            return []
    
    # ==================== CARGA MASIVA DESDE CSV ====================
    
    def load_candidates_from_csv(self, csv_file_path: str, election_type_id: int, 
                                created_by: Optional[int] = None) -> Dict[str, Any]:
        """
        Cargar candidatos masivamente desde archivo CSV
        
        Args:
            csv_file_path: Ruta del archivo CSV
            election_type_id: ID del tipo de elección
            created_by: ID del usuario que realiza la carga
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            results = {
                'success': True,
                'total_processed': 0,
                'successful': 0,
                'errors': [],
                'candidates_created': []
            }
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                    results['total_processed'] += 1
                    
                    try:
                        # Mapear datos del CSV
                        candidate_data = self._map_csv_to_candidate_data(row, election_type_id)
                        
                        # Crear candidato
                        result = self.create_candidate(candidate_data, created_by)
                        
                        if result['success']:
                            results['successful'] += 1
                            results['candidates_created'].append({
                                'row': row_num,
                                'name': candidate_data.nombre_completo,
                                'cedula': candidate_data.cedula,
                                'candidate_id': result['candidate_id']
                            })
                        else:
                            results['errors'].append({
                                'row': row_num,
                                'error': result['error'],
                                'data': row
                            })
                    
                    except Exception as e:
                        results['errors'].append({
                            'row': row_num,
                            'error': f'Error procesando fila: {str(e)}',
                            'data': row
                        })
            
            # Determinar si la operación fue exitosa en general
            if results['errors']:
                results['success'] = results['successful'] > 0
                results['message'] = f'Carga parcial: {results["successful"]} exitosos, {len(results["errors"])} errores'
            else:
                results['message'] = f'Carga exitosa: {results["successful"]} candidatos creados'
            
            self.logger.info(f"Carga masiva completada: {results['successful']}/{results['total_processed']} candidatos")
            
            return results
            
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'Archivo CSV no encontrado: {csv_file_path}'
            }
        except Exception as e:
            self.logger.error(f"Error en carga masiva: {e}")
            return {
                'success': False,
                'error': f'Error procesando archivo CSV: {str(e)}'
            }
    
    def _map_csv_to_candidate_data(self, row: Dict[str, str], election_type_id: int) -> CandidateData:
        """Mapear fila de CSV a datos de candidato"""
        
        # Determinar afiliación política
        party_id = None
        coalition_id = None
        es_independiente = False
        
        if row.get('party_siglas'):
            party_id = self._get_party_id_by_siglas(row['party_siglas'])
        elif row.get('coalition_name'):
            coalition_id = self._get_coalition_id_by_name(row['coalition_name'])
        else:
            es_independiente = True
        
        return CandidateData(
            nombre_completo=row['nombre_completo'],
            cedula=row['cedula'],
            numero_tarjeton=int(row['numero_tarjeton']),
            cargo_aspirado=row.get('cargo_aspirado', ''),
            election_type_id=election_type_id,
            circunscripcion=row.get('circunscripcion', ''),
            party_id=party_id,
            coalition_id=coalition_id,
            es_independiente=es_independiente,
            foto_url=row.get('foto_url'),
            biografia=row.get('biografia'),
            propuestas=row.get('propuestas'),
            experiencia=row.get('experiencia')
        )
    
    def _get_party_id_by_siglas(self, siglas: str) -> Optional[int]:
        """Obtener ID de partido por siglas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM political_parties WHERE siglas = ? AND activo = 1", (siglas,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error:
            return None
    
    def _get_coalition_id_by_name(self, name: str) -> Optional[int]:
        """Obtener ID de coalición por nombre"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM coalitions WHERE nombre_coalicion = ? AND activo = 1", (name,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error:
            return None
    
    # ==================== BÚSQUEDA AVANZADA ====================
    
    def search_candidates(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Búsqueda avanzada de candidatos con múltiples filtros
        
        Args:
            search_params: Parámetros de búsqueda
            
        Returns:
            Lista de candidatos que coinciden con los criterios
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT c.*, 
                   et.nombre as election_type_name,
                   pp.nombre_oficial as party_name,
                   pp.siglas as party_siglas,
                   co.nombre_coalicion as coalition_name
            FROM candidates c
            LEFT JOIN election_types et ON c.election_type_id = et.id
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            WHERE c.activo = 1
            '''
            
            params = []
            
            # Filtro por nombre
            if search_params.get('nombre'):
                query += " AND c.nombre_completo LIKE ?"
                params.append(f"%{search_params['nombre']}%")
            
            # Filtro por cédula
            if search_params.get('cedula'):
                query += " AND c.cedula LIKE ?"
                params.append(f"%{search_params['cedula']}%")
            
            # Filtro por cargo
            if search_params.get('cargo'):
                query += " AND c.cargo_aspirado LIKE ?"
                params.append(f"%{search_params['cargo']}%")
            
            # Filtro por tipo de elección
            if search_params.get('election_type_id'):
                query += " AND c.election_type_id = ?"
                params.append(search_params['election_type_id'])
            
            # Filtro por partido
            if search_params.get('party_id'):
                query += " AND c.party_id = ?"
                params.append(search_params['party_id'])
            
            # Filtro por coalición
            if search_params.get('coalition_id'):
                query += " AND c.coalition_id = ?"
                params.append(search_params['coalition_id'])
            
            # Filtro por independientes
            if search_params.get('independientes_only'):
                query += " AND c.es_independiente = 1"
            
            # Filtro por circunscripción
            if search_params.get('circunscripcion'):
                query += " AND c.circunscripcion LIKE ?"
                params.append(f"%{search_params['circunscripcion']}%")
            
            # Filtro por habilitación
            if search_params.get('habilitado') is not None:
                query += " AND c.habilitado_oficialmente = ?"
                params.append(search_params['habilitado'])
            
            query += " ORDER BY c.numero_tarjeton, c.nombre_completo"
            
            # Límite de resultados
            if search_params.get('limit'):
                query += " LIMIT ?"
                params.append(search_params['limit'])
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Error en búsqueda de candidatos: {e}")
            return []
    
    # ==================== VALIDACIÓN CON TARJETONES OFICIALES ====================
    
    def validate_candidates_with_ballot(self, election_type_id: int, 
                                       official_ballot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validar candidatos contra tarjetón oficial
        
        Args:
            election_type_id: ID del tipo de elección
            official_ballot_data: Datos del tarjetón oficial
            
        Returns:
            Dict con resultado de la validación
        """
        try:
            # Obtener candidatos actuales
            current_candidates = self.get_candidates(election_type_id=election_type_id)
            
            validation_result = {
                'success': True,
                'total_official': len(official_ballot_data),
                'total_system': len(current_candidates),
                'matches': [],
                'missing_in_system': [],
                'extra_in_system': [],
                'discrepancies': []
            }
            
            # Crear mapas para comparación
            official_map = {item['numero_tarjeton']: item for item in official_ballot_data}
            system_map = {candidate['numero_tarjeton']: candidate for candidate in current_candidates}
            
            # Encontrar coincidencias y discrepancias
            for tarjeton, official_data in official_map.items():
                if tarjeton in system_map:
                    system_data = system_map[tarjeton]
                    
                    # Verificar coincidencia exacta
                    if (official_data['nombre_completo'].strip().upper() == 
                        system_data['nombre_completo'].strip().upper() and
                        official_data['cedula'] == system_data['cedula']):
                        
                        validation_result['matches'].append({
                            'numero_tarjeton': tarjeton,
                            'nombre': official_data['nombre_completo'],
                            'cedula': official_data['cedula']
                        })
                    else:
                        validation_result['discrepancies'].append({
                            'numero_tarjeton': tarjeton,
                            'official': official_data,
                            'system': {
                                'nombre_completo': system_data['nombre_completo'],
                                'cedula': system_data['cedula']
                            }
                        })
                else:
                    validation_result['missing_in_system'].append(official_data)
            
            # Encontrar candidatos extra en el sistema
            for tarjeton, system_data in system_map.items():
                if tarjeton not in official_map:
                    validation_result['extra_in_system'].append({
                        'numero_tarjeton': tarjeton,
                        'nombre_completo': system_data['nombre_completo'],
                        'cedula': system_data['cedula']
                    })
            
            # Determinar si la validación fue exitosa
            validation_result['success'] = (
                len(validation_result['missing_in_system']) == 0 and
                len(validation_result['extra_in_system']) == 0 and
                len(validation_result['discrepancies']) == 0
            )
            
            validation_result['match_percentage'] = (
                len(validation_result['matches']) / max(validation_result['total_official'], 1) * 100
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validando candidatos con tarjetón: {e}")
            return {
                'success': False,
                'error': f'Error en validación: {str(e)}'
            }
    
    # ==================== GENERACIÓN DE LISTAS ====================
    
    def generate_candidate_lists(self, election_type_id: int) -> Dict[str, Any]:
        """
        Generar listas organizadas de candidatos por partido/coalición
        
        Args:
            election_type_id: ID del tipo de elección
            
        Returns:
            Dict con listas organizadas de candidatos
        """
        try:
            candidates = self.get_candidates(election_type_id=election_type_id)
            
            lists = {
                'by_party': {},
                'by_coalition': {},
                'independents': [],
                'summary': {
                    'total_candidates': len(candidates),
                    'total_parties': 0,
                    'total_coalitions': 0,
                    'total_independents': 0
                }
            }
            
            for candidate in candidates:
                if candidate['party_id']:
                    party_key = f"{candidate['party_name']} ({candidate['party_siglas']})"
                    if party_key not in lists['by_party']:
                        lists['by_party'][party_key] = {
                            'party_info': {
                                'id': candidate['party_id'],
                                'name': candidate['party_name'],
                                'siglas': candidate['party_siglas']
                            },
                            'candidates': []
                        }
                    lists['by_party'][party_key]['candidates'].append(candidate)
                
                elif candidate['coalition_id']:
                    coalition_key = candidate['coalition_name']
                    if coalition_key not in lists['by_coalition']:
                        lists['by_coalition'][coalition_key] = {
                            'coalition_info': {
                                'id': candidate['coalition_id'],
                                'name': candidate['coalition_name']
                            },
                            'candidates': []
                        }
                    lists['by_coalition'][coalition_key]['candidates'].append(candidate)
                
                else:  # Independiente
                    lists['independents'].append(candidate)
            
            # Actualizar resumen
            lists['summary']['total_parties'] = len(lists['by_party'])
            lists['summary']['total_coalitions'] = len(lists['by_coalition'])
            lists['summary']['total_independents'] = len(lists['independents'])
            
            # Ordenar candidatos dentro de cada lista por número de tarjetón
            for party_data in lists['by_party'].values():
                party_data['candidates'].sort(key=lambda x: x['numero_tarjeton'])
            
            for coalition_data in lists['by_coalition'].values():
                coalition_data['candidates'].sort(key=lambda x: x['numero_tarjeton'])
            
            lists['independents'].sort(key=lambda x: x['numero_tarjeton'])
            
            return {
                'success': True,
                'data': lists
            }
            
        except Exception as e:
            self.logger.error(f"Error generando listas de candidatos: {e}")
            return {
                'success': False,
                'error': f'Error generando listas: {str(e)}'
            }

if __name__ == "__main__":
    print("🗳️  Servicio de Gestión de Candidatos, Partidos y Coaliciones")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    
    # Ejemplo de uso
    service = CandidateManagementService()
    
    # Obtener partidos políticos
    parties = service.get_political_parties()
    print(f"Partidos políticos disponibles: {len(parties)}")
    
    # Obtener coaliciones
    coalitions = service.get_coalitions()
    print(f"Coaliciones disponibles: {len(coalitions)}")
    
    # Obtener candidatos
    candidates = service.get_candidates()
    print(f"Candidatos registrados: {len(candidates)}")