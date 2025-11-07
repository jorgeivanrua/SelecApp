"""
Servicio de Integración de Candidatos con Formularios E-14
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    form_template: Dict[str, Any]
    candidate_fields: List[E14CandidateField]
    validation_rules: Dict[str, Any]

class E14CandidateIntegrationService:
    """Servicio para integrar candidatos con formularios E-14"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logger
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== GENERACIÓN DE FORMULARIOS E-14 CON CANDIDATOS ====================
    
    def generate_e14_form_with_candidates(self, election_type_id: int, 
                                        mesa_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generar estructura de formulario E-14 con datos de candidatos
        
        Args:
            election_type_id: ID del tipo de elección
            mesa_id: ID de la mesa (opcional, para validaciones específicas)
            
        Returns:
            Dict con estructura del formulario E-14 con candidatos
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener información del tipo de elección
            cursor.execute('''
            SELECT * FROM election_types 
            WHERE id = ? AND activo = 1
            ''', (election_type_id,))
            
            election_type = cursor.fetchone()
            if not election_type:
                return {
                    'success': False,
                    'error': 'Tipo de elección no encontrado'
                }
            
            election_dict = dict(election_type)
            
            # Obtener candidatos del tipo de elección
            cursor.execute('''
            SELECT c.*, pp.siglas as party_siglas, co.nombre_coalicion as coalition_name
            FROM candidates c
            LEFT JOIN political_parties pp ON c.party_id = pp.id
            LEFT JOIN coalitions co ON c.coalition_id = co.id
            WHERE c.election_type_id = ? AND c.activo = 1 AND c.habilitado_oficialmente = 1
            ORDER BY c.numero_tarjeton
            ''', (election_type_id,))
            
            candidates = [dict(row) for row in cursor.fetchall()]
            
            # Generar campos de candidatos para el formulario
            candidate_fields = []
            for candidate in candidates:
                field = E14CandidateField(
                    candidate_id=candidate['id'],
                    nombre_completo=candidate['nombre_completo'],
                    numero_tarjeton=candidate['numero_tarjeton'],
                    party_siglas=candidate.get('party_siglas'),
                    coalition_name=candidate.get('coalition_name'),
                    field_name=f"votos_candidato_{candidate['numero_tarjeton']}"
                )
                candidate_fields.append(field)
            
            # Obtener plantilla base del formulario
            base_template = json.loads(election_dict['plantilla_e14']) if election_dict['plantilla_e14'] else {}
            
            # Generar estructura completa del formulario
            form_structure = self._build_e14_form_structure(
                election_dict, candidate_fields, base_template
            )
            
            # Generar reglas de validación
            validation_rules = self._generate_validation_rules(candidate_fields, base_template)
            
            conn.close()
            
            result = E14FormStructure(
                election_type_id=election_type_id,
                election_type_name=election_dict['nombre'],
                form_template=form_structure,
                candidate_fields=candidate_fields,
                validation_rules=validation_rules
            )
            
            return {
                'success': True,
                'data': result.__dict__
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error generando formulario E-14: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }
    
    def _build_e14_form_structure(self, election_type: Dict, 
                                 candidate_fields: List[E14CandidateField],
                                 base_template: Dict) -> Dict[str, Any]:
        """Construir estructura completa del formulario E-14"""
        
        # Estructura base del formulario E-14
        form_structure = {
            'metadata': {
                'election_type_id': election_type['id'],
                'election_type_name': election_type['nombre'],
                'form_version': '1.0',
                'generated_at': datetime.now().isoformat()
            },
            'sections': []
        }
        
        # Sección de información general
        info_section = {
            'section_id': 'informacion_general',
            'section_title': 'Información General',
            'fields': [
                {
                    'field_name': 'mesa_id',
                    'field_type': 'hidden',
                    'required': True
                },
                {
                    'field_name': 'testigo_id',
                    'field_type': 'hidden',
                    'required': True
                },
                {
                    'field_name': 'fecha_captura',
                    'field_type': 'datetime',
                    'label': 'Fecha y Hora de Captura',
                    'required': True,
                    'default': datetime.now().isoformat()
                }
            ]
        }
        form_structure['sections'].append(info_section)
        
        # Sección de candidatos
        candidates_section = {
            'section_id': 'candidatos',
            'section_title': f'Candidatos - {election_type["nombre"]}',
            'description': 'Registre los votos obtenidos por cada candidato',
            'fields': []
        }
        
        # Agregar campos de candidatos
        for candidate_field in candidate_fields:
            affiliation = ''
            if candidate_field.party_siglas:
                affiliation = f' ({candidate_field.party_siglas})'
            elif candidate_field.coalition_name:
                affiliation = f' ({candidate_field.coalition_name})'
            
            field = {
                'field_name': candidate_field.field_name,
                'field_type': 'number',
                'label': f'{candidate_field.numero_tarjeton}. {candidate_field.nombre_completo}{affiliation}',
                'required': True,
                'min_value': 0,
                'max_value': 9999,
                'candidate_id': candidate_field.candidate_id,
                'numero_tarjeton': candidate_field.numero_tarjeton,
                'validation': ['non_negative', 'integer']
            }
            candidates_section['fields'].append(field)
        
        form_structure['sections'].append(candidates_section)
        
        # Sección de totales y validación
        totals_section = {
            'section_id': 'totales',
            'section_title': 'Totales y Validación',
            'fields': [
                {
                    'field_name': 'total_votos_candidatos',
                    'field_type': 'number',
                    'label': 'Total Votos Candidatos (Calculado)',
                    'readonly': True,
                    'calculated': True,
                    'calculation': 'sum_candidate_votes'
                },
                {
                    'field_name': 'votos_blanco',
                    'field_type': 'number',
                    'label': 'Votos en Blanco',
                    'required': True,
                    'min_value': 0,
                    'validation': ['non_negative', 'integer']
                },
                {
                    'field_name': 'votos_nulos',
                    'field_type': 'number',
                    'label': 'Votos Nulos',
                    'required': True,
                    'min_value': 0,
                    'validation': ['non_negative', 'integer']
                },
                {
                    'field_name': 'total_votos_depositados',
                    'field_type': 'number',
                    'label': 'Total Votos Depositados',
                    'required': True,
                    'min_value': 0,
                    'validation': ['non_negative', 'integer', 'match_sum']
                }
            ]
        }
        form_structure['sections'].append(totals_section)
        
        # Sección de observaciones y anomalías
        observations_section = {
            'section_id': 'observaciones',
            'section_title': 'Observaciones y Anomalías',
            'fields': [
                {
                    'field_name': 'observaciones_generales',
                    'field_type': 'textarea',
                    'label': 'Observaciones Generales',
                    'required': False,
                    'max_length': 1000
                },
                {
                    'field_name': 'anomalias_reportadas',
                    'field_type': 'textarea',
                    'label': 'Anomalías Reportadas',
                    'required': True,
                    'placeholder': 'Describa cualquier anomalía observada durante el proceso electoral',
                    'max_length': 2000
                }
            ]
        }
        form_structure['sections'].append(observations_section)
        
        return form_structure
    
    def _generate_validation_rules(self, candidate_fields: List[E14CandidateField],
                                  base_template: Dict) -> Dict[str, Any]:
        """Generar reglas de validación para el formulario"""
        
        candidate_field_names = [field.field_name for field in candidate_fields]
        
        validation_rules = {
            'required_fields': [
                'mesa_id', 'testigo_id', 'fecha_captura',
                'votos_blanco', 'votos_nulos', 'total_votos_depositados',
                'anomalias_reportadas'
            ] + candidate_field_names,
            
            'numeric_fields': [
                'votos_blanco', 'votos_nulos', 'total_votos_depositados'
            ] + candidate_field_names,
            
            'non_negative_fields': [
                'votos_blanco', 'votos_nulos', 'total_votos_depositados'
            ] + candidate_field_names,
            
            'calculated_fields': {
                'total_votos_candidatos': {
                    'type': 'sum',
                    'source_fields': candidate_field_names
                }
            },
            
            'cross_validation': {
                'total_sum_validation': {
                    'rule': 'total_votos_depositados == total_votos_candidatos + votos_blanco + votos_nulos',
                    'error_message': 'La suma de votos no coincide con el total depositado'
                },
                'minimum_votes_validation': {
                    'rule': 'total_votos_depositados >= 0',
                    'error_message': 'El total de votos debe ser mayor o igual a cero'
                }
            },
            
            'candidate_specific': {
                'max_votes_per_candidate': 9999,
                'min_votes_per_candidate': 0,
                'total_candidates': len(candidate_fields)
            }
        }
        
        return validation_rules
    
    # ==================== VALIDACIÓN DE VOTOS CONTRA CANDIDATOS ====================
    
    def validate_votes_against_candidates(self, election_type_id: int, 
                                        form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar votos contra lista oficial de candidatos
        
        Args:
            election_type_id: ID del tipo de elección
            form_data: Datos del formulario E-14
            
        Returns:
            Dict con resultado de la validación
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener candidatos oficiales
            cursor.execute('''
            SELECT id, numero_tarjeton, nombre_completo
            FROM candidates
            WHERE election_type_id = ? AND activo = 1 AND habilitado_oficialmente = 1
            ORDER BY numero_tarjeton
            ''', (election_type_id,))
            
            official_candidates = {row[1]: {'id': row[0], 'name': row[2]} 
                                 for row in cursor.fetchall()}
            
            validation_result = {
                'success': True,
                'errors': [],
                'warnings': [],
                'candidate_votes': {},
                'total_candidate_votes': 0,
                'validation_summary': {}
            }
            
            # Validar votos de candidatos
            total_candidate_votes = 0
            for field_name, value in form_data.items():
                if field_name.startswith('votos_candidato_'):
                    try:
                        tarjeton_number = int(field_name.split('_')[-1])
                        votes = int(value) if value else 0
                        
                        if tarjeton_number not in official_candidates:
                            validation_result['errors'].append(
                                f'Candidato con tarjetón {tarjeton_number} no está en la lista oficial'
                            )
                            validation_result['success'] = False
                        else:
                            validation_result['candidate_votes'][tarjeton_number] = {
                                'candidate_id': official_candidates[tarjeton_number]['id'],
                                'candidate_name': official_candidates[tarjeton_number]['name'],
                                'votes': votes
                            }
                            total_candidate_votes += votes
                    
                    except (ValueError, IndexError) as e:
                        validation_result['errors'].append(
                            f'Error procesando campo {field_name}: {str(e)}'
                        )
                        validation_result['success'] = False
            
            validation_result['total_candidate_votes'] = total_candidate_votes
            
            # Validar totales
            votos_blanco = int(form_data.get('votos_blanco', 0))
            votos_nulos = int(form_data.get('votos_nulos', 0))
            total_depositados = int(form_data.get('total_votos_depositados', 0))
            
            calculated_total = total_candidate_votes + votos_blanco + votos_nulos
            
            if calculated_total != total_depositados:
                validation_result['errors'].append(
                    f'La suma de votos ({calculated_total}) no coincide con el total depositado ({total_depositados})'
                )
                validation_result['success'] = False
            
            # Verificar candidatos faltantes
            for tarjeton, candidate_info in official_candidates.items():
                if tarjeton not in validation_result['candidate_votes']:
                    validation_result['warnings'].append(
                        f'No se registraron votos para el candidato {tarjeton}: {candidate_info["name"]}'
                    )
            
            # Resumen de validación
            validation_result['validation_summary'] = {
                'total_official_candidates': len(official_candidates),
                'candidates_with_votes': len(validation_result['candidate_votes']),
                'total_errors': len(validation_result['errors']),
                'total_warnings': len(validation_result['warnings']),
                'math_validation_passed': calculated_total == total_depositados
            }
            
            conn.close()
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validando votos contra candidatos: {e}")
            return {
                'success': False,
                'error': f'Error en validación: {str(e)}'
            }
    
    # ==================== CÁLCULO AUTOMÁTICO DE TOTALES ====================
    
    def calculate_candidate_totals_from_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcular totales por candidato desde formulario E-14
        
        Args:
            form_data: Datos del formulario E-14
            
        Returns:
            Dict con totales calculados
        """
        try:
            candidate_totals = {}
            total_candidate_votes = 0
            
            # Extraer votos de candidatos
            for field_name, value in form_data.items():
                if field_name.startswith('votos_candidato_'):
                    try:
                        tarjeton_number = int(field_name.split('_')[-1])
                        votes = int(value) if value else 0
                        
                        candidate_totals[tarjeton_number] = votes
                        total_candidate_votes += votes
                        
                    except (ValueError, IndexError):
                        continue
            
            # Calcular otros totales
            votos_blanco = int(form_data.get('votos_blanco', 0))
            votos_nulos = int(form_data.get('votos_nulos', 0))
            total_depositados = int(form_data.get('total_votos_depositados', 0))
            
            calculated_total = total_candidate_votes + votos_blanco + votos_nulos
            
            return {
                'success': True,
                'data': {
                    'candidate_totals': candidate_totals,
                    'total_candidate_votes': total_candidate_votes,
                    'votos_blanco': votos_blanco,
                    'votos_nulos': votos_nulos,
                    'total_depositados': total_depositados,
                    'calculated_total': calculated_total,
                    'totals_match': calculated_total == total_depositados,
                    'total_candidates_with_votes': len([v for v in candidate_totals.values() if v > 0])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando totales: {e}")
            return {
                'success': False,
                'error': f'Error en cálculo: {str(e)}'
            }
    
    # ==================== VINCULACIÓN DE VOTOS CON CANDIDATOS ====================
    
    def link_votes_to_candidates(self, form_data: Dict[str, Any], 
                               election_type_id: int, mesa_id: int) -> Dict[str, Any]:
        """
        Vincular votos con candidatos específicos
        
        Args:
            form_data: Datos del formulario E-14
            election_type_id: ID del tipo de elección
            mesa_id: ID de la mesa
            
        Returns:
            Dict con resultado de la vinculación
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Obtener candidatos del tipo de elección
            cursor.execute('''
            SELECT id, numero_tarjeton, nombre_completo
            FROM candidates
            WHERE election_type_id = ? AND activo = 1
            ORDER BY numero_tarjeton
            ''', (election_type_id,))
            
            candidates_map = {row[1]: {'id': row[0], 'name': row[2]} 
                            for row in cursor.fetchall()}
            
            # Crear registros de votos por candidato
            vote_records = []
            for field_name, value in form_data.items():
                if field_name.startswith('votos_candidato_'):
                    try:
                        tarjeton_number = int(field_name.split('_')[-1])
                        votes = int(value) if value else 0
                        
                        if tarjeton_number in candidates_map and votes > 0:
                            vote_record = {
                                'candidate_id': candidates_map[tarjeton_number]['id'],
                                'candidate_name': candidates_map[tarjeton_number]['name'],
                                'numero_tarjeton': tarjeton_number,
                                'votes': votes,
                                'mesa_id': mesa_id,
                                'election_type_id': election_type_id,
                                'fecha_registro': datetime.now().isoformat()
                            }
                            vote_records.append(vote_record)
                    
                    except (ValueError, IndexError):
                        continue
            
            conn.close()
            
            return {
                'success': True,
                'data': {
                    'vote_records': vote_records,
                    'total_records': len(vote_records),
                    'total_votes_linked': sum(record['votes'] for record in vote_records)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error vinculando votos: {e}")
            return {
                'success': False,
                'error': f'Error en vinculación: {str(e)}'
            }
    
    # ==================== UTILIDADES ====================
    
    def get_candidate_field_mapping(self, election_type_id: int) -> Dict[str, Any]:
        """
        Obtener mapeo de campos de candidatos para un tipo de elección
        
        Args:
            election_type_id: ID del tipo de elección
            
        Returns:
            Dict con mapeo de campos
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, numero_tarjeton, nombre_completo, cedula
            FROM candidates
            WHERE election_type_id = ? AND activo = 1 AND habilitado_oficialmente = 1
            ORDER BY numero_tarjeton
            ''', (election_type_id,))
            
            candidates = [dict(row) for row in cursor.fetchall()]
            
            field_mapping = {}
            for candidate in candidates:
                field_name = f"votos_candidato_{candidate['numero_tarjeton']}"
                field_mapping[field_name] = {
                    'candidate_id': candidate['id'],
                    'numero_tarjeton': candidate['numero_tarjeton'],
                    'nombre_completo': candidate['nombre_completo'],
                    'cedula': candidate['cedula']
                }
            
            conn.close()
            
            return {
                'success': True,
                'data': field_mapping
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error obteniendo mapeo de campos: {e}")
            return {
                'success': False,
                'error': f'Error de base de datos: {str(e)}'
            }

if __name__ == "__main__":
    print("🗳️  Servicio de Integración de Candidatos con Formularios E-14")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    
    # Ejemplo de uso
    service = E14CandidateIntegrationService()
    
    print("Funcionalidades disponibles:")
    print("- Generación de formularios E-14 con datos de candidatos")
    print("- Validación de votos contra lista oficial de candidatos")
    print("- Cálculo automático de totales por candidato")
    print("- Vinculación de votos con candidatos específicos")
    print("- Mapeo de campos de candidatos para formularios")