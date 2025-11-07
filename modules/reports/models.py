"""
Modelos de datos para el módulo de reportes
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ReportFilter:
    """Filtros para generación de reportes"""
    process_id: Optional[int] = None
    election_type_id: Optional[int] = None
    party_id: Optional[int] = None
    candidate_id: Optional[int] = None
    municipality_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    top_n: int = 10

@dataclass
class ElectoralSummary:
    """Resumen electoral"""
    general_stats: Dict[str, Any]
    collection_progress: Dict[str, Any]
    top_candidates: List[Dict[str, Any]]
    participation_by_municipality: List[Dict[str, Any]]
    generated_at: str

@dataclass
class CandidateResult:
    """Resultado de candidato"""
    id: int
    nombre_completo: str
    cargo_aspirado: str
    numero_tarjeton: int
    partido_siglas: Optional[str]
    partido_nombre: Optional[str]
    tipo_eleccion: str
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int

@dataclass
class CandidateResultsReport:
    """Reporte de resultados de candidatos"""
    candidates: List[CandidateResult]
    statistics: Dict[str, Any]
    generated_at: str
    filters: Dict[str, Any]

@dataclass
class PartyPerformance:
    """Desempeño de partido"""
    id: int
    nombre_oficial: str
    siglas: str
    total_candidatos: int
    total_votos_partido: int
    promedio_porcentaje: float
    mejor_candidato_votos: int
    peor_candidato_votos: int

@dataclass
class PartyPerformanceReport:
    """Reporte de desempeño por partido"""
    parties: List[PartyPerformance]
    generated_at: str
    filters: Dict[str, Any]

@dataclass
class MunicipalityData:
    """Datos de municipio"""
    nombre_municipio: str
    total_mesas: int
    total_votantes: int
    mesas_completadas: int
    porcentaje_completado: float

@dataclass
class GeographicAnalysis:
    """Análisis geográfico"""
    municipalities: List[MunicipalityData]
    candidate_performance: Optional[Dict[str, Any]]
    generated_at: str
    filters: Dict[str, Any]

@dataclass
class ParticipationStats:
    """Estadísticas de participación"""
    general_stats: Dict[str, Any]
    hourly_participation: List[Dict[str, Any]]
    participation_by_election: List[Dict[str, Any]]
    generated_at: str

@dataclass
class SystemAuditReport:
    """Reporte de auditoría del sistema"""
    user_stats: Dict[str, Any]
    system_activity: Dict[str, Any]
    data_integrity: Dict[str, Any]
    audit_period: Dict[str, Any]
    generated_at: str

@dataclass
class ScheduledReport:
    """Reporte programado"""
    id: int
    name: str
    report_type: str
    schedule: str
    next_run: str
    active: bool
    user_id: int
    filters: Dict[str, Any]

@dataclass
class ReportTemplate:
    """Plantilla de reporte"""
    id: str
    name: str
    description: str
    parameters: List[str]
    category: str

@dataclass
class ExportRequest:
    """Solicitud de exportación"""
    report_type: str
    format: str  # 'excel', 'pdf', 'csv'
    filters: Dict[str, Any]
    user_id: int
    filename: Optional[str] = None