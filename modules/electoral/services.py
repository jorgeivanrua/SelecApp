"""
Módulo Electoral - Servicios
Lógica de negocio para gestión electoral
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ElectoralService:
    """Servicio para gestión electoral"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_electoral_processes(self, page=1, per_page=20, search='', status=''):
        """Obtener procesos electorales con paginación y filtros"""
        try:
            base_query = """
                SELECT 
                    ep.id,
                    ep.nombre,
                    ep.fecha_inicio,
                    ep.fecha_fin,
                    ep.estado,
                    ej.nombre as jornada_nombre,
                    et.nombre as tipo_eleccion,
                    ep.activo
                FROM electoral_processes ep
                JOIN electoral_journeys ej ON ep.jornada_electoral_id = ej.id
                JOIN election_types et ON ep.election_type_id = et.id
            """
            
            conditions = []
            
            if search:
                conditions.append(f"(ep.nombre LIKE '%{search}%' OR ej.nombre LIKE '%{search}%')")
            
            if status:
                conditions.append(f"ep.estado = '{status}'")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY ep.fecha_creacion DESC"
            
            # Paginación
            offset = (page - 1) * per_page
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            total_result = self.db.execute_query(count_query)
            total = total_result[0][0] if total_result else 0
            
            paginated_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            data = self.db.execute_query(paginated_query)
            
            processes = [
                {
                    'id': row[0],
                    'nombre': row[1],
                    'fecha_inicio': row[2],
                    'fecha_fin': row[3],
                    'estado': row[4],
                    'jornada_nombre': row[5],
                    'tipo_eleccion': row[6],
                    'activo': row[7]
                }
                for row in data
            ]
            
            return {
                'success': True,
                'data': processes,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Get electoral processes error: {e}")
            raise
    
    def get_electoral_process_by_id(self, process_id):
        """Obtener proceso electoral por ID"""
        try:
            query = """
                SELECT 
                    ep.id,
                    ep.nombre,
                    ep.fecha_inicio,
                    ep.fecha_fin,
                    ep.estado,
                    ep.configuracion,
                    ep.activo,
                    ej.id as jornada_id,
                    ej.nombre as jornada_nombre,
                    et.id as tipo_eleccion_id,
                    et.nombre as tipo_eleccion
                FROM electoral_processes ep
                JOIN electoral_journeys ej ON ep.jornada_electoral_id = ej.id
                JOIN election_types et ON ep.election_type_id = et.id
                WHERE ep.id = :process_id
            """
            
            result = self.db.execute_query(query, {'process_id': process_id})
            
            if not result:
                return None
            
            row = result[0]
            return {
                'id': row[0],
                'nombre': row[1],
                'fecha_inicio': row[2],
                'fecha_fin': row[3],
                'estado': row[4],
                'configuracion': row[5],
                'activo': row[6],
                'jornada': {
                    'id': row[7],
                    'nombre': row[8]
                },
                'tipo_eleccion': {
                    'id': row[9],
                    'nombre': row[10]
                }
            }
            
        except Exception as e:
            logger.error(f"Get electoral process by ID error: {e}")
            raise
    
    def create_electoral_process(self, data, user_id):
        """Crear nuevo proceso electoral"""
        try:
            query = """
                INSERT INTO electoral_processes (
                    nombre, jornada_electoral_id, election_type_id,
                    fecha_inicio, fecha_fin, estado, configuracion, activo
                ) VALUES (
                    :nombre, :jornada_electoral_id, :election_type_id,
                    :fecha_inicio, :fecha_fin, :estado, :configuracion, :activo
                )
            """
            
            params = {
                'nombre': data['nombre'],
                'jornada_electoral_id': data['jornada_electoral_id'],
                'election_type_id': data['election_type_id'],
                'fecha_inicio': data['fecha_inicio'],
                'fecha_fin': data['fecha_fin'],
                'estado': data.get('estado', 'configuracion'),
                'configuracion': data.get('configuracion', '{}'),
                'activo': data.get('activo', True)
            }
            
            process_id = self.db.execute_insert(query, params)
            return process_id
            
        except Exception as e:
            logger.error(f"Create electoral process error: {e}")
            raise
    
    def update_electoral_process(self, process_id, data, user_id):
        """Actualizar proceso electoral"""
        try:
            # Construir query dinámicamente
            set_clauses = []
            params = {'process_id': process_id}
            
            allowed_fields = [
                'nombre', 'jornada_electoral_id', 'election_type_id',
                'fecha_inicio', 'fecha_fin', 'estado', 'configuracion', 'activo'
            ]
            
            for field in allowed_fields:
                if field in data:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            if not set_clauses:
                return False
            
            query = f"""
                UPDATE electoral_processes 
                SET {', '.join(set_clauses)}, fecha_actualizacion = datetime('now')
                WHERE id = :process_id
            """
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Update electoral process error: {e}")
            raise
    
    def get_electoral_journeys(self):
        """Obtener jornadas electorales"""
        try:
            query = """
                SELECT id, nombre, fecha_jornada, descripcion, estado, activo
                FROM electoral_journeys
                WHERE activo = 1
                ORDER BY fecha_jornada DESC
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'id': row[0],
                    'nombre': row[1],
                    'fecha_jornada': row[2],
                    'descripcion': row[3],
                    'estado': row[4],
                    'activo': row[5]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get electoral journeys error: {e}")
            raise
    
    def create_electoral_journey(self, data):
        """Crear nueva jornada electoral"""
        try:
            query = """
                INSERT INTO electoral_journeys (
                    nombre, fecha_jornada, descripcion, estado, activo
                ) VALUES (
                    :nombre, :fecha_jornada, :descripcion, :estado, :activo
                )
            """
            
            params = {
                'nombre': data['nombre'],
                'fecha_jornada': data['fecha_jornada'],
                'descripcion': data.get('descripcion', ''),
                'estado': data.get('estado', 'planificada'),
                'activo': data.get('activo', True)
            }
            
            journey_id = self.db.execute_insert(query, params)
            return journey_id
            
        except Exception as e:
            logger.error(f"Create electoral journey error: {e}")
            raise
    
    def get_election_types(self):
        """Obtener tipos de elección"""
        try:
            query = """
                SELECT id, nombre, descripcion, codigo, activo
                FROM election_types
                WHERE activo = 1
                ORDER BY nombre
            """
            
            result = self.db.execute_query(query)
            
            return [
                {
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'codigo': row[3],
                    'activo': row[4]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get election types error: {e}")
            raise
    
    def get_electoral_mesas(self, page=1, per_page=20, municipio_id=None, puesto_id=None, estado=''):
        """Obtener mesas electorales con filtros"""
        try:
            base_query = """
                SELECT 
                    me.id,
                    me.codigo_mesa,
                    me.numero_mesa,
                    me.total_votantes_habilitados,
                    me.estado_recoleccion,
                    l.nombre_puesto,
                    lm.nombre_municipio,
                    u.nombre_completo as testigo_nombre
                FROM mesas_electorales me
                JOIN locations l ON me.puesto_id = l.id
                JOIN locations lm ON l.parent_id = lm.id
                LEFT JOIN users u ON me.testigo_asignado_id = u.id
            """
            
            conditions = []
            
            if municipio_id:
                conditions.append(f"lm.id = {municipio_id}")
            
            if puesto_id:
                conditions.append(f"l.id = {puesto_id}")
            
            if estado:
                conditions.append(f"me.estado_recoleccion = '{estado}'")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY lm.nombre_municipio, l.nombre_puesto, me.numero_mesa"
            
            # Paginación
            offset = (page - 1) * per_page
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            total_result = self.db.execute_query(count_query)
            total = total_result[0][0] if total_result else 0
            
            paginated_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            data = self.db.execute_query(paginated_query)
            
            mesas = [
                {
                    'id': row[0],
                    'codigo_mesa': row[1],
                    'numero_mesa': row[2],
                    'total_votantes_habilitados': row[3],
                    'estado_recoleccion': row[4],
                    'puesto_nombre': row[5],
                    'municipio_nombre': row[6],
                    'testigo_nombre': row[7]
                }
                for row in data
            ]
            
            return {
                'success': True,
                'data': mesas,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Get electoral mesas error: {e}")
            raise
    
    def assign_mesa_witness(self, mesa_id, testigo_id, user_id):
        """Asignar testigo a mesa electoral"""
        try:
            query = """
                UPDATE mesas_electorales 
                SET testigo_asignado_id = :testigo_id,
                    fecha_actualizacion = datetime('now')
                WHERE id = :mesa_id
            """
            
            params = {
                'mesa_id': mesa_id,
                'testigo_id': testigo_id
            }
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Assign mesa witness error: {e}")
            raise
    
    def get_results_summary(self, process_id=None, election_type_id=None):
        """Obtener resumen de resultados electorales"""
        try:
            # Estadísticas generales
            stats_query = """
                SELECT 
                    COUNT(*) as total_mesas,
                    SUM(CASE WHEN estado_recoleccion = 'completada' THEN 1 ELSE 0 END) as mesas_completadas,
                    SUM(CASE WHEN estado_recoleccion = 'en_proceso' THEN 1 ELSE 0 END) as mesas_en_proceso,
                    SUM(total_votantes_habilitados) as total_votantes_habilitados
                FROM mesas_electorales
            """
            
            stats_result = self.db.execute_query(stats_query)
            stats = stats_result[0] if stats_result else (0, 0, 0, 0)
            
            return {
                'estadisticas': {
                    'total_mesas': stats[0],
                    'mesas_completadas': stats[1],
                    'mesas_en_proceso': stats[2],
                    'total_votantes_habilitados': stats[3],
                    'porcentaje_completado': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Get results summary error: {e}")
            raise
    
    def get_locations(self, location_type='', parent_id=None):
        """Obtener ubicaciones geográficas"""
        try:
            query = """
                SELECT id, nombre_departamento, nombre_municipio, nombre_puesto, tipo, parent_id
                FROM locations
                WHERE activo = 1
            """
            
            conditions = []
            params = {}
            
            if location_type:
                conditions.append("tipo = :location_type")
                params['location_type'] = location_type
            
            if parent_id:
                conditions.append("parent_id = :parent_id")
                params['parent_id'] = parent_id
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            query += " ORDER BY nombre_departamento, nombre_municipio, nombre_puesto"
            
            result = self.db.execute_query(query, params)
            
            return [
                {
                    'id': row[0],
                    'nombre_departamento': row[1],
                    'nombre_municipio': row[2],
                    'nombre_puesto': row[3],
                    'tipo': row[4],
                    'parent_id': row[5]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get locations error: {e}")
            raise