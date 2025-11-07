"""
Servicio de Gestión de Prioridades
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..models import PriorityData

class PriorityService:
    """Servicio para gestión de prioridades del sistema"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN DE PRIORIDADES ====================
    
    def create_priority(self, priority_data: PriorityData) -> Dict[str, Any]:
        """Crear nueva prioridad"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_priorities 
                (entity_type, entity_id, priority_level, priority_reason, 
                 assigned_by, assigned_date, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                priority_data.entity_type,
                priority_data.entity_id,
                priority_data.priority_level,
                priority_data.priority_reason,
                priority_data.assigned_by,
                priority_data.assigned_date or datetime.now(),
                priority_data.active
            ))
            
            priority_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Prioridad creada: {priority_data.entity_type} {priority_data.entity_id}")
            
            return {
                'success': True,
                'priority_id': priority_id,
                'message': 'Prioridad asignada exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error creando prioridad: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def get_priorities_by_type(self, entity_type: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtener prioridades por tipo de entidad"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT sp.*, u.nombre_completo as assigned_by_name
                FROM system_priorities sp
                LEFT JOIN users u ON sp.assigned_by = u.id
                WHERE sp.entity_type = ?
            """
            
            params = [entity_type]
            
            if active_only:
                query += " AND sp.active = 1"
            
            query += " ORDER BY sp.priority_level, sp.assigned_date DESC"
            
            cursor.execute(query, params)
            priorities = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo prioridades: {e}")
            return []
    
    def get_high_priority_entities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener entidades de alta prioridad"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sp.*, u.nombre_completo as assigned_by_name,
                       CASE sp.entity_type
                           WHEN 'mesa' THEN (SELECT CONCAT('Mesa ', numero_mesa) FROM mesas_electorales WHERE id = sp.entity_id)
                           WHEN 'puesto' THEN (SELECT nombre_puesto FROM locations WHERE id = sp.entity_id)
                           WHEN 'municipio' THEN (SELECT nombre_municipio FROM locations WHERE id = sp.entity_id)
                           WHEN 'candidato' THEN (SELECT nombre_completo FROM candidates WHERE id = sp.entity_id)
                           ELSE 'Desconocido'
                       END as entity_name
                FROM system_priorities sp
                LEFT JOIN users u ON sp.assigned_by = u.id
                WHERE sp.active = 1 AND sp.priority_level <= 2
                ORDER BY sp.priority_level, sp.assigned_date DESC
                LIMIT ?
            """, (limit,))
            
            priorities = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo entidades de alta prioridad: {e}")
            return []
    
    def update_priority(self, priority_id: int, new_level: int, 
                       new_reason: str, updated_by: int) -> Dict[str, Any]:
        """Actualizar prioridad existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE system_priorities 
                SET priority_level = ?, priority_reason = ?, 
                    assigned_by = ?, assigned_date = ?
                WHERE id = ?
            """, (new_level, new_reason, updated_by, datetime.now(), priority_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Prioridad actualizada exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error actualizando prioridad: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def deactivate_priority(self, priority_id: int) -> Dict[str, Any]:
        """Desactivar prioridad"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE system_priorities 
                SET active = 0
                WHERE id = ?
            """, (priority_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Prioridad desactivada exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error desactivando prioridad: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def bulk_assign_priorities(self, entity_type: str, entity_ids: List[int], 
                              priority_level: int, reason: str, 
                              assigned_by: int) -> Dict[str, Any]:
        """Asignación masiva de prioridades"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            successful_assignments = 0
            errors = []
            
            for entity_id in entity_ids:
                try:
                    # Verificar si ya existe una prioridad activa
                    cursor.execute("""
                        SELECT id FROM system_priorities 
                        WHERE entity_type = ? AND entity_id = ? AND active = 1
                    """, (entity_type, entity_id))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Actualizar prioridad existente
                        cursor.execute("""
                            UPDATE system_priorities 
                            SET priority_level = ?, priority_reason = ?, 
                                assigned_by = ?, assigned_date = ?
                            WHERE id = ?
                        """, (priority_level, reason, assigned_by, datetime.now(), existing[0]))
                    else:
                        # Crear nueva prioridad
                        cursor.execute("""
                            INSERT INTO system_priorities 
                            (entity_type, entity_id, priority_level, priority_reason, 
                             assigned_by, assigned_date, active)
                            VALUES (?, ?, ?, ?, ?, ?, 1)
                        """, (entity_type, entity_id, priority_level, reason, 
                             assigned_by, datetime.now()))
                    
                    successful_assignments += 1
                    
                except Exception as e:
                    errors.append({
                        'entity_id': entity_id,
                        'error': str(e)
                    })
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'successful_assignments': successful_assignments,
                'total_requested': len(entity_ids),
                'errors': errors,
                'message': f'Se asignaron {successful_assignments} prioridades'
            }
            
        except Exception as e:
            self.logger.error(f"Error en asignación masiva: {e}")
            return {
                'success': False,
                'error': f'Error en asignación masiva: {str(e)}'
            }
    
    def get_priority_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de prioridades"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Estadísticas por nivel de prioridad
            cursor.execute("""
                SELECT priority_level, COUNT(*) as count
                FROM system_priorities 
                WHERE active = 1
                GROUP BY priority_level
                ORDER BY priority_level
            """)
            
            priority_levels = [dict(row) for row in cursor.fetchall()]
            
            # Estadísticas por tipo de entidad
            cursor.execute("""
                SELECT entity_type, COUNT(*) as count,
                       AVG(priority_level) as avg_priority
                FROM system_priorities 
                WHERE active = 1
                GROUP BY entity_type
            """)
            
            entity_types = [dict(row) for row in cursor.fetchall()]
            
            # Total de prioridades activas
            cursor.execute("SELECT COUNT(*) FROM system_priorities WHERE active = 1")
            total_active = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'data': {
                    'total_active_priorities': total_active,
                    'by_priority_level': priority_levels,
                    'by_entity_type': entity_types,
                    'fecha_calculo': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'success': False,
                'error': f'Error obteniendo estadísticas: {str(e)}'
            }