#!/usr/bin/env python3
"""
API de Testigo Electoral
Maneja capturas E14, OCR automático y registro de datos
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
import base64
import os

testigo_api = Blueprint('testigo_api', __name__)

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('caqueta_electoral.db')
    conn.row_factory = sqlite3.Row
    return conn

@testigo_api.route('/api/testigo/enviar-e14', methods=['POST'])
def enviar_e14():
    """Enviar formulario E14 con foto y datos digitados"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('candidatos') or len(data['candidatos']) == 0:
            return jsonify({'error': 'Debe incluir al menos un candidato'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener información del testigo (simulado por ahora)
        testigo_id = 1  # En producción, obtener del token JWT
        mesa_id = 1  # En producción, obtener de la asignación del testigo
        
        # Calcular totales
        total_votos_candidatos = sum(c['votos'] for c in data['candidatos'])
        votos_blanco = data.get('votosBlanco', 0)
        votos_nulos = data.get('votosNulos', 0)
        tarjetas_no_marcadas = data.get('tarjetasNoMarcadas', 0)
        
        total_votos = total_votos_candidatos + votos_blanco + votos_nulos
        
        # Insertar captura E14
        cursor.execute("""
            INSERT INTO capturas_e14 (
                testigo_id, mesa_id, imagen_path, 
                total_votos_candidatos, votos_blanco, votos_nulos, tarjetas_no_marcadas,
                total_votos, observaciones, estado, procesado_ocr
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            testigo_id, mesa_id, 'uploads/e14/temp.jpg',
            total_votos_candidatos, votos_blanco, votos_nulos, tarjetas_no_marcadas,
            total_votos, data.get('observaciones', ''), 'enviado', 1
        ))
        
        captura_id = cursor.lastrowid
        
        # Insertar votos por candidato
        for candidato in data['candidatos']:
            cursor.execute("""
                INSERT INTO datos_ocr_e14 (
                    captura_e14_id, posicion, tipo, nombre_candidato, partido,
                    votos_detectados, votos_confirmados, confianza, editado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                captura_id, 0, 'candidato', 
                candidato['nombre'], candidato['partido'],
                candidato['votos'], candidato['votos'], 0.95, 1
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Formulario E14 enviado exitosamente',
            'captura_id': captura_id,
            'total_votos': total_votos
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@testigo_api.route('/api/testigo/info/<int:user_id>', methods=['GET'])
def get_testigo_info(user_id):
    """Obtener información completa del testigo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.id, u.cedula, u.nombre_completo, u.email, u.telefono, u.rol,
                u.municipio_id, u.puesto_id, u.mesa_id,
                mu.nombre as municipio_nombre, mu.codigo as municipio_codigo,
                p.nombre as puesto_nombre, p.direccion as puesto_direccion,
                m.numero as mesa_numero, m.votantes_habilitados,
                z.codigo_zz as zona_codigo, z.nombre as zona_nombre
            FROM users u
            LEFT JOIN municipios mu ON u.municipio_id = mu.id
            LEFT JOIN puestos_votacion p ON u.puesto_id = p.id
            LEFT JOIN mesas_votacion m ON u.mesa_id = m.id
            LEFT JOIN zonas z ON p.zona_id = z.id
            WHERE u.id = ? AND u.activo = 1
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Contar capturas E14
        cursor.execute("""
            SELECT COUNT(*) as total_capturas
            FROM capturas_e14
            WHERE testigo_id = ?
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'user': {
                'id': row['id'],
                'cedula': row['cedula'],
                'nombre_completo': row['nombre_completo'],
                'email': row['email'],
                'telefono': row['telefono'],
                'rol': row['rol'],
                'municipio_id': row['municipio_id'],
                'municipio_nombre': row['municipio_nombre'],
                'municipio_codigo': row['municipio_codigo'],
                'puesto_id': row['puesto_id'],
                'puesto_nombre': row['puesto_nombre'],
                'puesto_direccion': row['puesto_direccion'],
                'mesa_id': row['mesa_id'],
                'mesa_numero': row['mesa_numero'],
                'votantes_habilitados': row['votantes_habilitados'],
                'zona_codigo': row['zona_codigo'],
                'zona_nombre': row['zona_nombre'],
                'total_capturas': stats['total_capturas'] or 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@testigo_api.route('/api/testigo/mesa-asignada', methods=['GET'])
def get_mesa_asignada():
    """Obtener información de la mesa asignada al testigo"""
    try:
        # En producción, obtener del token JWT
        testigo_id = 1
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.id, m.numero, m.votantes_habilitados,
                p.nombre as puesto_nombre,
                mu.nombre as municipio_nombre
            FROM users u
            LEFT JOIN mesas_votacion m ON u.mesa_id = m.id
            LEFT JOIN puestos_votacion p ON m.puesto_id = p.id
            LEFT JOIN municipios mu ON m.municipio_id = mu.id
            WHERE u.id = ?
        """, (testigo_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'No se encontró mesa asignada'}), 404
        
        # Contar votos registrados
        cursor.execute("""
            SELECT COUNT(*) as total_capturas,
                   SUM(total_votos) as votos_registrados
            FROM capturas_e14
            WHERE testigo_id = ? AND mesa_id = ?
        """, (testigo_id, row['id']))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'mesa': {
                'id': row['id'],
                'numero': row['numero'],
                'votantes_habilitados': row['votantes_habilitados'],
                'puesto_nombre': row['puesto_nombre'],
                'municipio_nombre': row['municipio_nombre'],
                'votos_registrados': stats['votos_registrados'] or 0,
                'total_capturas': stats['total_capturas'] or 0
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@testigo_api.route('/api/testigo/candidatos', methods=['GET'])
def get_candidatos():
    """Obtener lista de candidatos para el proceso electoral"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id, c.nombre, c.apellidos,
                p.nombre as partido_nombre, p.sigla as partido_sigla,
                ce.nombre as cargo_nombre
            FROM candidatos c
            LEFT JOIN partidos_politicos p ON c.partido_id = p.id
            LEFT JOIN cargos_electorales ce ON c.cargo_id = ce.id
            WHERE c.activo = 1
            ORDER BY c.nombre
        """)
        
        candidatos = []
        for row in cursor.fetchall():
            candidatos.append({
                'id': row['id'],
                'nombre': f"{row['nombre']} {row['apellidos']}",
                'partido': row['partido_nombre'],
                'sigla': row['partido_sigla'],
                'cargo': row['cargo_nombre']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'candidatos': candidatos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@testigo_api.route('/api/testigo/procesar-ocr', methods=['POST'])
def procesar_ocr():
    """Procesar imagen del E14 con OCR y extraer datos"""
    try:
        # Verificar que se envió una imagen
        if 'imagen' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió imagen'}), 400
        
        file = request.files['imagen']
        tipo_eleccion = request.form.get('tipo_eleccion', 'senado')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Archivo vacío'}), 400
        
        # Guardar imagen temporalmente
        import os
        from werkzeug.utils import secure_filename
        
        upload_folder = 'uploads/e14'
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_folder, filename)
        
        file.save(filepath)
        
        # Procesar con OCR
        from services.ocr_e14_service import ocr_service
        
        resultado = ocr_service.procesar_imagen_e14(filepath, tipo_eleccion)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'candidatos': [],
            'votos_especiales': {},
            'totales': {}
        }), 500


def register_testigo_api(app):
    """Registrar el blueprint de testigo"""
    app.register_blueprint(testigo_api)
    print("✅ API de testigo electoral registrada exitosamente")
