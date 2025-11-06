"""
Core Permission Manager
Sistema de permisos granular basado en roles y recursos
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Permisos disponibles en el sistema"""
    # Permisos generales
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    
    # Permisos específicos de módulos
    ELECTORAL_MANAGE = "electoral.manage"
    ELECTORAL_VIEW = "electoral.view"
    ELECTORAL_RESULTS = "electoral.results"
    
    CANDIDATES_MANAGE = "candidates.manage"
    CANDIDATES_VIEW = "candidates.view"
    CANDIDATES_REGISTER = "candidates.register"
    
    USERS_MANAGE = "users.manage"
    USERS_VIEW = "users.view"
    USERS_CREATE = "users.create"
    
    REPORTS_VIEW = "reports.view"
    REPORTS_GENERATE = "reports.generate"
    REPORTS_EXPORT = "reports.export"
    
    DASHBOARD_VIEW = "dashboard.view"
    DASHBOARD_ADMIN = "dashboard.admin"

class Role(Enum):
    """Roles del sistema"""
    SUPER_ADMIN = "super_admin"
    ADMIN_DEPARTAMENTAL = "admin_departamental"
    ADMIN_MUNICIPAL = "admin_municipal"
    COORDINADOR_PUESTO = "coordinador_puesto"
    TESTIGO_MESA = "testigo_mesa"
    DIGITADOR = "digitador"
    OBSERVADOR = "observador"
    AUDITOR = "auditor"

class PermissionManager:
    """Gestor de permisos del sistema"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._role_permissions = self._initialize_role_permissions()
    
    def _initialize_role_permissions(self):
        """Inicializar matriz de permisos por rol"""
        return {
            Role.SUPER_ADMIN.value: [
                # Acceso total al sistema
                Permission.ADMIN.value,
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.DELETE.value,
                Permission.ELECTORAL_MANAGE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.ELECTORAL_RESULTS.value,
                Permission.CANDIDATES_MANAGE.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.CANDIDATES_REGISTER.value,
                Permission.USERS_MANAGE.value,
                Permission.USERS_VIEW.value,
                Permission.USERS_CREATE.value,
                Permission.REPORTS_VIEW.value,
                Permission.REPORTS_GENERATE.value,
                Permission.REPORTS_EXPORT.value,
                Permission.DASHBOARD_VIEW.value,
                Permission.DASHBOARD_ADMIN.value,
            ],
            
            Role.ADMIN_DEPARTAMENTAL.value: [
                # Administración a nivel departamental
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ELECTORAL_MANAGE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.ELECTORAL_RESULTS.value,
                Permission.CANDIDATES_MANAGE.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.CANDIDATES_REGISTER.value,
                Permission.USERS_VIEW.value,
                Permission.USERS_CREATE.value,
                Permission.REPORTS_VIEW.value,
                Permission.REPORTS_GENERATE.value,
                Permission.REPORTS_EXPORT.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.ADMIN_MUNICIPAL.value: [
                # Administración a nivel municipal
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.ELECTORAL_RESULTS.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.USERS_VIEW.value,
                Permission.REPORTS_VIEW.value,
                Permission.REPORTS_GENERATE.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.COORDINADOR_PUESTO.value: [
                # Coordinación de puesto electoral
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.USERS_VIEW.value,
                Permission.REPORTS_VIEW.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.TESTIGO_MESA.value: [
                # Testigo de mesa electoral
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.DIGITADOR.value: [
                # Digitación de resultados
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.OBSERVADOR.value: [
                # Solo lectura y observación
                Permission.READ.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.REPORTS_VIEW.value,
                Permission.DASHBOARD_VIEW.value,
            ],
            
            Role.AUDITOR.value: [
                # Auditoría y reportes
                Permission.READ.value,
                Permission.ELECTORAL_VIEW.value,
                Permission.ELECTORAL_RESULTS.value,
                Permission.CANDIDATES_VIEW.value,
                Permission.USERS_VIEW.value,
                Permission.REPORTS_VIEW.value,
                Permission.REPORTS_GENERATE.value,
                Permission.REPORTS_EXPORT.value,
                Permission.DASHBOARD_VIEW.value,
            ],
        }
    
    def get_user_permissions(self, user_id):
        """Obtener permisos de un usuario"""
        try:
            # Obtener rol del usuario
            query = "SELECT rol FROM users WHERE id = :user_id AND activo = 1"
            result = self.db.execute_query(query, {'user_id': user_id})
            
            if not result:
                return []
            
            user_role = result[0][0]
            
            # Obtener permisos del rol
            return self._role_permissions.get(user_role, [])
            
        except Exception as e:
            logger.error(f"Get user permissions error: {e}")
            return []
    
    def has_permission(self, user_id, permission):
        """Verificar si un usuario tiene un permiso específico"""
        user_permissions = self.get_user_permissions(user_id)
        
        # Super admin tiene todos los permisos
        if Permission.ADMIN.value in user_permissions:
            return True
        
        # Verificar permiso específico
        return permission in user_permissions
    
    def has_any_permission(self, user_id, permissions):
        """Verificar si un usuario tiene alguno de los permisos especificados"""
        user_permissions = self.get_user_permissions(user_id)
        
        # Super admin tiene todos los permisos
        if Permission.ADMIN.value in user_permissions:
            return True
        
        # Verificar si tiene algún permiso
        return any(perm in user_permissions for perm in permissions)
    
    def has_all_permissions(self, user_id, permissions):
        """Verificar si un usuario tiene todos los permisos especificados"""
        user_permissions = self.get_user_permissions(user_id)
        
        # Super admin tiene todos los permisos
        if Permission.ADMIN.value in user_permissions:
            return True
        
        # Verificar si tiene todos los permisos
        return all(perm in user_permissions for perm in permissions)
    
    def get_role_permissions(self, role):
        """Obtener permisos de un rol específico"""
        return self._role_permissions.get(role, [])
    
    def get_all_roles(self):
        """Obtener todos los roles disponibles"""
        return [
            {
                'value': role.value,
                'name': role.value.replace('_', ' ').title(),
                'permissions': self._role_permissions.get(role.value, [])
            }
            for role in Role
        ]
    
    def get_all_permissions(self):
        """Obtener todos los permisos disponibles"""
        return [
            {
                'value': perm.value,
                'name': perm.value.replace('_', ' ').replace('.', ' - ').title(),
                'module': perm.value.split('.')[0] if '.' in perm.value else 'general'
            }
            for perm in Permission
        ]
    
    def can_access_module(self, user_id, module_name):
        """Verificar si un usuario puede acceder a un módulo"""
        module_permissions = {
            'electoral': [Permission.ELECTORAL_VIEW.value, Permission.ELECTORAL_MANAGE.value],
            'candidates': [Permission.CANDIDATES_VIEW.value, Permission.CANDIDATES_MANAGE.value],
            'users': [Permission.USERS_VIEW.value, Permission.USERS_MANAGE.value],
            'reports': [Permission.REPORTS_VIEW.value, Permission.REPORTS_GENERATE.value],
            'dashboard': [Permission.DASHBOARD_VIEW.value, Permission.DASHBOARD_ADMIN.value]
        }
        
        required_permissions = module_permissions.get(module_name, [])
        if not required_permissions:
            return True  # Módulo sin restricciones específicas
        
        return self.has_any_permission(user_id, required_permissions)
    
    def get_user_accessible_modules(self, user_id):
        """Obtener módulos accesibles para un usuario"""
        modules = ['electoral', 'candidates', 'users', 'reports', 'dashboard']
        accessible_modules = []
        
        for module in modules:
            if self.can_access_module(user_id, module):
                accessible_modules.append(module)
        
        return accessible_modules