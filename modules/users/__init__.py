"""
Módulo de Gestión de Usuarios
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from .services import UserService, AuthService
from .models import UserData, AuthData, SessionData
from .routes import users_bp

__all__ = [
    'UserService',
    'AuthService',
    'UserData',
    'AuthData',
    'SessionData',
    'users_bp'
]

__version__ = '1.0.0'
__author__ = 'Sistema Electoral Caquetá'