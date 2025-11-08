#!/usr/bin/env python3
"""
API para carga dinámica de ubicación (Departamento → Municipio → Zona → Puesto → Mesa)
"""

from flask import Blueprint, jsonify
import sqlite3

ubicacion_api = Blueprint('ubicacion_api', __name__)

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('caqueta_electoral.db')
    conn.row_factory = sqlite3.Row
    return conn

@ubicacion_api.route('/api/ubicacion/municipios', methods=['GET'])
def get_municipios():
    """Obtener todos los municipios del Caquetá"""
    try:
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, codigo, nombre, poblacion
            FROM municipios
            WHERE activo = 1
            ORDER BY nombre
        ''')
        
        municipios = []
        for row in cursor.fetchall():
            municipios.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'poblacion': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'municipios': municipios
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ubicacion_api.route('/api/ubicacion/zonas/<int:municipio_id>', methods=['GET'])
def get_zonas(municipio_id):
    """Obtener zonas de un municipio"""
    try:
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, codigo_zz, nombre, descripcion, tipo_zona
            FROM zonas
            WHERE municipio_id = ? AND activo = 1
            ORDER BY codigo_zz
        ''', (municipio_id,))
        
        zonas = []
        for row in cursor.fetchall():
            zonas.append({
                'id': row[0],
                'codigo': row[1] or '',
                'nombre': row[2] or '',
                'descripcion': row[3] or '',
                'tipo': row[4] or ''
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'zonas': zonas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ubicacion_api.route('/api/ubicacion/puestos/<int:zona_id>', methods=['GET'])
def get_puestos(zona_id):
    """Obtener puestos de votación de una zona"""
    try:
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        print(f"DEBUG: Buscando puestos para zona_id={zona_id}")
        
        cursor.execute('''
            SELECT id, nombre, direccion
            FROM puestos_votacion
            WHERE zona_id = ? AND activo = 1
            ORDER BY nombre
        ''', (zona_id,))
        
        rows = cursor.fetchall()
        print(f"DEBUG: Encontradas {len(rows)} filas")
        
        puestos = []
        for row in rows:
            print(f"DEBUG: Puesto ID={row[0]}, Nombre={row[1]}")
            puestos.append({
                'id': row[0],
                'nombre': row[1],
                'direccion': row[2] or ''
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'puestos': puestos
        })
        
    except Exception as e:
        print(f"DEBUG: Error={e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ubicacion_api.route('/api/ubicacion/mesas/<int:puesto_id>', methods=['GET'])
def get_mesas(puesto_id):
    """Obtener mesas de votación de un puesto"""
    try:
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, numero, votantes_habilitados
            FROM mesas_votacion
            WHERE puesto_id = ? AND activa = 1
            ORDER BY numero
        ''', (puesto_id,))
        
        mesas = []
        for row in cursor.fetchall():
            mesas.append({
                'id': row[0],
                'numero': row[1],
                'votantes_habilitados': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'mesas': mesas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@ubicacion_api.route('/api/ubicacion/usuario-por-ubicacion', methods=['GET'])
def get_usuario_por_ubicacion():
    """
    Buscar usuario por ubicación (municipio, puesto, mesa)
    Query params: municipio_id, puesto_id, mesa_id
    """
    try:
        from flask import request
        
        municipio_id = request.args.get('municipio_id', type=int)
        puesto_id = request.args.get('puesto_id', type=int)
        mesa_id = request.args.get('mesa_id', type=int)
        
        if not all([municipio_id, puesto_id, mesa_id]):
            return jsonify({
                'success': False,
                'error': 'Faltan parámetros: municipio_id, puesto_id, mesa_id'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                u.id, u.username, u.nombre_completo, u.cedula, u.rol,
                m_mun.nombre as municipio,
                pv.nombre as puesto,
                mv.numero as mesa
            FROM users u
            LEFT JOIN municipios m_mun ON u.municipio_id = m_mun.id
            LEFT JOIN puestos_votacion pv ON u.puesto_id = pv.id
            LEFT JOIN mesas_votacion mv ON u.mesa_id = mv.id
            WHERE u.municipio_id = ? 
              AND u.puesto_id = ? 
              AND u.mesa_id = ?
              AND u.activo = 1
            LIMIT 1
        ''', (municipio_id, puesto_id, mesa_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                'success': True,
                'usuario': {
                    'id': row['id'],
                    'username': row['username'],
                    'nombre_completo': row['nombre_completo'],
                    'cedula': row['cedula'],
                    'rol': row['rol'],
                    'municipio': row['municipio'],
                    'puesto': row['puesto'],
                    'mesa': row['mesa']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró usuario para esta ubicación'
            }), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def register_ubicacion_api(app):
    """Registrar el blueprint de ubicación"""
    app.register_blueprint(ubicacion_api)
    print("✅ API de ubicación dinámica registrada exitosamente")
