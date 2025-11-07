"""
Modelos de datos para el módulo de dashboard
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class DashboardOverview:
    """Vista general del dashboard"""
    user_role: str
    last_updated: str
    quick_stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    system_status: Dict[str, str]
    user_permissions: List[str]
    admin_widgets: Optional[List[str]] = None
    operational_widgets: Optional[List[str]] = None

@dataclass
class ElectoralProgressWidget:
    """Widget de progreso electoral"""
    total_mesas: int
    progress_by_status: Dict[str, int]
    progress_percentages: Dict[str, float]
    municipality_progress: List[Dict[str, Any]]
    time_series: List[Dict[str, Any]]
    last_updated: str

@dataclass
class CandidateRankingWidget:
    """Widget de ranking de candidatos"""
    candidates: List[Dict[str, Any]]
    total_votos_top: int
    election_type_id: Optional[int]
    last_updated: str

@dataclass
class PartyDistributionWidget:
    """Widget de distribución por partido"""
    parties: List[Dict[str, Any]]
    total_votos_all: int
    total_parties: int
    last_updated: str

@dataclass
class GeographicMapWidget:
    """Widget de mapa geográfico"""
    metric: str
    data: List[Dict[str, Any]]
    map_center: Dict[str, float]
    zoom_level: int
    last_updated: str

@dataclass
class RealTimeStatsWidget:
    """Widget de estadísticas en tiempo real"""
    current_time: str
    active_users: int
    mesas_being_processed: int
    votes_per_minute: int
    system_load: Dict[str, float]
    recent_activities: List[Dict[str, Any]]

@dataclass
class UserActivityWidget:
    """Widget de actividad de usuarios"""
    time_range: str
    role_activity: List[Dict[str, Any]]
    top_users: List[Dict[str, Any]]
    hourly_activity: List[Dict[str, Any]]
    total_active_users: int
    last_updated: str

@dataclass
class AlertsWidget:
    """Widget de alertas del sistema"""
    alerts: List[Dict[str, Any]]
    total_alerts: int
    severity_filter: str
    last_updated: str

@dataclass
class PerformanceMetricsWidget:
    """Widget de métricas de rendimiento"""
    metrics: Dict[str, Dict[str, float]]
    trends: Dict[str, List[float]]
    status: str
    last_updated: str

@dataclass
class DashboardConfig:
    """Configuración del dashboard"""
    layout: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int
    theme: str

@dataclass
class WidgetPosition:
    """Posición de widget en el dashboard"""
    x: int
    y: int
    w: int
    h: int

@dataclass
class DashboardWidget:
    """Widget del dashboard"""
    type: str
    position: WidgetPosition
    config: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

@dataclass
class SystemAlert:
    """Alerta del sistema"""
    id: int
    type: str  # 'info', 'warning', 'error', 'success'
    severity: str  # 'low', 'medium', 'high'
    title: str
    message: str
    timestamp: str
    action_required: bool
    resolved: bool = False

@dataclass
class QuickStats:
    """Estadísticas rápidas"""
    total_candidates: int
    total_mesas: int
    mesas_completed: int
    active_users: int
    completion_percentage: float

@dataclass
class SystemStatus:
    """Estado del sistema"""
    database: str
    api: str
    storage: str
    network: str
    overall: str

@dataclass
class RecentActivity:
    """Actividad reciente"""
    type: str
    message: str
    timestamp: str
    user_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None