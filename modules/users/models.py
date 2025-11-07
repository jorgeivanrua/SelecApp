"""
Modelos de datos para el módulo de usuarios
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class UserData:
    """Datos de usuario del sistema"""
    user_id: Optional[int] = None
    nombre_completo: str = ""
    cedula: str = ""
    telefono: str = ""
    email: str = ""
    username: str = ""
    rol: str = ""
    municipio_id: Optional[int] = None
    puesto_id: Optional[int] = None
    activo: bool = True
    ultimo_login: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None

@dataclass
class AuthData:
    """Datos de autenticación"""
    username: str
    password: str
    remember_me: bool = False

@dataclass
class LoginData:
    """Datos de login"""
    username: str
    password: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    remember_me: bool = False

@dataclass
class AuthToken:
    """Token de autenticación"""
    token: str
    user_id: int
    expires_at: datetime
    token_type: str = "Bearer"

@dataclass
class SessionData:
    """Datos de sesión de usuario"""
    session_id: str
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_time: Optional[datetime] = None
    logout_time: Optional[datetime] = None
    active: bool = True

@dataclass
class UserSessionData:
    """Datos completos de sesión de usuario"""
    user_id: int
    username: str
    nombre_completo: str
    rol: str
    permissions: List[str]
    municipio_id: Optional[int] = None
    puesto_id: Optional[int] = None
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None

@dataclass
class UserProfile:
    """Perfil completo de usuario"""
    user_data: UserData
    location_info: Dict[str, Any]
    role_permissions: List[str]
    activity_summary: Dict[str, Any]
    preferences: Dict[str, Any]

@dataclass
class PasswordChangeData:
    """Datos para cambio de contraseña"""
    user_id: int
    current_password: str
    new_password: str
    confirm_password: str

@dataclass
class UserActivity:
    """Actividad de usuario"""
    user_id: int
    action: str
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None