"""
Modelos de datos para el módulo de candidatos
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class PoliticalPartyData:
    """Clase para datos de partido político"""
    nombre_oficial: str
    siglas: str
    color_representativo: Optional[str] = None
    logo_url: Optional[str] = None
    descripcion: Optional[str] = None
    fundacion_year: Optional[int] = None
    ideologia: Optional[str] = None
    activo: bool = True
    reconocido_oficialmente: bool = True

@dataclass
class CoalitionData:
    """Clase para datos de coalición"""
    nombre_coalicion: str
    descripcion: Optional[str] = None
    fecha_formacion: Optional[datetime] = None
    partidos_ids: List[int] = None
    activo: bool = True

@dataclass
class CandidateData:
    """Clase para datos de candidato"""
    nombre_completo: str
    cedula: str
    numero_tarjeton: int
    cargo_aspirado: str
    election_type_id: int
    circunscripcion: str
    party_id: Optional[int] = None
    coalition_id: Optional[int] = None
    es_independiente: bool = False
    foto_url: Optional[str] = None
    biografia: Optional[str] = None
    propuestas: Optional[str] = None
    experiencia: Optional[str] = None
    activo: bool = True
    habilitado_oficialmente: bool = True

@dataclass
class CandidateResult:
    """Clase para resultado de candidato"""
    candidate_id: int
    nombre_completo: str
    cedula: str
    numero_tarjeton: int
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    party_name: Optional[str] = None
    coalition_name: Optional[str] = None

@dataclass
class PartyResult:
    """Clase para resultado de partido"""
    party_id: int
    party_name: str
    siglas: str
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    total_candidatos: int
    mejor_candidato: Optional[CandidateResult] = None

@dataclass
class CoalitionResult:
    """Clase para resultado de coalición"""
    coalition_id: int
    coalition_name: str
    total_votos: int
    porcentaje_votacion: float
    posicion_ranking: int
    total_candidatos: int
    partidos_participantes: List[str] = None

@dataclass
class E14CandidateField:
    """Campo de candidato en formulario E-14"""
    candidate_id: int
    nombre_completo: str
    numero_tarjeton: int
    party_siglas: Optional[str]
    coalition_name: Optional[str]
    field_name: str  # Nombre del campo en el formulario
    votos: int = 0

@dataclass
class E14FormStructure:
    """Estructura de formulario E-14 con candidatos"""
    election_type_id: int
    election_type_name: str
    form_template: dict
    candidate_fields: List[E14CandidateField]
    validation_rules: dict