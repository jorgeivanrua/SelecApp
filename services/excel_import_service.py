#!/usr/bin/env python3
"""
ExcelImportService - Servicio para importar datos desde archivos Excel
Carga masiva de partidos, coaliciones, candidatos y tipos de elección
"""

import pandas as pd
import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import logging
import os

class ExcelImportService:
    """Servicio para importar datos desde archivos Excel"""
    
    def __init__(self, db_path: str = 'caqueta_electoral.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== IMPORTACIÓN DE PARTIDOS ====================
    
    def import_parties_from_excel(self, excel_file_path: str, sheet_name: str = 'Partidos') -> Dict:
        """
        Importar partidos desde Excel
        Columnas esperadas: nombre, sigla, color_principal (opcional)
        """
        try:
            results = {
                'total_rows': 0,
                'processed': 0,
                'errors': [],
                'warnings': [],
                'parties_created': []
            }
            
            # Leer archivo Excel
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            results['total_rows'] = len(df)
            
            # Validar columnas requeridas
            required_columns = ['nombre', 'sigla']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas faltantes en Excel: {missing_columns}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos
                    if pd.isna(row['nombre']) or pd.isna(row['sigla']):
                        results['errors'].append(f"Fila {index + 2}: Nombre y sigla son requeridos")
                        continue
                    
                    nombre = str(row['nombre']).strip()
                    sigla = str(row['sigla']).strip()
                    
                    # Verificar duplicados
                    cursor.execute("SELECT id FROM partidos_politicos WHERE nombre = ? OR sigla = ?", 
                                  (nombre, sigla))
                    if cursor.fetchone():
                        results['warnings'].append(f"Fila {index + 2}: Partido {nombre} ({sigla}) ya existe")
                        continue
                    
                    # Obtener color (opcional)
                    color = '#007bff'  # Color por defecto
                    if 'color_principal' in df.columns and not pd.isna(row['color_principal']):
                        color = str(row['color_principal']).strip()
                        if not color.startswith('#'):
                            color = f"#{color}"
                    
                    # Crear partido
                    cursor.execute("""
                        INSERT INTO partidos_politicos (nombre, sigla, color_principal)
                        VALUES (?, ?, ?)
                    """, (nombre, sigla, color))
                    
                    party_id = cursor.lastrowid
                    results['parties_created'].append({
                        'id': party_id,
                        'nombre': nombre,
                        'sigla': sigla
                    })
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Fila {index + 2}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Importación de partidos completada: {results['processed']} procesados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error importando partidos: {e}")
            raise
    
    # ==================== IMPORTACIÓN DE TIPOS DE ELECCIÓN ====================
    
    def import_election_types_from_excel(self, excel_file_path: str, sheet_name: str = 'TiposEleccion') -> Dict:
        """
        Importar tipos de elección desde Excel
        Columnas esperadas: nombre, descripcion, nivel
        """
        try:
            results = {
                'total_rows': 0,
                'processed': 0,
                'errors': [],
                'warnings': [],
                'election_types_created': []
            }
            
            # Leer archivo Excel
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            results['total_rows'] = len(df)
            
            # Validar columnas requeridas
            required_columns = ['nombre', 'nivel']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas faltantes en Excel: {missing_columns}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos
                    if pd.isna(row['nombre']) or pd.isna(row['nivel']):
                        results['errors'].append(f"Fila {index + 2}: Nombre y nivel son requeridos")
                        continue
                    
                    nombre = str(row['nombre']).strip()
                    nivel = str(row['nivel']).strip().lower()
                    descripcion = str(row.get('descripcion', '')).strip() if not pd.isna(row.get('descripcion')) else None
                    
                    # Validar nivel
                    valid_levels = ['nacional', 'departamental', 'municipal']
                    if nivel not in valid_levels:
                        results['errors'].append(f"Fila {index + 2}: Nivel debe ser uno de: {valid_levels}")
                        continue
                    
                    # Verificar duplicados
                    cursor.execute("SELECT id FROM cargos_electorales WHERE nombre = ?", (nombre,))
                    if cursor.fetchone():
                        results['warnings'].append(f"Fila {index + 2}: Cargo {nombre} ya existe")
                        continue
                    
                    # Crear cargo electoral
                    cursor.execute("""
                        INSERT INTO cargos_electorales (nombre, descripcion, nivel)
                        VALUES (?, ?, ?)
                    """, (nombre, descripcion, nivel))
                    
                    cargo_id = cursor.lastrowid
                    results['election_types_created'].append({
                        'id': cargo_id,
                        'nombre': nombre,
                        'nivel': nivel
                    })
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Fila {index + 2}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Importación de tipos de elección completada: {results['processed']} procesados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error importando tipos de elección: {e}")
            raise
    
    # ==================== IMPORTACIÓN DE CANDIDATOS ====================
    
    def import_candidates_from_excel(self, excel_file_path: str, sheet_name: str = 'Candidatos') -> Dict:
        """
        Importar candidatos desde Excel
        Columnas esperadas: cedula, nombre_completo, partido_sigla, cargo_nombre, municipio_nombre (opcional)
        """
        try:
            results = {
                'total_rows': 0,
                'processed': 0,
                'errors': [],
                'warnings': [],
                'candidates_created': []
            }
            
            # Leer archivo Excel
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            results['total_rows'] = len(df)
            
            # Validar columnas requeridas
            required_columns = ['cedula', 'nombre_completo', 'partido_sigla', 'cargo_nombre']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas faltantes en Excel: {missing_columns}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear mapas de referencia para optimizar consultas
            party_map = self._create_party_map(cursor)
            cargo_map = self._create_cargo_map(cursor)
            municipio_map = self._create_municipio_map(cursor)
            
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos
                    if pd.isna(row['cedula']) or pd.isna(row['nombre_completo']):
                        results['errors'].append(f"Fila {index + 2}: Cédula y nombre son requeridos")
                        continue
                    
                    cedula = str(row['cedula']).strip()
                    nombre_completo = str(row['nombre_completo']).strip()
                    partido_sigla = str(row['partido_sigla']).strip()
                    cargo_nombre = str(row['cargo_nombre']).strip()
                    
                    # Verificar duplicados
                    cursor.execute("SELECT id FROM candidatos WHERE cedula = ? AND activo = 1", (cedula,))
                    if cursor.fetchone():
                        results['warnings'].append(f"Fila {index + 2}: Candidato con cédula {cedula} ya existe")
                        continue
                    
                    # Buscar partido
                    partido_id = party_map.get(partido_sigla.upper())
                    if not partido_id:
                        results['errors'].append(f"Fila {index + 2}: Partido con sigla '{partido_sigla}' no encontrado")
                        continue
                    
                    # Buscar cargo
                    cargo_id = cargo_map.get(cargo_nombre)
                    if not cargo_id:
                        results['errors'].append(f"Fila {index + 2}: Cargo '{cargo_nombre}' no encontrado")
                        continue
                    
                    # Buscar municipio (opcional)
                    municipio_id = None
                    if 'municipio_nombre' in df.columns and not pd.isna(row['municipio_nombre']):
                        municipio_nombre = str(row['municipio_nombre']).strip()
                        municipio_id = municipio_map.get(municipio_nombre)
                    
                    # Obtener datos adicionales opcionales
                    telefono = str(row.get('telefono', '')).strip() if not pd.isna(row.get('telefono')) else None
                    email = str(row.get('email', '')).strip() if not pd.isna(row.get('email')) else None
                    numero_lista = None
                    if 'numero_lista' in df.columns and not pd.isna(row['numero_lista']):
                        try:
                            numero_lista = int(row['numero_lista'])
                        except:
                            pass
                    
                    # Crear candidato
                    cursor.execute("""
                        INSERT INTO candidatos 
                        (cedula, nombre_completo, telefono, email, partido_id, cargo_id, 
                         municipio_id, numero_lista, estado, fecha_inscripcion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cedula, nombre_completo, telefono, email, partido_id, cargo_id,
                        municipio_id, numero_lista, 'inscrito', date.today().isoformat()
                    ))
                    
                    candidate_id = cursor.lastrowid
                    results['candidates_created'].append({
                        'id': candidate_id,
                        'cedula': cedula,
                        'nombre': nombre_completo,
                        'partido': partido_sigla,
                        'cargo': cargo_nombre
                    })
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Fila {index + 2}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Importación de candidatos completada: {results['processed']} procesados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error importando candidatos: {e}")
            raise
    
    # ==================== IMPORTACIÓN DE COALICIONES ====================
    
    def import_coalitions_from_excel(self, excel_file_path: str, sheet_name: str = 'Coaliciones') -> Dict:
        """
        Importar coaliciones desde Excel
        Columnas esperadas: nombre, descripcion, partidos_siglas (separadas por coma)
        """
        try:
            results = {
                'total_rows': 0,
                'processed': 0,
                'errors': [],
                'warnings': [],
                'coalitions_created': []
            }
            
            # Leer archivo Excel
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            results['total_rows'] = len(df)
            
            # Validar columnas requeridas
            required_columns = ['nombre', 'partidos_siglas']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas faltantes en Excel: {missing_columns}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear mapa de partidos
            party_map = self._create_party_map(cursor)
            
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos
                    if pd.isna(row['nombre']) or pd.isna(row['partidos_siglas']):
                        results['errors'].append(f"Fila {index + 2}: Nombre y partidos son requeridos")
                        continue
                    
                    nombre = str(row['nombre']).strip()
                    descripcion = str(row.get('descripcion', '')).strip() if not pd.isna(row.get('descripcion')) else None
                    partidos_siglas = str(row['partidos_siglas']).strip()
                    
                    # Verificar duplicados
                    cursor.execute("SELECT id FROM coaliciones WHERE nombre = ?", (nombre,))
                    if cursor.fetchone():
                        results['warnings'].append(f"Fila {index + 2}: Coalición {nombre} ya existe")
                        continue
                    
                    # Procesar siglas de partidos
                    siglas_list = [s.strip().upper() for s in partidos_siglas.split(',')]
                    party_ids = []
                    
                    for sigla in siglas_list:
                        party_id = party_map.get(sigla)
                        if party_id:
                            party_ids.append(party_id)
                        else:
                            results['warnings'].append(f"Fila {index + 2}: Partido con sigla '{sigla}' no encontrado")
                    
                    if not party_ids:
                        results['errors'].append(f"Fila {index + 2}: No se encontraron partidos válidos para la coalición")
                        continue
                    
                    # Crear coalición
                    cursor.execute("""
                        INSERT INTO coaliciones (nombre, descripcion, fecha_conformacion)
                        VALUES (?, ?, ?)
                    """, (nombre, descripcion, date.today().isoformat()))
                    
                    coalition_id = cursor.lastrowid
                    
                    # Agregar partidos a la coalición
                    for party_id in party_ids:
                        cursor.execute("""
                            INSERT INTO coalicion_partidos (coalicion_id, partido_id)
                            VALUES (?, ?)
                        """, (coalition_id, party_id))
                    
                    results['coalitions_created'].append({
                        'id': coalition_id,
                        'nombre': nombre,
                        'partidos_count': len(party_ids)
                    })
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Fila {index + 2}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Importación de coaliciones completada: {results['processed']} procesados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error importando coaliciones: {e}")
            raise
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _create_party_map(self, cursor) -> Dict[str, int]:
        """Crear mapa de siglas de partidos a IDs"""
        cursor.execute("SELECT id, sigla FROM partidos_politicos WHERE activo = 1")
        return {row['sigla'].upper(): row['id'] for row in cursor.fetchall()}
    
    def _create_cargo_map(self, cursor) -> Dict[str, int]:
        """Crear mapa de nombres de cargos a IDs"""
        cursor.execute("SELECT id, nombre FROM cargos_electorales WHERE activo = 1")
        return {row['nombre']: row['id'] for row in cursor.fetchall()}
    
    def _create_municipio_map(self, cursor) -> Dict[str, int]:
        """Crear mapa de nombres de municipios a IDs"""
        cursor.execute("SELECT id, nombre FROM municipios WHERE activo = 1")
        return {row['nombre']: row['id'] for row in cursor.fetchall()}
    
    # ==================== IMPORTACIÓN COMPLETA ====================
    
    def import_all_from_excel(self, excel_file_path: str) -> Dict:
        """
        Importar todos los datos desde un archivo Excel con múltiples hojas
        Orden: Partidos -> Tipos de Elección -> Coaliciones -> Candidatos
        """
        try:
            results = {
                'parties': None,
                'election_types': None,
                'coalitions': None,
                'candidates': None,
                'total_processed': 0,
                'total_errors': 0
            }
            
            # Verificar que el archivo existe
            if not os.path.exists(excel_file_path):
                raise FileNotFoundError(f"Archivo Excel no encontrado: {excel_file_path}")
            
            # Obtener hojas disponibles
            excel_file = pd.ExcelFile(excel_file_path)
            available_sheets = excel_file.sheet_names
            
            # Importar partidos
            if 'Partidos' in available_sheets:
                self.logger.info("Importando partidos...")
                results['parties'] = self.import_parties_from_excel(excel_file_path, 'Partidos')
                results['total_processed'] += results['parties']['processed']
                results['total_errors'] += len(results['parties']['errors'])
            
            # Importar tipos de elección
            if 'TiposEleccion' in available_sheets:
                self.logger.info("Importando tipos de elección...")
                results['election_types'] = self.import_election_types_from_excel(excel_file_path, 'TiposEleccion')
                results['total_processed'] += results['election_types']['processed']
                results['total_errors'] += len(results['election_types']['errors'])
            
            # Importar coaliciones
            if 'Coaliciones' in available_sheets:
                self.logger.info("Importando coaliciones...")
                results['coalitions'] = self.import_coalitions_from_excel(excel_file_path, 'Coaliciones')
                results['total_processed'] += results['coalitions']['processed']
                results['total_errors'] += len(results['coalitions']['errors'])
            
            # Importar candidatos
            if 'Candidatos' in available_sheets:
                self.logger.info("Importando candidatos...")
                results['candidates'] = self.import_candidates_from_excel(excel_file_path, 'Candidatos')
                results['total_processed'] += results['candidates']['processed']
                results['total_errors'] += len(results['candidates']['errors'])
            
            self.logger.info(f"Importación completa: {results['total_processed']} registros procesados, {results['total_errors']} errores")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en importación completa: {e}")
            raise
    
    def validate_excel_structure(self, excel_file_path: str) -> Dict:
        """Validar estructura del archivo Excel antes de importar"""
        try:
            validation_results = {
                'valid': True,
                'sheets_found': [],
                'sheets_missing': [],
                'column_validation': {},
                'errors': []
            }
            
            if not os.path.exists(excel_file_path):
                validation_results['valid'] = False
                validation_results['errors'].append("Archivo Excel no encontrado")
                return validation_results
            
            excel_file = pd.ExcelFile(excel_file_path)
            available_sheets = excel_file.sheet_names
            validation_results['sheets_found'] = available_sheets
            
            # Definir estructura esperada
            expected_structure = {
                'Partidos': ['nombre', 'sigla'],
                'TiposEleccion': ['nombre', 'nivel'],
                'Coaliciones': ['nombre', 'partidos_siglas'],
                'Candidatos': ['cedula', 'nombre_completo', 'partido_sigla', 'cargo_nombre']
            }
            
            # Validar cada hoja
            for sheet_name, required_columns in expected_structure.items():
                if sheet_name in available_sheets:
                    try:
                        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, nrows=0)  # Solo headers
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        
                        validation_results['column_validation'][sheet_name] = {
                            'found_columns': list(df.columns),
                            'missing_columns': missing_columns,
                            'valid': len(missing_columns) == 0
                        }
                        
                        if missing_columns:
                            validation_results['valid'] = False
                            validation_results['errors'].append(f"Hoja '{sheet_name}': columnas faltantes {missing_columns}")
                    
                    except Exception as e:
                        validation_results['valid'] = False
                        validation_results['errors'].append(f"Error leyendo hoja '{sheet_name}': {str(e)}")
                else:
                    validation_results['sheets_missing'].append(sheet_name)
            
            return validation_results
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Error validando archivo: {str(e)}"],
                'sheets_found': [],
                'sheets_missing': [],
                'column_validation': {}
            }