"""
Módulo Candidatos - Servicios
Lógica de negocio para gestión de candidatos y partidos
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CandidateService:
    """Servicio para gestión de candidatos"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_candidates(self, page=1, per_page=20, search='', election_type_id=None, party_id=None, cargo=''):
        """Obtener candidatos con paginación y filtros"""
        try:
            base_query = """
                SELECT 
                    c.id,
                    c.nombre_completo,
                    c.cedula,
                    c.numero_tarjeton,
                    c.cargo_aspirado,
                    c.circunscripcion,
                    c.activo,
                    c.habilitado_oficialmente,
                    p.nombre_oficial as partido_nombre,
                    p.siglas as partido_siglas,
                    et.nombre as tipo_eleccion,
                    co.nombre_coalicion
                FROM candidates c
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN coalitions co ON c.coalition_id = co.id
                LEFT JOIN election_types et ON c.election_type_id = et.id
            """
            
            conditions = []
            params = {}
            
            if search:
                conditions.append("(c.nombre_completo LIKE :search OR c.cedula LIKE :search)")
                params['search'] = f'%{search}%'
            
            if election_type_id:
                conditions.append("c.election_type_id = :election_type_id")
                params['election_type_id'] = election_type_id
            
            if party_id:
                conditions.append("c.party_id = :party_id")
                params['party_id'] = party_id
            
            if cargo:
                conditions.append("c.cargo_aspirado = :cargo")
                params['cargo'] = cargo
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY c.nombre_completo"
            
            # Paginación
            offset = (page - 1) * per_page
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            total_result = self.db.execute_query(count_query, params)
            total = total_result[0][0] if total_result else 0
            
            paginated_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            data = self.db.execute_query(paginated_query, params)
            
            candidates = [
                {
                    'id': row[0],
                    'nombre_completo': row[1],
                    'cedula': row[2],
                    'numero_tarjeton': row[3],
                    'cargo_aspirado': row[4],
                    'circunscripcion': row[5],
                    'activo': row[6],
                    'habilitado_oficialmente': row[7],
                    'partido_nombre': row[8],
                    'partido_siglas': row[9],
                    'tipo_eleccion': row[10],
                    'coalicion_nombre': row[11]
                }
                for row in data
            ]
            
            return {
                'success': True,
                'data': candidates,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Get candidates error: {e}")
            raise
    
    def get_candidate_by_id(self, candidate_id):
        """Obtener candidato por ID"""
        try:
            query = """
                SELECT 
                    c.id,
                    c.nombre_completo,
                    c.cedula,
                    c.numero_tarjeton,
                    c.cargo_aspirado,
                    c.circunscripcion,
                    c.biografia,
                    c.propuestas,
                    c.experiencia,
                    c.foto_url,
                    c.activo,
                    c.habilitado_oficialmente,
                    c.party_id,
                    c.coalition_id,
                    c.election_type_id,
                    p.nombre_oficial as partido_nombre,
                    p.siglas as partido_siglas,
                    et.nombre as tipo_eleccion,
                    co.nombre_coalicion
                FROM candidates c
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN coalitions co ON c.coalition_id = co.id
                LEFT JOIN election_types et ON c.election_type_id = et.id
                WHERE c.id = :candidate_id
            """
            
            result = self.db.execute_query(query, {'candidate_id': candidate_id})
            
            if not result:
                return None
            
            row = result[0]
            return {
                'id': row[0],
                'nombre_completo': row[1],
                'cedula': row[2],
                'numero_tarjeton': row[3],
                'cargo_aspirado': row[4],
                'circunscripcion': row[5],
                'biografia': row[6],
                'propuestas': row[7],
                'experiencia': row[8],
                'foto_url': row[9],
                'activo': row[10],
                'habilitado_oficialmente': row[11],
                'party_id': row[12],
                'coalition_id': row[13],
                'election_type_id': row[14],
                'partido': {
                    'nombre': row[15],
                    'siglas': row[16]
                } if row[15] else None,
                'tipo_eleccion': row[17],
                'coalicion_nombre': row[18]
            }
            
        except Exception as e:
            logger.error(f"Get candidate by ID error: {e}")
            raise
    
    def create_candidate(self, data, user_id):
        """Crear nuevo candidato"""
        try:
            # Validar datos únicos
            if self._candidate_exists(data.get('cedula'), data.get('numero_tarjeton'), data.get('election_type_id')):
                raise ValueError("Candidate with this cedula or tarjeton number already exists")
            
            query = """
                INSERT INTO candidates (
                    nombre_completo, cedula, numero_tarjeton, cargo_aspirado,
                    election_type_id, circunscripcion, party_id, coalition_id,
                    es_independiente, biografia, propuestas, experiencia,
                    foto_url, activo, habilitado_oficialmente, creado_por
                ) VALUES (
                    :nombre_completo, :cedula, :numero_tarjeton, :cargo_aspirado,
                    :election_type_id, :circunscripcion, :party_id, :coalition_id,
                    :es_independiente, :biografia, :propuestas, :experiencia,
                    :foto_url, :activo, :habilitado_oficialmente, :creado_por
                )
            """
            
            params = {
                'nombre_completo': data['nombre_completo'],
                'cedula': data['cedula'],
                'numero_tarjeton': data['numero_tarjeton'],
                'cargo_aspirado': data['cargo_aspirado'],
                'election_type_id': data['election_type_id'],
                'circunscripcion': data.get('circunscripcion', ''),
                'party_id': data.get('party_id'),
                'coalition_id': data.get('coalition_id'),
                'es_independiente': data.get('es_independiente', False),
                'biografia': data.get('biografia', ''),
                'propuestas': data.get('propuestas', ''),
                'experiencia': data.get('experiencia', ''),
                'foto_url': data.get('foto_url', ''),
                'activo': data.get('activo', True),
                'habilitado_oficialmente': data.get('habilitado_oficialmente', True),
                'creado_por': user_id
            }
            
            candidate_id = self.db.execute_insert(query, params)
            return candidate_id
            
        except Exception as e:
            logger.error(f"Create candidate error: {e}")
            raise
    
    def update_candidate(self, candidate_id, data, user_id):
        """Actualizar candidato"""
        try:
            # Construir query dinámicamente
            set_clauses = []
            params = {'candidate_id': candidate_id}
            
            allowed_fields = [
                'nombre_completo', 'cedula', 'numero_tarjeton', 'cargo_aspirado',
                'circunscripcion', 'party_id', 'coalition_id', 'es_independiente',
                'biografia', 'propuestas', 'experiencia', 'foto_url',
                'activo', 'habilitado_oficialmente'
            ]
            
            for field in allowed_fields:
                if field in data:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            if not set_clauses:
                return False
            
            query = f"""
                UPDATE candidates 
                SET {', '.join(set_clauses)}, fecha_actualizacion = datetime('now')
                WHERE id = :candidate_id
            """
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Update candidate error: {e}")
            raise
    
    def get_political_parties(self):
        """Obtener partidos políticos"""
        try:
            query = """
                SELECT 
                    id, nombre_oficial, siglas, color_representativo,
                    descripcion, ideologia, activo, reconocido_oficialmente
                FROM political_parties
                WHERE activo = 1
                ORDER BY siglas
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'id': row[0],
                    'nombre_oficial': row[1],
                    'siglas': row[2],
                    'color_representativo': row[3],
                    'descripcion': row[4],
                    'ideologia': row[5],
                    'activo': row[6],
                    'reconocido_oficialmente': row[7]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get political parties error: {e}")
            raise
    
    def create_political_party(self, data, user_id):
        """Crear nuevo partido político"""
        try:
            query = """
                INSERT INTO political_parties (
                    nombre_oficial, siglas, color_representativo, logo_url,
                    descripcion, fundacion_year, ideologia, activo,
                    reconocido_oficialmente, creado_por
                ) VALUES (
                    :nombre_oficial, :siglas, :color_representativo, :logo_url,
                    :descripcion, :fundacion_year, :ideologia, :activo,
                    :reconocido_oficialmente, :creado_por
                )
            """
            
            params = {
                'nombre_oficial': data['nombre_oficial'],
                'siglas': data['siglas'],
                'color_representativo': data.get('color_representativo', ''),
                'logo_url': data.get('logo_url', ''),
                'descripcion': data.get('descripcion', ''),
                'fundacion_year': data.get('fundacion_year'),
                'ideologia': data.get('ideologia', ''),
                'activo': data.get('activo', True),
                'reconocido_oficialmente': data.get('reconocido_oficialmente', True),
                'creado_por': user_id
            }
            
            party_id = self.db.execute_insert(query, params)
            return party_id
            
        except Exception as e:
            logger.error(f"Create political party error: {e}")
            raise
    
    def get_coalitions(self):
        """Obtener coaliciones"""
        try:
            query = """
                SELECT 
                    c.id,
                    c.nombre_coalicion,
                    c.descripcion,
                    c.fecha_formacion,
                    c.fecha_disolucion,
                    c.activo,
                    GROUP_CONCAT(p.siglas) as partidos_siglas
                FROM coalitions c
                LEFT JOIN coalition_parties cp ON c.id = cp.coalition_id
                LEFT JOIN political_parties p ON cp.party_id = p.id
                WHERE c.activo = 1
                GROUP BY c.id
                ORDER BY c.nombre_coalicion
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'id': row[0],
                    'nombre_coalicion': row[1],
                    'descripcion': row[2],
                    'fecha_formacion': row[3],
                    'fecha_disolucion': row[4],
                    'activo': row[5],
                    'partidos_siglas': row[6].split(',') if row[6] else []
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get coalitions error: {e}")
            raise
    
    def create_coalition(self, data, user_id):
        """Crear nueva coalición"""
        try:
            query = """
                INSERT INTO coalitions (
                    nombre_coalicion, descripcion, fecha_formacion,
                    fecha_disolucion, activo, creado_por
                ) VALUES (
                    :nombre_coalicion, :descripcion, :fecha_formacion,
                    :fecha_disolucion, :activo, :creado_por
                )
            """
            
            params = {
                'nombre_coalicion': data['nombre_coalicion'],
                'descripcion': data.get('descripcion', ''),
                'fecha_formacion': data.get('fecha_formacion'),
                'fecha_disolucion': data.get('fecha_disolucion'),
                'activo': data.get('activo', True),
                'creado_por': user_id
            }
            
            coalition_id = self.db.execute_insert(query, params)
            
            # Agregar partidos a la coalición si se especifican
            if 'party_ids' in data and data['party_ids']:
                self._add_parties_to_coalition(coalition_id, data['party_ids'])
            
            return coalition_id
            
        except Exception as e:
            logger.error(f"Create coalition error: {e}")
            raise
    
    def get_candidate_results(self, election_type_id=None, candidate_id=None, party_id=None):
        """Obtener resultados de candidatos"""
        try:
            base_query = """
                SELECT 
                    cr.id,
                    cr.candidate_id,
                    cr.total_votos,
                    cr.porcentaje_votacion,
                    cr.posicion_ranking,
                    c.nombre_completo,
                    c.cargo_aspirado,
                    p.siglas as partido_siglas,
                    et.nombre as tipo_eleccion
                FROM candidate_results cr
                JOIN candidates c ON cr.candidate_id = c.id
                LEFT JOIN political_parties p ON c.party_id = p.id
                LEFT JOIN election_types et ON cr.election_type_id = et.id
            """
            
            conditions = []
            params = {}
            
            if election_type_id:
                conditions.append("cr.election_type_id = :election_type_id")
                params['election_type_id'] = election_type_id
            
            if candidate_id:
                conditions.append("cr.candidate_id = :candidate_id")
                params['candidate_id'] = candidate_id
            
            if party_id:
                conditions.append("c.party_id = :party_id")
                params['party_id'] = party_id
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY cr.total_votos DESC"
            
            result = self.db.execute_query(base_query, params)
            
            return [
                {
                    'id': row[0],
                    'candidate_id': row[1],
                    'total_votos': row[2],
                    'porcentaje_votacion': row[3],
                    'posicion_ranking': row[4],
                    'nombre_completo': row[5],
                    'cargo_aspirado': row[6],
                    'partido_siglas': row[7],
                    'tipo_eleccion': row[8]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get candidate results error: {e}")
            raise
    
    def calculate_candidate_results(self, election_type_id=None, user_id=None):
        """Calcular resultados de candidatos (simulación)"""
        try:
            # Esta es una implementación básica de ejemplo
            # En un sistema real, esto calcularía los resultados basado en los votos reales
            
            # Por ahora, solo creamos resultados de ejemplo
            candidates_query = """
                SELECT id, nombre_completo, election_type_id
                FROM candidates
                WHERE activo = 1
            """
            
            if election_type_id:
                candidates_query += f" AND election_type_id = {election_type_id}"
            
            candidates = self.db.execute_query(candidates_query)
            
            for candidate in candidates:
                # Simular votos (en producción esto vendría de los datos reales)
                import random
                total_votos = random.randint(1000, 50000)
                porcentaje = round(random.uniform(1.0, 25.0), 2)
                
                # Insertar o actualizar resultado
                result_query = """
                    INSERT OR REPLACE INTO candidate_results (
                        candidate_id, election_type_id, total_votos,
                        porcentaje_votacion, fecha_calculo, calculado_por
                    ) VALUES (
                        :candidate_id, :election_type_id, :total_votos,
                        :porcentaje_votacion, datetime('now'), :calculado_por
                    )
                """
                
                params = {
                    'candidate_id': candidate[0],
                    'election_type_id': candidate[2],
                    'total_votos': total_votos,
                    'porcentaje_votacion': porcentaje,
                    'calculado_por': user_id
                }
                
                self.db.execute_insert(result_query, params)
            
            return True
            
        except Exception as e:
            logger.error(f"Calculate candidate results error: {e}")
            raise
    
    def validate_candidate_data(self, data):
        """Validar datos de candidato"""
        try:
            errors = []
            warnings = []
            
            # Validaciones requeridas
            required_fields = ['nombre_completo', 'cedula', 'cargo_aspirado', 'election_type_id']
            for field in required_fields:
                if not data.get(field):
                    errors.append(f"Field '{field}' is required")
            
            # Validar cédula única
            if data.get('cedula'):
                existing_query = "SELECT id FROM candidates WHERE cedula = :cedula"
                existing = self.db.execute_query(existing_query, {'cedula': data['cedula']})
                if existing:
                    errors.append("Candidate with this cedula already exists")
            
            # Validar número de tarjetón único por tipo de elección
            if data.get('numero_tarjeton') and data.get('election_type_id'):
                tarjeton_query = """
                    SELECT id FROM candidates 
                    WHERE numero_tarjeton = :numero_tarjeton 
                    AND election_type_id = :election_type_id
                """
                existing_tarjeton = self.db.execute_query(tarjeton_query, {
                    'numero_tarjeton': data['numero_tarjeton'],
                    'election_type_id': data['election_type_id']
                })
                if existing_tarjeton:
                    errors.append("Tarjeton number already exists for this election type")
            
            # Validaciones de advertencia
            if not data.get('biografia'):
                warnings.append("Biography is recommended for better candidate profile")
            
            if not data.get('party_id') and not data.get('coalition_id') and not data.get('es_independiente'):
                warnings.append("Candidate should have party affiliation or be marked as independent")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"Validate candidate data error: {e}")
            raise
    
    def _candidate_exists(self, cedula, numero_tarjeton, election_type_id):
        """Verificar si candidato ya existe"""
        try:
            query = """
                SELECT id FROM candidates 
                WHERE cedula = :cedula 
                OR (numero_tarjeton = :numero_tarjeton AND election_type_id = :election_type_id)
            """
            
            result = self.db.execute_query(query, {
                'cedula': cedula,
                'numero_tarjeton': numero_tarjeton,
                'election_type_id': election_type_id
            })
            
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Check candidate exists error: {e}")
            return False
    
    def _add_parties_to_coalition(self, coalition_id, party_ids):
        """Agregar partidos a coalición"""
        try:
            for party_id in party_ids:
                query = """
                    INSERT INTO coalition_parties (coalition_id, party_id, fecha_adhesion)
                    VALUES (:coalition_id, :party_id, date('now'))
                """
                
                self.db.execute_insert(query, {
                    'coalition_id': coalition_id,
                    'party_id': party_id
                })
                
        except Exception as e:
            logger.error(f"Add parties to coalition error: {e}")
            raise