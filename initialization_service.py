"""
Servicio de Inicialización para el Sistema de Recolección Inicial de Votaciones
Departamento de Caquetá - Colombia

Este servicio carga y procesa los datos DIVIPOLA específicamente para Caquetá
y crea la estructura de mesas electorales.
"""

import csv
import logging
import random
import string
from typing import List, Dict, Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, Location, MesaElectoral, LocationType, User, ElectionType, 
    ElectoralJourney, ElectoralProcess, MesaElectoralProcess,
    PoliticalParty, Coalition, CoalitionParty, Candidate, CandidateResults,
    PartyResults, CoalitionResults, CargoElectoral, TipoCircunscripcion, EstadoCandidato
)
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InitializationService:
    """Servicio para inicializar la base de datos con datos de Caquetá"""
    
    def __init__(self, database_url: str = "sqlite:///caqueta_electoral.db"):
        """
        Inicializa el servicio con la conexión a la base de datos
        
        Args:
            database_url: URL de conexión a la base de datos
        """
        self.engine = create_engine(database_url, echo=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_database_schema(self) -> bool:
        """
        Crea el esquema de la base de datos
        
        Returns:
            bool: True si se creó exitosamente
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Esquema de base de datos creado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error creando esquema de base de datos: {e}")
            return False
    
    def load_divipola_data(self, csv_path: str) -> Dict[str, any]:
        """
        Carga datos DIVIPOLA desde CSV y crea estructura jerárquica para Caquetá
        
        Args:
            csv_path: Ruta al archivo CSV de DIVIPOLA
            
        Returns:
            dict: Resultado de la carga con estadísticas
        """
        result = {
            'success': False,
            'total_records': 0,
            'caqueta_records': 0,
            'locations_created': 0,
            'mesas_created': 0,
            'errors': []
        }
        
        try:
            with self.SessionLocal() as db:
                # Primero crear el departamento de Caquetá
                caqueta_dept = self._create_caqueta_department(db)
                
                # Leer y procesar el archivo CSV
                with open(csv_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    
                    municipios_created = {}
                    puestos_created = {}
                    
                    for row in csv_reader:
                        result['total_records'] += 1
                        
                        # Filtrar solo registros de Caquetá (código 44)
                        if (row.get('departamento', '').upper() == 'CAQUETA' and 
                            row.get('dd', '').strip() == '44'):
                            result['caqueta_records'] += 1
                            
                            try:
                                # Procesar municipio
                                municipio = self._process_municipio(db, row, caqueta_dept, municipios_created)
                                
                                # Procesar puesto
                                puesto = self._process_puesto(db, row, municipio, puestos_created)
                                
                                # Crear mesa electoral
                                mesa = self._create_mesa_electoral(db, row, puesto)
                                
                                if mesa:
                                    result['mesas_created'] += 1
                                    
                            except Exception as e:
                                error_msg = f"Error procesando fila {result['total_records']}: {e}"
                                logger.error(error_msg)
                                result['errors'].append(error_msg)
                
                # Actualizar contadores de ubicaciones
                result['locations_created'] = len(municipios_created) + len(puestos_created) + 1  # +1 por el departamento
                
                db.commit()
                result['success'] = True
                
                logger.info(f"Carga completada: {result['caqueta_records']} registros de Caquetá procesados")
                logger.info(f"Ubicaciones creadas: {result['locations_created']}")
                logger.info(f"Mesas creadas: {result['mesas_created']}")
                
        except Exception as e:
            logger.error(f"Error en carga de datos DIVIPOLA: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def _create_caqueta_department(self, db) -> Location:
        """Crea el registro del departamento de Caquetá"""
        
        # Verificar si ya existe
        existing = db.query(Location).filter(
            Location.codigo_departamento == '44',
            Location.tipo == LocationType.DEPARTAMENTO
        ).first()
        
        if existing:
            return existing
        
        caqueta = Location(
            codigo_departamento='44',
            codigo_municipio='000',
            nombre_departamento='CAQUETÁ',
            nombre_municipio='',
            tipo=LocationType.DEPARTAMENTO,
            activo=True
        )
        
        db.add(caqueta)
        db.flush()  # Para obtener el ID
        
        logger.info("Departamento de Caquetá creado")
        return caqueta
    
    def _process_municipio(self, db, row: Dict, departamento: Location, municipios_created: Dict) -> Location:
        """Procesa y crea un municipio si no existe"""
        
        municipio_nombre = row.get('municipio', '').strip().upper()
        codigo_municipio = row.get('mm', '').strip()
        
        # Usar nombre como clave única
        municipio_key = f"{municipio_nombre}"
        
        if municipio_key in municipios_created:
            return municipios_created[municipio_key]
        
        # Verificar si ya existe en la base de datos
        existing = db.query(Location).filter(
            Location.codigo_departamento == '44',
            Location.nombre_municipio == municipio_nombre,
            Location.tipo == LocationType.MUNICIPIO
        ).first()
        
        if existing:
            municipios_created[municipio_key] = existing
            return existing
        
        # Crear nuevo municipio
        municipio = Location(
            codigo_departamento='44',
            codigo_municipio=codigo_municipio,
            nombre_departamento='CAQUETÁ',
            nombre_municipio=municipio_nombre,
            tipo=LocationType.MUNICIPIO,
            parent_id=departamento.id,
            activo=True
        )
        
        db.add(municipio)
        db.flush()
        
        municipios_created[municipio_key] = municipio
        logger.info(f"Municipio creado: {municipio_nombre}")
        
        return municipio
    
    def _process_puesto(self, db, row: Dict, municipio: Location, puestos_created: Dict) -> Location:
        """Procesa y crea un puesto electoral si no existe"""
        
        puesto_nombre = row.get('puesto', '').strip()
        codigo_puesto = row.get('pp', '').strip()
        direccion = row.get('dirección', '').strip()
        comuna = row.get('comuna', '').strip()
        
        # Usar combinación de municipio y puesto como clave única
        puesto_key = f"{municipio.nombre_municipio}_{puesto_nombre}"
        
        if puesto_key in puestos_created:
            return puestos_created[puesto_key]
        
        # Verificar si ya existe en la base de datos
        existing = db.query(Location).filter(
            Location.codigo_departamento == '44',
            Location.nombre_municipio == municipio.nombre_municipio,
            Location.nombre_puesto == puesto_nombre,
            Location.tipo == LocationType.PUESTO
        ).first()
        
        if existing:
            puestos_created[puesto_key] = existing
            return existing
        
        # Obtener coordenadas GPS
        latitud = self._parse_float(row.get('LATITUD'))
        longitud = self._parse_float(row.get('LONGITUD'))
        
        # Crear nuevo puesto
        puesto = Location(
            codigo_departamento='44',
            codigo_municipio=municipio.codigo_municipio,
            codigo_puesto=codigo_puesto,
            nombre_departamento='CAQUETÁ',
            nombre_municipio=municipio.nombre_municipio,
            nombre_puesto=puesto_nombre,
            tipo=LocationType.PUESTO,
            comuna=comuna if comuna else None,
            direccion=direccion if direccion else None,
            latitud=latitud,
            longitud=longitud,
            parent_id=municipio.id,
            activo=True
        )
        
        db.add(puesto)
        db.flush()
        
        puestos_created[puesto_key] = puesto
        logger.info(f"Puesto creado: {puesto_nombre} en {municipio.nombre_municipio}")
        
        return puesto
    
    def _create_mesa_electoral(self, db, row: Dict, puesto: Location) -> Optional[MesaElectoral]:
        """Crea una mesa electoral basada en los datos del CSV"""
        
        try:
            # Obtener datos de la mesa
            total_mujeres = self._parse_int(row.get('mujeres', '0'))
            total_hombres = self._parse_int(row.get('hombres', '0'))
            total_votantes = self._parse_int(row.get('total', '0'))
            total_mesas = self._parse_int(row.get('mesas', '1'))
            
            # Crear mesas según el número especificado
            mesas_creadas = []
            
            for i in range(1, total_mesas + 1):
                # Generar código único de mesa
                codigo_mesa = f"44{puesto.codigo_municipio}{puesto.codigo_puesto}{i:02d}"
                
                # Verificar si ya existe
                existing = db.query(MesaElectoral).filter(
                    MesaElectoral.codigo_mesa == codigo_mesa
                ).first()
                
                if existing:
                    continue
                
                # Calcular votantes por mesa (distribución equitativa)
                votantes_por_mesa = total_votantes // total_mesas
                if i <= (total_votantes % total_mesas):
                    votantes_por_mesa += 1
                
                mesa = MesaElectoral(
                    codigo_mesa=codigo_mesa,
                    numero_mesa=i,
                    puesto_id=puesto.id,
                    total_votantes_habilitados=votantes_por_mesa,
                    total_mujeres=total_mujeres // total_mesas,
                    total_hombres=total_hombres // total_mesas,
                    estado_recoleccion='pendiente',
                    activo=True
                )
                
                db.add(mesa)
                mesas_creadas.append(mesa)
            
            if mesas_creadas:
                db.flush()
                logger.info(f"Creadas {len(mesas_creadas)} mesas para {puesto.nombre_puesto}")
                return mesas_creadas[0]  # Retornar la primera mesa creada
            
        except Exception as e:
            logger.error(f"Error creando mesa electoral: {e}")
            
        return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Convierte string a float de forma segura"""
        try:
            if value and value.strip():
                return float(value.strip())
        except (ValueError, AttributeError):
            pass
        return None
    
    def _parse_int(self, value: str) -> int:
        """Convierte string a int de forma segura"""
        try:
            if value and value.strip():
                return int(float(value.strip()))  # float primero para manejar decimales
        except (ValueError, AttributeError):
            pass
        return 0
    
    def validate_geographic_hierarchy(self) -> Dict[str, any]:
        """
        Valida integridad de la jerarquía geográfica
        
        Returns:
            dict: Resultado de la validación
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            with self.SessionLocal() as db:
                # Contar ubicaciones por tipo
                dept_count = db.query(Location).filter(Location.tipo == LocationType.DEPARTAMENTO).count()
                mun_count = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).count()
                puesto_count = db.query(Location).filter(Location.tipo == LocationType.PUESTO).count()
                mesa_count = db.query(MesaElectoral).count()
                
                result['statistics'] = {
                    'departamentos': dept_count,
                    'municipios': mun_count,
                    'puestos': puesto_count,
                    'mesas': mesa_count
                }
                
                # Validaciones
                if dept_count != 1:
                    result['errors'].append(f"Debe haber exactamente 1 departamento, encontrados: {dept_count}")
                    result['valid'] = False
                
                if mun_count == 0:
                    result['errors'].append("No se encontraron municipios")
                    result['valid'] = False
                
                if puesto_count == 0:
                    result['errors'].append("No se encontraron puestos electorales")
                    result['valid'] = False
                
                if mesa_count == 0:
                    result['errors'].append("No se encontraron mesas electorales")
                    result['valid'] = False
                
                # Validar que todos los puestos tengan coordenadas
                puestos_sin_coordenadas = db.query(Location).filter(
                    Location.tipo == LocationType.PUESTO,
                    (Location.latitud.is_(None) | Location.longitud.is_(None))
                ).count()
                
                if puestos_sin_coordenadas > 0:
                    result['warnings'].append(f"{puestos_sin_coordenadas} puestos sin coordenadas GPS")
                
                logger.info("Validación de jerarquía geográfica completada")
                
        except Exception as e:
            logger.error(f"Error en validación: {e}")
            result['errors'].append(str(e))
            result['valid'] = False
            
        return result
    
    def load_sample_election_data(self) -> Dict[str, any]:
        """
        Carga datos de ejemplo para tipos de elecciones, jornadas y procesos electorales
        
        Returns:
            dict: Resultado de la carga con estadísticas
        """
        result = {
            'success': False,
            'election_types_created': 0,
            'journeys_created': 0,
            'processes_created': 0,
            'users_created': 0,
            'errors': []
        }
        
        try:
            with self.SessionLocal() as db:
                # Cargar tipos de elecciones
                election_types_result = self._load_election_types(db)
                result['election_types_created'] = election_types_result['created']
                result['errors'].extend(election_types_result['errors'])
                
                # Cargar jornadas electorales
                journeys_result = self._load_electoral_journeys(db)
                result['journeys_created'] = journeys_result['created']
                result['errors'].extend(journeys_result['errors'])
                
                # Cargar procesos electorales
                processes_result = self._load_electoral_processes(db)
                result['processes_created'] = processes_result['created']
                result['errors'].extend(processes_result['errors'])
                
                # Cargar usuarios de ejemplo
                users_result = self._load_sample_users(db)
                result['users_created'] = users_result['created']
                result['errors'].extend(users_result['errors'])
                
                # Cargar partidos políticos de ejemplo
                parties_result = self._load_sample_parties(db)
                result['parties_created'] = parties_result['created']
                result['errors'].extend(parties_result['errors'])
                
                # Cargar coaliciones de ejemplo
                coalitions_result = self._load_sample_coalitions(db)
                result['coalitions_created'] = coalitions_result['created']
                result['errors'].extend(coalitions_result['errors'])
                
                # Cargar candidatos de ejemplo
                candidates_result = self._load_sample_candidates(db)
                result['candidates_created'] = candidates_result['created']
                result['errors'].extend(candidates_result['errors'])
                
                db.commit()
                result['success'] = True
                
                logger.info(f"Datos de ejemplo cargados exitosamente")
                logger.info(f"Tipos de elección: {result['election_types_created']}")
                logger.info(f"Jornadas: {result['journeys_created']}")
                logger.info(f"Procesos: {result['processes_created']}")
                logger.info(f"Usuarios: {result['users_created']}")
                logger.info(f"Partidos políticos: {result['parties_created']}")
                logger.info(f"Coaliciones: {result['coalitions_created']}")
                logger.info(f"Candidatos: {result['candidates_created']}")
                
        except Exception as e:
            logger.error(f"Error cargando datos de ejemplo: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def _load_election_types(self, db) -> Dict[str, any]:
        """Carga tipos de elecciones con configuraciones específicas"""
        result = {'created': 0, 'errors': []}
        
        election_types_data = [
            {
                'nombre': 'Concejos de Juventudes',
                'codigo': 'CJ',
                'descripcion': 'Elección de Concejos Municipales de Juventudes',
                'plantilla_e14': {
                    'candidatos': [
                        {'nombre': 'LISTA_1', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'LISTA_2', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'LISTA_3', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'VOTOS_BLANCOS', 'tipo': 'especial', 'max_votos': None},
                        {'nombre': 'VOTOS_NULOS', 'tipo': 'especial', 'max_votos': None}
                    ],
                    'campos_adicionales': [
                        {'nombre': 'TOTAL_VOTOS_DEPOSITADOS', 'tipo': 'numero', 'requerido': True},
                        {'nombre': 'TOTAL_VOTANTES_HABILITADOS', 'tipo': 'numero', 'requerido': True}
                    ]
                },
                'validation_rules': {
                    'suma_votos_debe_coincidir': True,
                    'max_votos_por_candidato': None,
                    'campos_obligatorios': ['TOTAL_VOTOS_DEPOSITADOS', 'TOTAL_VOTANTES_HABILITADOS']
                }
            },
            {
                'nombre': 'Senado de la República',
                'codigo': 'SEN',
                'descripcion': 'Elección de Senadores de la República',
                'plantilla_e14': {
                    'candidatos': [
                        {'nombre': 'PARTIDO_CONSERVADOR', 'tipo': 'partido', 'max_votos': None},
                        {'nombre': 'PARTIDO_LIBERAL', 'tipo': 'partido', 'max_votos': None},
                        {'nombre': 'CENTRO_DEMOCRATICO', 'tipo': 'partido', 'max_votos': None},
                        {'nombre': 'PACTO_HISTORICO', 'tipo': 'partido', 'max_votos': None},
                        {'nombre': 'OTROS_PARTIDOS', 'tipo': 'agrupacion', 'max_votos': None},
                        {'nombre': 'VOTOS_BLANCOS', 'tipo': 'especial', 'max_votos': None},
                        {'nombre': 'VOTOS_NULOS', 'tipo': 'especial', 'max_votos': None}
                    ],
                    'campos_adicionales': [
                        {'nombre': 'TOTAL_VOTOS_DEPOSITADOS', 'tipo': 'numero', 'requerido': True},
                        {'nombre': 'TOTAL_VOTANTES_HABILITADOS', 'tipo': 'numero', 'requerido': True}
                    ]
                },
                'validation_rules': {
                    'suma_votos_debe_coincidir': True,
                    'max_votos_por_candidato': None,
                    'campos_obligatorios': ['TOTAL_VOTOS_DEPOSITADOS', 'TOTAL_VOTANTES_HABILITADOS']
                }
            },
            {
                'nombre': 'Cámara de Representantes',
                'codigo': 'CAM',
                'descripcion': 'Elección de Representantes a la Cámara',
                'plantilla_e14': {
                    'candidatos': [
                        {'nombre': 'CANDIDATO_1', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'CANDIDATO_2', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'CANDIDATO_3', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'CANDIDATO_4', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'VOTOS_BLANCOS', 'tipo': 'especial', 'max_votos': None},
                        {'nombre': 'VOTOS_NULOS', 'tipo': 'especial', 'max_votos': None}
                    ],
                    'campos_adicionales': [
                        {'nombre': 'TOTAL_VOTOS_DEPOSITADOS', 'tipo': 'numero', 'requerido': True},
                        {'nombre': 'TOTAL_VOTANTES_HABILITADOS', 'tipo': 'numero', 'requerido': True}
                    ]
                },
                'validation_rules': {
                    'suma_votos_debe_coincidir': True,
                    'max_votos_por_candidato': None,
                    'campos_obligatorios': ['TOTAL_VOTOS_DEPOSITADOS', 'TOTAL_VOTANTES_HABILITADOS']
                }
            },
            {
                'nombre': 'Gobernación de Caquetá',
                'codigo': 'GOB',
                'descripcion': 'Elección de Gobernador del Departamento de Caquetá',
                'plantilla_e14': {
                    'candidatos': [
                        {'nombre': 'CANDIDATO_A', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'CANDIDATO_B', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'CANDIDATO_C', 'tipo': 'individual', 'max_votos': None},
                        {'nombre': 'VOTOS_BLANCOS', 'tipo': 'especial', 'max_votos': None},
                        {'nombre': 'VOTOS_NULOS', 'tipo': 'especial', 'max_votos': None}
                    ],
                    'campos_adicionales': [
                        {'nombre': 'TOTAL_VOTOS_DEPOSITADOS', 'tipo': 'numero', 'requerido': True},
                        {'nombre': 'TOTAL_VOTANTES_HABILITADOS', 'tipo': 'numero', 'requerido': True}
                    ]
                },
                'validation_rules': {
                    'suma_votos_debe_coincidir': True,
                    'max_votos_por_candidato': None,
                    'campos_obligatorios': ['TOTAL_VOTOS_DEPOSITADOS', 'TOTAL_VOTANTES_HABILITADOS']
                }
            },
            {
                'nombre': 'Asamblea Departamental',
                'codigo': 'ASA',
                'descripcion': 'Elección de Diputados a la Asamblea Departamental de Caquetá',
                'plantilla_e14': {
                    'candidatos': [
                        {'nombre': 'LISTA_1', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'LISTA_2', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'LISTA_3', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'LISTA_4', 'tipo': 'lista', 'max_votos': None},
                        {'nombre': 'VOTOS_BLANCOS', 'tipo': 'especial', 'max_votos': None},
                        {'nombre': 'VOTOS_NULOS', 'tipo': 'especial', 'max_votos': None}
                    ],
                    'campos_adicionales': [
                        {'nombre': 'TOTAL_VOTOS_DEPOSITADOS', 'tipo': 'numero', 'requerido': True},
                        {'nombre': 'TOTAL_VOTANTES_HABILITADOS', 'tipo': 'numero', 'requerido': True}
                    ]
                },
                'validation_rules': {
                    'suma_votos_debe_coincidir': True,
                    'max_votos_por_candidato': None,
                    'campos_obligatorios': ['TOTAL_VOTOS_DEPOSITADOS', 'TOTAL_VOTANTES_HABILITADOS']
                }
            }
        ]
        
        for election_data in election_types_data:
            try:
                # Verificar si ya existe
                existing = db.query(ElectionType).filter(
                    ElectionType.codigo == election_data['codigo']
                ).first()
                
                if existing:
                    continue
                
                election_type = ElectionType(
                    nombre=election_data['nombre'],
                    codigo=election_data['codigo'],
                    descripcion=election_data['descripcion'],
                    plantilla_e14=election_data['plantilla_e14'],
                    validation_rules=election_data['validation_rules'],
                    activo=True
                )
                
                db.add(election_type)
                result['created'] += 1
                logger.info(f"Tipo de elección creado: {election_data['nombre']}")
                
            except Exception as e:
                error_msg = f"Error creando tipo de elección {election_data['nombre']}: {e}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        db.flush()
        return result
    
    def _load_electoral_journeys(self, db) -> Dict[str, any]:
        """Carga jornadas electorales de ejemplo"""
        result = {'created': 0, 'errors': []}
        
        # Fechas de ejemplo (próximas elecciones)
        base_date = datetime.now() + timedelta(days=30)
        
        journeys_data = [
            {
                'nombre': 'Elecciones Territoriales 2027',
                'fecha_jornada': base_date + timedelta(days=60),
                'descripcion': 'Elecciones de autoridades territoriales: Gobernadores, Alcaldes, Diputados, Concejales y Ediles',
                'estado': 'programada'
            },
            {
                'nombre': 'Concejos de Juventudes 2024',
                'fecha_jornada': base_date,
                'descripcion': 'Elección de Concejos Municipales de Juventudes en todo el departamento de Caquetá',
                'estado': 'activa'
            },
            {
                'nombre': 'Elecciones Congreso 2026',
                'fecha_jornada': base_date + timedelta(days=180),
                'descripcion': 'Elecciones de Senado y Cámara de Representantes',
                'estado': 'configuracion'
            }
        ]
        
        for journey_data in journeys_data:
            try:
                # Verificar si ya existe
                existing = db.query(ElectoralJourney).filter(
                    ElectoralJourney.nombre == journey_data['nombre']
                ).first()
                
                if existing:
                    continue
                
                journey = ElectoralJourney(
                    nombre=journey_data['nombre'],
                    fecha_jornada=journey_data['fecha_jornada'],
                    descripcion=journey_data['descripcion'],
                    estado=journey_data['estado'],
                    activo=True
                )
                
                db.add(journey)
                result['created'] += 1
                logger.info(f"Jornada electoral creada: {journey_data['nombre']}")
                
            except Exception as e:
                error_msg = f"Error creando jornada electoral {journey_data['nombre']}: {e}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        db.flush()
        return result
    
    def _load_electoral_processes(self, db) -> Dict[str, any]:
        """Carga procesos electorales específicos"""
        result = {'created': 0, 'errors': []}
        
        try:
            # Obtener jornadas y tipos de elección creados
            journeys = db.query(ElectoralJourney).all()
            election_types = db.query(ElectionType).all()
            
            if not journeys or not election_types:
                result['errors'].append("No hay jornadas o tipos de elección disponibles")
                return result
            
            # Crear procesos de ejemplo
            processes_data = [
                {
                    'nombre': 'Concejos de Juventudes - Caquetá 2024',
                    'jornada_nombre': 'Concejos de Juventudes 2024',
                    'election_type_codigo': 'CJ',
                    'fecha_inicio': datetime.now(),
                    'fecha_fin': datetime.now() + timedelta(days=45),
                    'estado': 'activo',
                    'configuracion': {
                        'permite_captura_multiple': False,
                        'requiere_validacion_manual': True,
                        'tiempo_limite_captura': 3600,  # 1 hora en segundos
                        'notificaciones_activas': True
                    }
                },
                {
                    'nombre': 'Gobernación Caquetá - Territoriales 2027',
                    'jornada_nombre': 'Elecciones Territoriales 2027',
                    'election_type_codigo': 'GOB',
                    'fecha_inicio': datetime.now() + timedelta(days=30),
                    'fecha_fin': datetime.now() + timedelta(days=90),
                    'estado': 'configuracion',
                    'configuracion': {
                        'permite_captura_multiple': True,
                        'requiere_validacion_manual': True,
                        'tiempo_limite_captura': 7200,  # 2 horas en segundos
                        'notificaciones_activas': True
                    }
                },
                {
                    'nombre': 'Asamblea Departamental - Territoriales 2027',
                    'jornada_nombre': 'Elecciones Territoriales 2027',
                    'election_type_codigo': 'ASA',
                    'fecha_inicio': datetime.now() + timedelta(days=30),
                    'fecha_fin': datetime.now() + timedelta(days=90),
                    'estado': 'configuracion',
                    'configuracion': {
                        'permite_captura_multiple': True,
                        'requiere_validacion_manual': True,
                        'tiempo_limite_captura': 7200,
                        'notificaciones_activas': True
                    }
                }
            ]
            
            for process_data in processes_data:
                try:
                    # Buscar jornada y tipo de elección
                    journey = next((j for j in journeys if j.nombre == process_data['jornada_nombre']), None)
                    election_type = next((et for et in election_types if et.codigo == process_data['election_type_codigo']), None)
                    
                    if not journey or not election_type:
                        result['errors'].append(f"No se encontró jornada o tipo de elección para {process_data['nombre']}")
                        continue
                    
                    # Verificar si ya existe
                    existing = db.query(ElectoralProcess).filter(
                        ElectoralProcess.nombre == process_data['nombre']
                    ).first()
                    
                    if existing:
                        continue
                    
                    process = ElectoralProcess(
                        nombre=process_data['nombre'],
                        jornada_electoral_id=journey.id,
                        election_type_id=election_type.id,
                        fecha_inicio=process_data['fecha_inicio'],
                        fecha_fin=process_data['fecha_fin'],
                        estado=process_data['estado'],
                        configuracion=process_data['configuracion'],
                        activo=True
                    )
                    
                    db.add(process)
                    result['created'] += 1
                    logger.info(f"Proceso electoral creado: {process_data['nombre']}")
                    
                except Exception as e:
                    error_msg = f"Error creando proceso electoral {process_data['nombre']}: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            db.flush()
            
        except Exception as e:
            error_msg = f"Error general en carga de procesos electorales: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _load_sample_users(self, db) -> Dict[str, any]:
        """Carga usuarios de ejemplo del sistema"""
        result = {'created': 0, 'errors': []}
        
        # Obtener algunos municipios para asignar usuarios
        municipios = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).limit(3).all()
        
        users_data = [
            {
                'nombre_completo': 'Administrador del Sistema',
                'cedula': '12345678',
                'telefono': '3001234567',
                'email': 'admin@caqueta.gov.co',
                'username': 'admin',
                'password_hash': 'hashed_password_admin',  # En producción usar hash real
                'rol': 'administrador',
                'municipio_id': None,
                'puesto_id': None
            },
            {
                'nombre_completo': 'Coordinador Municipal Florencia',
                'cedula': '87654321',
                'telefono': '3007654321',
                'email': 'coord.florencia@caqueta.gov.co',
                'username': 'coord_florencia',
                'password_hash': 'hashed_password_coord1',
                'rol': 'coordinador_municipal',
                'municipio_id': municipios[0].id if municipios else None,
                'puesto_id': None
            },
            {
                'nombre_completo': 'Testigo Electoral 001',
                'cedula': '11223344',
                'telefono': '3009876543',
                'email': 'testigo001@caqueta.gov.co',
                'username': 'testigo001',
                'password_hash': 'hashed_password_testigo1',
                'rol': 'testigo',
                'municipio_id': municipios[0].id if municipios else None,
                'puesto_id': None
            },
            {
                'nombre_completo': 'Testigo Electoral 002',
                'cedula': '44332211',
                'telefono': '3001122334',
                'email': 'testigo002@caqueta.gov.co',
                'username': 'testigo002',
                'password_hash': 'hashed_password_testigo2',
                'rol': 'testigo',
                'municipio_id': municipios[1].id if len(municipios) > 1 else (municipios[0].id if municipios else None),
                'puesto_id': None
            }
        ]
        
        for user_data in users_data:
            try:
                # Verificar si ya existe
                existing = db.query(User).filter(
                    User.cedula == user_data['cedula']
                ).first()
                
                if existing:
                    continue
                
                user = User(
                    nombre_completo=user_data['nombre_completo'],
                    cedula=user_data['cedula'],
                    telefono=user_data['telefono'],
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    rol=user_data['rol'],
                    municipio_id=user_data['municipio_id'],
                    puesto_id=user_data['puesto_id'],
                    activo=True
                )
                
                db.add(user)
                result['created'] += 1
                logger.info(f"Usuario creado: {user_data['nombre_completo']} ({user_data['rol']})")
                
            except Exception as e:
                error_msg = f"Error creando usuario {user_data['nombre_completo']}: {e}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        db.flush()
        return result

    def generate_users_automatically(self) -> Dict[str, any]:
        """
        Genera usuarios automáticamente para toda la estructura organizacional
        
        Returns:
            dict: Resultado de la generación con estadísticas
        """
        result = {
            'success': False,
            'coordinadores_departamento': 0,
            'coordinadores_municipales': 0,
            'coordinadores_puesto': 0,
            'testigos_mesa': 0,
            'total_users_created': 0,
            'errors': []
        }
        
        try:
            with self.SessionLocal() as db:
                # Generar coordinador departamental
                dept_result = self._generate_departmental_coordinators(db)
                result['coordinadores_departamento'] = dept_result['created']
                result['errors'].extend(dept_result['errors'])
                
                # Generar coordinadores municipales
                mun_result = self._generate_municipal_coordinators(db)
                result['coordinadores_municipales'] = mun_result['created']
                result['errors'].extend(mun_result['errors'])
                
                # Generar coordinadores de puesto
                puesto_result = self._generate_puesto_coordinators(db)
                result['coordinadores_puesto'] = puesto_result['created']
                result['errors'].extend(puesto_result['errors'])
                
                # Generar testigos para mesas
                testigo_result = self._generate_mesa_testigos(db)
                result['testigos_mesa'] = testigo_result['created']
                result['errors'].extend(testigo_result['errors'])
                
                # Asignar testigos a mesas
                assignment_result = self._assign_testigos_to_mesas(db)
                result['errors'].extend(assignment_result['errors'])
                
                result['total_users_created'] = (
                    result['coordinadores_departamento'] + 
                    result['coordinadores_municipales'] + 
                    result['coordinadores_puesto'] + 
                    result['testigos_mesa']
                )
                
                db.commit()
                result['success'] = True
                
                logger.info(f"Generación automática de usuarios completada")
                logger.info(f"Coordinadores departamentales: {result['coordinadores_departamento']}")
                logger.info(f"Coordinadores municipales: {result['coordinadores_municipales']}")
                logger.info(f"Coordinadores de puesto: {result['coordinadores_puesto']}")
                logger.info(f"Testigos de mesa: {result['testigos_mesa']}")
                logger.info(f"Total usuarios creados: {result['total_users_created']}")
                
        except Exception as e:
            logger.error(f"Error en generación automática de usuarios: {e}")
            result['errors'].append(str(e))
            
        return result
    
    def _generate_departmental_coordinators(self, db) -> Dict[str, any]:
        """Genera coordinadores departamentales"""
        result = {'created': 0, 'errors': []}
        
        try:
            departamento = db.query(Location).filter(Location.tipo == LocationType.DEPARTAMENTO).first()
            
            if not departamento:
                result['errors'].append("No se encontró el departamento")
                return result
            
            coordinators_data = [
                {
                    'nombre_completo': 'Coordinador General Departamental',
                    'cedula': self._generate_cedula(),
                    'telefono': self._generate_phone(),
                    'email': 'coord.general@caqueta.gov.co',
                    'username': 'coord_general',
                    'rol': 'coordinador_departamental'
                },
                {
                    'nombre_completo': 'Coordinador Técnico Departamental',
                    'cedula': self._generate_cedula(),
                    'telefono': self._generate_phone(),
                    'email': 'coord.tecnico@caqueta.gov.co',
                    'username': 'coord_tecnico',
                    'rol': 'coordinador_departamental'
                }
            ]
            
            for coord_data in coordinators_data:
                # Verificar si ya existe
                existing = db.query(User).filter(
                    User.username == coord_data['username']
                ).first()
                
                if existing:
                    continue
                
                user = User(
                    nombre_completo=coord_data['nombre_completo'],
                    cedula=coord_data['cedula'],
                    telefono=coord_data['telefono'],
                    email=coord_data['email'],
                    username=coord_data['username'],
                    password_hash=self._generate_password_hash(),
                    rol=coord_data['rol'],
                    municipio_id=None,
                    puesto_id=None,
                    activo=True
                )
                
                db.add(user)
                result['created'] += 1
                logger.info(f"Coordinador departamental creado: {coord_data['nombre_completo']}")
                
        except Exception as e:
            error_msg = f"Error generando coordinadores departamentales: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _generate_municipal_coordinators(self, db) -> Dict[str, any]:
        """Genera coordinadores municipales para todos los municipios"""
        result = {'created': 0, 'errors': []}
        
        try:
            municipios = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).all()
            
            for municipio in municipios:
                # Verificar si ya existe un coordinador para este municipio
                existing = db.query(User).filter(
                    User.rol == 'coordinador_municipal',
                    User.municipio_id == municipio.id
                ).first()
                
                if existing:
                    continue
                
                # Generar nombre basado en el municipio
                municipio_clean = municipio.nombre_municipio.replace(' ', '_').lower()
                
                user = User(
                    nombre_completo=f'Coordinador Municipal {municipio.nombre_municipio}',
                    cedula=self._generate_cedula(),
                    telefono=self._generate_phone(),
                    email=f'coord.{municipio_clean}@caqueta.gov.co',
                    username=f'coord_{municipio_clean}',
                    password_hash=self._generate_password_hash(),
                    rol='coordinador_municipal',
                    municipio_id=municipio.id,
                    puesto_id=None,
                    activo=True
                )
                
                db.add(user)
                result['created'] += 1
                logger.info(f"Coordinador municipal creado: {municipio.nombre_municipio}")
                
        except Exception as e:
            error_msg = f"Error generando coordinadores municipales: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _generate_puesto_coordinators(self, db) -> Dict[str, any]:
        """Genera coordinadores para cada puesto electoral"""
        result = {'created': 0, 'errors': []}
        
        try:
            puestos = db.query(Location).filter(Location.tipo == LocationType.PUESTO).all()
            
            for puesto in puestos:
                # Verificar si ya existe un coordinador para este puesto
                existing = db.query(User).filter(
                    User.rol == 'coordinador_puesto',
                    User.puesto_id == puesto.id
                ).first()
                
                if existing:
                    continue
                
                # Generar identificador único para el puesto
                puesto_id = f"{puesto.codigo_municipio}_{puesto.codigo_zona}_{puesto.codigo_puesto}"
                
                user = User(
                    nombre_completo=f'Coordinador Puesto {puesto_id}',
                    cedula=self._generate_cedula(),
                    telefono=self._generate_phone(),
                    email=f'coord.puesto.{puesto_id}@caqueta.gov.co',
                    username=f'coord_puesto_{puesto.id}',  # Usar ID único del puesto
                    password_hash=self._generate_password_hash(),
                    rol='coordinador_puesto',
                    municipio_id=puesto.parent_id,
                    puesto_id=puesto.id,
                    activo=True
                )
                
                db.add(user)
                result['created'] += 1
                
                if result['created'] % 20 == 0:  # Log cada 20 coordinadores
                    logger.info(f"Coordinadores de puesto creados: {result['created']}")
                
        except Exception as e:
            error_msg = f"Error generando coordinadores de puesto: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        logger.info(f"Total coordinadores de puesto creados: {result['created']}")
        return result
    
    def _generate_mesa_testigos(self, db) -> Dict[str, any]:
        """Genera testigos para cada mesa electoral"""
        result = {'created': 0, 'errors': []}
        
        try:
            mesas = db.query(MesaElectoral).all()
            
            for mesa in mesas:
                # Generar 2 testigos por mesa (principal y suplente)
                for i in range(1, 3):
                    tipo = "Principal" if i == 1 else "Suplente"
                    
                    # Verificar si ya existe
                    existing = db.query(User).filter(
                        User.rol == 'testigo',
                        User.username == f'testigo_{mesa.codigo_mesa}_{i}'
                    ).first()
                    
                    if existing:
                        continue
                    
                    user = User(
                        nombre_completo=f'Testigo {tipo} Mesa {mesa.codigo_mesa}',
                        cedula=self._generate_cedula(),
                        telefono=self._generate_phone(),
                        email=f'testigo.mesa{mesa.id}.{i}@caqueta.gov.co',
                        username=f'testigo_mesa_{mesa.id}_{i}',  # Usar ID único de la mesa
                        password_hash=self._generate_password_hash(),
                        rol='testigo',
                        municipio_id=mesa.puesto.parent_id,
                        puesto_id=mesa.puesto_id,
                        activo=True
                    )
                    
                    db.add(user)
                    result['created'] += 1
                    
                    if result['created'] % 50 == 0:  # Log cada 50 testigos
                        logger.info(f"Testigos creados: {result['created']}")
                
        except Exception as e:
            error_msg = f"Error generando testigos de mesa: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        logger.info(f"Total testigos creados: {result['created']}")
        return result
    
    def _assign_testigos_to_mesas(self, db) -> Dict[str, any]:
        """Asigna testigos principales a sus mesas correspondientes"""
        result = {'assigned': 0, 'errors': []}
        
        try:
            mesas = db.query(MesaElectoral).all()
            
            for mesa in mesas:
                # Buscar el testigo principal para esta mesa
                testigo = db.query(User).filter(
                    User.rol == 'testigo',
                    User.username == f'testigo_mesa_{mesa.id}_1'
                ).first()
                
                if testigo and not mesa.testigo_asignado_id:
                    mesa.testigo_asignado_id = testigo.id
                    result['assigned'] += 1
                    
                    if result['assigned'] % 20 == 0:  # Log cada 20 asignaciones
                        logger.info(f"Testigos asignados a mesas: {result['assigned']}")
                
        except Exception as e:
            error_msg = f"Error asignando testigos a mesas: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        logger.info(f"Total testigos asignados a mesas: {result['assigned']}")
        return result
    
    def _generate_cedula(self) -> str:
        """Genera una cédula ficticia para usuarios de ejemplo"""
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    def _generate_phone(self) -> str:
        """Genera un teléfono ficticio para usuarios de ejemplo"""
        return f"300{random.randint(1000000, 9999999)}"
    
    def _generate_password_hash(self) -> str:
        """Genera un hash de contraseña ficticio para usuarios de ejemplo"""
        return f"hash_{''.join(random.choices(string.ascii_letters + string.digits, k=16))}"

    def _load_sample_parties(self, db) -> Dict[str, any]:
        """Carga partidos políticos de ejemplo"""
        result = {'created': 0, 'errors': []}
        
        parties_data = [
            {
                'nombre_oficial': 'Partido Liberal Colombiano',
                'siglas': 'PLC',
                'color_representativo': '#FF0000',
                'descripcion': 'Partido político tradicional de Colombia',
                'ideologia': 'Liberal',
                'fundacion_year': 1848
            },
            {
                'nombre_oficial': 'Partido Conservador Colombiano',
                'siglas': 'PCC',
                'color_representativo': '#0000FF',
                'descripcion': 'Partido político tradicional conservador',
                'ideologia': 'Conservador',
                'fundacion_year': 1849
            },
            {
                'nombre_oficial': 'Centro Democrático',
                'siglas': 'CD',
                'color_representativo': '#FF8C00',
                'descripcion': 'Partido político de centro derecha',
                'ideologia': 'Centro derecha',
                'fundacion_year': 2013
            },
            {
                'nombre_oficial': 'Pacto Histórico',
                'siglas': 'PH',
                'color_representativo': '#800080',
                'descripcion': 'Coalición política de izquierda',
                'ideologia': 'Izquierda',
                'fundacion_year': 2021
            },
            {
                'nombre_oficial': 'Cambio Radical',
                'siglas': 'CR',
                'color_representativo': '#FFA500',
                'descripcion': 'Partido político de centro',
                'ideologia': 'Centro',
                'fundacion_year': 1998
            },
            {
                'nombre_oficial': 'Alianza Verde',
                'siglas': 'AV',
                'color_representativo': '#00FF00',
                'descripcion': 'Partido político ambientalista',
                'ideologia': 'Verde',
                'fundacion_year': 2009
            },
            {
                'nombre_oficial': 'Polo Democrático Alternativo',
                'siglas': 'PDA',
                'color_representativo': '#FFFF00',
                'descripcion': 'Partido político de izquierda democrática',
                'ideologia': 'Izquierda',
                'fundacion_year': 2005
            },
            {
                'nombre_oficial': 'Partido de la U',
                'siglas': 'PU',
                'color_representativo': '#4169E1',
                'descripcion': 'Partido Social de Unidad Nacional',
                'ideologia': 'Centro',
                'fundacion_year': 2005
            }
        ]
        
        try:
            for party_data in parties_data:
                # Verificar si ya existe
                existing = db.query(PoliticalParty).filter(
                    PoliticalParty.siglas == party_data['siglas']
                ).first()
                
                if existing:
                    continue
                
                party = PoliticalParty(
                    nombre_oficial=party_data['nombre_oficial'],
                    siglas=party_data['siglas'],
                    color_representativo=party_data['color_representativo'],
                    descripcion=party_data['descripcion'],
                    ideologia=party_data['ideologia'],
                    fundacion_year=party_data['fundacion_year'],
                    activo=True,
                    reconocido_oficialmente=True
                )
                
                db.add(party)
                result['created'] += 1
                logger.info(f"Partido creado: {party_data['nombre_oficial']} ({party_data['siglas']})")
                
        except Exception as e:
            error_msg = f"Error creando partidos políticos: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        db.flush()
        return result

    def _load_sample_coalitions(self, db) -> Dict[str, any]:
        """Carga coaliciones de ejemplo"""
        result = {'created': 0, 'errors': []}
        
        coalitions_data = [
            {
                'nombre_coalicion': 'Coalición Centro Esperanza',
                'descripcion': 'Coalición de partidos de centro para las elecciones',
                'partidos': ['CR', 'AV']  # Siglas de los partidos
            },
            {
                'nombre_coalicion': 'Equipo por Colombia',
                'descripcion': 'Coalición de partidos tradicionales',
                'partidos': ['PCC', 'CD']
            }
        ]
        
        try:
            for coalition_data in coalitions_data:
                # Verificar si ya existe
                existing = db.query(Coalition).filter(
                    Coalition.nombre_coalicion == coalition_data['nombre_coalicion']
                ).first()
                
                if existing:
                    continue
                
                coalition = Coalition(
                    nombre_coalicion=coalition_data['nombre_coalicion'],
                    descripcion=coalition_data['descripcion'],
                    fecha_formacion=datetime.utcnow(),
                    activo=True
                )
                
                db.add(coalition)
                db.flush()  # Para obtener el ID
                
                # Agregar partidos a la coalición
                for sigla in coalition_data['partidos']:
                    party = db.query(PoliticalParty).filter(
                        PoliticalParty.siglas == sigla
                    ).first()
                    
                    if party:
                        coalition_party = CoalitionParty(
                            coalition_id=coalition.id,
                            party_id=party.id,
                            fecha_adhesion=datetime.utcnow(),
                            es_partido_principal=(sigla == coalition_data['partidos'][0])
                        )
                        db.add(coalition_party)
                
                result['created'] += 1
                logger.info(f"Coalición creada: {coalition_data['nombre_coalicion']}")
                
        except Exception as e:
            error_msg = f"Error creando coaliciones: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        db.flush()
        return result

    def _load_sample_candidates(self, db) -> Dict[str, any]:
        """Carga candidatos de ejemplo"""
        result = {'created': 0, 'errors': []}
        
        # Obtener tipos de elección y partidos
        concejos_juventudes = db.query(ElectionType).filter(
            ElectionType.codigo == 'concejos_juventudes'
        ).first()
        
        senado = db.query(ElectionType).filter(
            ElectionType.codigo == 'senado'
        ).first()
        
        parties = db.query(PoliticalParty).all()
        coalitions = db.query(Coalition).all()
        
        if not concejos_juventudes or not parties:
            result['errors'].append("No se encontraron tipos de elección o partidos para crear candidatos")
            return result
        
        # Candidatos para Concejos de Juventudes
        concejos_candidates = [
            {
                'nombre_completo': 'Ana María Rodríguez García',
                'numero_tarjeton': 1,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'party_sigla': 'PLC'
            },
            {
                'nombre_completo': 'Carlos Eduardo Martínez López',
                'numero_tarjeton': 2,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'party_sigla': 'PCC'
            },
            {
                'nombre_completo': 'Diana Patricia Gómez Ruiz',
                'numero_tarjeton': 3,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'party_sigla': 'CD'
            },
            {
                'nombre_completo': 'Javier Alejandro Torres Mendoza',
                'numero_tarjeton': 4,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'party_sigla': 'AV'
            },
            {
                'nombre_completo': 'María Fernanda Castro Jiménez',
                'numero_tarjeton': 5,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'party_sigla': 'CR'
            },
            {
                'nombre_completo': 'Luis Fernando Vargas Peña',
                'numero_tarjeton': 6,
                'cargo_aspirado': 'Consejero de Juventud',
                'circunscripcion': 'Caquetá',
                'es_independiente': True
            }
        ]
        
        # Candidatos para Senado (si existe)
        senado_candidates = []
        if senado:
            senado_candidates = [
                {
                    'nombre_completo': 'Roberto Carlos Hernández Silva',
                    'numero_tarjeton': 101,
                    'cargo_aspirado': 'Senador',
                    'circunscripcion': 'Nacional',
                    'party_sigla': 'PLC'
                },
                {
                    'nombre_completo': 'Gloria Elena Ramírez Vega',
                    'numero_tarjeton': 102,
                    'cargo_aspirado': 'Senador',
                    'circunscripcion': 'Nacional',
                    'party_sigla': 'PCC'
                },
                {
                    'nombre_completo': 'Miguel Ángel Sánchez Ortiz',
                    'numero_tarjeton': 103,
                    'cargo_aspirado': 'Senador',
                    'circunscripcion': 'Nacional',
                    'coalition_name': 'Coalición Centro Esperanza'
                }
            ]
        
        all_candidates = concejos_candidates + senado_candidates
        
        try:
            for candidate_data in all_candidates:
                # Verificar si ya existe
                existing = db.query(Candidate).filter(
                    Candidate.cedula == self._generate_cedula()
                ).first()
                
                # Buscar partido o coalición
                party = None
                coalition = None
                
                if candidate_data.get('party_sigla'):
                    party = db.query(PoliticalParty).filter(
                        PoliticalParty.siglas == candidate_data['party_sigla']
                    ).first()
                elif candidate_data.get('coalition_name'):
                    coalition = db.query(Coalition).filter(
                        Coalition.nombre_coalicion == candidate_data['coalition_name']
                    ).first()
                
                # Determinar tipo de elección
                election_type = concejos_juventudes
                if candidate_data['cargo_aspirado'] == 'Senador' and senado:
                    election_type = senado
                
                candidate = Candidate(
                    nombre_completo=candidate_data['nombre_completo'],
                    cedula=self._generate_cedula(),
                    numero_tarjeton=candidate_data['numero_tarjeton'],
                    cargo_aspirado=candidate_data['cargo_aspirado'],
                    election_type_id=election_type.id,
                    circunscripcion=candidate_data['circunscripcion'],
                    party_id=party.id if party else None,
                    coalition_id=coalition.id if coalition else None,
                    es_independiente=candidate_data.get('es_independiente', False),
                    activo=True,
                    habilitado_oficialmente=True
                )
                
                db.add(candidate)
                result['created'] += 1
                logger.info(f"Candidato creado: {candidate_data['nombre_completo']} - {candidate_data['cargo_aspirado']}")
                
        except Exception as e:
            error_msg = f"Error creando candidatos: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        db.flush()
        return result

    def generate_initialization_report(self) -> Dict[str, any]:
        """
        Genera reporte de configuración inicial
        
        Returns:
            dict: Reporte completo de inicialización
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'database_status': 'unknown',
            'geographic_validation': {},
            'summary': {}
        }
        
        try:
            with self.SessionLocal() as db:
                # Verificar conexión a la base de datos
                db.execute("SELECT 1")
                report['database_status'] = 'connected'
                
                # Obtener estadísticas generales
                stats = {}
                stats['total_locations'] = db.query(Location).count()
                stats['total_mesas'] = db.query(MesaElectoral).count()
                stats['departamentos'] = db.query(Location).filter(Location.tipo == LocationType.DEPARTAMENTO).count()
                stats['municipios'] = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).count()
                stats['puestos'] = db.query(Location).filter(Location.tipo == LocationType.PUESTO).count()
                
                # Estadísticas de datos electorales
                stats['election_types'] = db.query(ElectionType).count()
                stats['electoral_journeys'] = db.query(ElectoralJourney).count()
                stats['electoral_processes'] = db.query(ElectoralProcess).count()
                stats['users'] = db.query(User).count()
                
                # Estadísticas de candidatos y partidos
                stats['political_parties'] = db.query(PoliticalParty).count()
                stats['coalitions'] = db.query(Coalition).count()
                stats['candidates'] = db.query(Candidate).count()
                
                # Estadísticas por municipio
                municipios = db.query(Location).filter(Location.tipo == LocationType.MUNICIPIO).all()
                stats['municipios_detail'] = []
                
                for municipio in municipios:
                    puestos_count = db.query(Location).filter(
                        Location.parent_id == municipio.id,
                        Location.tipo == LocationType.PUESTO
                    ).count()
                    
                    mesas_count = db.query(MesaElectoral).join(Location).filter(
                        Location.parent_id == municipio.id
                    ).count()
                    
                    stats['municipios_detail'].append({
                        'nombre': municipio.nombre_municipio,
                        'codigo': municipio.codigo_municipio,
                        'puestos': puestos_count,
                        'mesas': mesas_count
                    })
                
                # Estadísticas de procesos electorales
                stats['processes_by_status'] = {}
                processes = db.query(ElectoralProcess).all()
                for process in processes:
                    status = process.estado
                    if status not in stats['processes_by_status']:
                        stats['processes_by_status'][status] = 0
                    stats['processes_by_status'][status] += 1
                
                report['summary'] = stats
                
                # Validación geográfica
                report['geographic_validation'] = self.validate_geographic_hierarchy()
                
                logger.info("Reporte de inicialización generado")
                
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            report['database_status'] = 'error'
            report['error'] = str(e)
            
        return report

def main():
    """Función principal para ejecutar la inicialización"""
    
    print("=== Sistema de Recolección Inicial de Votaciones - Caquetá ===")
    print("Inicializando base de datos...")
    
    # Crear servicio de inicialización
    service = InitializationService()
    
    # Crear esquema de base de datos
    if not service.create_database_schema():
        print("Error: No se pudo crear el esquema de la base de datos")
        return
    
    # Cargar datos DIVIPOLA
    print("Cargando datos DIVIPOLA de Caquetá...")
    result = service.load_divipola_data('divipola_corregido.csv')
    
    if result['success']:
        print(f"✓ Carga DIVIPOLA exitosa:")
        print(f"  - Total registros procesados: {result['total_records']}")
        print(f"  - Registros de Caquetá: {result['caqueta_records']}")
        print(f"  - Ubicaciones creadas: {result['locations_created']}")
        print(f"  - Mesas creadas: {result['mesas_created']}")
        
        if result['errors']:
            print(f"  - Errores: {len(result['errors'])}")
            for error in result['errors'][:5]:  # Mostrar solo los primeros 5 errores
                print(f"    • {error}")
    else:
        print("✗ Error en la carga de datos DIVIPOLA")
        for error in result['errors']:
            print(f"  • {error}")
        return
    
    # Cargar datos de ejemplo electorales
    print("\nCargando datos de ejemplo electorales...")
    sample_result = service.load_sample_election_data()
    
    if sample_result['success']:
        print(f"✓ Carga de datos electorales exitosa:")
        print(f"  - Tipos de elección creados: {sample_result['election_types_created']}")
        print(f"  - Jornadas electorales creadas: {sample_result['journeys_created']}")
        print(f"  - Procesos electorales creados: {sample_result['processes_created']}")
        print(f"  - Usuarios creados: {sample_result['users_created']}")
        print(f"  - Partidos políticos creados: {sample_result.get('parties_created', 0)}")
        print(f"  - Coaliciones creadas: {sample_result.get('coalitions_created', 0)}")
        print(f"  - Candidatos creados: {sample_result.get('candidates_created', 0)}")
        
        if sample_result['errors']:
            print(f"  - Errores: {len(sample_result['errors'])}")
            for error in sample_result['errors'][:5]:
                print(f"    • {error}")
    else:
        print("✗ Error en la carga de datos electorales")
        for error in sample_result['errors']:
            print(f"  • {error}")
    
    # Generar usuarios automáticamente
    print("\nGenerando usuarios automáticamente...")
    users_result = service.generate_users_automatically()
    
    if users_result['success']:
        print(f"✓ Generación automática de usuarios exitosa:")
        print(f"  - Coordinadores departamentales: {users_result['coordinadores_departamento']}")
        print(f"  - Coordinadores municipales: {users_result['coordinadores_municipales']}")
        print(f"  - Coordinadores de puesto: {users_result['coordinadores_puesto']}")
        print(f"  - Testigos de mesa: {users_result['testigos_mesa']}")
        print(f"  - Total usuarios creados: {users_result['total_users_created']}")
        
        if users_result['errors']:
            print(f"  - Errores: {len(users_result['errors'])}")
            for error in users_result['errors'][:5]:
                print(f"    • {error}")
    else:
        print("✗ Error en la generación automática de usuarios")
        for error in users_result['errors']:
            print(f"  • {error}")
    
    # Generar reporte final
    print("\nGenerando reporte de inicialización...")
    report = service.generate_initialization_report()
    
    print(f"\n=== REPORTE DE INICIALIZACIÓN ===")
    print(f"Fecha: {report['timestamp']}")
    print(f"Estado BD: {report['database_status']}")
    
    if 'summary' in report:
        summary = report['summary']
        print(f"\nESTADÍSTICAS GENERALES:")
        print(f"  - Departamentos: {summary['departamentos']}")
        print(f"  - Municipios: {summary['municipios']}")
        print(f"  - Puestos electorales: {summary['puestos']}")
        print(f"  - Mesas electorales: {summary['total_mesas']}")
        
        print(f"\nDATOS ELECTORALES:")
        print(f"  - Tipos de elección: {summary['election_types']}")
        print(f"  - Jornadas electorales: {summary['electoral_journeys']}")
        print(f"  - Procesos electorales: {summary['electoral_processes']}")
        print(f"  - Usuarios del sistema: {summary['users']}")
        print(f"  - Partidos políticos: {summary.get('political_parties', 0)}")
        print(f"  - Coaliciones: {summary.get('coalitions', 0)}")
        print(f"  - Candidatos: {summary.get('candidates', 0)}")
        
        if 'processes_by_status' in summary:
            print(f"\nPROCESOS POR ESTADO:")
            for status, count in summary['processes_by_status'].items():
                print(f"  - {status.title()}: {count}")
        
        print(f"\nDETALLE POR MUNICIPIO:")
        for mun in summary['municipios_detail']:
            print(f"  - {mun['nombre']}: {mun['puestos']} puestos, {mun['mesas']} mesas")
    
    validation = report.get('geographic_validation', {})
    if validation.get('valid'):
        print(f"\n✓ Validación geográfica: EXITOSA")
    else:
        print(f"\n✗ Validación geográfica: ERRORES ENCONTRADOS")
        for error in validation.get('errors', []):
            print(f"  • {error}")
    
    if validation.get('warnings'):
        print(f"\nADVERTENCIAS:")
        for warning in validation.get('warnings', []):
            print(f"  • {warning}")
    
    print(f"\n=== INICIALIZACIÓN COMPLETADA ===")
    print("El sistema está listo para comenzar la recolección de votaciones.")
    print("Datos disponibles:")
    print("- Estructura geográfica completa de Caquetá")
    print("- Tipos de elecciones configurados")
    print("- Jornadas electorales de ejemplo")
    print("- Procesos electorales activos")
    print("- Usuarios del sistema")
    print("- Partidos políticos y coaliciones")
    print("- Candidatos de ejemplo por tipo de elección")

if __name__ == "__main__":
    main()