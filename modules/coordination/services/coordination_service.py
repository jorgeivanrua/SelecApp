"""
Servicio de Coordinación Municipal
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging

from ..models import CoordinationData, WitnessData, AssignmentData, DashboardData, CoverageReport

class CoordinationService:
    """Servicio para herramientas de coordinación municipal"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
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
                SELECT u.*, l.nombre_municipio, l.codigo_municipio
                FROM users u
                LEFT JOIN locations l ON u.municipio_id = l.id
                WHERE u.id = ? AND u.activo = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del coordinador: {e}")
            return None
    
    def get_dashboard_data(self, coordinator_id: int) -> Optional[DashboardData]:
        """Obtener datos del dashboard para coordinador"""
        try:
            coordinator_info = self.get_coordinator_info(coordinator_id)
            if not coordinator_info:
                return None
            
            statistics = self.get_coordination_statistics(coordinator_id)
            coverage_summary = self.get_coverage_summary(coordinator_info.get('municipio_id'))
            pending_tasks = self.get_pending_tasks(coordinator_id)
            alerts = self.get_coordination_alerts(coordinator_id)
            
            return DashboardData(
                coordinator_info=coordinator_info,
                statistics=statistics,
                coverage_summary=coverage_summary,
                pending_tasks=pending_tasks,
                alerts=alerts
            )
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos del dashboard: {e}")
            return None
    
    def get_coordination_statistics(self, coordinator_id: int) -> Dict[str, Any]:
        """Obtener estadísticas de coordinación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            coordinator_info = self.get_coordinator_info(coordinator_id)
            municipio_id = coordinator_info.get('municipio_id') if coordinator_info else None
            
            if not municipio_id:
                return {}
            
            # Estadísticas básicas
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT me.id) as total_mesas,
                    COUNT(DISTINCT ta.testigo_id) as testigos_asignados,
                    COUNT(DISTINCT CASE WHEN ta.id IS NOT NULL THEN me.id END) as mesas_cubiertas
                FROM mesas_electorales me
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE me.municipio_id = ?
            """, (municipio_id,))
            
            stats = cursor.fetchone()
            
            total_mesas = stats['total_mesas'] or 0
            mesas_cubiertas = stats['mesas_cubiertas'] or 0
            testigos_asignados = stats['testigos_asignados'] or 0
            
            porcentaje_cobertura = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
            
            conn.close()
            
            return {
                'total_testigos': testigos_asignados,
                'testigos_asignados': testigos_asignados,
                'mesas_cubiertas': mesas_cubiertas,
                'total_mesas': total_mesas,
                'mesas_sin_cobertura': total_mesas - mesas_cubiertas,
                'porcentaje_cobertura': round(porcentaje_cobertura, 1),
                'testigos_disponibles': 0  # TODO: Implementar lógica de disponibilidad
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def get_coverage_summary(self, municipio_id: Optional[int]) -> List[Dict[str, Any]]:
        """Obtener resumen de cobertura por puesto"""
        try:
            if not municipio_id:
                return []
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    l.id as puesto_id,
                    l.nombre_puesto as puesto_nombre,
                    COUNT(me.id) as total_mesas,
                    COUNT(ta.id) as mesas_cubiertas,
                    ROUND(COUNT(ta.id) * 100.0 / COUNT(me.id), 1) as porcentaje_cobertura
                FROM locations l
                JOIN mesas_electorales me ON l.id = me.puesto_id
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE l.tipo = 'puesto' AND me.municipio_id = ?
                GROUP BY l.id, l.nombre_puesto
                ORDER BY porcentaje_cobertura DESC
            """, (municipio_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de cobertura: {e}")
            return []
    
    def get_pending_tasks(self, coordinator_id: int) -> List[Dict[str, Any]]:
        """Obtener tareas pendientes del coordinador"""
        try:
            # TODO: Implementar sistema de tareas
            return [
                {
                    'id': 1,
                    'titulo': 'Asignar testigos a mesas sin cobertura',
                    'descripcion': 'Hay mesas sin testigos asignados',
                    'prioridad': 'alta',
                    'fecha_limite': datetime.now().isoformat(),
                    'progreso': 0
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error obteniendo tareas pendientes: {e}")
            return []
    
    def get_coordination_alerts(self, coordinator_id: int) -> List[Dict[str, Any]]:
        """Obtener alertas de coordinación"""
        try:
            alerts = []
            
            # Verificar cobertura baja
            stats = self.get_coordination_statistics(coordinator_id)
            if stats.get('porcentaje_cobertura', 0) < 50:
                alerts.append({
                    'type': 'warning',
                    'message': f"Cobertura baja: {stats.get('porcentaje_cobertura', 0)}%",
                    'action': 'assign_witnesses'
                })
            
            # Verificar mesas sin cobertura
            if stats.get('mesas_sin_cobertura', 0) > 0:
                alerts.append({
                    'type': 'danger',
                    'message': f"{stats.get('mesas_sin_cobertura', 0)} mesas sin cobertura",
                    'action': 'show_uncovered_tables'
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas: {e}")
            return []
    
    # ==================== GESTIÓN DE TESTIGOS ====================
    
    def create_witness(self, witness_data: WitnessData, created_by: int) -> Dict[str, Any]:
        """Crear nuevo testigo electoral"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO testigos_electorales 
                (nombre_completo, cedula, telefono, email, direccion, partido_id, 
                 tipo_testigo, observaciones, activo, creado_por, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                witness_data.nombre_completo,
                witness_data.cedula,
                witness_data.telefono,
                witness_data.email,
                witness_data.direccion,
                witness_data.partido_id,
                witness_data.tipo_testigo,
                witness_data.observaciones,
                witness_data.activo,
                created_by,
                datetime.now()
            ))
            
            witness_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Testigo creado: {witness_data.nombre_completo}")
            
            return {
                'success': True,
                'witness_id': witness_id,
                'message': f'Testigo {witness_data.nombre_completo} creado exitosamente'
            }
            
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Error de integridad creando testigo: {e}")
            return {
                'success': False,
                'error': 'Ya existe un testigo con esa cédula'
            }
        except Exception as e:
            self.logger.error(f"Error creando testigo: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def get_available_witnesses(self, municipio_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener testigos disponibles para asignación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT te.*, pp.nombre_oficial as partido_nombre, pp.siglas as partido_siglas
                FROM testigos_electorales te
                LEFT JOIN political_parties pp ON te.partido_id = pp.id
                LEFT JOIN testigo_asignaciones ta ON te.id = ta.testigo_id AND ta.estado = 'activo'
                WHERE te.activo = 1 AND ta.id IS NULL
            """
            
            params = []
            if municipio_id:
                query += " AND te.municipio_id = ?"
                params.append(municipio_id)
            
            query += " ORDER BY te.nombre_completo"
            
            cursor.execute(query, params)
            witnesses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return witnesses
            
        except Exception as e:
            self.logger.error(f"Error obteniendo testigos disponibles: {e}")
            return []
    
    def assign_witness_to_mesa(self, assignment_data: AssignmentData, assigned_by: int) -> Dict[str, Any]:
        """Asignar testigo a mesa electoral"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que la mesa no tenga ya un testigo asignado
            cursor.execute("""
                SELECT COUNT(*) FROM testigo_asignaciones 
                WHERE mesa_id = ? AND estado = 'activo'
            """, (assignment_data.mesa_id,))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {
                    'success': False,
                    'error': 'La mesa ya tiene un testigo asignado'
                }
            
            # Crear la asignación
            cursor.execute("""
                INSERT INTO testigo_asignaciones 
                (testigo_id, mesa_id, proceso_electoral_id, hora_inicio, hora_fin, 
                 observaciones, estado, asignado_por, fecha_asignacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment_data.testigo_id,
                assignment_data.mesa_id,
                assignment_data.proceso_electoral_id,
                assignment_data.hora_inicio,
                assignment_data.hora_fin,
                assignment_data.observaciones,
                assignment_data.estado,
                assigned_by,
                datetime.now()
            ))
            
            assignment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Testigo asignado: {assignment_data.testigo_id} -> Mesa {assignment_data.mesa_id}")
            
            return {
                'success': True,
                'assignment_id': assignment_id,
                'message': 'Testigo asignado exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error asignando testigo: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def get_uncovered_tables(self, municipio_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener mesas sin cobertura de testigos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT me.*, l.nombre_puesto as puesto_nombre
                FROM mesas_electorales me
                JOIN locations l ON me.puesto_id = l.id
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE ta.id IS NULL AND me.activo = 1
            """
            
            params = []
            if municipio_id:
                query += " AND me.municipio_id = ?"
                params.append(municipio_id)
            
            query += " ORDER BY l.nombre_puesto, me.numero_mesa"
            
            cursor.execute(query, params)
            tables = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return tables
            
        except Exception as e:
            self.logger.error(f"Error obteniendo mesas sin cobertura: {e}")
            return []
    
    # ==================== REPORTES ====================
    
    def generate_coverage_report(self, municipio_id: Optional[int] = None) -> Dict[str, Any]:
        """Generar reporte de cobertura de testigos"""
        try:
            coverage_data = self.get_coverage_summary(municipio_id)
            uncovered_tables = self.get_uncovered_tables(municipio_id)
            
            total_mesas = sum(item['total_mesas'] for item in coverage_data)
            total_cubiertas = sum(item['mesas_cubiertas'] for item in coverage_data)
            
            return {
                'success': True,
                'data': {
                    'coverage_by_puesto': coverage_data,
                    'uncovered_tables': uncovered_tables,
                    'summary': {
                        'total_mesas': total_mesas,
                        'mesas_cubiertas': total_cubiertas,
                        'mesas_sin_cobertura': len(uncovered_tables),
                        'porcentaje_cobertura': round(total_cubiertas / total_mesas * 100, 1) if total_mesas > 0 else 0
                    },
                    'fecha_reporte': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte de cobertura: {e}")
            return {
                'success': False,
                'error': f'Error generando reporte: {str(e)}'
            }