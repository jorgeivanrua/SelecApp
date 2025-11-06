"""
Core Authentication Manager
Maneja autenticación y autorización de usuarios
"""

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Gestor de autenticación y autorización"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def authenticate_user(self, username, password):
        """Autenticar usuario con username/password"""
        try:
            query = """
                SELECT id, username, nombre_completo, password_hash, rol, activo
                FROM users 
                WHERE username = :username AND activo = 1
            """
            
            result = self.db.execute_query(query, {'username': username})
            
            if not result:
                return None
            
            user_data = result[0]
            
            # Verificar password
            if not check_password_hash(user_data[3], password):
                return None
            
            # Actualizar último acceso
            self.update_last_access(user_data[0])
            
            return {
                'id': user_data[0],
                'username': user_data[1],
                'nombre_completo': user_data[2],
                'rol': user_data[4]
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            query = """
                SELECT id, username, nombre_completo, cedula, email, rol, activo
                FROM users 
                WHERE id = :user_id
            """
            
            result = self.db.execute_query(query, {'user_id': user_id})
            
            if not result:
                return None
            
            user_data = result[0]
            
            return {
                'id': user_data[0],
                'username': user_data[1],
                'nombre_completo': user_data[2],
                'cedula': user_data[3],
                'email': user_data[4],
                'rol': user_data[5],
                'activo': user_data[6]
            }
            
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    def create_user(self, user_data):
        """Crear nuevo usuario"""
        try:
            password_hash = generate_password_hash(user_data['password'])
            
            query = """
                INSERT INTO users (
                    nombre_completo, cedula, telefono, email, username, 
                    password_hash, rol, municipio_id, puesto_id, activo
                ) VALUES (
                    :nombre_completo, :cedula, :telefono, :email, :username,
                    :password_hash, :rol, :municipio_id, :puesto_id, :activo
                )
            """
            
            params = {
                'nombre_completo': user_data['nombre_completo'],
                'cedula': user_data['cedula'],
                'telefono': user_data.get('telefono'),
                'email': user_data.get('email'),
                'username': user_data['username'],
                'password_hash': password_hash,
                'rol': user_data['rol'],
                'municipio_id': user_data.get('municipio_id'),
                'puesto_id': user_data.get('puesto_id'),
                'activo': user_data.get('activo', True)
            }
            
            user_id = self.db.execute_insert(query, params)
            return user_id
            
        except Exception as e:
            logger.error(f"Create user error: {e}")
            raise
    
    def update_user(self, user_id, user_data):
        """Actualizar usuario existente"""
        try:
            # Construir query dinámicamente
            set_clauses = []
            params = {'user_id': user_id}
            
            for field in ['nombre_completo', 'cedula', 'telefono', 'email', 'rol', 'activo']:
                if field in user_data:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = user_data[field]
            
            if 'password' in user_data:
                set_clauses.append("password_hash = :password_hash")
                params['password_hash'] = generate_password_hash(user_data['password'])
            
            if not set_clauses:
                return 0
            
            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            return self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Update user error: {e}")
            raise
    
    def update_last_access(self, user_id):
        """Actualizar último acceso del usuario"""
        try:
            query = """
                UPDATE users 
                SET ultimo_acceso = datetime('now')
                WHERE id = :user_id
            """
            
            self.db.execute_update(query, {'user_id': user_id})
            
        except Exception as e:
            logger.error(f"Update last access error: {e}")
    
    def get_users_by_role(self, role):
        """Obtener usuarios por rol"""
        try:
            query = """
                SELECT id, username, nombre_completo, cedula, email, rol, activo
                FROM users 
                WHERE rol = :role
                ORDER BY nombre_completo
            """
            
            result = self.db.execute_query(query, {'role': role})
            
            return [
                {
                    'id': row[0],
                    'username': row[1],
                    'nombre_completo': row[2],
                    'cedula': row[3],
                    'email': row[4],
                    'rol': row[5],
                    'activo': row[6]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Get users by role error: {e}")
            return []
    
    def validate_user_access(self, user_id, required_role=None):
        """Validar acceso de usuario"""
        user = self.get_user_by_id(user_id)
        
        if not user or not user['activo']:
            return False
        
        if required_role and user['rol'] != required_role:
            return False
        
        return True