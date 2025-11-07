"""
Módulo de Coordinación Municipal y Electoral
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from .services import CoordinationService, MunicipalCoordinationService
from .models import CoordinationData, WitnessData, AssignmentData
from .routes import coordination_bp

__all__ = [
    'CoordinationService',
    'MunicipalCoordinationService',
    'CoordinationData',
    'WitnessData', 
    'AssignmentData',
    'coordination_bp'
]

__version__ = '1.0.0'
__author__ = 'Sistema Electoral Caquetá'