"""
Módulo de Dashboard
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from .routes import dashboard_bp
from .services import DashboardService, WidgetService

__all__ = [
    'dashboard_bp',
    'DashboardService',
    'WidgetService'
]