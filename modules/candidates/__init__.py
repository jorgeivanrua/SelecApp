"""
Módulo de Gestión de Candidatos, Partidos Políticos y Coaliciones
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from .services import CandidateManagementService, CandidateReportingService, E14CandidateIntegrationService
from .models import PoliticalPartyData, CoalitionData, CandidateData
from .routes import candidate_bp

__all__ = [
    'CandidateManagementService',
    'CandidateReportingService', 
    'E14CandidateIntegrationService',
    'PoliticalPartyData',
    'CoalitionData',
    'CandidateData',
    'candidate_bp'
]

__version__ = '1.0.0'
__author__ = 'Sistema Electoral Caquetá'