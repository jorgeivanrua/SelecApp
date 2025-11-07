"""
Servicio de Coordinación Municipal Específica
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from ..models import CoordinationData, WitnessData, AssignmentData

class MunicipalCoordinationService:
    """Servicio especializado para coordinación a nivel municipal"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN MUNICIPAL ====================
    
    def get_municipal_overview(self, municipio_id: int) -> Dict[str, Any]:
        """Obtener vista general del municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Información básica del municipio
            cursor.execute("""
                SELECT * FROM locations 
                WHERE id = ? AND tipo = 'municipio'
            """, (municipio_id,))
            
            municipio_info = dict(cursor.fetchone() or {})
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT l.id) as total_puestos,
                    COUNT(DISTINCT me.id) as total_mesas,
                    COUNT(DISTINCT ta.testigo_id) as testigos_asignados,
                    COUNT(DISTINCT CASE WHEN ta.id IS NOT NULL THEN me.id END) as mesas_cubiertas
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.puesto_id
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE l.parent_id = ? AND l.tipo = 'puesto'
            """, (municipio_id,))
            
            stats = dict(cursor.fetchone() or {})
            
            # Calcular porcentajes
            total_mesas = stats.get('total_mesas', 0)
            mesas_cubiertas = stats.get('mesas_cubiertas', 0)
            porcentaje_cobertura = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
            
            conn.close()
            
            return {
                'municipio_info': municipio_info,
                'statistics': {
                    **stats,
                    'porcentaje_cobertura': round(porcentaje_cobertura, 1),
                    'mesas_sin_cobertura': total_mesas - mesas_cubiertas
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vista municipal: {e}")
            return {}
    
    def get_puestos_by_municipio(self, municipio_id: int) -> List[Dict[str, Any]]:
        """Obtener puestos de votación por municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    l.*,
                    COUNT(me.id) as total_mesas,
                    COUNT(ta.id) as mesas_cubiertas,
                    ROUND(COUNT(ta.id) * 100.0 / NULLIF(COUNT(me.id), 0), 1) as porcentaje_cobertura
                FROM locations l
                LEFT JOIN mesas_electorales me ON l.id = me.puesto_id
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE l.parent_id = ? AND l.tipo = 'puesto' AND l.activo = 1
                GROUP BY l.id
                ORDER BY l.nombre_puesto
            """, (municipio_id,))
            
            puestos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return puestos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo puestos: {e}")
            return []
    
    def get_mesas_by_puesto(self, puesto_id: int) -> List[Dict[str, Any]]:
        """Obtener mesas por puesto de votación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    me.*,
                    te.nombre_completo as testigo_nombre,
                    te.cedula as testigo_cedula,
                    te.telefono as testigo_telefono,
                    ta.estado as asignacion_estado,
                    ta.fecha_asignacion
                FROM mesas_electorales me
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                LEFT JOIN testigos_electorales te ON ta.testigo_id = te.id
                WHERE me.puesto_id = ? AND me.activo = 1
                ORDER BY me.numero_mesa
            """, (puesto_id,))
            
            mesas = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return mesas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo mesas: {e}")
            return []
    
    def get_testigos_by_municipio(self, municipio_id: int) -> List[Dict[str, Any]]:
        """Obtener testigos por municipio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    te.*,
                    pp.nombre_oficial as partido_nombre,
                    pp.siglas as partido_siglas,
                    me.numero_mesa,
                    l.nombre_puesto,
                    ta.estado as asignacion_estado
                FROM testigos_electorales te
                LEFT JOIN political_parties pp ON te.partido_id = pp.id
                LEFT JOIN testigo_asignaciones ta ON te.id = ta.testigo_id AND ta.estado = 'activo'
                LEFT JOIN mesas_electorales me ON ta.mesa_id = me.id
                LEFT JOIN locations l ON me.puesto_id = l.id
                WHERE te.municipio_id = ? AND te.activo = 1
                ORDER BY te.nombre_completo
            """, (municipio_id,))
            
            testigos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return testigos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo testigos: {e}")
            return []
    
    # ==================== ASIGNACIONES MASIVAS ====================
    
    def auto_assign_witnesses(self, municipio_id: int, assigned_by: int) -> Dict[str, Any]:
        """Asignación automática de testigos disponibles a mesas sin cobertura"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener mesas sin cobertura
            cursor.execute("""
                SELECT me.id as mesa_id
                FROM mesas_electorales me
                LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                WHERE me.municipio_id = ? AND ta.id IS NULL AND me.activo = 1
                ORDER BY me.numero_mesa
            """, (municipio_id,))
            
            mesas_sin_cobertura = [row['mesa_id'] for row in cursor.fetchall()]
            
            # Obtener testigos disponibles
            cursor.execute("""
                SELECT te.id as testigo_id
                FROM testigos_electorales te
                LEFT JOIN testigo_asignaciones ta ON te.id = ta.testigo_id AND ta.estado = 'activo'
                WHERE te.municipio_id = ? AND ta.id IS NULL AND te.activo = 1
                ORDER BY te.nombre_completo
            """, (municipio_id,))
            
            testigos_disponibles = [row['testigo_id'] for row in cursor.fetchall()]
            
            # Realizar asignaciones automáticas
            asignaciones_realizadas = 0
            for i, mesa_id in enumerate(mesas_sin_cobertura):
                if i < len(testigos_disponibles):
                    testigo_id = testigos_disponibles[i]
                    
                    cursor.execute("""
                        INSERT INTO testigo_asignaciones 
                        (testigo_id, mesa_id, proceso_electoral_id, estado, asignado_por, fecha_asignacion)
                        VALUES (?, ?, 1, 'asignado', ?, ?)
                    """, (testigo_id, mesa_id, assigned_by, datetime.now()))
                    
                    asignaciones_realizadas += 1
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'asignaciones_realizadas': asignaciones_realizadas,
                'mesas_sin_cobertura': len(mesas_sin_cobertura),
                'testigos_disponibles': len(testigos_disponibles),
                'message': f'Se realizaron {asignaciones_realizadas} asignaciones automáticas'
            }
            
        except Exception as e:
            self.logger.error(f"Error en asignación automática: {e}")
            return {
                'success': False,
                'error': f'Error en asignación automática: {str(e)}'
            }
    
    def bulk_reassign_witnesses(self, reassignments: List[Dict[str, int]], 
                               assigned_by: int) -> Dict[str, Any]:
        """Reasignación masiva de testigos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            successful_reassignments = 0
            errors = []
            
            for reassignment in reassignments:
                try:
                    old_mesa_id = reassignment['old_mesa_id']
                    new_mesa_id = reassignment['new_mesa_id']
                    testigo_id = reassignment['testigo_id']
                    
                    # Desactivar asignación anterior
                    cursor.execute("""
                        UPDATE testigo_asignaciones 
                        SET estado = 'reasignado', fecha_reasignacion = ?
                        WHERE testigo_id = ? AND mesa_id = ? AND estado = 'activo'
                    """, (datetime.now(), testigo_id, old_mesa_id))
                    
                    # Crear nueva asignación
                    cursor.execute("""
                        INSERT INTO testigo_asignaciones 
                        (testigo_id, mesa_id, proceso_electoral_id, estado, asignado_por, fecha_asignacion)
                        VALUES (?, ?, 1, 'asignado', ?, ?)
                    """, (testigo_id, new_mesa_id, assigned_by, datetime.now()))
                    
                    successful_reassignments += 1
                    
                except Exception as e:
                    errors.append({
                        'reassignment': reassignment,
                        'error': str(e)
                    })
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'successful_reassignments': successful_reassignments,
                'total_requested': len(reassignments),
                'errors': errors,
                'message': f'Se completaron {successful_reassignments} reasignaciones'
            }
            
        except Exception as e:
            self.logger.error(f"Error en reasignación masiva: {e}")
            return {
                'success': False,
                'error': f'Error en reasignación masiva: {str(e)}'
            }
    
    # ==================== REPORTES MUNICIPALES ====================
    
    def generate_municipal_report(self, municipio_id: int) -> Dict[str, Any]:
        """Generar reporte completo municipal"""
        try:
            overview = self.get_municipal_overview(municipio_id)
            puestos = self.get_puestos_by_municipio(municipio_id)
            testigos = self.get_testigos_by_municipio(municipio_id)
            
            # Análisis adicional
            testigos_por_partido = {}
            for testigo in testigos:
                partido = testigo.get('partido_siglas', 'Independiente')
                testigos_por_partido[partido] = testigos_por_partido.get(partido, 0) + 1
            
            return {
                'success': True,
                'data': {
                    'overview': overview,
                    'puestos': puestos,
                    'testigos_summary': {
                        'total_testigos': len(testigos),
                        'testigos_asignados': len([t for t in testigos if t.get('asignacion_estado') == 'activo']),
                        'testigos_disponibles': len([t for t in testigos if not t.get('asignacion_estado')]),
                        'por_partido': testigos_por_partido
                    },
                    'fecha_reporte': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generando reporte municipal: {e}")
            return {
                'success': False,
                'error': f'Error generando reporte: {str(e)}'
            }