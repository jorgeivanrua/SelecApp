#!/usr/bin/env python3
"""
MunicipalCoordinationService - Servicio para coordinación municipal
Consolidación de E-14 a E-24, verificación y generación de informes
"""

import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import logging
import os
import hashlib

class MunicipalCoordinationService:
    """Servicio para coordinación municipal electoral"""
    
    def __init__(self, db_path: str = 'caqueta_electoral.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def log_action(self, municipio_id: int, usuario_id: int, accion: str, 
                   entidad_tipo: str = None, entidad_id: int = None, 
                   descripcion: str = None, datos_adicionales: Dict = None):
        """Registrar acción en el log de coordinación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO log_coordinacion_municipal 
                (municipio_id, usuario_id, accion, entidad_tipo, entidad_id, 
                 descripcion, datos_adicionales)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                municipio_id, usuario_id, accion, entidad_tipo, entidad_id,
                descripcion, json.dumps(datos_adicionales) if datos_adicionales else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando acción: {e}")
    
    # ==================== GESTIÓN DE CONSOLIDACIONES ====================
    
    def get_municipal_consolidations(self, municipio_id: int, proceso_id: int = None) -> List[Dict]:
        """Obtener consolidaciones municipales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT c.*, m.nombre as municipio_nombre, pe.nombre as proceso_nombre,
                       u1.nombre_completo as consolidado_por_nombre,
                       u2.nombre_completo as verificado_por_nombre,
                       ec.porcentaje_participacion, ec.anomalias_detectadas, ec.calidad_datos
                FROM consolidaciones_e24 c
                JOIN municipios m ON c.municipio_id = m.id
                LEFT JOIN procesos_electorales pe ON c.proceso_electoral_id = pe.id
                LEFT JOIN users u1 ON c.consolidado_por = u1.id
                LEFT JOIN users u2 ON c.verificado_por = u2.id
                LEFT JOIN estadisticas_consolidacion ec ON c.id = ec.consolidacion_id
                WHERE c.municipio_id = ?
            """
            
            params = [municipio_id]
            
            if proceso_id:
                query += " AND c.proceso_electoral_id = ?"
                params.append(proceso_id)
            
            query += " ORDER BY c.tipo_eleccion, c.created_at DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            consolidations = []
            for row in results:
                consolidation = dict(row)
                # Calcular progreso
                if consolidation['total_mesas'] > 0:
                    consolidation['progreso_porcentaje'] = (
                        consolidation['mesas_procesadas'] / consolidation['total_mesas'] * 100
                    )
                else:
                    consolidation['progreso_porcentaje'] = 0
                
                consolidations.append(consolidation)
            
            return consolidations
            
        except Exception as e:
            self.logger.error(f"Error obteniendo consolidaciones: {e}")
            raise
    
    def get_consolidation_status(self, municipio_id: int) -> Dict:
        """Obtener estado general de consolidación municipal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_consolidaciones,
                    SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as completadas,
                    SUM(CASE WHEN estado = 'consolidando' THEN 1 ELSE 0 END) as en_proceso,
                    SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
                    SUM(total_mesas) as total_mesas,
                    SUM(mesas_procesadas) as mesas_procesadas,
                    SUM(total_votos_validos + total_votos_blancos + total_votos_nulos) as total_votos
                FROM consolidaciones_e24 
                WHERE municipio_id = ?
            """, (municipio_id,))
            
            stats = dict(cursor.fetchone())
            
            # Calcular progreso general
            if stats['total_mesas'] > 0:
                stats['progreso_general'] = (stats['mesas_procesadas'] / stats['total_mesas'] * 100)
            else:
                stats['progreso_general'] = 0
            
            # Discrepancias pendientes
            cursor.execute("""
                SELECT COUNT(*) as discrepancias_pendientes
                FROM discrepancias_e24 d
                JOIN consolidaciones_e24 c ON d.consolidacion_id = c.id
                WHERE c.municipio_id = ? AND d.estado = 'pendiente'
            """, (municipio_id,))
            
            stats['discrepancias_pendientes'] = cursor.fetchone()[0]
            
            # Reclamaciones activas
            cursor.execute("""
                SELECT COUNT(*) as reclamaciones_activas
                FROM reclamaciones_e24 r
                JOIN consolidaciones_e24 c ON r.consolidacion_id = c.id
                WHERE c.municipio_id = ? AND r.estado IN ('generada', 'enviada', 'en_revision')
            """, (municipio_id,))
            
            stats['reclamaciones_activas'] = cursor.fetchone()[0]
            
            conn.close()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de consolidación: {e}")
            raise
    
    def start_consolidation(self, municipio_id: int, proceso_id: int, tipo_eleccion: str, usuario_id: int) -> int:
        """Iniciar proceso de consolidación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("""
                SELECT id FROM consolidaciones_e24 
                WHERE municipio_id = ? AND proceso_electoral_id = ? AND tipo_eleccion = ?
            """, (municipio_id, proceso_id, tipo_eleccion))
            
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar estado si existe
                cursor.execute("""
                    UPDATE consolidaciones_e24 
                    SET estado = 'consolidando', consolidado_por = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (usuario_id, existing[0]))
                consolidation_id = existing[0]
            else:
                # Contar mesas disponibles para este tipo de elección
                cursor.execute("""
                    SELECT COUNT(*) FROM mesas_votacion mv
                    JOIN puestos_votacion pv ON mv.puesto_id = pv.id
                    WHERE pv.municipio_id = ? AND mv.activa = 1
                """, (municipio_id,))
                
                total_mesas = cursor.fetchone()[0]
                
                # Crear nueva consolidación
                cursor.execute("""
                    INSERT INTO consolidaciones_e24 
                    (municipio_id, proceso_electoral_id, tipo_eleccion, estado, 
                     total_mesas, consolidado_por)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (municipio_id, proceso_id, tipo_eleccion, 'consolidando', total_mesas, usuario_id))
                
                consolidation_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(municipio_id, usuario_id, 'iniciar_consolidacion', 
                          'consolidacion', consolidation_id, 
                          f'Iniciada consolidación {tipo_eleccion}')
            
            self.logger.info(f"Consolidación iniciada: {consolidation_id}")
            return consolidation_id
            
        except Exception as e:
            self.logger.error(f"Error iniciando consolidación: {e}")
            raise
    
    def process_e14_to_consolidation(self, consolidation_id: int, usuario_id: int) -> Dict:
        """Procesar E-14s para consolidación automática"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información de la consolidación
            cursor.execute("""
                SELECT c.*, m.nombre as municipio_nombre 
                FROM consolidaciones_e24 c
                JOIN municipios m ON c.municipio_id = m.id
                WHERE c.id = ?
            """, (consolidation_id,))
            
            consolidation = dict(cursor.fetchone())
            
            # Obtener E-14s del municipio para este tipo de elección
            cursor.execute("""
                SELECT e14.*, mv.numero as mesa_numero, pv.nombre as puesto_nombre
                FROM e14_capturas e14
                JOIN mesas_votacion mv ON e14.mesa_id = mv.id
                JOIN puestos_votacion pv ON mv.puesto_id = pv.id
                WHERE pv.municipio_id = ? AND e14.confirmado = 1
                ORDER BY pv.nombre, mv.numero
            """, (consolidation['municipio_id'],))
            
            e14_forms = cursor.fetchall()
            
            # Consolidar datos
            total_votos_validos = 0
            total_votos_blancos = 0
            total_votos_nulos = 0
            mesas_procesadas = 0
            
            for e14 in e14_forms:
                total_votos_validos += e14['votos_validos'] or 0
                total_votos_blancos += e14['votos_blanco'] or 0
                total_votos_nulos += e14['votos_nulos'] or 0
                mesas_procesadas += 1
            
            total_tarjetones = total_votos_validos + total_votos_blancos + total_votos_nulos
            
            # Actualizar consolidación
            cursor.execute("""
                UPDATE consolidaciones_e24 
                SET mesas_procesadas = ?, total_votos_validos = ?, total_votos_blancos = ?,
                    total_votos_nulos = ?, total_tarjetones = ?, 
                    estado = CASE WHEN ? >= total_mesas THEN 'completado' ELSE 'consolidando' END,
                    fecha_consolidacion = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (mesas_procesadas, total_votos_validos, total_votos_blancos, 
                  total_votos_nulos, total_tarjetones, mesas_procesadas, consolidation_id))
            
            # Crear/actualizar estadísticas
            cursor.execute("""
                INSERT OR REPLACE INTO estadisticas_consolidacion 
                (consolidacion_id, total_votos_depositados, total_mesas_instaladas)
                VALUES (?, ?, ?)
            """, (consolidation_id, total_tarjetones, mesas_procesadas))
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(consolidation['municipio_id'], usuario_id, 'procesar_e14', 
                          'consolidacion', consolidation_id, 
                          f'Procesados {mesas_procesadas} E-14s')
            
            result = {
                'consolidation_id': consolidation_id,
                'mesas_procesadas': mesas_procesadas,
                'total_votos_validos': total_votos_validos,
                'total_votos_blancos': total_votos_blancos,
                'total_votos_nulos': total_votos_nulos,
                'total_tarjetones': total_tarjetones,
                'estado': 'completado' if mesas_procesadas >= consolidation['total_mesas'] else 'consolidando'
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error procesando E-14s: {e}")
            raise
    
    def generate_e24_image(self, consolidation_id: int, usuario_id: int) -> str:
        """Generar imagen E-24 a partir de consolidación"""
        try:
            # Simulación de generación de imagen E-24
            # En implementación real, aquí se generaría la imagen del formulario
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener datos de consolidación
            cursor.execute("""
                SELECT c.*, m.nombre as municipio_nombre 
                FROM consolidaciones_e24 c
                JOIN municipios m ON c.municipio_id = m.id
                WHERE c.id = ?
            """, (consolidation_id,))
            
            consolidation = dict(cursor.fetchone())
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"E24_{consolidation['municipio_nombre']}_{consolidation['tipo_eleccion']}_{timestamp}.png"
            filepath = f"static/generated_e24/{filename}"
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Simular creación de archivo (en implementación real sería generación de imagen)
            with open(filepath, 'w') as f:
                f.write(f"E-24 Generado para {consolidation['municipio_nombre']} - {consolidation['tipo_eleccion']}\n")
                f.write(f"Votos válidos: {consolidation['total_votos_validos']}\n")
                f.write(f"Votos en blanco: {consolidation['total_votos_blancos']}\n")
                f.write(f"Votos nulos: {consolidation['total_votos_nulos']}\n")
                f.write(f"Total tarjetones: {consolidation['total_tarjetones']}\n")
            
            # Actualizar consolidación con ruta de imagen
            cursor.execute("""
                UPDATE consolidaciones_e24 
                SET imagen_e24_generado = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (filepath, consolidation_id))
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(consolidation['municipio_id'], usuario_id, 'generar_e24', 
                          'consolidacion', consolidation_id, 
                          f'E-24 generado: {filename}')
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generando E-24: {e}")
            raise
    
    # ==================== VERIFICACIÓN E-24 ====================
    
    def upload_official_e24(self, consolidation_id: int, image_path: str, usuario_id: int) -> bool:
        """Subir imagen oficial E-24 de Registraduría"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Actualizar consolidación con imagen oficial
            cursor.execute("""
                UPDATE consolidaciones_e24 
                SET imagen_e24_oficial = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (image_path, consolidation_id))
            
            if cursor.rowcount == 0:
                raise ValueError("Consolidación no encontrada")
            
            # Obtener información de consolidación
            cursor.execute("""
                SELECT municipio_id FROM consolidaciones_e24 WHERE id = ?
            """, (consolidation_id,))
            
            municipio_id = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(municipio_id, usuario_id, 'subir_e24_oficial', 
                          'consolidacion', consolidation_id, 
                          'E-24 oficial subido para verificación')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error subiendo E-24 oficial: {e}")
            raise
    
    def verify_e24_comparison(self, consolidation_id: int, usuario_id: int) -> Dict:
        """Verificar y comparar E-24 generado vs oficial"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener consolidación
            cursor.execute("""
                SELECT * FROM consolidaciones_e24 WHERE id = ?
            """, (consolidation_id,))
            
            consolidation = dict(cursor.fetchone())
            
            if not consolidation['imagen_e24_oficial']:
                raise ValueError("No se ha subido E-24 oficial para comparar")
            
            # Simulación de comparación OCR (en implementación real sería OCR real)
            # Generar algunas discrepancias de ejemplo
            discrepancias = []
            
            # Simular diferencia menor en votos válidos
            if consolidation['total_votos_validos'] > 1000:
                diferencia = 2  # Diferencia simulada
                discrepancias.append({
                    'tipo_discrepancia': 'total_votos',
                    'campo_afectado': 'total_votos_validos',
                    'valor_generado': str(consolidation['total_votos_validos']),
                    'valor_oficial': str(consolidation['total_votos_validos'] - diferencia),
                    'diferencia': diferencia,
                    'severidad': 'baja',
                    'descripcion': f'Diferencia de {diferencia} votos en total válidos'
                })
            
            # Insertar discrepancias encontradas
            discrepancias_creadas = 0
            for disc in discrepancias:
                cursor.execute("""
                    INSERT INTO discrepancias_e24 
                    (consolidacion_id, tipo_discrepancia, campo_afectado, valor_generado,
                     valor_oficial, diferencia, severidad, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (consolidation_id, disc['tipo_discrepancia'], disc['campo_afectado'],
                      disc['valor_generado'], disc['valor_oficial'], disc['diferencia'],
                      disc['severidad'], disc['descripcion']))
                discrepancias_creadas += 1
            
            # Actualizar estado de verificación
            estado_verificacion = 'con_discrepancias' if discrepancias_creadas > 0 else 'verificado'
            
            cursor.execute("""
                UPDATE consolidaciones_e24 
                SET discrepancias_detectadas = ?, estado_verificacion = ?, 
                    verificado_por = ?, fecha_verificacion = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (discrepancias_creadas, estado_verificacion, usuario_id, consolidation_id))
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(consolidation['municipio_id'], usuario_id, 'verificar_e24', 
                          'consolidacion', consolidation_id, 
                          f'Verificación completada: {discrepancias_creadas} discrepancias')
            
            result = {
                'consolidation_id': consolidation_id,
                'discrepancias_encontradas': discrepancias_creadas,
                'estado_verificacion': estado_verificacion,
                'discrepancias': discrepancias
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error verificando E-24: {e}")
            raise
    
    def get_discrepancies(self, consolidation_id: int) -> List[Dict]:
        """Obtener discrepancias de una consolidación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT d.*, u.nombre_completo as revisado_por_nombre
                FROM discrepancias_e24 d
                LEFT JOIN users u ON d.revisado_por = u.id
                WHERE d.consolidacion_id = ?
                ORDER BY d.severidad DESC, d.created_at DESC
            """, (consolidation_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            discrepancies = [dict(row) for row in results]
            return discrepancies
            
        except Exception as e:
            self.logger.error(f"Error obteniendo discrepancias: {e}")
            raise
    
    # ==================== GENERACIÓN DE RECLAMACIONES ====================
    
    def generate_claim(self, consolidation_id: int, tipo_reclamacion: str, 
                      descripcion: str, usuario_id: int) -> int:
        """Generar reclamación por discrepancias"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generar número de reclamación único
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            numero_reclamacion = f"REC-{consolidation_id}-{timestamp}"
            
            # Obtener información de consolidación
            cursor.execute("""
                SELECT municipio_id FROM consolidaciones_e24 WHERE id = ?
            """, (consolidation_id,))
            
            municipio_id = cursor.fetchone()[0]
            
            # Crear reclamación
            cursor.execute("""
                INSERT INTO reclamaciones_e24 
                (consolidacion_id, numero_reclamacion, tipo_reclamacion, descripcion, 
                 generada_por, enviada_a)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (consolidation_id, numero_reclamacion, tipo_reclamacion, descripcion,
                  usuario_id, 'Registraduría Nacional del Estado Civil'))
            
            claim_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Registrar acción
            self.log_action(municipio_id, usuario_id, 'generar_reclamacion', 
                          'reclamacion', claim_id, 
                          f'Reclamación generada: {numero_reclamacion}')
            
            return claim_id
            
        except Exception as e:
            self.logger.error(f"Error generando reclamación: {e}")
            raise
    
    def get_claims(self, consolidation_id: int = None, municipio_id: int = None) -> List[Dict]:
        """Obtener reclamaciones"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT r.*, c.tipo_eleccion, c.municipio_id, m.nombre as municipio_nombre,
                       u.nombre_completo as generada_por_nombre
                FROM reclamaciones_e24 r
                JOIN consolidaciones_e24 c ON r.consolidacion_id = c.id
                JOIN municipios m ON c.municipio_id = m.id
                JOIN users u ON r.generada_por = u.id
                WHERE 1=1
            """
            
            params = []
            
            if consolidation_id:
                query += " AND r.consolidacion_id = ?"
                params.append(consolidation_id)
            
            if municipio_id:
                query += " AND c.municipio_id = ?"
                params.append(municipio_id)
            
            query += " ORDER BY r.fecha_generacion DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            claims = [dict(row) for row in results]
            return claims
            
        except Exception as e:
            self.logger.error(f"Error obteniendo reclamaciones: {e}")
            raise
    
    # ==================== REPORTES Y ESTADÍSTICAS ====================
    
    def get_municipal_dashboard_data(self, municipio_id: int, usuario_id: int) -> Dict:
        """Obtener datos para dashboard municipal"""
        try:
            # Obtener estado de consolidación
            consolidation_status = self.get_consolidation_status(municipio_id)
            
            # Obtener consolidaciones recientes
            recent_consolidations = self.get_municipal_consolidations(municipio_id)[:5]
            
            # Obtener reclamaciones activas
            active_claims = self.get_claims(municipio_id=municipio_id)
            active_claims = [c for c in active_claims if c['estado'] in ['generada', 'enviada', 'en_revision']]
            
            # Registrar acceso al dashboard
            self.log_action(municipio_id, usuario_id, 'acceder_dashboard', 
                          descripcion='Acceso a dashboard municipal')
            
            dashboard_data = {
                'consolidation_status': consolidation_status,
                'recent_consolidations': recent_consolidations,
                'active_claims': active_claims[:3],  # Solo las 3 más recientes
                'summary': {
                    'total_consolidaciones': consolidation_status['total_consolidaciones'],
                    'progreso_general': round(consolidation_status['progreso_general'], 1),
                    'discrepancias_pendientes': consolidation_status['discrepancias_pendientes'],
                    'reclamaciones_activas': len(active_claims)
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de dashboard: {e}")
            raise