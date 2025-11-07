#!/usr/bin/env python3
"""
CoordinationService - Servicio para herramientas de coordinación municipal
Gestión de testigos, asignaciones, mesas, reportes y supervisión municipal
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging

class CoordinationService:
    """Servicio para herramientas de coordinación municipal"""
    
    def __init__(self, db_path: str = 'caqueta_electoral.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN DE COORDINADORES ====================
    
    def get_coordinator_info(self, user_id: int) -> Optional[Dict]:
        """Obtener información del coordinador municipal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cm.*, m.nombre as municipio_nombre, m.codigo as municipio_codigo,
                       u.nombre_completo as usuario_nombre, u.email as usuario_email
                FROM coordinadores_municipales cm
                JOIN municipios m ON cm.municipio_id = m.id
                JOIN users u ON cm.user_id = u.id
                WHERE cm.user_id = ? AND cm.estado = 'activo'
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del coordinador: {e}")
            raise
    
    def get_coordination_dashboard(self, coordinator_id: int) -> Dict:
        """Obtener datos del dashboard de coordinación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            dashboard = {
                'coordinator_info': {},
                'statistics': {},
                'recent_activities': [],
                'pending_tasks': [],
                'notifications': [],
                'coverage_summary': {}
            }
            
            # Información del coordinador
            cursor.execute("""
                SELECT cm.*, m.nombre as municipio_nombre
                FROM coordinadores_municipales cm
                JOIN municipios m ON cm.municipio_id = m.id
                WHERE cm.id = ?
            """, (coordinator_id,))
            
            coordinator = cursor.fetchone()
            if coordinator:
                dashboard['coordinator_info'] = dict(coordinator)
                municipio_id = coordinator['municipio_id']
                
                # Estadísticas generales
                cursor.execute("""
                    SELECT COUNT(*) as total_testigos
                    FROM testigos_electorales 
                    WHERE coordinador_id = ? AND estado != 'inactivo'
                """, (coordinator_id,))
                total_testigos = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) as testigos_asignados
                    FROM testigos_electorales te
                    JOIN asignaciones_testigos at ON te.id = at.testigo_id
                    WHERE te.coordinador_id = ? AND at.estado = 'asignado'
                """, (coordinator_id,))
                testigos_asignados = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) as total_mesas
                    FROM mesas_votacion 
                    WHERE municipio_id = ? AND estado IN ('activa', 'configurada')
                """, (municipio_id,))
                total_mesas = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(DISTINCT at.mesa_id) as mesas_cubiertas
                    FROM asignaciones_testigos at
                    JOIN testigos_electorales te ON at.testigo_id = te.id
                    WHERE te.coordinador_id = ? AND at.estado = 'asignado'
                """, (coordinator_id,))
                mesas_cubiertas = cursor.fetchone()[0]
                
                porcentaje_cobertura = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
                
                dashboard['statistics'] = {
                    'total_testigos': total_testigos,
                    'testigos_asignados': testigos_asignados,
                    'testigos_disponibles': total_testigos - testigos_asignados,
                    'total_mesas': total_mesas,
                    'mesas_cubiertas': mesas_cubiertas,
                    'mesas_sin_cobertura': total_mesas - mesas_cubiertas,
                    'porcentaje_cobertura': round(porcentaje_cobertura, 1)
                }
                
                # Tareas pendientes
                cursor.execute("""
                    SELECT * FROM tareas_coordinacion 
                    WHERE coordinador_id = ? AND estado IN ('pendiente', 'en_progreso')
                    ORDER BY prioridad ASC, fecha_limite ASC
                    LIMIT 5
                """, (coordinator_id,))
                
                dashboard['pending_tasks'] = [dict(row) for row in cursor.fetchall()]
                
                # Notificaciones no leídas
                cursor.execute("""
                    SELECT * FROM notificaciones_coordinacion 
                    WHERE coordinador_id = ? AND leida = 0
                    ORDER BY fecha_envio DESC
                    LIMIT 5
                """, (coordinator_id,))
                
                dashboard['notifications'] = [dict(row) for row in cursor.fetchall()]
                
                # Resumen de cobertura por puesto
                cursor.execute("""
                    SELECT pv.nombre as puesto_nombre, pv.id as puesto_id,
                           COUNT(mv.id) as total_mesas,
                           COUNT(DISTINCT at.mesa_id) as mesas_cubiertas
                    FROM puestos_votacion pv
                    LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_votacion_id AND mv.estado IN ('activa', 'configurada')
                    LEFT JOIN asignaciones_testigos at ON mv.id = at.mesa_id 
                        AND at.testigo_id IN (
                            SELECT id FROM testigos_electorales WHERE coordinador_id = ?
                        ) AND at.estado = 'asignado'
                    WHERE pv.municipio_id = ?
                    GROUP BY pv.id, pv.nombre
                    ORDER BY pv.nombre
                """, (coordinator_id, municipio_id))
                
                coverage_data = []
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    total = row_dict['total_mesas'] or 0
                    cubiertas = row_dict['mesas_cubiertas'] or 0
                    porcentaje = (cubiertas / total * 100) if total > 0 else 0
                    row_dict['porcentaje_cobertura'] = round(porcentaje, 1)
                    coverage_data.append(row_dict)
                
                dashboard['coverage_summary'] = coverage_data
            
            conn.close()
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error obteniendo dashboard de coordinación: {e}")
            raise
    
    # ==================== GESTIÓN DE TESTIGOS ====================
    
    def get_witnesses(self, coordinator_id: int, filters: Dict = None) -> List[Dict]:
        """Obtener testigos del coordinador con filtros"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT te.*, p.nombre as partido_nombre, p.sigla as partido_sigla,
                       p.color_principal as partido_color,
                       COUNT(at.id) as total_asignaciones,
                       MAX(at.fecha_asignacion) as ultima_asignacion
                FROM testigos_electorales te
                LEFT JOIN partidos_politicos p ON te.partido_id = p.id
                LEFT JOIN asignaciones_testigos at ON te.id = at.testigo_id
                WHERE te.coordinador_id = ?
            """
            
            params = [coordinator_id]
            
            # Aplicar filtros
            if filters:
                if filters.get('estado'):
                    query += " AND te.estado = ?"
                    params.append(filters['estado'])
                
                if filters.get('partido_id'):
                    query += " AND te.partido_id = ?"
                    params.append(filters['partido_id'])
                
                if filters.get('tipo_testigo'):
                    query += " AND te.tipo_testigo = ?"
                    params.append(filters['tipo_testigo'])
                
                if filters.get('search'):
                    query += " AND (te.nombre_completo LIKE ? OR te.cedula LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term])
            
            query += """
                GROUP BY te.id
                ORDER BY te.nombre_completo
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            witnesses = [dict(row) for row in results]
            return witnesses
            
        except Exception as e:
            self.logger.error(f"Error obteniendo testigos: {e}")
            raise
    
    def create_witness(self, coordinator_id: int, witness_data: Dict) -> int:
        """Crear nuevo testigo electoral"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validar datos requeridos
            required_fields = ['nombre_completo', 'cedula', 'telefono']
            for field in required_fields:
                if not witness_data.get(field):
                    raise ValueError(f"Campo requerido: {field}")
            
            # Verificar que no exista testigo con la misma cédula
            cursor.execute("SELECT id FROM testigos_electorales WHERE cedula = ?", 
                          (witness_data['cedula'],))
            if cursor.fetchone():
                raise ValueError("Ya existe un testigo con esta cédula")
            
            # Obtener municipio del coordinador
            cursor.execute("SELECT municipio_id FROM coordinadores_municipales WHERE id = ?", 
                          (coordinator_id,))
            coordinator_info = cursor.fetchone()
            if not coordinator_info:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator_info[0]
            
            query = """
                INSERT INTO testigos_electorales 
                (coordinador_id, municipio_id, nombre_completo, cedula, telefono, email, 
                 direccion, fecha_nacimiento, profesion, experiencia_electoral, partido_id, 
                 tipo_testigo, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                coordinator_id,
                municipio_id,
                witness_data['nombre_completo'],
                witness_data['cedula'],
                witness_data['telefono'],
                witness_data.get('email'),
                witness_data.get('direccion'),
                witness_data.get('fecha_nacimiento'),
                witness_data.get('profesion'),
                witness_data.get('experiencia_electoral'),
                witness_data.get('partido_id'),
                witness_data.get('tipo_testigo', 'principal'),
                witness_data.get('observaciones')
            ))
            
            witness_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Testigo creado: {witness_id} - {witness_data['nombre_completo']}")
            return witness_id
            
        except Exception as e:
            self.logger.error(f"Error creando testigo: {e}")
            raise
    
    def update_witness(self, witness_id: int, witness_data: Dict, coordinator_id: int) -> bool:
        """Actualizar testigo electoral"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que el testigo pertenece al coordinador
            cursor.execute("""
                SELECT id FROM testigos_electorales 
                WHERE id = ? AND coordinador_id = ?
            """, (witness_id, coordinator_id))
            
            if not cursor.fetchone():
                raise ValueError("Testigo no encontrado o no autorizado")
            
            # Si se está cambiando la cédula, verificar que no exista otra
            if 'cedula' in witness_data:
                cursor.execute("""
                    SELECT id FROM testigos_electorales 
                    WHERE cedula = ? AND id != ?
                """, (witness_data['cedula'], witness_id))
                if cursor.fetchone():
                    raise ValueError("Ya existe otro testigo con esta cédula")
            
            # Construir query de actualización dinámicamente
            update_fields = []
            params = []
            
            updatable_fields = [
                'nombre_completo', 'cedula', 'telefono', 'email', 'direccion',
                'fecha_nacimiento', 'profesion', 'experiencia_electoral', 'partido_id',
                'tipo_testigo', 'estado', 'observaciones'
            ]
            
            for field in updatable_fields:
                if field in witness_data:
                    update_fields.append(f"{field} = ?")
                    params.append(witness_data[field])
            
            if not update_fields:
                return True  # No hay nada que actualizar
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(witness_id)
            
            query = f"UPDATE testigos_electorales SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Testigo actualizado: {witness_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando testigo: {e}")
            raise
    
    # ==================== GESTIÓN DE MESAS Y PUESTOS ====================
    
    def get_voting_tables(self, coordinator_id: int, filters: Dict = None) -> List[Dict]:
        """Obtener mesas de votación del municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener municipio del coordinador
            cursor.execute("SELECT municipio_id FROM coordinadores_municipales WHERE id = ?", 
                          (coordinator_id,))
            coordinator_info = cursor.fetchone()
            if not coordinator_info:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator_info[0]
            
            query = """
                SELECT mv.*, pv.nombre as puesto_nombre, pv.codigo as puesto_codigo,
                       COUNT(at.id) as total_asignaciones,
                       GROUP_CONCAT(te.nombre_completo, ', ') as testigos_asignados,
                       mv.numero as numero_mesa
                FROM mesas_votacion mv
                LEFT JOIN puestos_votacion pv ON mv.puesto_votacion_id = pv.id
                LEFT JOIN asignaciones_testigos at ON mv.id = at.mesa_id AND at.estado = 'asignado'
                LEFT JOIN testigos_electorales te ON at.testigo_id = te.id
                WHERE mv.municipio_id = ?
            """
            
            params = [municipio_id]
            
            # Aplicar filtros
            if filters:
                if filters.get('puesto_id'):
                    query += " AND mv.puesto_votacion_id = ?"
                    params.append(filters['puesto_id'])
                
                if filters.get('estado'):
                    query += " AND mv.estado = ?"
                    params.append(filters['estado'])
                
                if filters.get('sin_cobertura'):
                    query += " AND mv.id NOT IN (SELECT DISTINCT mesa_id FROM asignaciones_testigos WHERE estado = 'asignado')"
            
            query += """
                GROUP BY mv.id
                ORDER BY mv.numero
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            tables = []
            for row in results:
                table = dict(row)
                table['tiene_cobertura'] = table['total_asignaciones'] > 0
                tables.append(table)
            
            return tables
            
        except Exception as e:
            self.logger.error(f"Error obteniendo mesas de votación: {e}")
            raise
    
    def get_voting_stations(self, coordinator_id: int) -> List[Dict]:
        """Obtener puestos de votación del municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener municipio del coordinador
            cursor.execute("SELECT municipio_id FROM coordinadores_municipales WHERE id = ?", 
                          (coordinator_id,))
            coordinator_info = cursor.fetchone()
            if not coordinator_info:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator_info[0]
            
            cursor.execute("""
                SELECT pv.*, 
                       COUNT(mv.id) as total_mesas,
                       COUNT(DISTINCT at.mesa_id) as mesas_cubiertas,
                       SUM(mv.total_votantes) as total_votantes
                FROM puestos_votacion pv
                LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_votacion_id AND mv.estado IN ('activa', 'configurada')
                LEFT JOIN asignaciones_testigos at ON mv.id = at.mesa_id AND at.estado = 'asignado'
                WHERE pv.municipio_id = ?
                GROUP BY pv.id
                ORDER BY pv.nombre
            """, (municipio_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            stations = []
            for row in results:
                station = dict(row)
                total_mesas = station['total_mesas'] or 0
                mesas_cubiertas = station['mesas_cubiertas'] or 0
                station['porcentaje_cobertura'] = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
                stations.append(station)
            
            return stations
            
        except Exception as e:
            self.logger.error(f"Error obteniendo puestos de votación: {e}")
            raise
    
    # ==================== GESTIÓN DE ASIGNACIONES ====================
    
    def assign_witness_to_table(self, assignment_data: Dict, coordinator_id: int) -> int:
        """Asignar testigo a mesa de votación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validar datos requeridos
            required_fields = ['testigo_id', 'mesa_id', 'proceso_electoral_id']
            for field in required_fields:
                if not assignment_data.get(field):
                    raise ValueError(f"Campo requerido: {field}")
            
            testigo_id = assignment_data['testigo_id']
            mesa_id = assignment_data['mesa_id']
            proceso_id = assignment_data['proceso_electoral_id']
            
            # Verificar que el testigo pertenece al coordinador
            cursor.execute("""
                SELECT id, estado FROM testigos_electorales 
                WHERE id = ? AND coordinador_id = ?
            """, (testigo_id, coordinator_id))
            
            testigo = cursor.fetchone()
            if not testigo:
                raise ValueError("Testigo no encontrado o no autorizado")
            
            if testigo[1] == 'inactivo':
                raise ValueError("No se puede asignar un testigo inactivo")
            
            # Verificar que no exista asignación duplicada
            cursor.execute("""
                SELECT id FROM asignaciones_testigos 
                WHERE testigo_id = ? AND mesa_id = ? AND proceso_electoral_id = ?
            """, (testigo_id, mesa_id, proceso_id))
            
            if cursor.fetchone():
                raise ValueError("Ya existe una asignación para este testigo en esta mesa")
            
            # Crear asignación
            cursor.execute("""
                INSERT INTO asignaciones_testigos 
                (testigo_id, mesa_id, coordinador_id, proceso_electoral_id, 
                 tipo_asignacion, hora_inicio, hora_fin, observaciones, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                testigo_id,
                mesa_id,
                coordinator_id,
                proceso_id,
                assignment_data.get('tipo_asignacion', 'principal'),
                assignment_data.get('hora_inicio', '06:00'),
                assignment_data.get('hora_fin', '18:00'),
                assignment_data.get('observaciones'),
                coordinator_id  # created_by
            ))
            
            assignment_id = cursor.lastrowid
            
            # Actualizar estado del testigo
            cursor.execute("""
                UPDATE testigos_electorales 
                SET estado = 'asignado', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (testigo_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Asignación creada: {assignment_id} - Testigo {testigo_id} a Mesa {mesa_id}")
            return assignment_id
            
        except Exception as e:
            self.logger.error(f"Error creando asignación: {e}")
            raise
    
    def get_assignments(self, coordinator_id: int, filters: Dict = None) -> List[Dict]:
        """Obtener asignaciones del coordinador"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT at.*, 
                       te.nombre_completo as testigo_nombre, te.cedula as testigo_cedula,
                       te.telefono as testigo_telefono,
                       mv.numero as numero_mesa, COALESCE(mv.ubicacion_especifica, pv.direccion) as mesa_direccion,
                       pv.nombre as puesto_nombre,
                       pe.nombre as proceso_nombre
                FROM asignaciones_testigos at
                JOIN testigos_electorales te ON at.testigo_id = te.id
                JOIN mesas_votacion mv ON at.mesa_id = mv.id
                LEFT JOIN puestos_votacion pv ON mv.puesto_votacion_id = pv.id
                LEFT JOIN procesos_electorales pe ON at.proceso_electoral_id = pe.id
                WHERE at.coordinador_id = ?
            """
            
            params = [coordinator_id]
            
            # Aplicar filtros
            if filters:
                if filters.get('estado'):
                    query += " AND at.estado = ?"
                    params.append(filters['estado'])
                
                if filters.get('proceso_id'):
                    query += " AND at.proceso_electoral_id = ?"
                    params.append(filters['proceso_id'])
                
                if filters.get('mesa_id'):
                    query += " AND at.mesa_id = ?"
                    params.append(filters['mesa_id'])
            
            query += " ORDER BY mv.numero, te.nombre_completo"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            assignments = [dict(row) for row in results]
            return assignments
            
        except Exception as e:
            self.logger.error(f"Error obteniendo asignaciones: {e}")
            raise
    
    def update_assignment_status(self, assignment_id: int, new_status: str, coordinator_id: int, observations: str = None) -> bool:
        """Actualizar estado de asignación"""
        try:
            valid_statuses = ['asignado', 'confirmado', 'presente', 'ausente', 'reemplazado']
            if new_status not in valid_statuses:
                raise ValueError(f"Estado inválido. Debe ser uno de: {valid_statuses}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que la asignación pertenece al coordinador
            cursor.execute("""
                SELECT testigo_id FROM asignaciones_testigos 
                WHERE id = ? AND coordinador_id = ?
            """, (assignment_id, coordinator_id))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("Asignación no encontrada o no autorizada")
            
            testigo_id = result[0]
            
            # Actualizar asignación
            cursor.execute("""
                UPDATE asignaciones_testigos 
                SET estado = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_status, observations, assignment_id))
            
            # Actualizar estado del testigo si es necesario
            if new_status == 'ausente':
                cursor.execute("""
                    UPDATE testigos_electorales 
                    SET estado = 'disponible', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (testigo_id,))
            elif new_status in ['confirmado', 'presente']:
                cursor.execute("""
                    UPDATE testigos_electorales 
                    SET estado = 'asignado', updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (testigo_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Estado de asignación actualizado: {assignment_id} -> {new_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando estado de asignación: {e}")
            raise
    
    # ==================== GESTIÓN DE TAREAS ====================
    
    def get_tasks(self, coordinator_id: int, filters: Dict = None) -> List[Dict]:
        """Obtener tareas del coordinador"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT tc.*, u.nombre_completo as asignada_por_nombre
                FROM tareas_coordinacion tc
                LEFT JOIN users u ON tc.asignada_por = u.id
                WHERE tc.coordinador_id = ?
            """
            
            params = [coordinator_id]
            
            # Aplicar filtros
            if filters:
                if filters.get('estado'):
                    query += " AND tc.estado = ?"
                    params.append(filters['estado'])
                
                if filters.get('prioridad'):
                    query += " AND tc.prioridad = ?"
                    params.append(filters['prioridad'])
                
                if filters.get('tipo_tarea'):
                    query += " AND tc.tipo_tarea = ?"
                    params.append(filters['tipo_tarea'])
            
            query += " ORDER BY tc.prioridad ASC, tc.fecha_limite ASC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            tasks = [dict(row) for row in results]
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error obteniendo tareas: {e}")
            raise
    
    def update_task_progress(self, task_id: int, progress: int, coordinator_id: int, observations: str = None) -> bool:
        """Actualizar progreso de tarea"""
        try:
            if not 0 <= progress <= 100:
                raise ValueError("El progreso debe estar entre 0 y 100")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que la tarea pertenece al coordinador
            cursor.execute("""
                SELECT estado FROM tareas_coordinacion 
                WHERE id = ? AND coordinador_id = ?
            """, (task_id, coordinator_id))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("Tarea no encontrada o no autorizada")
            
            # Determinar nuevo estado basado en progreso
            if progress == 0:
                new_status = 'pendiente'
            elif progress == 100:
                new_status = 'completada'
            else:
                new_status = 'en_progreso'
            
            # Actualizar tarea
            cursor.execute("""
                UPDATE tareas_coordinacion 
                SET progreso = ?, estado = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (progress, new_status, observations, task_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Progreso de tarea actualizado: {task_id} -> {progress}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando progreso de tarea: {e}")
            raise
    
    # ==================== REPORTES Y ESTADÍSTICAS ====================
    
    def generate_coverage_report(self, coordinator_id: int, process_id: int = None) -> Dict:
        """Generar reporte de cobertura de mesas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información del coordinador
            cursor.execute("""
                SELECT cm.*, m.nombre as municipio_nombre
                FROM coordinadores_municipales cm
                JOIN municipios m ON cm.municipio_id = m.id
                WHERE cm.id = ?
            """, (coordinator_id,))
            
            coordinator = cursor.fetchone()
            if not coordinator:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator['municipio_id']
            
            report = {
                'title': f'Reporte de Cobertura - {coordinator["municipio_nombre"]}',
                'generated_at': datetime.now().isoformat(),
                'coordinator': dict(coordinator),
                'summary': {},
                'coverage_by_station': [],
                'uncovered_tables': [],
                'witness_distribution': {}
            }
            
            # Resumen general
            cursor.execute("""
                SELECT COUNT(*) as total_mesas
                FROM mesas_votacion 
                WHERE municipio_id = ? AND estado IN ('activa', 'configurada')
            """, (municipio_id,))
            total_mesas = cursor.fetchone()[0]
            
            query_filter = "" if not process_id else " AND at.proceso_electoral_id = ?"
            params = [municipio_id] + ([process_id] if process_id else [])
            
            cursor.execute(f"""
                SELECT COUNT(DISTINCT at.mesa_id) as mesas_cubiertas
                FROM asignaciones_testigos at
                JOIN testigos_electorales te ON at.testigo_id = te.id
                WHERE te.municipio_id = ? AND at.estado = 'asignado'{query_filter}
            """, params)
            mesas_cubiertas = cursor.fetchone()[0]
            
            porcentaje_cobertura = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
            
            report['summary'] = {
                'total_mesas': total_mesas,
                'mesas_cubiertas': mesas_cubiertas,
                'mesas_sin_cobertura': total_mesas - mesas_cubiertas,
                'porcentaje_cobertura': round(porcentaje_cobertura, 1)
            }
            
            # Cobertura por puesto
            cursor.execute(f"""
                SELECT pv.nombre as puesto_nombre, pv.direccion,
                       COUNT(mv.id) as total_mesas,
                       COUNT(DISTINCT at.mesa_id) as mesas_cubiertas
                FROM puestos_votacion pv
                LEFT JOIN mesas_votacion mv ON pv.id = mv.puesto_votacion_id AND mv.estado IN ('activa', 'configurada')
                LEFT JOIN asignaciones_testigos at ON mv.id = at.mesa_id 
                    AND at.testigo_id IN (
                        SELECT id FROM testigos_electorales WHERE municipio_id = ?
                    ) AND at.estado = 'asignado'{query_filter}
                WHERE pv.municipio_id = ?
                GROUP BY pv.id
                ORDER BY pv.nombre
            """, params + [municipio_id])
            
            coverage_by_station = []
            for row in cursor.fetchall():
                station = dict(row)
                total = station['total_mesas'] or 0
                cubiertas = station['mesas_cubiertas'] or 0
                station['porcentaje_cobertura'] = (cubiertas / total * 100) if total > 0 else 0
                coverage_by_station.append(station)
            
            report['coverage_by_station'] = coverage_by_station
            
            # Mesas sin cobertura
            cursor.execute(f"""
                SELECT mv.numero as numero_mesa, COALESCE(mv.ubicacion_especifica, pv.direccion) as direccion, pv.nombre as puesto_nombre
                FROM mesas_votacion mv
                LEFT JOIN puestos_votacion pv ON mv.puesto_votacion_id = pv.id
                WHERE mv.municipio_id = ? AND mv.estado IN ('activa', 'configurada')
                AND mv.id NOT IN (
                    SELECT DISTINCT at.mesa_id 
                    FROM asignaciones_testigos at
                    JOIN testigos_electorales te ON at.testigo_id = te.id
                    WHERE te.municipio_id = ? AND at.estado = 'asignado'{query_filter}
                )
                ORDER BY mv.numero
            """, params + params)
            
            report['uncovered_tables'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de cobertura: {e}")
            raise
    
    def update_coordination_statistics(self, coordinator_id: int) -> bool:
        """Actualizar estadísticas de coordinación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información del coordinador
            cursor.execute("""
                SELECT municipio_id FROM coordinadores_municipales WHERE id = ?
            """, (coordinator_id,))
            
            coordinator = cursor.fetchone()
            if not coordinator:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator[0]
            
            # Calcular estadísticas
            cursor.execute("""
                SELECT COUNT(*) FROM testigos_electorales 
                WHERE coordinador_id = ? AND estado != 'inactivo'
            """, (coordinator_id,))
            total_testigos = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM testigos_electorales te
                JOIN asignaciones_testigos at ON te.id = at.testigo_id
                WHERE te.coordinador_id = ? AND at.estado = 'asignado'
            """, (coordinator_id,))
            testigos_asignados = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM mesas_votacion 
                WHERE municipio_id = ? AND estado IN ('activa', 'configurada')
            """, (municipio_id,))
            total_mesas = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT at.mesa_id) FROM asignaciones_testigos at
                JOIN testigos_electorales te ON at.testigo_id = te.id
                WHERE te.coordinador_id = ? AND at.estado = 'asignado'
            """, (coordinator_id,))
            mesas_cubiertas = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM reportes_coordinacion 
                WHERE coordinador_id = ? AND DATE(created_at) = DATE('now')
            """, (coordinator_id,))
            reportes_enviados = cursor.fetchone()[0]
            
            porcentaje_cobertura = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
            testigos_disponibles = total_testigos - testigos_asignados
            mesas_sin_cobertura = total_mesas - mesas_cubiertas
            
            # Insertar o actualizar estadísticas
            cursor.execute("""
                INSERT OR REPLACE INTO estadisticas_coordinacion 
                (coordinador_id, municipio_id, fecha_estadistica, total_testigos, 
                 testigos_asignados, testigos_disponibles, total_mesas, mesas_cubiertas, 
                 mesas_sin_cobertura, porcentaje_cobertura, reportes_enviados)
                VALUES (?, ?, DATE('now'), ?, ?, ?, ?, ?, ?, ?, ?)
            """, (coordinator_id, municipio_id, total_testigos, testigos_asignados, 
                  testigos_disponibles, total_mesas, mesas_cubiertas, mesas_sin_cobertura, 
                  porcentaje_cobertura, reportes_enviados))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Estadísticas de coordinación actualizadas para coordinador {coordinator_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando estadísticas de coordinación: {e}")
            raise
    
    # ==================== NOTIFICACIONES ====================
    
    def create_notification(self, coordinator_id: int, notification_data: Dict) -> int:
        """Crear notificación para coordinador"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            required_fields = ['tipo_notificacion', 'titulo', 'mensaje']
            for field in required_fields:
                if not notification_data.get(field):
                    raise ValueError(f"Campo requerido: {field}")
            
            cursor.execute("""
                INSERT INTO notificaciones_coordinacion 
                (coordinador_id, tipo_notificacion, titulo, mensaje, datos_json, 
                 prioridad, remitente_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                coordinator_id,
                notification_data['tipo_notificacion'],
                notification_data['titulo'],
                notification_data['mensaje'],
                notification_data.get('datos_json'),
                notification_data.get('prioridad', 2),
                notification_data.get('remitente_id')
            ))
            
            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Notificación creada: {notification_id} para coordinador {coordinator_id}")
            return notification_id
            
        except Exception as e:
            self.logger.error(f"Error creando notificación: {e}")
            raise
    
    def mark_notification_as_read(self, notification_id: int, coordinator_id: int) -> bool:
        """Marcar notificación como leída"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE notificaciones_coordinacion 
                SET leida = 1, fecha_lectura = CURRENT_TIMESTAMP
                WHERE id = ? AND coordinador_id = ?
            """, (notification_id, coordinator_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Notificación no encontrada o no autorizada")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Notificación {notification_id} marcada como leída")
            return True
            
        except Exception as e:
            self.logger.error(f"Error marcando notificación como leída: {e}")
            raise
    
    # ==================== UTILIDADES ====================
    
    def get_available_witnesses_for_assignment(self, coordinator_id: int, mesa_id: int = None) -> List[Dict]:
        """Obtener testigos disponibles para asignación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT te.*, p.nombre as partido_nombre, p.sigla as partido_sigla
                FROM testigos_electorales te
                LEFT JOIN partidos_politicos p ON te.partido_id = p.id
                WHERE te.coordinador_id = ? AND te.estado = 'disponible'
            """
            
            params = [coordinator_id]
            
            # Si se especifica una mesa, excluir testigos ya asignados a esa mesa
            if mesa_id:
                query += """
                    AND te.id NOT IN (
                        SELECT testigo_id FROM asignaciones_testigos 
                        WHERE mesa_id = ? AND estado = 'asignado'
                    )
                """
                params.append(mesa_id)
            
            query += " ORDER BY te.nombre_completo"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            witnesses = [dict(row) for row in results]
            return witnesses
            
        except Exception as e:
            self.logger.error(f"Error obteniendo testigos disponibles: {e}")
            raise
    
    def get_coordination_summary(self, coordinator_id: int) -> Dict:
        """Obtener resumen ejecutivo de coordinación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información básica del coordinador
            cursor.execute("""
                SELECT cm.*, m.nombre as municipio_nombre
                FROM coordinadores_municipales cm
                JOIN municipios m ON cm.municipio_id = m.id
                WHERE cm.id = ?
            """, (coordinator_id,))
            
            coordinator = cursor.fetchone()
            if not coordinator:
                raise ValueError("Coordinador no encontrado")
            
            municipio_id = coordinator['municipio_id']
            
            summary = {
                'coordinator_name': coordinator['nombre_completo'],
                'municipality': coordinator['municipio_nombre'],
                'last_updated': datetime.now().isoformat(),
                'metrics': {},
                'alerts': [],
                'recent_activity': []
            }
            
            # Métricas principales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_testigos,
                    SUM(CASE WHEN estado = 'disponible' THEN 1 ELSE 0 END) as disponibles,
                    SUM(CASE WHEN estado = 'asignado' THEN 1 ELSE 0 END) as asignados,
                    SUM(CASE WHEN estado = 'inactivo' THEN 1 ELSE 0 END) as inactivos
                FROM testigos_electorales 
                WHERE coordinador_id = ?
            """, (coordinator_id,))
            
            testigos_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) FROM mesas_votacion 
                WHERE municipio_id = ? AND estado IN ('activa', 'configurada')
            """, (municipio_id,))
            total_mesas = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(DISTINCT at.mesa_id) FROM asignaciones_testigos at
                JOIN testigos_electorales te ON at.testigo_id = te.id
                WHERE te.coordinador_id = ? AND at.estado = 'asignado'
            """, (coordinator_id,))
            mesas_cubiertas = cursor.fetchone()[0]
            
            summary['metrics'] = {
                'total_testigos': testigos_stats[0],
                'testigos_disponibles': testigos_stats[1],
                'testigos_asignados': testigos_stats[2],
                'testigos_inactivos': testigos_stats[3],
                'total_mesas': total_mesas,
                'mesas_cubiertas': mesas_cubiertas,
                'mesas_sin_cobertura': total_mesas - mesas_cubiertas,
                'porcentaje_cobertura': round((mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0, 1)
            }
            
            # Alertas (mesas sin cobertura, tareas vencidas, etc.)
            if summary['metrics']['mesas_sin_cobertura'] > 0:
                summary['alerts'].append({
                    'type': 'warning',
                    'message': f"{summary['metrics']['mesas_sin_cobertura']} mesas sin cobertura de testigos"
                })
            
            cursor.execute("""
                SELECT COUNT(*) FROM tareas_coordinacion 
                WHERE coordinador_id = ? AND estado IN ('pendiente', 'en_progreso') 
                AND fecha_limite < DATE('now')
            """, (coordinator_id,))
            tareas_vencidas = cursor.fetchone()[0]
            
            if tareas_vencidas > 0:
                summary['alerts'].append({
                    'type': 'error',
                    'message': f"{tareas_vencidas} tareas vencidas pendientes"
                })
            
            conn.close()
            return summary
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de coordinación: {e}")
            raise