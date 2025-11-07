"""
Servicio del Panel de Administración
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from werkzeug.security import generate_password_hash

from ..models import AdminData, SystemStats, UserManagementData, BulkActionData

class AdminPanelService:
    """Servicio para el panel de administración del sistema"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== ESTADÍSTICAS DEL SISTEMA ====================
    
    def get_system_statistics(self) -> SystemStats:
        """Obtener estadísticas generales del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Usuarios
            cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN activo = 1 THEN 1 END) as active FROM users")
            user_stats = cursor.fetchone()
            
            # Candidatos
            cursor.execute("SELECT COUNT(*) FROM candidates WHERE activo = 1")
            total_candidates = cursor.fetchone()[0]
            
            # Partidos
            cursor.execute("SELECT COUNT(*) FROM political_parties WHERE activo = 1")
            total_parties = cursor.fetchone()[0]
            
            # Testigos (si existe la tabla)
            try:
                cursor.execute("SELECT COUNT(*) FROM testigos_electorales WHERE activo = 1")
                total_witnesses = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                total_witnesses = 0
            
            # Mesas
            cursor.execute("SELECT COUNT(*) FROM mesas_electorales WHERE activo = 1")
            total_tables = cursor.fetchone()[0]
            
            # Cobertura (si existe la tabla de asignaciones)
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT me.id) as total_mesas,
                        COUNT(DISTINCT ta.mesa_id) as mesas_cubiertas
                    FROM mesas_electorales me
                    LEFT JOIN testigo_asignaciones ta ON me.id = ta.mesa_id AND ta.estado = 'activo'
                    WHERE me.activo = 1
                """)
                coverage_stats = cursor.fetchone()
                total_mesas = coverage_stats['total_mesas'] or 0
                mesas_cubiertas = coverage_stats['mesas_cubiertas'] or 0
                coverage_percentage = (mesas_cubiertas / total_mesas * 100) if total_mesas > 0 else 0
            except sqlite3.OperationalError:
                coverage_percentage = 0
            
            conn.close()
            
            return SystemStats(
                total_users=user_stats['total'] or 0,
                active_users=user_stats['active'] or 0,
                total_candidates=total_candidates or 0,
                total_parties=total_parties or 0,
                total_witnesses=total_witnesses,
                total_tables=total_tables or 0,
                coverage_percentage=round(coverage_percentage, 1),
                system_health=95.0  # TODO: Implementar cálculo real de salud del sistema
            )
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas del sistema: {e}")
            return SystemStats(0, 0, 0, 0, 0, 0, 0.0, 0.0)
    
    # ==================== GESTIÓN DE USUARIOS ====================
    
    def get_all_users(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT u.*, 
                       l1.nombre_municipio as municipio_nombre,
                       l2.nombre_puesto as puesto_nombre
                FROM users u
                LEFT JOIN locations l1 ON u.municipio_id = l1.id
                LEFT JOIN locations l2 ON u.puesto_id = l2.id
            """
            
            if active_only:
                query += " WHERE u.activo = 1"
            
            query += " ORDER BY u.nombre_completo"
            
            cursor.execute(query)
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return users
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return []
    
    def create_user(self, user_data: UserManagementData, created_by: int) -> Dict[str, Any]:
        """Crear nuevo usuario del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generar username único
            username = self._generate_username(user_data.nombre_completo, user_data.cedula)
            
            # Hash de la contraseña
            password_hash = generate_password_hash(user_data.password or user_data.cedula)
            
            cursor.execute("""
                INSERT INTO users 
                (nombre_completo, cedula, telefono, email, username, password_hash, 
                 rol, municipio_id, puesto_id, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data.nombre_completo,
                user_data.cedula,
                user_data.telefono,
                user_data.email,
                username,
                password_hash,
                user_data.rol,
                user_data.municipio_id,
                user_data.puesto_id,
                user_data.activo,
                datetime.now()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Usuario creado: {user_data.nombre_completo} ({username})")
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'message': f'Usuario {user_data.nombre_completo} creado exitosamente'
            }
            
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Error de integridad creando usuario: {e}")
            return {
                'success': False,
                'error': 'Ya existe un usuario con esa cédula o username'
            }
        except Exception as e:
            self.logger.error(f"Error creando usuario: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def update_user(self, user_id: int, user_data: UserManagementData, updated_by: int) -> Dict[str, Any]:
        """Actualizar usuario existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Construir query dinámicamente
            update_fields = []
            params = []
            
            if user_data.nombre_completo:
                update_fields.append("nombre_completo = ?")
                params.append(user_data.nombre_completo)
            
            if user_data.telefono:
                update_fields.append("telefono = ?")
                params.append(user_data.telefono)
            
            if user_data.email:
                update_fields.append("email = ?")
                params.append(user_data.email)
            
            if user_data.rol:
                update_fields.append("rol = ?")
                params.append(user_data.rol)
            
            if user_data.municipio_id is not None:
                update_fields.append("municipio_id = ?")
                params.append(user_data.municipio_id)
            
            if user_data.puesto_id is not None:
                update_fields.append("puesto_id = ?")
                params.append(user_data.puesto_id)
            
            update_fields.append("activo = ?")
            params.append(user_data.activo)
            
            update_fields.append("fecha_actualizacion = ?")
            params.append(datetime.now())
            
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Usuario actualizado exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error actualizando usuario: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def delete_user(self, user_id: int, deleted_by: int) -> Dict[str, Any]:
        """Eliminar usuario (desactivar)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET activo = 0, fecha_actualizacion = ?
                WHERE id = ?
            """, (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Usuario desactivado exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error eliminando usuario: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def bulk_user_actions(self, action_data: BulkActionData) -> Dict[str, Any]:
        """Ejecutar acciones masivas en usuarios"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            successful_actions = 0
            errors = []
            
            for user_id in action_data.target_ids:
                try:
                    if action_data.action_type == 'activate':
                        cursor.execute("UPDATE users SET activo = 1 WHERE id = ?", (user_id,))
                    elif action_data.action_type == 'deactivate':
                        cursor.execute("UPDATE users SET activo = 0 WHERE id = ?", (user_id,))
                    elif action_data.action_type == 'assign_role':
                        new_role = action_data.parameters.get('role')
                        cursor.execute("UPDATE users SET rol = ? WHERE id = ?", (new_role, user_id))
                    
                    successful_actions += 1
                    
                except Exception as e:
                    errors.append({
                        'user_id': user_id,
                        'error': str(e)
                    })
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'successful_actions': successful_actions,
                'total_requested': len(action_data.target_ids),
                'errors': errors,
                'message': f'Se completaron {successful_actions} acciones'
            }
            
        except Exception as e:
            self.logger.error(f"Error en acciones masivas: {e}")
            return {
                'success': False,
                'error': f'Error en acciones masivas: {str(e)}'
            }
    
    # ==================== UTILIDADES ====================
    
    def _generate_username(self, nombre_completo: str, cedula: str) -> str:
        """Generar username único"""
        # Tomar primeras letras del nombre y últimos dígitos de cédula
        nombres = nombre_completo.split()
        if len(nombres) >= 2:
            base_username = f"{nombres[0][:2]}{nombres[1][:2]}{cedula[-4:]}".lower()
        else:
            base_username = f"{nombres[0][:4]}{cedula[-4:]}".lower()
        
        return base_username
    
    def get_system_health(self) -> Dict[str, Any]:
        """Obtener estado de salud del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar conectividad de BD
            cursor.execute("SELECT 1")
            db_health = True
            
            # Verificar tablas principales
            required_tables = ['users', 'candidates', 'political_parties', 'locations']
            missing_tables = []
            
            for table in required_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                except sqlite3.OperationalError:
                    missing_tables.append(table)
            
            conn.close()
            
            health_score = 100
            if missing_tables:
                health_score -= len(missing_tables) * 20
            
            return {
                'success': True,
                'health_score': max(health_score, 0),
                'database_connected': db_health,
                'missing_tables': missing_tables,
                'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical'
            }
            
        except Exception as e:
            self.logger.error(f"Error verificando salud del sistema: {e}")
            return {
                'success': False,
                'health_score': 0,
                'database_connected': False,
                'error': str(e),
                'status': 'critical'
            }