"""
Modelos de datos para el Sistema de Recolección Inicial de Votaciones
Departamento de Caquetá - Colombia
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Enumeraciones
class LocationType(enum.Enum):
    DEPARTAMENTO = "departamento"
    MUNICIPIO = "municipio"
    PUESTO = "puesto"
    MESA = "mesa"

class EstadoRecoleccion(enum.Enum):
    PENDIENTE = "pendiente"
    IMAGEN_CAPTURADA = "imagen_capturada"
    PROCESANDO_OCR = "procesando_ocr"
    DATOS_RECONOCIDOS = "datos_reconocidos"
    VALIDANDO_MANUAL = "validando_manual"
    CAPTURADO = "capturado"
    EN_REVISION = "en_revision"
    VALIDADO = "validado"
    RECHAZADO = "rechazado"
    CONSOLIDADO = "consolidado"
    CERRADO = "cerrado"

class TipoEleccion(enum.Enum):
    CONCEJOS_JUVENTUDES = "concejos_juventudes"
    SENADO = "senado"
    CAMARA = "camara"
    CITREP = "citrep"
    PRESIDENCIALES = "presidenciales"
    GOBERNACION = "gobernacion"
    ASAMBLEA = "asamblea"
    ALCALDIA = "alcaldia"
    CONCEJO = "concejo"
    EDILES = "ediles"

class CargoElectoral(enum.Enum):
    PRESIDENTE = "presidente"
    VICEPRESIDENTE = "vicepresidente"
    SENADOR = "senador"
    REPRESENTANTE_CAMARA = "representante_camara"
    GOBERNADOR = "gobernador"
    DIPUTADO_ASAMBLEA = "diputado_asamblea"
    ALCALDE = "alcalde"
    CONCEJAL = "concejal"
    EDIL = "edil"
    CONSEJERO_JUVENTUD = "consejero_juventud"
    CITREP = "citrep"

class TipoCircunscripcion(enum.Enum):
    NACIONAL = "nacional"
    DEPARTAMENTAL = "departamental"
    MUNICIPAL = "municipal"
    DISTRITAL = "distrital"
    ESPECIAL = "especial"

class EstadoCandidato(enum.Enum):
    REGISTRADO = "registrado"
    HABILITADO = "habilitado"
    INHABILITADO = "inhabilitado"
    RETIRADO = "retirado"
    FALLECIDO = "fallecido"

# Modelo principal de ubicaciones geográficas basado en DIVIPOLA
class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    
    # Códigos DIVIPOLA
    codigo_departamento = Column(String(2), nullable=False, index=True)  # 18 para Caquetá
    codigo_municipio = Column(String(3), nullable=False, index=True)
    codigo_zona = Column(String(3), nullable=True, index=True)
    codigo_puesto = Column(String(2), nullable=True, index=True)
    
    # Nombres
    nombre_departamento = Column(String(100), nullable=False)
    nombre_municipio = Column(String(100), nullable=False)
    nombre_puesto = Column(String(200), nullable=True)
    
    # Tipo de ubicación
    tipo = Column(SQLEnum(LocationType), nullable=False, index=True)
    
    # Información adicional
    comuna = Column(String(100), nullable=True)
    direccion = Column(String(500), nullable=True)
    
    # Coordenadas GPS
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    
    # Datos electorales
    total_mujeres = Column(Integer, default=0)
    total_hombres = Column(Integer, default=0)
    total_votantes = Column(Integer, default=0)
    total_mesas = Column(Integer, default=0)
    
    # Metadatos
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    parent_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    parent = relationship("Location", remote_side=[id], backref="children")

# Modelo de mesas electorales específicas
class MesaElectoral(Base):
    __tablename__ = 'mesas_electorales'
    
    id = Column(Integer, primary_key=True)
    
    # Identificación de la mesa
    codigo_mesa = Column(String(20), unique=True, nullable=False, index=True)
    numero_mesa = Column(Integer, nullable=False)
    
    # Ubicación
    puesto_id = Column(Integer, ForeignKey('locations.id'), nullable=False, index=True)
    puesto = relationship("Location", backref="mesas")
    
    # Datos electorales
    total_votantes_habilitados = Column(Integer, nullable=False)
    total_mujeres = Column(Integer, default=0)
    total_hombres = Column(Integer, default=0)
    
    # Estado de recolección
    estado_recoleccion = Column(String(50), default='pendiente', index=True)
    
    # Testigo asignado
    testigo_asignado_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Timestamps del proceso
    fecha_inicio_captura = Column(DateTime, nullable=True)
    fecha_cierre_captura = Column(DateTime, nullable=True)
    
    # Metadatos de proceso
    intentos_captura = Column(Integer, default=0)
    tiempo_total_captura = Column(Integer, nullable=True)  # en segundos
    dispositivo_captura = Column(String(100), nullable=True)
    ip_captura = Column(String(45), nullable=True)
    
    # Metadatos
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelo de usuarios del sistema
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    
    # Información personal
    nombre_completo = Column(String(200), nullable=False, index=True)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=True, index=True)
    email = Column(String(100), nullable=True, index=True)
    
    # Credenciales
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Rol y permisos
    rol = Column(String(50), nullable=False, index=True)  # testigo, coordinador_puesto, coordinador_municipal, administrador
    
    # Ubicación asignada
    municipio_id = Column(Integer, ForeignKey('locations.id'), nullable=True, index=True)
    puesto_id = Column(Integer, ForeignKey('locations.id'), nullable=True, index=True)
    
    # Estado del usuario
    activo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    municipio = relationship("Location", foreign_keys=[municipio_id])
    puesto = relationship("Location", foreign_keys=[puesto_id])
    mesas_asignadas = relationship("MesaElectoral", backref="testigo")

# Modelo de tipos de elecciones
class ElectionType(Base):
    __tablename__ = 'election_types'
    
    id = Column(Integer, primary_key=True)
    
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    
    # Configuración del formulario E-14
    plantilla_e14 = Column(JSON, nullable=False)  # Configuración de campos del formulario
    
    # Configuración OCR específica
    ocr_template_config = Column(JSON, nullable=True)  # Configuración específica para OCR
    validation_rules = Column(JSON, nullable=True)  # Reglas de validación específicas
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelo de jornadas electorales
class ElectoralJourney(Base):
    __tablename__ = 'electoral_journeys'
    
    id = Column(Integer, primary_key=True)
    
    nombre = Column(String(200), nullable=False)
    fecha_jornada = Column(DateTime, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Estado de la jornada
    estado = Column(String(50), default='configuracion', index=True)  # configuracion, programada, activa, finalizada, cancelada
    
    # Configuración
    activo = Column(Boolean, default=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelo de procesos electorales específicos
class ElectoralProcess(Base):
    __tablename__ = 'electoral_processes'
    
    id = Column(Integer, primary_key=True)
    
    nombre = Column(String(200), nullable=False)
    jornada_electoral_id = Column(Integer, ForeignKey('electoral_journeys.id'), nullable=False, index=True)
    election_type_id = Column(Integer, ForeignKey('election_types.id'), nullable=False, index=True)
    
    # Fechas del proceso
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    
    # Estado del proceso
    estado = Column(String(50), default='configuracion', index=True)  # configuracion, activo, pausado, finalizado, cancelado
    
    # Configuración específica del proceso
    configuracion = Column(JSON, nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    jornada = relationship("ElectoralJourney", backref="procesos")
    tipo_eleccion = relationship("ElectionType", backref="procesos")

# Modelo de relación mesa-proceso electoral
class MesaElectoralProcess(Base):
    __tablename__ = 'mesa_electoral_processes'
    
    id = Column(Integer, primary_key=True)
    
    mesa_id = Column(Integer, ForeignKey('mesas_electorales.id'), nullable=False, index=True)
    proceso_electoral_id = Column(Integer, ForeignKey('electoral_processes.id'), nullable=False, index=True)
    
    # Estado del proceso en esta mesa
    estado_proceso = Column(String(50), default='asignado', index=True)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    mesa = relationship("MesaElectoral", backref="procesos_electorales")
    proceso = relationship("ElectoralProcess", backref="mesas_asignadas")
    
    # Constraint único: Una mesa puede tener múltiples procesos electorales simultáneos
    # pero solo uno por tipo de elección
    __table_args__ = (
        # UniqueConstraint('mesa_id', 'proceso_electoral_id'),
    )

# Modelo de partidos políticos
class PoliticalParty(Base):
    __tablename__ = 'political_parties'
    
    id = Column(Integer, primary_key=True)
    
    # Información del partido
    nombre_oficial = Column(String(200), nullable=False, index=True)
    siglas = Column(String(20), unique=True, nullable=False, index=True)
    color_representativo = Column(String(7), nullable=True)  # Código hexadecimal
    logo_url = Column(String(500), nullable=True)
    
    # Información adicional
    descripcion = Column(Text, nullable=True)
    fundacion_year = Column(Integer, nullable=True)
    ideologia = Column(String(100), nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    reconocido_oficialmente = Column(Boolean, default=True)
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelo de coaliciones
class Coalition(Base):
    __tablename__ = 'coalitions'
    
    id = Column(Integer, primary_key=True)
    
    # Información de la coalición
    nombre_coalicion = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    fecha_formacion = Column(DateTime, nullable=True)
    fecha_disolucion = Column(DateTime, nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modelo de relación coalición-partido
class CoalitionParty(Base):
    __tablename__ = 'coalition_parties'
    
    id = Column(Integer, primary_key=True)
    
    coalition_id = Column(Integer, ForeignKey('coalitions.id'), nullable=False, index=True)
    party_id = Column(Integer, ForeignKey('political_parties.id'), nullable=False, index=True)
    
    # Información de la relación
    fecha_adhesion = Column(DateTime, default=datetime.utcnow)
    fecha_retiro = Column(DateTime, nullable=True)
    es_partido_principal = Column(Boolean, default=False)
    porcentaje_participacion = Column(Float, nullable=True)
    
    # Relaciones
    coalicion = relationship("Coalition", backref="partidos")
    partido = relationship("PoliticalParty", backref="coaliciones")

# Modelo de candidatos
class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    
    # Información personal
    nombre_completo = Column(String(200), nullable=False, index=True)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    numero_tarjeton = Column(Integer, nullable=False, index=True)
    
    # Información electoral
    cargo_aspirado = Column(String(100), nullable=False, index=True)
    election_type_id = Column(Integer, ForeignKey('election_types.id'), nullable=False, index=True)
    circunscripcion = Column(String(100), nullable=False)
    
    # Afiliación política (solo una puede ser no nula)
    party_id = Column(Integer, ForeignKey('political_parties.id'), nullable=True, index=True)
    coalition_id = Column(Integer, ForeignKey('coalitions.id'), nullable=True, index=True)
    es_independiente = Column(Boolean, default=False)
    
    # Información adicional
    foto_url = Column(String(500), nullable=True)
    biografia = Column(Text, nullable=True)
    propuestas = Column(Text, nullable=True)
    experiencia = Column(Text, nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True)
    habilitado_oficialmente = Column(Boolean, default=True)
    
    # Metadatos
    creado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    tipo_eleccion = relationship("ElectionType", backref="candidatos")
    partido = relationship("PoliticalParty", backref="candidatos")
    coalicion = relationship("Coalition", backref="candidatos")

# Modelo de resultados por candidato
class CandidateResults(Base):
    __tablename__ = 'candidate_results'
    
    id = Column(Integer, primary_key=True)
    
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False, index=True)
    election_type_id = Column(Integer, ForeignKey('election_types.id'), nullable=False, index=True)
    
    # Resultados de votación
    total_votos = Column(Integer, default=0)
    porcentaje_votacion = Column(Float, default=0.0)
    posicion_ranking = Column(Integer, nullable=True)
    
    # Distribución geográfica
    votos_por_municipio = Column(JSON, nullable=True)
    votos_por_puesto = Column(JSON, nullable=True)
    mejor_municipio = Column(String(100), nullable=True)
    peor_municipio = Column(String(100), nullable=True)
    
    # Estadísticas
    promedio_votos_por_mesa = Column(Float, nullable=True)
    desviacion_estandar = Column(Float, nullable=True)
    coeficiente_variacion = Column(Float, nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    calculado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    total_mesas_incluidas = Column(Integer, default=0)
    total_votos_validos_contexto = Column(Integer, default=0)
    
    # Relaciones
    candidato = relationship("Candidate", backref="resultados")
    tipo_eleccion = relationship("ElectionType")

# Modelo de resultados por partido
class PartyResults(Base):
    __tablename__ = 'party_results'
    
    id = Column(Integer, primary_key=True)
    
    party_id = Column(Integer, ForeignKey('political_parties.id'), nullable=False, index=True)
    election_type_id = Column(Integer, ForeignKey('election_types.id'), nullable=False, index=True)
    
    # Resultados agregados
    total_votos_partido = Column(Integer, default=0)
    porcentaje_votacion_partido = Column(Float, default=0.0)
    posicion_ranking_partido = Column(Integer, nullable=True)
    
    # Candidatos del partido
    total_candidatos = Column(Integer, default=0)
    candidatos_resultados = Column(JSON, nullable=True)
    mejor_candidato_id = Column(Integer, ForeignKey('candidates.id'), nullable=True)
    peor_candidato_id = Column(Integer, ForeignKey('candidates.id'), nullable=True)
    
    # Distribución geográfica del partido
    votos_por_municipio = Column(JSON, nullable=True)
    mejor_municipio_partido = Column(String(100), nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    calculado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    partido = relationship("PoliticalParty", backref="resultados")
    tipo_eleccion = relationship("ElectionType")

# Modelo de resultados por coalición
class CoalitionResults(Base):
    __tablename__ = 'coalition_results'
    
    id = Column(Integer, primary_key=True)
    
    coalition_id = Column(Integer, ForeignKey('coalitions.id'), nullable=False, index=True)
    election_type_id = Column(Integer, ForeignKey('election_types.id'), nullable=False, index=True)
    
    # Resultados agregados
    total_votos_coalicion = Column(Integer, default=0)
    porcentaje_votacion_coalicion = Column(Float, default=0.0)
    posicion_ranking_coalicion = Column(Integer, nullable=True)
    
    # Partidos de la coalición
    partidos_resultados = Column(JSON, nullable=True)
    mejor_partido_id = Column(Integer, ForeignKey('political_parties.id'), nullable=True)
    
    # Candidatos de la coalición
    total_candidatos_coalicion = Column(Integer, default=0)
    mejor_candidato_coalicion_id = Column(Integer, ForeignKey('candidates.id'), nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    calculado_por = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    coalicion = relationship("Coalition", backref="resultados")
    tipo_eleccion = relationship("ElectionType")

if __name__ == "__main__":
    print("Modelos de datos para el Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("Modelos definidos:")
    print("- Location: Ubicaciones geográficas basadas en DIVIPOLA")
    print("- MesaElectoral: Mesas electorales específicas")
    print("- User: Usuarios del sistema (testigos, coordinadores, administradores)")
    print("- ElectionType: Tipos de elecciones")
    print("- ElectoralJourney: Jornadas electorales")
    print("- ElectoralProcess: Procesos electorales específicos")
    print("- MesaElectoralProcess: Relación mesa-proceso electoral")
    print("- PoliticalParty: Partidos políticos")
    print("- Coalition: Coaliciones entre partidos")
    print("- CoalitionParty: Relación coalición-partido")
    print("- Candidate: Candidatos electorales")
    print("- CandidateResults: Resultados por candidato")
    print("- PartyResults: Resultados por partido")
    print("- CoalitionResults: Resultados por coalición")