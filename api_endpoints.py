#!/usr/bin/env python3
"""
APIs RESTful para el Sistema Electoral ERP
"""

from flask import request, jsonify, current_app
import sqlite3
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

class DatabaseManager:
    """Gestor de base de datos para las APIs"""
    
    @staticmethod
    def get_connection():
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect('caqueta_electoral.db')
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        return conn
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """Ejecutar query de forma segura"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

def register_api_routes(app):
    """Registrar todas las rutas de API"""
    
    # ==================== OBSERVACIONES API ====================
    
    @app.route('/api/observaciones', methods=['GET'])
    def get_observaciones():
        """Obtener observaciones con filtros opcionales"""
        try:
            testigo_id = request.args.get('testigo_id')
            mesa_id = request.args.get('mesa_id')
            fecha_desde = request.args.get('fecha_desde')
            fecha_hasta = request.args.get('fecha_hasta')
            
            query = """
                SELECT o.*, u.nombre_completo as testigo_nombre, 
                       m.numero as mesa_numero, p.nombre as puesto_nombre
                FROM observaciones o
                LEFT JOIN users u ON o.testigo_id = u.id
                LEFT JOIN mesas_votacion m ON o.mesa_id = m.id
                LEFT JOIN puestos_votacion p ON o.puesto_id = p.id
                WHERE 1=1
            """
            params = []
            
            if testigo_id:
                query += " AND o.testigo_id = ?"
                params.append(testigo_id)
            
            if mesa_id:
                query += " AND o.mesa_id = ?"
                params.append(mesa_id)
            
            if fecha_desde:
                query += " AND DATE(o.fecha_hora) >= ?"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND DATE(o.fecha_hora) <= ?"
                params.append(fecha_hasta)
            
            query += " ORDER BY o.fecha_hora DESC"
            
            observaciones = DatabaseManager.execute_query(query, params, fetch_all=True)
            
            return jsonify({
                'success': True,
                'data': observaciones,
                'total': len(observaciones)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/observaciones', methods=['POST'])
    def create_observacion():
        """Crear nueva observación"""
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['testigo_id', 'tipo_observacion', 'descripcion']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
            
            # Insertar observación
            query = """
                INSERT INTO observaciones 
                (testigo_id, mesa_id, puesto_id, tipo_observacion, descripcion, 
                 evidencia_fotos, ubicacion_gps_lat, ubicacion_gps_lng, severidad, calificacion_proceso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data['testigo_id'],
                data.get('mesa_id'),
                data.get('puesto_id'),
                data['tipo_observacion'],
                data['descripcion'],
                json.dumps(data.get('evidencia_fotos', [])),
                data.get('ubicacion_gps_lat'),
                data.get('ubicacion_gps_lng'),
                data.get('severidad', 'normal'),
                data.get('calificacion_proceso')
            )
            
            observacion_id = DatabaseManager.execute_query(query, params)
            
            # Crear notificación para supervisores si es necesario
            if data.get('severidad') in ['alta', 'critica']:
                create_notification_for_supervisors(
                    f"Nueva observación {data.get('severidad')}",
                    f"Se ha registrado una observación de severidad {data.get('severidad')} en {data.get('tipo_observacion')}",
                    'observacion_critica'
                )
            
            return jsonify({
                'success': True,
                'message': 'Observación registrada exitosamente',
                'observacion_id': observacion_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== INCIDENCIAS API ====================
    
    @app.route('/api/incidencias', methods=['GET'])
    def get_incidencias():
        """Obtener incidencias con filtros"""
        try:
            estado = request.args.get('estado')
            severidad = request.args.get('severidad')
            puesto_id = request.args.get('puesto_id')
            
            query = """
                SELECT i.*, u.nombre_completo as reportado_por_nombre,
                       ur.nombre_completo as resuelto_por_nombre,
                       m.numero as mesa_numero, p.nombre as puesto_nombre
                FROM incidencias i
                LEFT JOIN users u ON i.reportado_por = u.id
                LEFT JOIN users ur ON i.resuelto_por = ur.id
                LEFT JOIN mesas_votacion m ON i.mesa_id = m.id
                LEFT JOIN puestos_votacion p ON i.puesto_id = p.id
                WHERE 1=1
            """
            params = []
            
            if estado:
                query += " AND i.estado = ?"
                params.append(estado)
            
            if severidad:
                query += " AND i.severidad = ?"
                params.append(severidad)
            
            if puesto_id:
                query += " AND i.puesto_id = ?"
                params.append(puesto_id)
            
            query += " ORDER BY i.fecha_hora DESC"
            
            incidencias = DatabaseManager.execute_query(query, params, fetch_all=True)
            
            return jsonify({
                'success': True,
                'data': incidencias,
                'total': len(incidencias)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/incidencias', methods=['POST'])
    def create_incidencia():
        """Crear nueva incidencia"""
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['reportado_por', 'tipo_incidencia', 'descripcion', 'severidad']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
            
            # Insertar incidencia
            query = """
                INSERT INTO incidencias 
                (reportado_por, mesa_id, puesto_id, tipo_incidencia, descripcion, severidad,
                 evidencia_fotos, ubicacion_gps_lat, ubicacion_gps_lng)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data['reportado_por'],
                data.get('mesa_id'),
                data.get('puesto_id'),
                data['tipo_incidencia'],
                data['descripcion'],
                data['severidad'],
                json.dumps(data.get('evidencia_fotos', [])),
                data.get('ubicacion_gps_lat'),
                data.get('ubicacion_gps_lng')
            )
            
            incidencia_id = DatabaseManager.execute_query(query, params)
            
            # Crear notificación urgente para coordinadores
            if data.get('severidad') in ['alta', 'critica']:
                create_notification_for_coordinators(
                    f"Incidencia {data.get('severidad')} reportada",
                    f"Se ha reportado una incidencia de tipo {data.get('tipo_incidencia')} con severidad {data.get('severidad')}",
                    'incidencia_critica',
                    data.get('puesto_id')
                )
            
            return jsonify({
                'success': True,
                'message': 'Incidencia registrada exitosamente',
                'incidencia_id': incidencia_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== PERSONAL API ====================
    
    @app.route('/api/personal/asignaciones', methods=['GET'])
    def get_asignaciones_personal():
        """Obtener asignaciones de personal"""
        try:
            puesto_id = request.args.get('puesto_id')
            fecha = request.args.get('fecha')
            
            query = """
                SELECT a.*, u.nombre_completo, u.cedula, u.telefono,
                       p.nombre as puesto_nombre, m.numero as mesa_numero,
                       ua.nombre_completo as asignado_por_nombre
                FROM asignaciones_personal a
                LEFT JOIN users u ON a.usuario_id = u.id
                LEFT JOIN puestos_votacion p ON a.puesto_id = p.id
                LEFT JOIN mesas_votacion m ON a.mesa_id = m.id
                LEFT JOIN users ua ON a.asignado_por = ua.id
                WHERE a.estado = 'asignado'
            """
            params = []
            
            if puesto_id:
                query += " AND a.puesto_id = ?"
                params.append(puesto_id)
            
            if fecha:
                query += " AND a.fecha_asignacion = ?"
                params.append(fecha)
            
            query += " ORDER BY a.fecha_asignacion DESC, a.puesto_id, a.mesa_id"
            
            asignaciones = DatabaseManager.execute_query(query, params, fetch_all=True)
            
            return jsonify({
                'success': True,
                'data': asignaciones,
                'total': len(asignaciones)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/personal/asignaciones', methods=['POST'])
    def create_asignacion_personal():
        """Crear nueva asignación de personal"""
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['usuario_id', 'rol_asignado', 'fecha_asignacion', 'asignado_por']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
            
            # Verificar que el usuario no esté ya asignado en la misma fecha
            check_query = """
                SELECT id FROM asignaciones_personal 
                WHERE usuario_id = ? AND fecha_asignacion = ? AND estado = 'asignado'
            """
            existing = DatabaseManager.execute_query(
                check_query, 
                (data['usuario_id'], data['fecha_asignacion']), 
                fetch_one=True
            )
            
            if existing:
                return jsonify({
                    'success': False, 
                    'error': 'El usuario ya tiene una asignación para esta fecha'
                }), 400
            
            # Insertar asignación
            query = """
                INSERT INTO asignaciones_personal 
                (usuario_id, puesto_id, mesa_id, rol_asignado, fecha_asignacion, 
                 turno, asignado_por, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data['usuario_id'],
                data.get('puesto_id'),
                data.get('mesa_id'),
                data['rol_asignado'],
                data['fecha_asignacion'],
                data.get('turno', 'completo'),
                data['asignado_por'],
                data.get('notas')
            )
            
            asignacion_id = DatabaseManager.execute_query(query, params)
            
            # Notificar al usuario asignado
            create_notification(
                data['usuario_id'],
                'Nueva asignación',
                f'Has sido asignado como {data["rol_asignado"]} para el {data["fecha_asignacion"]}',
                'asignacion_personal'
            )
            
            return jsonify({
                'success': True,
                'message': 'Asignación creada exitosamente',
                'asignacion_id': asignacion_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== INVENTARIO API ====================
    
    @app.route('/api/inventario', methods=['GET'])
    def get_inventario():
        """Obtener inventario de materiales"""
        try:
            puesto_id = request.args.get('puesto_id')
            estado = request.args.get('estado')
            
            query = """
                SELECT i.*, p.nombre as puesto_nombre,
                       us.nombre_completo as solicitado_por_nombre,
                       ue.nombre_completo as entregado_por_nombre
                FROM inventario_materiales i
                LEFT JOIN puestos_votacion p ON i.puesto_id = p.id
                LEFT JOIN users us ON i.solicitado_por = us.id
                LEFT JOIN users ue ON i.entregado_por = ue.id
                WHERE 1=1
            """
            params = []
            
            if puesto_id:
                query += " AND i.puesto_id = ?"
                params.append(puesto_id)
            
            if estado:
                query += " AND i.estado = ?"
                params.append(estado)
            
            query += " ORDER BY i.prioridad DESC, i.fecha_solicitud DESC"
            
            inventario = DatabaseManager.execute_query(query, params, fetch_all=True)
            
            return jsonify({
                'success': True,
                'data': inventario,
                'total': len(inventario)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/inventario', methods=['POST'])
    def create_solicitud_material():
        """Crear solicitud de material"""
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['puesto_id', 'tipo_material', 'cantidad_requerida', 'solicitado_por']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Campo requerido: {field}'}), 400
            
            # Insertar solicitud
            query = """
                INSERT INTO inventario_materiales 
                (puesto_id, tipo_material, descripcion, cantidad_requerida, 
                 prioridad, solicitado_por, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data['puesto_id'],
                data['tipo_material'],
                data.get('descripcion'),
                data['cantidad_requerida'],
                data.get('prioridad', 'normal'),
                data['solicitado_por'],
                data.get('notas')
            )
            
            solicitud_id = DatabaseManager.execute_query(query, params)
            
            # Notificar a coordinadores si es prioridad alta
            if data.get('prioridad') == 'alta':
                create_notification_for_coordinators(
                    'Solicitud urgente de material',
                    f'Se ha solicitado {data["tipo_material"]} con prioridad alta',
                    'solicitud_material_urgente',
                    data['puesto_id']
                )
            
            return jsonify({
                'success': True,
                'message': 'Solicitud de material creada exitosamente',
                'solicitud_id': solicitud_id
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== NOTIFICACIONES API ====================
    
    @app.route('/api/notificaciones/<int:usuario_id>', methods=['GET'])
    def get_notificaciones_usuario(usuario_id):
        """Obtener notificaciones de un usuario"""
        try:
            solo_no_leidas = request.args.get('no_leidas', 'false').lower() == 'true'
            
            query = """
                SELECT * FROM notificaciones 
                WHERE usuario_id = ?
            """
            params = [usuario_id]
            
            if solo_no_leidas:
                query += " AND leida = 0"
            
            query += " ORDER BY urgente DESC, created_at DESC LIMIT 50"
            
            notificaciones = DatabaseManager.execute_query(query, params, fetch_all=True)
            
            return jsonify({
                'success': True,
                'data': notificaciones,
                'total': len(notificaciones)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/notificaciones/<int:notificacion_id>/marcar-leida', methods=['PUT'])
    def marcar_notificacion_leida(notificacion_id):
        """Marcar notificación como leída"""
        try:
            query = """
                UPDATE notificaciones 
                SET leida = 1, leida_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            DatabaseManager.execute_query(query, (notificacion_id,))
            
            return jsonify({
                'success': True,
                'message': 'Notificación marcada como leída'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== UPLOAD DE ARCHIVOS ====================
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Subir archivo (imagen, documento)"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No se encontró archivo'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
            
            # Validar tipo de archivo
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
            
            # Crear directorio de uploads si no existe
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Generar nombre único para el archivo
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Guardar archivo
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'message': 'Archivo subido exitosamente',
                'filename': unique_filename,
                'path': file_path
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# ==================== FUNCIONES AUXILIARES ====================

def create_notification(usuario_id, titulo, mensaje, tipo, urgente=False):
    """Crear notificación para un usuario específico"""
    query = """
        INSERT INTO notificaciones (usuario_id, tipo, titulo, mensaje, urgente)
        VALUES (?, ?, ?, ?, ?)
    """
    DatabaseManager.execute_query(query, (usuario_id, tipo, titulo, mensaje, int(urgente)))

def create_notification_for_coordinators(titulo, mensaje, tipo, puesto_id=None):
    """Crear notificación para coordinadores relevantes"""
    # Obtener coordinadores según el contexto
    if puesto_id:
        # Notificar coordinador de puesto específico
        query = """
            SELECT id FROM users 
            WHERE rol IN ('coordinador_puesto', 'coordinador_municipal', 'coordinador_departamental')
            AND (puesto_id = ? OR puesto_id IS NULL)
            AND activo = 1
        """
        coordinadores = DatabaseManager.execute_query(query, (puesto_id,), fetch_all=True)
    else:
        # Notificar todos los coordinadores
        query = """
            SELECT id FROM users 
            WHERE rol IN ('coordinador_municipal', 'coordinador_departamental')
            AND activo = 1
        """
        coordinadores = DatabaseManager.execute_query(query, fetch_all=True)
    
    for coordinador in coordinadores:
        create_notification(coordinador['id'], titulo, mensaje, tipo, urgente=True)

def create_notification_for_supervisors(titulo, mensaje, tipo):
    """Crear notificación para supervisores"""
    query = """
        SELECT id FROM users 
        WHERE rol IN ('coordinador_departamental', 'super_admin')
        AND activo = 1
    """
    supervisores = DatabaseManager.execute_query(query, fetch_all=True)
    
    for supervisor in supervisores:
        create_notification(supervisor['id'], titulo, mensaje, tipo, urgente=True)