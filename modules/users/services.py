"""
Módulo Usuarios - Servicios
Lógica de negocio para gestión de usuarios
"""

import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

logger = logging.getLogger(__name__)

class UserService:
    """Servicio para gestión de usuarios"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_users(self, page=1, per_page=20, search='', role='', active_only=True):
        """Obtener usuarios con paginación y filtros"""
        try:
            base_query = """
                SELECT 
                    u.id,
                    u.nombre_completo,
                    u.cedula,
                    u.username,
                    u.email,
                    u.telefono,
                    u.rol,
                    u.activo,
                    u.ultimo_acceso,
                    u.fecha_creacion,
                    lm.nombre_municipio,
                    lp.nombre_puesto
                FROM users u
                LEFT JOIN locations lm ON u.municipio_id = lm.id
                LEFT JOIN locations lp ON u.puesto_id = lp.id
            """
            
            conditions = []
            params = {}
            
            if search:
                conditions.append("""
                    (u.nombre_completo LIKE :search 
                     OR u.cedula LIKE :search 
                     OR u.username LIKE :search 
                     OR u.email LIKE :search)
                """)
                params['search'] = f'%{search}%'
            
            if role:
                conditions.append("u.rol = :role")
                params['role'] = role
            
            if active_only:
                conditions.append("u.activo = 1")
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY u.nombre_completo"
            
            # Paginación
            offset = (page - 1) * per_page
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_table"
            total_result = self.db.execute_query(count_query, params)
            total = total_result[0][0] if total_result else 0
            
            paginated_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            data = self.db.execute_query(paginated_query, params)
            
            users = [
                {
                    'id': row[0],
                    'nombre_completo': row[1],
                    'cedula': row[2],
                    'username': row[3],
                    'email': row[4],
                    'telefono': row[5],
                    'rol': row[6],
                    'activo': row[7],
                    'ultimo_acceso': row[8],
                    'fecha_creacion': row[9],
                    'municipio_nombre': row[10],
                    'puesto_nombre': row[11]
                }
                for row in data
            ]
            
            return {
                'success': True,
                'data': users,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Get users error: {e}")
            raise
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            query = """
                SELECT 
                    u.id,
                    u.nombre_completo,
                    u.cedula,
                    u.username,
                    u.email,
                    u.telefono,
                    u.rol,
                    u.activo,
                    u.ultimo_acceso,
                    u.fecha_creacion,
                    u.municipio_id,
                    u.puesto_id,
                    lm.nombre_municipio,
                    lp.nombre_puesto
                FROM users u
                LEFT JOIN locations lm ON u.municipio_id = lm.id
                LEFT JOIN locations lp ON u.puesto_id = lp.id
                WHERE u.id = :user_id
            """
            
            result = self.db.execute_query(query, {'user_id': user_id})
            
            if not result:
                return None
            
            row = result[0]
            return {
                'id': row[0],
                'nombre_completo': row[1],
                'cedula': row[2],
                'username': row[3],
                'email': row[4],
                'telefono': row[5],
                'rol': row[6],
                'activo': row[7],
                'ultimo_acceso': row[8],
                'fecha_creacion': row[9],
                'municipio_id': row[10],
                'puesto_id': row[11],
                'municipio_nombre': row[12],
                'puesto_nombre': row[13]
            }
            
        except Exception as e:
            logger.error(f"Get user by ID error: {e}")
            raise
    
    def create_user(self, data, creator_id):
        """Crear nuevo usuario"""
        try:
            # Validar datos únicos
            if self._user_exists(data.get('username'), data.get('cedula'), data.get('email')):
                raise ValueError("User with this username, cedula, or email already exists")
            
            password_hash = generate_password_hash(data['password'])
            
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
                'nombre_completo': data['nombre_completo'],
                'cedula': data['cedula'],
                'telefono': data.get('telefono', ''),
                'email': data.get('email', ''),
                'username': data['username'],
                'password_hash': password_hash,
                'rol': data['rol'],
                'municipio_id': data.get('municipio_id'),
                'puesto_id': data.get('puesto_id'),
                'activo': data.get('activo', True)
            }
            
            user_id = self.db.execute_insert(query, params)
            return user_id
            
        except Exception as e:
            logger.error(f"Create user error: {e}")
            raise
    
    def update_user(self, user_id, data, updater_id):
        """Actualizar usuario"""
        try:
            # Construir query dinámicamente
            set_clauses = []
            params = {'user_id': user_id}
            
            allowed_fields = [
                'nombre_completo', 'cedula', 'telefono', 'email',
                'rol', 'municipio_id', 'puesto_id', 'activo'
            ]
            
            for field in allowed_fields:
                if field in data:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            # Manejar cambio de contraseña
            if 'password' in data and data['password']:
                set_clauses.append("password_hash = :password_hash")
                params['password_hash'] = generate_password_hash(data['password'])
            
            if not set_clauses:
                return False
            
            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Update user error: {e}")
            raise
    
    def activate_user(self, user_id, activator_id):
        """Activar usuario"""
        try:
            query = """
                UPDATE users 
                SET activo = 1, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            rows_affected = self.db.execute_update(query, {'user_id': user_id})
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Activate user error: {e}")
            raise
    
    def deactivate_user(self, user_id, deactivator_id):
        """Desactivar usuario"""
        try:
            query = """
                UPDATE users 
                SET activo = 0, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            rows_affected = self.db.execute_update(query, {'user_id': user_id})
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Deactivate user error: {e}")
            raise
    
    def get_user_statistics(self):
        """Obtener estadísticas de usuarios"""
        try:
            # Total de usuarios
            total_query = "SELECT COUNT(*) FROM users"
            total_result = self.db.execute_query(total_query)
            total_users = total_result[0][0] if total_result else 0
            
            # Usuarios activos
            active_query = "SELECT COUNT(*) FROM users WHERE activo = 1"
            active_result = self.db.execute_query(active_query)
            active_users = active_result[0][0] if active_result else 0
            
            # Usuarios por rol
            role_query = """
                SELECT rol, COUNT(*) as count
                FROM users
                WHERE activo = 1
                GROUP BY rol
                ORDER BY count DESC
            """
            role_result = self.db.execute_query(role_query)
            users_by_role = {row[0]: row[1] for row in role_result}
            
            # Usuarios por municipio
            municipality_query = """
                SELECT l.nombre_municipio, COUNT(*) as count
                FROM users u
                JOIN locations l ON u.municipio_id = l.id
                WHERE u.activo = 1
                GROUP BY l.nombre_municipio
                ORDER BY count DESC
                LIMIT 10
            """
            municipality_result = self.db.execute_query(municipality_query)
            users_by_municipality = {row[0]: row[1] for row in municipality_result}
            
            # Usuarios registrados por mes (últimos 6 meses)
            monthly_query = """
                SELECT 
                    strftime('%Y-%m', fecha_creacion) as month,
                    COUNT(*) as count
                FROM users
                WHERE fecha_creacion >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', fecha_creacion)
                ORDER BY month
            """
            monthly_result = self.db.execute_query(monthly_query)
            users_by_month = {row[0]: row[1] for row in monthly_result}
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'users_by_role': users_by_role,
                'users_by_municipality': users_by_municipality,
                'users_by_month': users_by_month
            }
            
        except Exception as e:
            logger.error(f"Get user statistics error: {e}")
            raise
    
    def get_user_profile(self, user_id):
        """Obtener perfil completo del usuario"""
        try:
            query = """
                SELECT 
                    u.id,
                    u.nombre_completo,
                    u.cedula,
                    u.username,
                    u.email,
                    u.telefono,
                    u.rol,
                    u.ultimo_acceso,
                    u.fecha_creacion,
                    lm.nombre_municipio,
                    lp.nombre_puesto
                FROM users u
                LEFT JOIN locations lm ON u.municipio_id = lm.id
                LEFT JOIN locations lp ON u.puesto_id = lp.id
                WHERE u.id = :user_id AND u.activo = 1
            """
            
            result = self.db.execute_query(query, {'user_id': user_id})
            
            if not result:
                return None
            
            row = result[0]
            profile = {
                'id': row[0],
                'nombre_completo': row[1],
                'cedula': row[2],
                'username': row[3],
                'email': row[4],
                'telefono': row[5],
                'rol': row[6],
                'ultimo_acceso': row[7],
                'fecha_creacion': row[8],
                'municipio_nombre': row[9],
                'puesto_nombre': row[10]
            }
            
            # Agregar estadísticas de actividad del usuario
            activity_stats = self._get_user_activity_stats(user_id)
            profile['activity_stats'] = activity_stats
            
            return profile
            
        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            raise
    
    def update_user_profile(self, user_id, data):
        """Actualizar perfil del usuario"""
        try:
            # Solo permitir actualizar ciertos campos del perfil
            allowed_fields = ['nombre_completo', 'email', 'telefono']
            
            set_clauses = []
            params = {'user_id': user_id}
            
            for field in allowed_fields:
                if field in data:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = data[field]
            
            if not set_clauses:
                return False
            
            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            rows_affected = self.db.execute_update(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Update user profile error: {e}")
            raise
    
    def change_password(self, user_id, current_password, new_password):
        """Cambiar contraseña del usuario"""
        try:
            # Verificar contraseña actual
            query = "SELECT password_hash FROM users WHERE id = :user_id"
            result = self.db.execute_query(query, {'user_id': user_id})
            
            if not result:
                return False
            
            current_hash = result[0][0]
            if not check_password_hash(current_hash, current_password):
                return False
            
            # Actualizar contraseña
            new_hash = generate_password_hash(new_password)
            update_query = """
                UPDATE users 
                SET password_hash = :password_hash, fecha_actualizacion = datetime('now')
                WHERE id = :user_id
            """
            
            rows_affected = self.db.execute_update(update_query, {
                'user_id': user_id,
                'password_hash': new_hash
            })
            
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Change password error: {e}")
            raise
    
    def _user_exists(self, username, cedula, email):
        """Verificar si usuario ya existe"""
        try:
            query = """
                SELECT id FROM users 
                WHERE username = :username 
                OR cedula = :cedula 
                OR (email = :email AND email != '')
            """
            
            result = self.db.execute_query(query, {
                'username': username,
                'cedula': cedula,
                'email': email or ''
            })
            
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Check user exists error: {e}")
            return False
    
    def _get_user_activity_stats(self, user_id):
        """Obtener estadísticas de actividad del usuario"""
        try:
            # Esta función podría expandirse para incluir más métricas
            # Por ahora, retornamos estadísticas básicas
            
            stats = {
                'total_logins': 0,  # Requeriría tabla de logs
                'last_activity': None,
                'assigned_mesas': 0
            }
            
            # Contar mesas asignadas si es testigo
            mesa_query = """
                SELECT COUNT(*) FROM mesas_electorales 
                WHERE testigo_asignado_id = :user_id
            """
            mesa_result = self.db.execute_query(mesa_query, {'user_id': user_id})
            stats['assigned_mesas'] = mesa_result[0][0] if mesa_result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Get user activity stats error: {e}")
            return {}