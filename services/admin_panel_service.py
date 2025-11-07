#!/usr/bin/env python3
"""
AdminPanelService - Servicio principal para el panel de administración
Gestión de candidatos, partidos, coaliciones, procesos electorales y configuración del sistema
"""

import sqlite3
import csv
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import os
import logging

class AdminPanelService:
    """Servicio principal para el panel de administración electoral"""
    
    def __init__(self, db_path: str = 'caqueta_electoral.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # ==================== GESTIÓN DE CANDIDATOS ====================
    
    def get_all_candidates(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Obtener todos los candidatos con filtros opcionales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT c.*, 
                       p.nombre as partido_nombre, p.sigla as partido_sigla, p.color_principal as partido_color,
                       coal.nombre as coalicion_nombre,
                       car.nombre as cargo_nombre, car.nivel as cargo_nivel,
                       m.nombre as municipio_nombre, m.codigo as municipio_codigo
                FROM candidatos c
                LEFT JOIN partidos_politicos p ON c.partido_id = p.id
                LEFT JOIN coaliciones coal ON c.coalicion_id = coal.id
                LEFT JOIN cargos_electorales car ON c.cargo_id = car.id
                LEFT JOIN municipios m ON c.municipio_id = m.id
                WHERE c.activo = 1
            """
            
            params = []
            
            # Aplicar filtros
            if filters:
                if filters.get('partido_id'):
                    query += " AND c.partido_id = ?"
                    params.append(filters['partido_id'])
                
                if filters.get('cargo_id'):
                    query += " AND c.cargo_id = ?"
                    params.append(filters['cargo_id'])
                
                if filters.get('municipio_id'):
                    query += " AND c.municipio_id = ?"
                    params.append(filters['municipio_id'])
                
                if filters.get('estado'):
                    query += " AND c.estado = ?"
                    params.append(filters['estado'])
                
                if filters.get('search'):
                    query += " AND (c.nombre_completo LIKE ? OR c.cedula LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term])
            
            query += " ORDER BY c.nombre_completo"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            candidates = []
            for row in results:
                candidate = dict(row)
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error obteniendo candidatos: {e}")
            raise
    
    def create_candidate(self, candidate_data: Dict) -> int:
        """Crear nuevo candidato"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validar datos requeridos
            required_fields = ['cedula', 'nombre_completo', 'cargo_id']
            for field in required_fields:
                if not candidate_data.get(field):
                    raise ValueError(f"Campo requerido: {field}")
            
            # Verificar que no exista candidato con la misma cédula
            cursor.execute("SELECT id FROM candidatos WHERE cedula = ? AND activo = 1", 
                          (candidate_data['cedula'],))
            if cursor.fetchone():
                raise ValueError("Ya existe un candidato con esta cédula")
            
            query = """
                INSERT INTO candidatos 
                (cedula, nombre_completo, fecha_nacimiento, lugar_nacimiento, profesion,
                 telefono, email, direccion, foto_url, hoja_vida_url, partido_id, coalicion_id,
                 cargo_id, municipio_id, numero_lista, estado, observaciones, fecha_inscripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                candidate_data['cedula'],
                candidate_data['nombre_completo'],
                candidate_data.get('fecha_nacimiento'),
                candidate_data.get('lugar_nacimiento'),
                candidate_data.get('profesion'),
                candidate_data.get('telefono'),
                candidate_data.get('email'),
                candidate_data.get('direccion'),
                candidate_data.get('foto_url'),
                candidate_data.get('hoja_vida_url'),
                candidate_data.get('partido_id'),
                candidate_data.get('coalicion_id'),
                candidate_data['cargo_id'],
                candidate_data.get('municipio_id'),
                candidate_data.get('numero_lista'),
                candidate_data.get('estado', 'inscrito'),
                candidate_data.get('observaciones'),
                candidate_data.get('fecha_inscripcion', date.today().isoformat())
            ))
            
            candidate_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Candidato creado: {candidate_id} - {candidate_data['nombre_completo']}")
            return candidate_id
            
        except Exception as e:
            self.logger.error(f"Error creando candidato: {e}")
            raise
    
    def update_candidate(self, candidate_id: int, candidate_data: Dict) -> bool:
        """Actualizar candidato existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Verificar que el candidato existe
            cursor.execute("SELECT id FROM candidatos WHERE id = ? AND activo = 1", (candidate_id,))
            if not cursor.fetchone():
                raise ValueError("Candidato no encontrado")
            
            # Si se está cambiando la cédula, verificar que no exista otra
            if 'cedula' in candidate_data:
                cursor.execute("SELECT id FROM candidatos WHERE cedula = ? AND id != ? AND activo = 1", 
                              (candidate_data['cedula'], candidate_id))
                if cursor.fetchone():
                    raise ValueError("Ya existe otro candidato con esta cédula")
            
            # Construir query de actualización dinámicamente
            update_fields = []
            params = []
            
            updatable_fields = [
                'cedula', 'nombre_completo', 'fecha_nacimiento', 'lugar_nacimiento', 'profesion',
                'telefono', 'email', 'direccion', 'foto_url', 'hoja_vida_url', 'partido_id',
                'coalicion_id', 'cargo_id', 'municipio_id', 'numero_lista', 'estado', 'observaciones'
            ]
            
            for field in updatable_fields:
                if field in candidate_data:
                    update_fields.append(f"{field} = ?")
                    params.append(candidate_data[field])
            
            if not update_fields:
                return True  # No hay nada que actualizar
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(candidate_id)
            
            query = f"UPDATE candidatos SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Candidato actualizado: {candidate_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando candidato: {e}")
            raise
    
    def delete_candidate(self, candidate_id: int) -> bool:
        """Eliminar candidato (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE candidatos 
                SET activo = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (candidate_id,))
            
            if cursor.rowcount == 0:
                raise ValueError("Candidato no encontrado")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Candidato eliminado: {candidate_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error eliminando candidato: {e}")
            raise
    
    def bulk_import_candidates(self, csv_file_path: str, validate_only: bool = False) -> Dict:
        """Importar candidatos desde archivo CSV"""
        try:
            results = {
                'total_rows': 0,
                'processed': 0,
                'errors': [],
                'warnings': [],
                'candidates_created': []
            }
            
            if not os.path.exists(csv_file_path):
                raise FileNotFoundError("Archivo CSV no encontrado")
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # Validar headers requeridos
                required_headers = ['cedula', 'nombre_completo', 'cargo_id']
                missing_headers = [h for h in required_headers if h not in csv_reader.fieldnames]
                if missing_headers:
                    raise ValueError(f"Headers faltantes en CSV: {missing_headers}")
                
                conn = self.get_connection()
                cursor = conn.cursor()
                
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                    results['total_rows'] += 1
                    
                    try:
                        # Validar datos básicos
                        if not row.get('cedula') or not row.get('nombre_completo'):
                            results['errors'].append(f"Fila {row_num}: Cédula y nombre son requeridos")
                            continue
                        
                        # Verificar duplicados
                        cursor.execute("SELECT id FROM candidatos WHERE cedula = ? AND activo = 1", 
                                      (row['cedula'],))
                        if cursor.fetchone():
                            results['warnings'].append(f"Fila {row_num}: Candidato con cédula {row['cedula']} ya existe")
                            continue
                        
                        if not validate_only:
                            # Crear candidato
                            candidate_data = {
                                'cedula': row['cedula'],
                                'nombre_completo': row['nombre_completo'],
                                'fecha_nacimiento': row.get('fecha_nacimiento') or None,
                                'lugar_nacimiento': row.get('lugar_nacimiento') or None,
                                'profesion': row.get('profesion') or None,
                                'telefono': row.get('telefono') or None,
                                'email': row.get('email') or None,
                                'direccion': row.get('direccion') or None,
                                'partido_id': int(row['partido_id']) if row.get('partido_id') else None,
                                'cargo_id': int(row['cargo_id']) if row.get('cargo_id') else None,
                                'municipio_id': int(row['municipio_id']) if row.get('municipio_id') else None,
                                'numero_lista': int(row['numero_lista']) if row.get('numero_lista') else None,
                                'estado': row.get('estado', 'inscrito'),
                                'observaciones': row.get('observaciones') or None
                            }
                            
                            candidate_id = self.create_candidate(candidate_data)
                            results['candidates_created'].append({
                                'id': candidate_id,
                                'cedula': row['cedula'],
                                'nombre': row['nombre_completo']
                            })
                        
                        results['processed'] += 1
                        
                    except Exception as e:
                        results['errors'].append(f"Fila {row_num}: {str(e)}")
                
                conn.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en importación masiva: {e}")
            raise
    
    # ==================== GESTIÓN DE PARTIDOS POLÍTICOS ====================
    
    def get_all_parties(self) -> List[Dict]:
        """Obtener todos los partidos políticos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, 
                       COUNT(c.id) as total_candidatos
                FROM partidos_politicos p
                LEFT JOIN candidatos c ON p.id = c.partido_id AND c.activo = 1
                WHERE p.activo = 1
                GROUP BY p.id
                ORDER BY p.nombre
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            parties = [dict(row) for row in results]
            return parties
            
        except Exception as e:
            self.logger.error(f"Error obteniendo partidos: {e}")
            raise
    
    def create_party(self, party_data: Dict) -> int:
        """Crear nuevo partido político"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validar datos requeridos
            if not party_data.get('nombre') or not party_data.get('sigla'):
                raise ValueError("Nombre y sigla son requeridos")
            
            # Verificar unicidad
            cursor.execute("SELECT id FROM partidos_politicos WHERE nombre = ? OR sigla = ?", 
                          (party_data['nombre'], party_data['sigla']))
            if cursor.fetchone():
                raise ValueError("Ya existe un partido con ese nombre o sigla")
            
            query = """
                INSERT INTO partidos_politicos 
                (nombre, sigla, color_principal, logo_url, representante_legal, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                party_data['nombre'],
                party_data['sigla'],
                party_data.get('color_principal', '#007bff'),
                party_data.get('logo_url'),
                party_data.get('representante_legal'),
                party_data.get('telefono'),
                party_data.get('email'),
                party_data.get('direccion')
            ))
            
            party_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Partido creado: {party_id} - {party_data['nombre']}")
            return party_id
            
        except Exception as e:
            self.logger.error(f"Error creando partido: {e}")
            raise
    
    # ==================== GESTIÓN DE COALICIONES ====================
    
    def get_all_coalitions(self) -> List[Dict]:
        """Obtener todas las coaliciones"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT coal.*, 
                       COUNT(DISTINCT cp.partido_id) as total_partidos,
                       COUNT(DISTINCT c.id) as total_candidatos,
                       GROUP_CONCAT(p.sigla, ', ') as partidos_siglas
                FROM coaliciones coal
                LEFT JOIN coalicion_partidos cp ON coal.id = cp.coalicion_id AND cp.activo = 1
                LEFT JOIN partidos_politicos p ON cp.partido_id = p.id
                LEFT JOIN candidatos c ON coal.id = c.coalicion_id AND c.activo = 1
                WHERE coal.activa = 1
                GROUP BY coal.id
                ORDER BY coal.nombre
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            coalitions = [dict(row) for row in results]
            return coalitions
            
        except Exception as e:
            self.logger.error(f"Error obteniendo coaliciones: {e}")
            raise
    
    def create_coalition(self, coalition_data: Dict, party_ids: List[int] = None) -> int:
        """Crear nueva coalición"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Validar datos requeridos
            if not coalition_data.get('nombre'):
                raise ValueError("Nombre es requerido")
            
            # Verificar unicidad
            cursor.execute("SELECT id FROM coaliciones WHERE nombre = ?", (coalition_data['nombre'],))
            if cursor.fetchone():
                raise ValueError("Ya existe una coalición con ese nombre")
            
            # Crear coalición
            query = """
                INSERT INTO coaliciones (nombre, descripcion, fecha_conformacion)
                VALUES (?, ?, ?)
            """
            
            cursor.execute(query, (
                coalition_data['nombre'],
                coalition_data.get('descripcion'),
                coalition_data.get('fecha_conformacion', date.today().isoformat())
            ))
            
            coalition_id = cursor.lastrowid
            
            # Agregar partidos a la coalición
            if party_ids:
                for party_id in party_ids:
                    cursor.execute("""
                        INSERT INTO coalicion_partidos (coalicion_id, partido_id)
                        VALUES (?, ?)
                    """, (coalition_id, party_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Coalición creada: {coalition_id} - {coalition_data['nombre']}")
            return coalition_id
            
        except Exception as e:
            self.logger.error(f"Error creando coalición: {e}")
            raise
    
    # ==================== GESTIÓN DE JORNADAS ELECTORALES ====================
    
    def create_electoral_journey(self, journey_data: Dict, election_types: List[Dict]) -> int:
        """Crear jornada electoral con múltiples elecciones simultáneas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Crear proceso electoral principal
            query = """
                INSERT INTO procesos_electorales 
                (nombre, descripcion, tipo, fecha_inicio, fecha_fin, fecha_eleccion, estado, municipio_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                journey_data['nombre'],
                journey_data.get('descripcion'),
                'multiple',  # Tipo especial para jornadas con múltiples elecciones
                journey_data['fecha_inicio'],
                journey_data['fecha_fin'],
                journey_data['fecha_eleccion'],
                journey_data.get('estado', 'configuracion'),
                journey_data.get('municipio_id')
            ))
            
            journey_id = cursor.lastrowid
            
            # Crear procesos específicos para cada tipo de elección
            for election_type in election_types:
                cursor.execute("""
                    INSERT INTO procesos_electorales 
                    (nombre, descripcion, tipo, fecha_inicio, fecha_fin, fecha_eleccion, 
                     estado, municipio_id, proceso_padre_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{journey_data['nombre']} - {election_type['nombre']}",
                    election_type.get('descripcion'),
                    election_type['tipo'],
                    journey_data['fecha_inicio'],
                    journey_data['fecha_fin'],
                    journey_data['fecha_eleccion'],
                    'configuracion',
                    journey_data.get('municipio_id'),
                    journey_id
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Jornada electoral creada: {journey_id} - {journey_data['nombre']}")
            return journey_id
            
        except Exception as e:
            self.logger.error(f"Error creando jornada electoral: {e}")
            raise
    
    # ==================== CONFIGURACIÓN DEL SISTEMA ====================
    
    def get_system_configuration(self, category: str = None) -> Dict:
        """Obtener configuración del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM configuracion_sistema WHERE 1=1"
            params = []
            
            if category:
                query += " AND categoria = ?"
                params.append(category)
            
            query += " ORDER BY categoria, clave"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            config = {}
            for row in results:
                row_dict = dict(row)
                if row_dict['categoria'] not in config:
                    config[row_dict['categoria']] = {}
                
                # Convertir valor según tipo
                value = row_dict['valor']
                if row_dict['tipo'] == 'number':
                    value = float(value) if '.' in value else int(value)
                elif row_dict['tipo'] == 'boolean':
                    value = value.lower() in ('true', '1', 'yes')
                elif row_dict['tipo'] == 'json':
                    value = json.loads(value)
                
                config[row_dict['categoria']][row_dict['clave']] = {
                    'value': value,
                    'description': row_dict['descripcion'],
                    'type': row_dict['tipo']
                }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración: {e}")
            raise
    
    def update_system_configuration(self, config_updates: Dict, user_id: int = None) -> bool:
        """Actualizar configuración del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for key, value in config_updates.items():
                # Convertir valor a string para almacenamiento
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value)
                elif isinstance(value, bool):
                    value_str = 'true' if value else 'false'
                else:
                    value_str = str(value)
                
                cursor.execute("""
                    UPDATE configuracion_sistema 
                    SET valor = ?, modificado_por = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE clave = ?
                """, (value_str, user_id, key))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Configuración actualizada: {list(config_updates.keys())}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
            raise
    
    # ==================== ESTADÍSTICAS Y REPORTES ====================
    
    def get_system_statistics(self) -> Dict:
        """Obtener estadísticas generales del sistema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Estadísticas de candidatos
            cursor.execute("SELECT COUNT(*) FROM candidatos WHERE activo = 1")
            stats['total_candidatos'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT estado, COUNT(*) as count 
                FROM candidatos WHERE activo = 1 
                GROUP BY estado
            """)
            stats['candidatos_por_estado'] = dict(cursor.fetchall())
            
            # Estadísticas de partidos
            cursor.execute("SELECT COUNT(*) FROM partidos_politicos WHERE activo = 1")
            stats['total_partidos'] = cursor.fetchone()[0]
            
            # Estadísticas de coaliciones
            cursor.execute("SELECT COUNT(*) FROM coaliciones WHERE activa = 1")
            stats['total_coaliciones'] = cursor.fetchone()[0]
            
            # Estadísticas de procesos electorales
            cursor.execute("SELECT COUNT(*) FROM procesos_electorales WHERE activo = 1")
            stats['total_procesos'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT estado, COUNT(*) as count 
                FROM procesos_electorales WHERE activo = 1 
                GROUP BY estado
            """)
            stats['procesos_por_estado'] = dict(cursor.fetchall())
            
            # Estadísticas de usuarios
            cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
            stats['total_usuarios'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT rol, COUNT(*) as count 
                FROM users WHERE activo = 1 
                GROUP BY rol
            """)
            stats['usuarios_por_rol'] = dict(cursor.fetchall())
            
            conn.close()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            raise
    
    def generate_admin_report(self, report_type: str, filters: Dict = None) -> Dict:
        """Generar reportes administrativos"""
        try:
            if report_type == 'candidates_summary':
                return self._generate_candidates_summary_report(filters)
            elif report_type == 'parties_summary':
                return self._generate_parties_summary_report(filters)
            elif report_type == 'system_overview':
                return self._generate_system_overview_report()
            else:
                raise ValueError(f"Tipo de reporte no válido: {report_type}")
                
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            raise
    
    def _generate_candidates_summary_report(self, filters: Dict = None) -> Dict:
        """Generar reporte resumen de candidatos"""
        candidates = self.get_all_candidates(filters)
        
        report = {
            'title': 'Reporte Resumen de Candidatos',
            'generated_at': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'summary_by_party': {},
            'summary_by_position': {},
            'summary_by_status': {},
            'candidates': candidates
        }
        
        # Agrupar por partido
        for candidate in candidates:
            party = candidate.get('partido_nombre', 'Sin partido')
            if party not in report['summary_by_party']:
                report['summary_by_party'][party] = 0
            report['summary_by_party'][party] += 1
        
        # Agrupar por cargo
        for candidate in candidates:
            position = candidate.get('cargo_nombre', 'Sin cargo')
            if position not in report['summary_by_position']:
                report['summary_by_position'][position] = 0
            report['summary_by_position'][position] += 1
        
        # Agrupar por estado
        for candidate in candidates:
            status = candidate.get('estado', 'Sin estado')
            if status not in report['summary_by_status']:
                report['summary_by_status'][status] = 0
            report['summary_by_status'][status] += 1
        
        return report
    
    def _generate_parties_summary_report(self, filters: Dict = None) -> Dict:
        """Generar reporte resumen de partidos"""
        parties = self.get_all_parties()
        
        report = {
            'title': 'Reporte Resumen de Partidos Políticos',
            'generated_at': datetime.now().isoformat(),
            'total_parties': len(parties),
            'parties': parties,
            'total_candidates_by_party': sum(p.get('total_candidatos', 0) for p in parties)
        }
        
        return report
    
    def _generate_system_overview_report(self) -> Dict:
        """Generar reporte general del sistema"""
        stats = self.get_system_statistics()
        config = self.get_system_configuration()
        
        report = {
            'title': 'Reporte General del Sistema',
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'system_configuration': config.get('general', {}),
            'electoral_configuration': config.get('electoral', {}),
            'system_health': {
                'database_status': 'ok',
                'last_backup': 'N/A',
                'disk_usage': 'N/A'
            }
        }
        
        return report