"""
Servicios del módulo de candidatos
"""

from .candidate_management_service import CandidateManagementService
from .candidate_reporting_service import CandidateReportingService
from .e14_integration_service import E14CandidateIntegrationService

__all__ = [
    'CandidateManagementService',
    'CandidateReportingService',
    'E14CandidateIntegrationService'
]