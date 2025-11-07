#!/usr/bin/env python3
"""
PriorityService - Servicio para gestión de prioridades de recolección electoral
Permite configurar y gestionar prioridades de partidos, coaliciones, candidatos y elecciones
"""

import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import logging

class PriorityService:
    """Servicio para gestión de prioridades de recolección electoral"""
    
    def __init__(self, db_path: str = 'caqueta_electoral.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN DE CONFIGURACIONES ====================
    
    def get_all_configurations(self) -> List[Dict]:
        """Obtener todas las configuraciones de prioridades"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cp.*, u.nombre_completo as created_by_name,
                       COUNT(DISTINCT pp.id) as total_partidos,
                       COUNT(DISTINCT pc.id) as total_coaliciones,
                       COUNT(DISTINCT pcan.id) as total_candidatos,
                       COUNT(DISTINCT ppr.id) as total_procesos,
                       COUNT(DISTINCT pm.id) as total_municipios
                FROM configuracion_prioridades cp
                LEFT JOIN users u ON cp.created_by = u.id
                LEFT JOIN prioridades_partidos pp ON cp.id = pp.configuracion_id AND pp.activo = 1
                LEFT JOIN prioridades_coaliciones pc ON cp.id = pc.configuracion_id AND pc.activo = 1
                LEFT JOIN prioridades_candidatos pcan ON cp.id = pcan.configuracion_id AND pcan.activo = 1
                LEFT JOIN prioridades_procesos ppr ON cp.id = ppr.configuracion_id AND ppr.activo = 1
                LEFT JOIN prioridades_municipios pm ON cp.id = pm.configuracion_id AND pm.activo = 1
                GROUP BY cp.id
                ORDER BY cp.activa DESC, cp.created_at DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            configurations = [dict(row) for row in results]
            return configurations
            
        except Exception as e:
            self.logger.error(f"Error obteniendo configuraciones: {e}")
            raise
    
    def get_active_configuration(self) -> Optional[Dict]:
        """Obtener la configuración activa"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM configuracion_prioridades 
                WHERE activa = 1 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración activa: {e}")
            raise
    
    def create_configuration(self, config_data: Dict, user_id: int) -> int:
        """Crear nueva configuración de prioridades"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Si se marca como activa, desactivar las demás
            if config_data.get('activa', False):
                cursor.execute("UPDATE configuracion_prioridades SET activa = 0")
            
            query = """
                INSERT INTO configuracion_prioridades 
                (nombre, descripcion, activa, fecha_inicio, fecha_fin, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                config_data['nombre'],
                config_data.get('descripcion'),
                1 if config_data.get('activa', False) else 0,
                config_data.get('fecha_inicio'),
                config_data.get('fecha_fin'),
                user_id
            ))
            
            config_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Configuración creada: {config_id} - {config_data['nombre']}")
            return config_id
            
        except Exception as e:
            self.logger.error(f"Error creando configuración: {e}")
            raise
    
    def activate_configuration(self, config_id: int) -> bool:
        """Activar una configuración específica"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Desactivar todas las configuraciones
            cursor.execute("UPDATE configuracion_prioridades SET activa = 0")
            
            # Activar la configuración específica
            cursor.execute("""
                UPDATE configuracion_prioridades 
                SET activa = 1, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (config_id,))
            
            if cursor.rowcount == 0:
                raise ValueError("Configuración no encontrada")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Configuración activada: {config_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error activando configuración: {e}")
            raise
    
    # ==================== GESTIÓN DE PRIORIDADES DE PARTIDOS ====================
    
    def get_party_priorities(self, config_id: int = None) -> List[Dict]:
        """Obtener prioridades de partidos"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return []
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT pp.*, p.nombre as partido_nombre, p.sigla as partido_sigla, 
                       p.color_principal as partido_color,
                       COUNT(c.id) as total_candidatos,
                       CASE pp.prioridad 
                           WHEN 1 THEN 'Alta'
                           WHEN 2 THEN 'Media'
                           WHEN 3 THEN 'Baja'
                           ELSE 'Sin definir'
                       END as prioridad_texto
                FROM prioridades_partidos pp
                JOIN partidos_politicos p ON pp.partido_id = p.id
                LEFT JOIN candidatos c ON p.id = c.partido_id AND c.activo = 1
                WHERE pp.configuracion_id = ? AND pp.activo = 1
                GROUP BY pp.id, p.id
                ORDER BY pp.prioridad ASC, p.nombre ASC
            """
            
            cursor.execute(query, (config_id,))
            results = cursor.fetchall()
            conn.close()
            
            priorities = [dict(row) for row in results]
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo prioridades de partidos: {e}")
            raise
    
    def set_party_priority(self, config_id: int, partido_id: int, prioridad: int, observaciones: str = None) -> bool:
        """Establecer prioridad de un partido"""
        try:
            if prioridad not in [1, 2, 3]:
                raise ValueError("La prioridad debe ser 1 (Alta), 2 (Media) o 3 (Baja)")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT id FROM prioridades_partidos 
                WHERE configuracion_id = ? AND partido_id = ?
            """, (config_id, partido_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar existente
                cursor.execute("""
                    UPDATE prioridades_partidos 
                    SET prioridad = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE configuracion_id = ? AND partido_id = ?
                """, (prioridad, observaciones, config_id, partido_id))
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO prioridades_partidos 
                    (configuracion_id, partido_id, prioridad, observaciones)
                    VALUES (?, ?, ?, ?)
                """, (config_id, partido_id, prioridad, observaciones))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Prioridad de partido establecida: {partido_id} - Prioridad {prioridad}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error estableciendo prioridad de partido: {e}")
            raise
    
    def bulk_set_party_priorities(self, config_id: int, priorities_data: List[Dict]) -> Dict:
        """Establecer prioridades de múltiples partidos"""
        try:
            results = {
                'processed': 0,
                'errors': []
            }
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for item in priorities_data:
                try:
                    partido_id = item['partido_id']
                    prioridad = item['prioridad']
                    observaciones = item.get('observaciones')
                    
                    if prioridad not in [1, 2, 3]:
                        results['errors'].append(f"Partido {partido_id}: Prioridad inválida")
                        continue
                    
                    # Verificar si ya existe
                    cursor.execute("""
                        SELECT id FROM prioridades_partidos 
                        WHERE configuracion_id = ? AND partido_id = ?
                    """, (config_id, partido_id))
                    
                    if cursor.fetchone():
                        # Actualizar
                        cursor.execute("""
                            UPDATE prioridades_partidos 
                            SET prioridad = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE configuracion_id = ? AND partido_id = ?
                        """, (prioridad, observaciones, config_id, partido_id))
                    else:
                        # Crear
                        cursor.execute("""
                            INSERT INTO prioridades_partidos 
                            (configuracion_id, partido_id, prioridad, observaciones)
                            VALUES (?, ?, ?, ?)
                        """, (config_id, partido_id, prioridad, observaciones))
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Partido {item.get('partido_id', 'N/A')}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en asignación masiva de prioridades: {e}")
            raise
    
    # ==================== GESTIÓN DE PRIORIDADES DE CANDIDATOS ====================
    
    def get_candidate_priorities(self, config_id: int = None, filters: Dict = None) -> List[Dict]:
        """Obtener prioridades de candidatos"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return []
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT pc.*, c.nombre_completo as candidato_nombre, c.cedula,
                       p.nombre as partido_nombre, p.sigla as partido_sigla,
                       car.nombre as cargo_nombre,
                       m.nombre as municipio_nombre,
                       CASE pc.prioridad 
                           WHEN 1 THEN 'Alta'
                           WHEN 2 THEN 'Media'
                           WHEN 3 THEN 'Baja'
                           ELSE 'Sin definir'
                       END as prioridad_texto
                FROM prioridades_candidatos pc
                JOIN candidatos c ON pc.candidato_id = c.id
                LEFT JOIN partidos_politicos p ON c.partido_id = p.id
                LEFT JOIN cargos_electorales car ON c.cargo_id = car.id
                LEFT JOIN municipios m ON c.municipio_id = m.id
                WHERE pc.configuracion_id = ? AND pc.activo = 1
            """
            
            params = [config_id]
            
            # Aplicar filtros
            if filters:
                if filters.get('partido_id'):
                    query += " AND c.partido_id = ?"
                    params.append(filters['partido_id'])
                
                if filters.get('cargo_id'):
                    query += " AND c.cargo_id = ?"
                    params.append(filters['cargo_id'])
                
                if filters.get('prioridad'):
                    query += " AND pc.prioridad = ?"
                    params.append(filters['prioridad'])
            
            query += " ORDER BY pc.prioridad ASC, c.nombre_completo ASC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            priorities = [dict(row) for row in results]
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo prioridades de candidatos: {e}")
            raise
    
    def set_candidate_priority(self, config_id: int, candidato_id: int, prioridad: int, observaciones: str = None) -> bool:
        """Establecer prioridad de un candidato"""
        try:
            if prioridad not in [1, 2, 3]:
                raise ValueError("La prioridad debe ser 1 (Alta), 2 (Media) o 3 (Baja)")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT id FROM prioridades_candidatos 
                WHERE configuracion_id = ? AND candidato_id = ?
            """, (config_id, candidato_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar existente
                cursor.execute("""
                    UPDATE prioridades_candidatos 
                    SET prioridad = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE configuracion_id = ? AND candidato_id = ?
                """, (prioridad, observaciones, config_id, candidato_id))
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO prioridades_candidatos 
                    (configuracion_id, candidato_id, prioridad, observaciones)
                    VALUES (?, ?, ?, ?)
                """, (config_id, candidato_id, prioridad, observaciones))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Prioridad de candidato establecida: {candidato_id} - Prioridad {prioridad}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error estableciendo prioridad de candidato: {e}")
            raise
    
    # ==================== GESTIÓN DE PRIORIDADES DE PROCESOS ELECTORALES ====================
    
    def get_process_priorities(self, config_id: int = None) -> List[Dict]:
        """Obtener prioridades de procesos electorales"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return []
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT pp.*, pe.nombre as proceso_nombre, pe.tipo as proceso_tipo,
                       pe.fecha_eleccion, pe.estado as proceso_estado,
                       CASE pp.prioridad 
                           WHEN 1 THEN 'Alta'
                           WHEN 2 THEN 'Media'
                           WHEN 3 THEN 'Baja'
                           ELSE 'Sin definir'
                       END as prioridad_texto
                FROM prioridades_procesos pp
                JOIN procesos_electorales pe ON pp.proceso_id = pe.id
                WHERE pp.configuracion_id = ? AND pp.activo = 1
                ORDER BY pp.prioridad ASC, pe.fecha_eleccion ASC
            """
            
            cursor.execute(query, (config_id,))
            results = cursor.fetchall()
            conn.close()
            
            priorities = [dict(row) for row in results]
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo prioridades de procesos: {e}")
            raise
    
    def set_process_priority(self, config_id: int, proceso_id: int, prioridad: int, observaciones: str = None) -> bool:
        """Establecer prioridad de un proceso electoral"""
        try:
            if prioridad not in [1, 2, 3]:
                raise ValueError("La prioridad debe ser 1 (Alta), 2 (Media) o 3 (Baja)")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT id FROM prioridades_procesos 
                WHERE configuracion_id = ? AND proceso_id = ?
            """, (config_id, proceso_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar existente
                cursor.execute("""
                    UPDATE prioridades_procesos 
                    SET prioridad = ?, observaciones = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE configuracion_id = ? AND proceso_id = ?
                """, (prioridad, observaciones, config_id, proceso_id))
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO prioridades_procesos 
                    (configuracion_id, proceso_id, prioridad, observaciones)
                    VALUES (?, ?, ?, ?)
                """, (config_id, proceso_id, prioridad, observaciones))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Prioridad de proceso establecida: {proceso_id} - Prioridad {prioridad}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error estableciendo prioridad de proceso: {e}")
            raise
    
    # ==================== GESTIÓN DE METAS DE RECOLECCIÓN ====================
    
    def get_collection_goals(self, config_id: int = None) -> List[Dict]:
        """Obtener metas de recolección"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return []
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT mr.*,
                       CASE mr.tipo_entidad
                           WHEN 'partido' THEN p.nombre
                           WHEN 'coalicion' THEN coal.nombre
                           WHEN 'candidato' THEN c.nombre_completo
                           WHEN 'proceso' THEN pe.nombre
                           WHEN 'municipio' THEN m.nombre
                           ELSE 'Entidad desconocida'
                       END as entidad_nombre,
                       CASE 
                           WHEN mr.meta_porcentaje IS NOT NULL THEN 
                               CAST(mr.progreso_actual AS FLOAT) / mr.meta_porcentaje * 100
                           WHEN mr.meta_cantidad IS NOT NULL THEN 
                               CAST(mr.progreso_actual AS FLOAT) / mr.meta_cantidad * 100
                           ELSE 0
                       END as porcentaje_cumplimiento
                FROM metas_recoleccion mr
                LEFT JOIN partidos_politicos p ON mr.tipo_entidad = 'partido' AND mr.entidad_id = p.id
                LEFT JOIN coaliciones coal ON mr.tipo_entidad = 'coalicion' AND mr.entidad_id = coal.id
                LEFT JOIN candidatos c ON mr.tipo_entidad = 'candidato' AND mr.entidad_id = c.id
                LEFT JOIN procesos_electorales pe ON mr.tipo_entidad = 'proceso' AND mr.entidad_id = pe.id
                LEFT JOIN municipios m ON mr.tipo_entidad = 'municipio' AND mr.entidad_id = m.id
                WHERE mr.configuracion_id = ? AND mr.activo = 1
                ORDER BY mr.fecha_limite ASC, mr.tipo_entidad ASC
            """
            
            cursor.execute(query, (config_id,))
            results = cursor.fetchall()
            conn.close()
            
            goals = [dict(row) for row in results]
            return goals
            
        except Exception as e:
            self.logger.error(f"Error obteniendo metas de recolección: {e}")
            raise
    
    def set_collection_goal(self, config_id: int, goal_data: Dict) -> int:
        """Establecer meta de recolección"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT id FROM metas_recoleccion 
                WHERE configuracion_id = ? AND tipo_entidad = ? AND entidad_id = ?
            """, (config_id, goal_data['tipo_entidad'], goal_data['entidad_id']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar existente
                cursor.execute("""
                    UPDATE metas_recoleccion 
                    SET meta_porcentaje = ?, meta_cantidad = ?, fecha_limite = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE configuracion_id = ? AND tipo_entidad = ? AND entidad_id = ?
                """, (
                    goal_data.get('meta_porcentaje'),
                    goal_data.get('meta_cantidad'),
                    goal_data.get('fecha_limite'),
                    config_id,
                    goal_data['tipo_entidad'],
                    goal_data['entidad_id']
                ))
                goal_id = existing[0]
            else:
                # Crear nuevo
                cursor.execute("""
                    INSERT INTO metas_recoleccion 
                    (configuracion_id, tipo_entidad, entidad_id, meta_porcentaje, 
                     meta_cantidad, fecha_limite)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    config_id,
                    goal_data['tipo_entidad'],
                    goal_data['entidad_id'],
                    goal_data.get('meta_porcentaje'),
                    goal_data.get('meta_cantidad'),
                    goal_data.get('fecha_limite')
                ))
                goal_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Meta de recolección establecida: {goal_id}")
            return goal_id
            
        except Exception as e:
            self.logger.error(f"Error estableciendo meta de recolección: {e}")
            raise
    
    # ==================== REPORTES Y ANÁLISIS ====================
    
    def get_priority_summary(self, config_id: int = None) -> Dict:
        """Obtener resumen de prioridades"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return {}
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            summary = {
                'configuracion_id': config_id,
                'partidos': {'alta': 0, 'media': 0, 'baja': 0, 'total': 0},
                'coaliciones': {'alta': 0, 'media': 0, 'baja': 0, 'total': 0},
                'candidatos': {'alta': 0, 'media': 0, 'baja': 0, 'total': 0},
                'procesos': {'alta': 0, 'media': 0, 'baja': 0, 'total': 0},
                'municipios': {'alta': 0, 'media': 0, 'baja': 0, 'total': 0}
            }
            
            # Contar prioridades de partidos
            cursor.execute("""
                SELECT prioridad, COUNT(*) as count 
                FROM prioridades_partidos 
                WHERE configuracion_id = ? AND activo = 1 
                GROUP BY prioridad
            """, (config_id,))
            
            for row in cursor.fetchall():
                prioridad_key = {1: 'alta', 2: 'media', 3: 'baja'}.get(row[0], 'baja')
                summary['partidos'][prioridad_key] = row[1]
                summary['partidos']['total'] += row[1]
            
            # Contar prioridades de candidatos
            cursor.execute("""
                SELECT prioridad, COUNT(*) as count 
                FROM prioridades_candidatos 
                WHERE configuracion_id = ? AND activo = 1 
                GROUP BY prioridad
            """, (config_id,))
            
            for row in cursor.fetchall():
                prioridad_key = {1: 'alta', 2: 'media', 3: 'baja'}.get(row[0], 'baja')
                summary['candidatos'][prioridad_key] = row[1]
                summary['candidatos']['total'] += row[1]
            
            # Contar prioridades de procesos
            cursor.execute("""
                SELECT prioridad, COUNT(*) as count 
                FROM prioridades_procesos 
                WHERE configuracion_id = ? AND activo = 1 
                GROUP BY prioridad
            """, (config_id,))
            
            for row in cursor.fetchall():
                prioridad_key = {1: 'alta', 2: 'media', 3: 'baja'}.get(row[0], 'baja')
                summary['procesos'][prioridad_key] = row[1]
                summary['procesos']['total'] += row[1]
            
            conn.close()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de prioridades: {e}")
            raise
    
    def get_high_priority_entities(self, config_id: int = None) -> Dict:
        """Obtener entidades de alta prioridad para enfocar recolección"""
        try:
            if config_id is None:
                active_config = self.get_active_configuration()
                if not active_config:
                    return {}
                config_id = active_config['id']
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            high_priority = {
                'partidos': [],
                'candidatos': [],
                'procesos': [],
                'municipios': []
            }
            
            # Partidos de alta prioridad
            cursor.execute("""
                SELECT pp.*, p.nombre, p.sigla, p.color_principal
                FROM prioridades_partidos pp
                JOIN partidos_politicos p ON pp.partido_id = p.id
                WHERE pp.configuracion_id = ? AND pp.prioridad = 1 AND pp.activo = 1
                ORDER BY p.nombre
            """, (config_id,))
            
            high_priority['partidos'] = [dict(row) for row in cursor.fetchall()]
            
            # Candidatos de alta prioridad
            cursor.execute("""
                SELECT pc.*, c.nombre_completo, c.cedula, p.sigla as partido_sigla,
                       car.nombre as cargo_nombre
                FROM prioridades_candidatos pc
                JOIN candidatos c ON pc.candidato_id = c.id
                LEFT JOIN partidos_politicos p ON c.partido_id = p.id
                LEFT JOIN cargos_electorales car ON c.cargo_id = car.id
                WHERE pc.configuracion_id = ? AND pc.prioridad = 1 AND pc.activo = 1
                ORDER BY c.nombre_completo
            """, (config_id,))
            
            high_priority['candidatos'] = [dict(row) for row in cursor.fetchall()]
            
            # Procesos de alta prioridad
            cursor.execute("""
                SELECT pp.*, pe.nombre, pe.tipo, pe.fecha_eleccion
                FROM prioridades_procesos pp
                JOIN procesos_electorales pe ON pp.proceso_id = pe.id
                WHERE pp.configuracion_id = ? AND pp.prioridad = 1 AND pp.activo = 1
                ORDER BY pe.fecha_eleccion
            """, (config_id,))
            
            high_priority['procesos'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return high_priority
            
        except Exception as e:
            self.logger.error(f"Error obteniendo entidades de alta prioridad: {e}")
            raise