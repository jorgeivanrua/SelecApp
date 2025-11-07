"""
Configuración de base de datos
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Configuración de base de datos"""
    
    def __init__(self):
        self.db_path = os.environ.get('DATABASE_URL', 'electoral_system.db')
        self.backup_path = os.environ.get('BACKUP_PATH', 'backups/')
        self.connection_timeout = 30
        self.enable_foreign_keys = True
    
    def get_connection_string(self) -> str:
        """Obtener cadena de conexión"""
        return self.db_path
    
    def get_backup_path(self) -> str:
        """Obtener ruta de backups"""
        return self.backup_path
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Obtener configuración como diccionario"""
        return {
            'db_path': self.db_path,
            'backup_path': self.backup_path,
            'connection_timeout': self.connection_timeout,
            'enable_foreign_keys': self.enable_foreign_keys
        }