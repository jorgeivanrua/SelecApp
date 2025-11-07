"""
Configuración para Producción
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import os
import secrets
from datetime import timedelta

class ProductionConfig:
    """Configuración optimizada para producción"""
    
    # Configuración básica
    DEBUG = False
    TESTING = False
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    # Base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///electoral_system_prod.db'
    
    # JSON y codificación UTF-8
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True  # Habilitado para mejor legibilidad
    JSON_SORT_KEYS = False
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Servidor
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Límites de seguridad
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Headers de seguridad
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
    }
    
    @classmethod
    def get_config_dict(cls):
        """Obtener configuración como diccionario"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }