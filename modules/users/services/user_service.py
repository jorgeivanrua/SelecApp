"""
Servicio de Gestión de Usuarios
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import UserData, UserProfile, PasswordChangeData, UserActivity

class UserService:
    """Servicio para gestión de usuarios del sistema"""
    
    def __init__(self, db_path: str = 'electoral_system_prod.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN DE USUARIOS ====================
    
    def get_user_by_id(self, user_id: int) -> Optional[UserData]:
        """Obtener usuario por ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users WHERE id = ? AND activo = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return UserData(
                    user_id=result['id'],
                    nombre_completo=result['nombre_completo'],
                    cedula=result['cedula'],
                    telefono=result['telefono'],
                    email=result['email'],
                    username=result['username'],
                    rol=result['rol'],
                    municipio_id=result['municipio_id'],
                    puesto_id=result['puesto_id'],
                    activo=bool(result['activo']),
                    ultimo_login=result['ultimo_login'],
                    fecha_creacion=result['fecha_creacion']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario por ID: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserData]:
        """Obtener usuario por username"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users WHERE username = ? AND activo = 1
            """, (username,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return UserData(
                    user_id=result['id'],
                    nombre_completo=result['nombre_completo'],
                    cedula=result['cedula'],
                    telefono=result['telefono'],
                    email=result['email'],
                    username=result['username'],
                    rol=result['rol'],
                    municipio_id=result['municipio_id'],
                    puesto_id=result['puesto_id'],
                    activo=bool(result['activo']),
                    ultimo_login=result['ultimo_login'],
                    fecha_creacion=result['fecha_creacion']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario por username: {e}")
            return None
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Obtener perfil completo de usuario"""
        try:
            user_data = self.get_user_by_id(user_id)
            if not user_data:
                return None
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Información de ubicación
            location_info = {}
            if user_data.municipio_id:
                cursor.execute("""
                    SELECT nombre_municipio, codigo_municipio 
                    FROM locations WHERE id = ?
                """, (user_data.municipio_id,))
                municipio = cursor.fetchone()
                if municipio:
                    location_info['municipio'] = dict(municipio)
            
            if user_data.puesto_id:
                cursor.execute("""
                    SELECT nombre_puesto, direccion 
                    FROM locations WHERE id = ?
                """, (user_data.puesto_id,))
                puesto = cursor.fetchone()
                if puesto:
                    location_info['puesto'] = dict(puesto)
            
            # Permisos del rol
            role_permissions = self._get_role_permissions(user_data.rol)
            
            # Resumen de actividad
            activity_summary = self._get_user_activity_summary(user_id)
            
            # Preferencias del usuario (placeholder)
            preferences = {
                'theme': 'light',
                'language': 'es',
                'notifications': True
            }
            
            conn.close()
            
            return UserProfile(
                user_data=user_data,
                location_info=location_info,
                role_permissions=role_permissions,
                activity_summary=activity_summary,
                preferences=preferences
            )
            
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil de usuario: {e}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar perfil de usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Campos actualizables
            update_fields = []
            params = []
            
            if 'telefono' in profile_data:
                update_fields.append("telefono = ?")
                params.append(profile_data['telefono'])
            
            if 'email' in profile_data:
                update_fields.append("email = ?")
                params.append(profile_data['email'])
            
            if update_fields:
                update_fields.append("fecha_actualizacion = ?")
                params.append(datetime.now())
                params.append(user_id)
                
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
            
            conn.close()
            
            return {
                'success': True,
                'message': 'Perfil actualizado exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error actualizando perfil: {e}")
            return {
                'success': False,
                'error': f'Error actualizando perfil: {str(e)}'
            }
    
    def change_password(self, password_data: PasswordChangeData) -> Dict[str, Any]:
        """Cambiar contraseña de usuario"""
        try:
            # Validar contraseña actual
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (password_data.user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {
                    'success': False,
                    'error': 'Usuario no encontrado'
                }
            
            if not check_password_hash(result['password_hash'], password_data.current_password):
                conn.close()
                return {
                    'success': False,
                    'error': 'Contraseña actual incorrecta'
                }
            
            # Validar nueva contraseña
            if password_data.new_password != password_data.confirm_password:
                conn.close()
                return {
                    'success': False,
                    'error': 'Las contraseñas no coinciden'
                }
            
            if len(password_data.new_password) < 6:
                conn.close()
                return {
                    'success': False,
                    'error': 'La contraseña debe tener al menos 6 caracteres'
                }
            
            # Actualizar contraseña
            new_password_hash = generate_password_hash(password_data.new_password)
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, fecha_actualizacion = ?
                WHERE id = ?
            """, (new_password_hash, datetime.now(), password_data.user_id))
            
            conn.commit()
            conn.close()
            
            # Registrar actividad
            self.log_user_activity(password_data.user_id, 'password_change', 'Contraseña cambiada')
            
            return {
                'success': True,
                'message': 'Contraseña cambiada exitosamente'
            }
            
        except Exception as e:
            self.logger.error(f"Error cambiando contraseña: {e}")
            return {
                'success': False,
                'error': f'Error cambiando contraseña: {str(e)}'
            }
    
    def update_last_login(self, user_id: int) -> None:
        """Actualizar último login del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET ultimo_login = ?
                WHERE id = ?
            """, (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error actualizando último login: {e}")
    
    # ==================== ACTIVIDAD DE USUARIOS ====================
    
    def log_user_activity(self, user_id: int, action: str, description: str, 
                          ip_address: Optional[str] = None, 
                          user_agent: Optional[str] = None,
                          additional_data: Optional[Dict[str, Any]] = None) -> None:
        """Registrar actividad de usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear tabla de actividad si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    description TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    additional_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO user_activities 
                (user_id, action, description, ip_address, user_agent, additional_data, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, action, description, ip_address, user_agent,
                json.dumps(additional_data) if additional_data else None,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando actividad: {e}")
    
    def get_user_activities(self, user_id: int, limit: int = 50) -> List[UserActivity]:
        """Obtener actividades recientes del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM user_activities 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            activities = []
            for row in cursor.fetchall():
                activity = UserActivity(
                    user_id=row['user_id'],
                    action=row['action'],
                    description=row['description'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    timestamp=row['timestamp'],
                    additional_data=json.loads(row['additional_data']) if row['additional_data'] else None
                )
                activities.append(activity)
            
            conn.close()
            return activities
            
        except Exception as e:
            self.logger.error(f"Error obteniendo actividades: {e}")
            return []
    
    # ==================== UTILIDADES ====================
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Obtener permisos del rol"""
        role_permissions = {
            'super_admin': [
                'admin.users.create', 'admin.users.read', 'admin.users.update', 'admin.users.delete',
                'admin.system.config', 'admin.system.stats', 'admin.import.data',
                'candidates.create', 'candidates.read', 'candidates.update', 'candidates.delete',
                'coordination.read', 'coordination.assign', 'coordination.reports'
            ],
            'admin_departamental': [
                'admin.users.read', 'admin.users.update', 'admin.system.stats',
                'candidates.read', 'candidates.update', 'coordination.read', 'coordination.reports'
            ],
            'coordinador_municipal': [
                'coordination.read', 'coordination.assign', 'coordination.witnesses',
                'candidates.read', 'reports.coverage'
            ],
            'testigo_electoral': [
                'forms.e14.create', 'forms.e14.read', 'dashboard.witness'
            ]
        }
        
        return role_permissions.get(role, [])
    
    def _get_user_activity_summary(self, user_id: int) -> Dict[str, Any]:
        """Obtener resumen de actividad del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Actividad reciente
            cursor.execute("""
                SELECT COUNT(*) as total_activities,
                       MAX(timestamp) as last_activity
                FROM user_activities 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            # Actividades por tipo
            cursor.execute("""
                SELECT action, COUNT(*) as count
                FROM user_activities 
                WHERE user_id = ?
                GROUP BY action
                ORDER BY count DESC
                LIMIT 5
            """, (user_id,))
            
            activity_types = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_activities': result['total_activities'] if result else 0,
                'last_activity': result['last_activity'] if result else None,
                'activity_types': activity_types
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo resumen de actividad: {e}")
            return {}