"""
Configuración de la aplicación Flask
"""

import os
from datetime import timedelta

class AppConfig:
    """Configuración de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///electoral_system.db')
    
    # Archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'electoral_system.log')
    
    @classmethod
    def get_config_dict(cls):
        """Obtener configuración como diccionario"""
        return {
            'SECRET_KEY': cls.SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'JWT_SECRET_KEY': cls.JWT_SECRET_KEY,
            'JWT_ACCESS_TOKEN_EXPIRES': cls.JWT_ACCESS_TOKEN_EXPIRES,
            'DATABASE_URL': cls.DATABASE_URL,
            'UPLOAD_FOLDER': cls.UPLOAD_FOLDER,
            'MAX_CONTENT_LENGTH': cls.MAX_CONTENT_LENGTH
        }