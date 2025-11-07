"""
Modelos de datos para el módulo de administración
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class AdminData:
    """Datos de administración general"""
    admin_id: int
    permissions: List[str]
    access_level: str
    last_activity: Optional[datetime] = None

@dataclass
class ImportData:
    """Datos de importación de archivos"""
    file_name: str
    file_type: str
    import_type: str  # candidates, witnesses, locations, etc.
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    errors: List[Dict[str, Any]] = None
    status: str = 'pending'  # pending, processing, completed, failed

@dataclass
class PriorityData:
    """Datos de prioridades del sistema"""
    entity_type: str  # mesa, puesto, municipio, candidato
    entity_id: int
    priority_level: int  # 1-5, donde 1 es más alta prioridad
    priority_reason: str
    assigned_by: int
    assigned_date: Optional[datetime] = None
    active: bool = True

@dataclass
class SystemStats:
    """Estadísticas del sistema"""
    total_users: int
    active_users: int
    total_candidates: int
    total_parties: int
    total_witnesses: int
    total_tables: int
    coverage_percentage: float
    system_health: float

@dataclass
class UserManagementData:
    """Datos de gestión de usuarios"""
    user_id: Optional[int] = None
    nombre_completo: str = ""
    cedula: str = ""
    email: str = ""
    telefono: str = ""
    rol: str = ""
    municipio_id: Optional[int] = None
    puesto_id: Optional[int] = None
    activo: bool = True
    password: Optional[str] = None

@dataclass
class BulkActionData:
    """Datos para acciones masivas"""
    action_type: str  # activate, deactivate, delete, assign_role, etc.
    target_ids: List[int]
    parameters: Dict[str, Any] = None
    executed_by: int = None
    execution_date: Optional[datetime] = None