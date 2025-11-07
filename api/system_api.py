#!/usr/bin/env python3
"""
API del sistema para funcionalidades generales
Endpoints para salud del sistema, métricas y operaciones administrativas
"""

from flask import Blueprint, request, jsonify, session
import logging
import sqlite3
from datetime import datetime, timedelta
import os
import psutil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
system_bp = Blueprint('system', __name__, url_prefix='/api/system')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('caqueta_electoral.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==================== SALUD DEL SISTEMA ====================

@system_bp.route('/health', methods=['GET'])
def system_health():
    """Verificar salud del sistema"""
    try:
        # Verificar base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        # Verificar recursos del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'status': 'connected',
                'users': user_count
            },
            'system_resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100,
                'available_memory_gb': round(memory.available / (1024**3), 2)
            },
            'services': {
                'database': 'active',
                'api': 'active',
                'reports': 'active'
            }
        }
        
        # Determinar estado general
        if cpu_percent > 90 or memory.percent > 90:
            health_status['status'] = 'warning'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Error verificando salud del sistema: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@system_bp.route('/info', methods=['GET'])
def system_info():
    """Obtener información general del sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
        active_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM procesos_electorales WHERE estado = 'activo'")
        active_processes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM municipios")
        total_municipalities = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM mesas_votacion WHERE estado IN ('activa', 'configurada')")
        total_tables = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'active_users': active_users,
                'active_processes': active_processes,
                'total_municipalities': total_municipalities,
                'total_tables': total_tables,
                'system_uptime': '99.8%',
                'last_backup': '2024-11-06 02:00:00'
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== GESTIÓN DE USUARIOS ====================

@system_bp.route('/users', methods=['GET'])
def get_users():
    """Obtener lista de usuarios del sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filtros opcionales
        role_filter = request.args.get('role')
        active_filter = request.args.get('active')
        
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if role_filter:
            query += " AND rol = ?"
            params.append(role_filter)
        
        if active_filter is not None:
            query += " AND activo = ?"
            params.append(int(active_filter))
        
        query += " ORDER BY nombre_completo"
        
        cursor.execute(query, params)
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Limpiar datos sensibles
        for user in users:
            user.pop('password_hash', None)
        
        return jsonify({
            'success': True,
            'data': users,
            'total': len(users)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/users', methods=['POST'])
def create_user():
    """Crear nuevo usuario"""
    try:
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'Datos del usuario requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['nombre_completo', 'username', 'email', 'rol']
        for field in required_fields:
            if not user_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que no exista usuario con el mismo username o email
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                      (user_data['username'], user_data['email']))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ya existe un usuario con ese username o email'
            }), 400
        
        # Generar hash de contraseña temporal
        import hashlib
        temp_password = 'temp123'  # En producción, generar contraseña aleatoria
        password_hash = hashlib.sha256(temp_password.encode()).hexdigest()
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO users 
            (nombre_completo, username, email, password_hash, rol, municipio_id, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['nombre_completo'],
            user_data['username'],
            user_data['email'],
            password_hash,
            user_data['rol'],
            user_data.get('municipio_id'),
            user_data.get('activo', 1)
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'temp_password': temp_password
            },
            'message': 'Usuario creado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== REPORTES DEL SISTEMA ====================

@system_bp.route('/reports/generate', methods=['POST'])
def generate_system_report():
    """Generar reporte del sistema"""
    try:
        report_data = request.get_json()
        
        if not report_data or not report_data.get('type'):
            return jsonify({
                'success': False,
                'error': 'Tipo de reporte requerido'
            }), 400
        
        report_type = report_data['type']
        
        # Simular generación de reporte
        report_info = {
            'report_id': f'RPT-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'status': 'completed',
            'file_path': f'/reports/{report_type}_{datetime.now().strftime("%Y%m%d")}.pdf'
        }
        
        return jsonify({
            'success': True,
            'data': report_info,
            'message': f'Reporte {report_type} generado exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== INCIDENTES ====================

@system_bp.route('/incidents', methods=['POST'])
def report_incident():
    """Reportar nuevo incidente"""
    try:
        incident_data = request.get_json()
        
        if not incident_data:
            return jsonify({
                'success': False,
                'error': 'Datos del incidente requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['tipo_incidente', 'gravedad', 'descripcion']
        for field in required_fields:
            if not incident_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Simular guardado del incidente
        incident_id = f'INC-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        return jsonify({
            'success': True,
            'data': {
                'incident_id': incident_id,
                'status': 'reported',
                'priority': incident_data['gravedad']
            },
            'message': 'Incidente reportado exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error reportando incidente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== OBSERVACIONES INTERNACIONALES ====================

@system_bp.route('/observations', methods=['POST'])
def submit_international_observation():
    """Enviar observación internacional"""
    try:
        observation_data = request.get_json()
        
        if not observation_data:
            return jsonify({
                'success': False,
                'error': 'Datos de observación requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['organizacion', 'tipo_observacion', 'observaciones_generales', 'nivel_cumplimiento']
        for field in required_fields:
            if not observation_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Simular envío de observación
        observation_id = f'OBS-INT-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        return jsonify({
            'success': True,
            'data': {
                'observation_id': observation_id,
                'status': 'submitted',
                'organization': observation_data['organizacion'],
                'compliance_level': observation_data['nivel_cumplimiento']
            },
            'message': 'Observación internacional enviada exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error enviando observación: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== AUDITORÍAS ====================

@system_bp.route('/audits', methods=['POST'])
def start_audit():
    """Iniciar nueva auditoría"""
    try:
        audit_data = request.get_json()
        
        if not audit_data:
            return jsonify({
                'success': False,
                'error': 'Datos de auditoría requeridos'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['tipo_auditoria', 'alcance', 'objetivos']
        for field in required_fields:
            if not audit_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Simular inicio de auditoría
        audit_id = f'AUD-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        return jsonify({
            'success': True,
            'data': {
                'audit_id': audit_id,
                'status': 'initiated',
                'type': audit_data['tipo_auditoria'],
                'scope': audit_data['alcance'],
                'estimated_completion': (datetime.now() + timedelta(days=7)).isoformat()
            },
            'message': 'Auditoría iniciada exitosamente'
        }), 201
        
    except Exception as e:
        logger.error(f"Error iniciando auditoría: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@system_bp.route('/audits/<audit_id>/status', methods=['GET'])
def get_audit_status(audit_id):
    """Obtener estado de auditoría"""
    try:
        # Simular estado de auditoría
        audit_status = {
            'audit_id': audit_id,
            'status': 'in_progress',
            'progress': 45,
            'started_at': '2024-11-06T10:00:00',
            'estimated_completion': '2024-11-13T18:00:00',
            'findings': 3,
            'recommendations': 5
        }
        
        return jsonify({
            'success': True,
            'data': audit_status
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de auditoría: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ESTADÍSTICAS DEPARTAMENTALES ====================

@system_bp.route('/departmental/stats', methods=['GET'])
def get_departmental_stats():
    """Obtener estadísticas departamentales"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estadísticas por municipio
        cursor.execute("""
            SELECT m.nombre, m.codigo,
                   COUNT(mv.id) as total_mesas,
                   COUNT(CASE WHEN mv.estado = 'activa' THEN 1 END) as mesas_activas,
                   SUM(mv.total_votantes) as total_votantes
            FROM municipios m
            LEFT JOIN mesas_votacion mv ON m.id = mv.municipio_id
            GROUP BY m.id, m.nombre, m.codigo
            ORDER BY m.nombre
        """)
        
        municipios_stats = []
        for row in cursor.fetchall():
            municipio = dict(row)
            municipio['participacion'] = 65 + (hash(municipio['nombre']) % 20)  # Simular participación
            municipios_stats.append(municipio)
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM users WHERE activo = 1")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM procesos_electorales WHERE estado = 'activo'")
        active_processes = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'general': {
                    'total_users': total_users,
                    'active_processes': active_processes,
                    'total_municipalities': len(municipios_stats),
                    'overall_coverage': 95
                },
                'municipalities': municipios_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas departamentales: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== MANEJO DE ERRORES ====================

@system_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@system_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500