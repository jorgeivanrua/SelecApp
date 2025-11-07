"""
Servicio de Autenticación
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import logging
import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from werkzeug.security import check_password_hash

from ..models import LoginData, AuthToken, SessionData

class AuthService:
    """Servicio para autenticación y gestión de sesiones"""
    
    def __init__(self, db_path: str = 'electoral_system_prod.db', secret_key: str = 'electoral_secret_key_production_2024'):
        self.db_path = db_path
        self.secret_key = secret_key
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def authenticate_user(self, login_data: LoginData) -> Dict[str, Any]:
        """Autenticar usuario con credenciales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar usuario por username o cédula
            cursor.execute("""
                SELECT id, nombre_completo, username, password_hash, rol, activo
                FROM users 
                WHERE (username = ? OR cedula = ?) AND activo = 1
            """, (login_data.username, login_data.username))
            
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {
                    'success': False,
                    'error': 'Usuario no encontrado'
                }
            
            # Verificar contraseña (usando SHA256)
            password_hash = hashlib.sha256(login_data.password.encode()).hexdigest()
            if user['password_hash'] != password_hash:
                conn.close()
                self._log_failed_login(login_data.username, login_data.ip_address)
                return {
                    'success': False,
                    'error': 'Contraseña incorrecta'
                }
            
            # Generar token JWT
            token_data = {
                'user_id': user['id'],
                'username': user['username'],
                'rol': user['rol'],
                'exp': datetime.utcnow() + timedelta(hours=8)
            }
            
            token = jwt.encode(token_data, self.secret_key, algorithm='HS256')
            
            # Actualizar último login
            cursor.execute("""
                UPDATE users SET ultimo_login = ? WHERE id = ?
            """, (datetime.now(), user['id']))
            
            # Crear sesión
            session_id = self._create_session(user['id'], token, login_data.ip_address, login_data.user_agent)
            
            conn.commit()
            conn.close()
            
            # Registrar login exitoso
            self._log_successful_login(user['id'], login_data.ip_address)
            
            return {
                'success': True,
                'token': token,
                'session_id': session_id,
                'user': {
                    'id': user['id'],
                    'nombre_completo': user['nombre_completo'],
                    'username': user['username'],
                    'rol': user['rol']
                },
                'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error autenticando usuario: {e}")
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verificar que el usuario sigue activo
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT activo FROM users WHERE id = ?
            """, (payload['user_id'],))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user or not user['activo']:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token inválido")
            return None
        except Exception as e:
            self.logger.error(f"Error validando token: {e}")
            return None    

    def logout_user(self, token: str, user_id: int) -> Dict[str, Any]:
        """Cerrar sesión de usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Buscar sesión por token hash y user_id
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            cursor.execute("""
                UPDATE user_sessions 
                SET active = 0, logout_time = ?
                WHERE token_hash = ? AND user_id = ? AND active = 1
            """, (datetime.now(), token_hash, user_id))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            # Registrar logout
            self._log_logout(user_id)
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'Sesión cerrada exitosamente'
                }
            else:
                # Aunque no se encuentre la sesión en BD, el logout es exitoso
                # porque el token ya no será válido en el cliente
                return {
                    'success': True,
                    'message': 'Sesión cerrada exitosamente'
                }
            
        except Exception as e:
            self.logger.error(f"Error cerrando sesión: {e}")
            # Incluso con error, consideramos el logout exitoso desde el punto de vista del cliente
            return {
                'success': True,
                'message': 'Sesión cerrada exitosamente'
            }
    
    def refresh_token(self, token: str) -> Dict[str, Any]:
        """Renovar token JWT"""
        try:
            # Validar token actual
            payload = self.validate_token(token)
            if not payload:
                return {
                    'success': False,
                    'error': 'Token inválido o expirado'
                }
            
            # Generar nuevo token
            new_token_data = {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'rol': payload['rol'],
                'exp': datetime.utcnow() + timedelta(hours=8)
            }
            
            new_token = jwt.encode(new_token_data, self.secret_key, algorithm='HS256')
            
            return {
                'success': True,
                'token': new_token,
                'expires_at': (datetime.utcnow() + timedelta(hours=8)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error renovando token: {e}")
            return {
                'success': False,
                'error': 'Error renovando token'
            }
    
    def get_user_sessions(self, user_id: int, active_only: bool = True) -> List[SessionData]:
        """Obtener sesiones del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM user_sessions 
                WHERE user_id = ?
            """
            params = [user_id]
            
            if active_only:
                query += " AND active = 1"
            
            query += " ORDER BY login_time DESC"
            
            cursor.execute(query, params)
            
            sessions = []
            for row in cursor.fetchall():
                session = SessionData(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    login_time=row['login_time'],
                    logout_time=row['logout_time'],
                    active=bool(row['active'])
                )
                sessions.append(session)
            
            conn.close()
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error obteniendo sesiones: {e}")
            return []
    
    def _create_session(self, user_id: int, token: str, ip_address: str, user_agent: str) -> str:
        """Crear nueva sesión"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear tabla de sesiones si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    token_hash VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    logout_time DATETIME,
                    active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Generar session_id único
            session_id = hashlib.sha256(f"{user_id}_{datetime.now().isoformat()}_{ip_address or 'unknown'}".encode()).hexdigest()
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO user_sessions 
                (session_id, user_id, token_hash, ip_address, user_agent, login_time, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, token_hash, ip_address, user_agent, datetime.now(), True))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creando sesión: {e}")
            return ""
    
    def _log_successful_login(self, user_id: int, ip_address: str):
        """Registrar login exitoso"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear tabla de logs si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username VARCHAR(100),
                    action VARCHAR(50),
                    ip_address VARCHAR(45),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    details TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO auth_logs (user_id, action, ip_address, timestamp, success)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, 'login', ip_address, datetime.now(), True))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando login exitoso: {e}")
    
    def _log_failed_login(self, username: str, ip_address: str):
        """Registrar intento de login fallido"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO auth_logs (username, action, ip_address, timestamp, success, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, 'login_failed', ip_address, datetime.now(), False, 'Credenciales incorrectas'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando login fallido: {e}")
    
    def _log_logout(self, user_id: int):
        """Registrar logout"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO auth_logs (user_id, action, timestamp, success)
                VALUES (?, ?, ?, ?)
            """, (user_id, 'logout', datetime.now(), True))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error registrando logout: {e}")
    
    def get_auth_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de autenticación"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Sesiones activas
            cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE active = 1")
            active_sessions = cursor.fetchone()[0]
            
            # Logins hoy
            cursor.execute("""
                SELECT COUNT(*) FROM auth_logs 
                WHERE action = 'login' AND success = 1 
                AND DATE(timestamp) = DATE('now')
            """)
            logins_today = cursor.fetchone()[0]
            
            # Intentos fallidos hoy
            cursor.execute("""
                SELECT COUNT(*) FROM auth_logs 
                WHERE action = 'login_failed' 
                AND DATE(timestamp) = DATE('now')
            """)
            failed_attempts_today = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'active_sessions': active_sessions,
                'logins_today': logins_today,
                'failed_attempts_today': failed_attempts_today
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas de auth: {e}")
            return {}