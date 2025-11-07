"""
Servicio de Importación de Excel
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

from ..models import ImportData

class ExcelImportService:
    """Servicio para importación de datos desde archivos Excel"""
    
    def __init__(self, db_path: str = 'electoral_system.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== IMPORTACIÓN DE CANDIDATOS ====================
    
    def import_candidates_from_excel(self, file_path: str, election_type_id: int, 
                                   imported_by: int) -> Dict[str, Any]:
        """Importar candidatos desde archivo Excel"""
        try:
            # Leer archivo Excel
            df = pd.read_excel(file_path)
            
            import_data = ImportData(
                file_name=os.path.basename(file_path),
                file_type='excel',
                import_type='candidates',
                total_records=len(df),
                status='processing'
            )
            
            successful_imports = 0
            errors = []
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    # Validar datos requeridos
                    if pd.isna(row.get('nombre_completo')) or pd.isna(row.get('cedula')):
                        errors.append({
                            'row': index + 2,  # +2 para header y 0-based index
                            'error': 'Nombre completo y cédula son requeridos'
                        })
                        continue
                    
                    # Determinar afiliación política
                    party_id = None
                    coalition_id = None
                    es_independiente = False
                    
                    if not pd.isna(row.get('party_siglas')):
                        party_id = self._get_party_id_by_siglas(row['party_siglas'])
                    elif not pd.isna(row.get('coalition_name')):
                        coalition_id = self._get_coalition_id_by_name(row['coalition_name'])
                    else:
                        es_independiente = True
                    
                    # Insertar candidato
                    cursor.execute("""
                        INSERT INTO candidates 
                        (nombre_completo, cedula, numero_tarjeton, cargo_aspirado, 
                         election_type_id, circunscripcion, party_id, coalition_id, 
                         es_independiente, biografia, propuestas, experiencia, 
                         activo, habilitado_oficialmente, creado_por, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['nombre_completo'],
                        str(row['cedula']),
                        int(row.get('numero_tarjeton', 0)),
                        row.get('cargo_aspirado', ''),
                        election_type_id,
                        row.get('circunscripcion', ''),
                        party_id,
                        coalition_id,
                        es_independiente,
                        row.get('biografia', ''),
                        row.get('propuestas', ''),
                        row.get('experiencia', ''),
                        True,
                        True,
                        imported_by,
                        datetime.now()
                    ))
                    
                    successful_imports += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 2,
                        'error': str(e)
                    })
            
            conn.commit()
            conn.close()
            
            import_data.successful_records = successful_imports
            import_data.failed_records = len(errors)
            import_data.errors = errors
            import_data.status = 'completed' if successful_imports > 0 else 'failed'
            
            self.logger.info(f"Importación completada: {successful_imports}/{import_data.total_records} candidatos")
            
            return {
                'success': True,
                'import_data': import_data.__dict__,
                'message': f'Importación completada: {successful_imports} exitosos, {len(errors)} errores'
            }
            
        except Exception as e:
            self.logger.error(f"Error en importación de candidatos: {e}")
            return {
                'success': False,
                'error': f'Error procesando archivo: {str(e)}'
            }
    
    def import_witnesses_from_excel(self, file_path: str, municipio_id: int, 
                                  imported_by: int) -> Dict[str, Any]:
        """Importar testigos desde archivo Excel"""
        try:
            df = pd.read_excel(file_path)
            
            import_data = ImportData(
                file_name=os.path.basename(file_path),
                file_type='excel',
                import_type='witnesses',
                total_records=len(df),
                status='processing'
            )
            
            successful_imports = 0
            errors = []
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    # Validar datos requeridos
                    if pd.isna(row.get('nombre_completo')) or pd.isna(row.get('cedula')):
                        errors.append({
                            'row': index + 2,
                            'error': 'Nombre completo y cédula son requeridos'
                        })
                        continue
                    
                    # Obtener partido si se especifica
                    party_id = None
                    if not pd.isna(row.get('party_siglas')):
                        party_id = self._get_party_id_by_siglas(row['party_siglas'])
                    
                    # Insertar testigo
                    cursor.execute("""
                        INSERT INTO testigos_electorales 
                        (nombre_completo, cedula, telefono, email, direccion, 
                         partido_id, tipo_testigo, observaciones, municipio_id,
                         activo, creado_por, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['nombre_completo'],
                        str(row['cedula']),
                        row.get('telefono', ''),
                        row.get('email', ''),
                        row.get('direccion', ''),
                        party_id,
                        row.get('tipo_testigo', 'principal'),
                        row.get('observaciones', ''),
                        municipio_id,
                        True,
                        imported_by,
                        datetime.now()
                    ))
                    
                    successful_imports += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 2,
                        'error': str(e)
                    })
            
            conn.commit()
            conn.close()
            
            import_data.successful_records = successful_imports
            import_data.failed_records = len(errors)
            import_data.errors = errors
            import_data.status = 'completed' if successful_imports > 0 else 'failed'
            
            return {
                'success': True,
                'import_data': import_data.__dict__,
                'message': f'Importación completada: {successful_imports} testigos importados'
            }
            
        except Exception as e:
            self.logger.error(f"Error en importación de testigos: {e}")
            return {
                'success': False,
                'error': f'Error procesando archivo: {str(e)}'
            }
    
    # ==================== UTILIDADES ====================
    
    def _get_party_id_by_siglas(self, siglas: str) -> Optional[int]:
        """Obtener ID de partido por siglas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM political_parties WHERE siglas = ? AND activo = 1", (siglas,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error:
            return None
    
    def _get_coalition_id_by_name(self, name: str) -> Optional[int]:
        """Obtener ID de coalición por nombre"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM coalitions WHERE nombre_coalicion = ? AND activo = 1", (name,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error:
            return None
    
    def generate_excel_template(self, template_type: str) -> Dict[str, Any]:
        """Generar plantilla Excel para importación"""
        try:
            templates = {
                'candidates': {
                    'columns': [
                        'nombre_completo', 'cedula', 'numero_tarjeton', 'cargo_aspirado',
                        'circunscripcion', 'party_siglas', 'coalition_name', 'biografia',
                        'propuestas', 'experiencia'
                    ],
                    'example_data': [
                        ['Juan Pérez García', '12345678', 1, 'Senador', 'Nacional', 'PLC', '', 
                         'Abogado con experiencia', 'Educación y salud', 'Alcalde 2016-2020']
                    ]
                },
                'witnesses': {
                    'columns': [
                        'nombre_completo', 'cedula', 'telefono', 'email', 'direccion',
                        'party_siglas', 'tipo_testigo', 'observaciones'
                    ],
                    'example_data': [
                        ['María González', '87654321', '3001234567', 'maria@email.com', 
                         'Calle 123', 'CD', 'principal', 'Testigo experimentado']
                    ]
                }
            }
            
            if template_type not in templates:
                return {
                    'success': False,
                    'error': f'Tipo de plantilla no válido: {template_type}'
                }
            
            template = templates[template_type]
            
            return {
                'success': True,
                'template': template,
                'instructions': {
                    'candidates': 'Complete todos los campos requeridos. Use party_siglas O coalition_name, no ambos.',
                    'witnesses': 'Complete nombre_completo, cedula y telefono como mínimo.'
                }.get(template_type, '')
            }
            
        except Exception as e:
            self.logger.error(f"Error generando plantilla: {e}")
            return {
                'success': False,
                'error': f'Error generando plantilla: {str(e)}'
            }