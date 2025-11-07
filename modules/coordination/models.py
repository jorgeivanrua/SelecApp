"""
Modelos de datos para el módulo de coordinación
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class CoordinationData:
    """Datos de coordinación general"""
    coordinator_id: int
    municipio_id: int
    puesto_id: Optional[int] = None
    total_mesas: int = 0
    mesas_cubiertas: int = 0
    porcentaje_cobertura: float = 0.0
    fecha_asignacion: Optional[datetime] = None

@dataclass
class WitnessData:
    """Datos de testigo electoral"""
    nombre_completo: str
    cedula: str
    telefono: str
    email: Optional[str] = None
    direccion: Optional[str] = None
    partido_id: Optional[int] = None
    tipo_testigo: str = 'principal'  # principal, suplente
    observaciones: Optional[str] = None
    activo: bool = True

@dataclass
class AssignmentData:
    """Datos de asignación de testigo a mesa"""
    testigo_id: int
    mesa_id: int
    proceso_electoral_id: int
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    observaciones: Optional[str] = None
    estado: str = 'asignado'  # asignado, confirmado, presente, ausente

@dataclass
class DashboardData:
    """Datos del dashboard de coordinación"""
    coordinator_info: Dict[str, Any]
    statistics: Dict[str, Any]
    coverage_summary: List[Dict[str, Any]]
    pending_tasks: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]

@dataclass
class CoverageReport:
    """Reporte de cobertura de mesas"""
    puesto_id: int
    puesto_nombre: str
    total_mesas: int
    mesas_cubiertas: int
    mesas_sin_cobertura: int
    porcentaje_cobertura: float
    testigos_asignados: int
    testigos_disponibles: int

@dataclass
class WitnessAssignment:
    """Asignación completa de testigo"""
    assignment_id: int
    testigo_info: WitnessData
    mesa_info: Dict[str, Any]
    assignment_info: AssignmentData
    status: str