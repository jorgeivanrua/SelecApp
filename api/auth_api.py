#!/usr/bin/env python3
"""
API de Autenticación y Registro
Maneja login, registro de usuarios y validación
"""

from flask import Blueprint, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_api = Blueprint('auth_api', __name__)

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('caqueta_electoral.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_api.route('/api/auth/register', methods=['POST'])
def register():
    """Registro de nuevo usuario (testigo o coordinador)"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos (email es opcional)
        required_fields = ['cedula', 'nombre_completo', 'telefono', 
                          'municipio_id', 'puesto_id', 'rol', 'password']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Validar rol permitido
        allowed_roles = ['testigo_mesa', 'coordinador_puesto', 'coordinador_municipal']
        if data['rol'] not in allowed_roles:
            return jsonify({'error': 'Rol no permitido para auto-registro'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la cédula ya existe
        cursor.execute("SELECT id FROM users WHERE cedula = ?", (data['cedula'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'La cédula ya está registrada'}), 400
        
        # Verificar si el email ya existe (solo si se proporcionó)
        if data.get('email'):
            cursor.execute("SELECT id FROM users WHERE email = ?", (data['email'],))
            if cursor.fetchone():
                conn.close()
                return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Generar username automático
        username = f"user_{data['cedula']}"
        
        # Hash de la contraseña
        password_hash = generate_password_hash(data['password'])
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO users (
                username, cedula, nombre_completo, email, telefono,
                password_hash, rol, municipio_id, puesto_id, mesa_id,
                activo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            data['cedula'],
            data['nombre_completo'],
            data.get('email', ''),  # Email opcional
            data['telefono'],
            password_hash,
            data['rol'],
            data['municipio_id'],
            data['puesto_id'],
            data.get('mesa_id'),
            1,  # activo
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'user_id': user_id,
            'username': username
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/ubicacion/municipios', methods=['GET'])
def get_municipios():
    """Obtener lista de municipios con códigos DIVIPOLA"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo, nombre, departamento, codigo_dd, codigo_mm
            FROM municipios
            WHERE activo = 1
            ORDER BY nombre
        """)
        
        municipios = []
        for row in cursor.fetchall():
            municipios.append({
                'id': row['id'],
                'codigo': row['codigo'],
                'codigo_dd': row['codigo_dd'],
                'codigo_mm': row['codigo_mm'],
                'nombre': row['nombre'],
                'departamento': row['departamento']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'municipios': municipios
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/ubicacion/zonas/<int:municipio_id>', methods=['GET'])
def get_zonas(municipio_id):
    """Obtener zonas de un municipio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, codigo_zz, nombre, codigo_completo
            FROM zonas
            WHERE municipio_id = ? AND activo = 1
            ORDER BY codigo_zz
        """, (municipio_id,))
        
        zonas = []
        for row in cursor.fetchall():
            zonas.append({
                'id': row['id'],
                'codigo_zz': row['codigo_zz'],
                'nombre': row['nombre'],
                'codigo_completo': row['codigo_completo']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'zonas': zonas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/ubicacion/puestos-municipio/<int:municipio_id>', methods=['GET'])
def get_puestos_municipio(municipio_id):
    """Obtener puestos de votación de un municipio con códigos DIVIPOLA"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.nombre, p.direccion, p.codigo, p.codigo_divipola, 
                   p.codigo_pp, z.codigo_zz, z.nombre as zona_nombre
            FROM puestos_votacion p
            LEFT JOIN zonas z ON p.zona_id = z.id
            WHERE p.municipio_id = ? AND p.activo = 1
            ORDER BY p.codigo_divipola
        """, (municipio_id,))
        
        puestos = []
        for row in cursor.fetchall():
            puestos.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'direccion': row['direccion'],
                'codigo': row['codigo'],
                'codigo_divipola': row['codigo_divipola'],
                'codigo_pp': row['codigo_pp'],
                'codigo_zz': row['codigo_zz'],
                'zona_nombre': row['zona_nombre']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'puestos': puestos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/ubicacion/mesas/<int:puesto_id>', methods=['GET'])
def get_mesas(puesto_id):
    """Obtener mesas de votación de un puesto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, numero, votantes_habilitados
            FROM mesas_votacion
            WHERE puesto_id = ? AND activa = 1
            ORDER BY numero
        """, (puesto_id,))
        
        mesas = []
        for row in cursor.fetchall():
            mesas.append({
                'id': row['id'],
                'numero': row['numero'],
                'votantes_habilitados': row['votantes_habilitados']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'mesas': mesas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Obtener todos los usuarios (solo admin)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                u.id, u.username, u.cedula, u.nombre_completo, u.email, u.telefono,
                u.rol, u.departamento, u.activo, u.created_at,
                m.nombre as municipio_nombre,
                p.nombre as puesto_nombre,
                mv.numero as mesa_numero
            FROM users u
            LEFT JOIN municipios m ON u.municipio_id = m.id
            LEFT JOIN puestos_votacion p ON u.puesto_id = p.id
            LEFT JOIN mesas_votacion mv ON u.mesa_id = mv.id
            ORDER BY u.created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row['id'],
                'username': row['username'],
                'cedula': row['cedula'],
                'nombre_completo': row['nombre_completo'],
                'email': row['email'],
                'telefono': row['telefono'],
                'rol': row['rol'],
                'departamento': row['departamento'],
                'activo': row['activo'],
                'created_at': row['created_at'],
                'municipio_nombre': row['municipio_nombre'],
                'puesto_nombre': row['puesto_nombre'],
                'mesa_numero': row['mesa_numero']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/users', methods=['POST'])
def create_user_by_admin():
    """Crear usuario desde el panel de admin"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['cedula', 'nombre_completo', 'telefono', 'rol', 'password']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la cédula ya existe
        cursor.execute("SELECT id FROM users WHERE cedula = ?", (data['cedula'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'La cédula ya está registrada'}), 400
        
        # Generar username automático
        username = data.get('username', f"user_{data['cedula']}")
        
        # Hash de la contraseña
        password_hash = generate_password_hash(data['password'])
        
        # Insertar usuario
        cursor.execute("""
            INSERT INTO users (
                username, cedula, nombre_completo, email, telefono,
                password_hash, rol, departamento, municipio_id, puesto_id, mesa_id,
                activo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            data['cedula'],
            data['nombre_completo'],
            data.get('email', ''),
            data['telefono'],
            password_hash,
            data['rol'],
            data.get('departamento', 'Caquetá'),
            data.get('municipio_id'),
            data.get('puesto_id'),
            data.get('mesa_id'),
            1,  # activo
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'user_id': user_id,
            'username': username
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Actualizar usuario (solo admin)"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        updates = []
        params = []
        
        if 'nombre_completo' in data:
            updates.append('nombre_completo = ?')
            params.append(data['nombre_completo'])
        
        if 'email' in data:
            updates.append('email = ?')
            params.append(data['email'])
        
        if 'telefono' in data:
            updates.append('telefono = ?')
            params.append(data['telefono'])
        
        if 'rol' in data:
            updates.append('rol = ?')
            params.append(data['rol'])
        
        if 'departamento' in data:
            updates.append('departamento = ?')
            params.append(data['departamento'])
        
        if 'activo' in data:
            updates.append('activo = ?')
            params.append(data['activo'])
        
        if 'municipio_id' in data:
            updates.append('municipio_id = ?')
            params.append(data['municipio_id'])
        
        if 'puesto_id' in data:
            updates.append('puesto_id = ?')
            params.append(data['puesto_id'])
        
        if 'mesa_id' in data:
            updates.append('mesa_id = ?')
            params.append(data['mesa_id'])
        
        if 'password' in data:
            updates.append('password_hash = ?')
            params.append(generate_password_hash(data['password']))
        
        if not updates:
            conn.close()
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Eliminar usuario (solo admin)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Desactivar en lugar de eliminar
        cursor.execute("UPDATE users SET activo = 0 WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Usuario desactivado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/generation-stats', methods=['GET'])
def get_generation_stats():
    """Obtener estadísticas para generación automática"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar municipios
        cursor.execute("SELECT COUNT(*) as count FROM municipios WHERE activo = 1")
        municipios = cursor.fetchone()['count']
        
        # Contar puestos
        cursor.execute("SELECT COUNT(*) as count FROM puestos_votacion WHERE activo = 1")
        puestos = cursor.fetchone()['count']
        
        # Contar mesas
        cursor.execute("SELECT COUNT(*) as count FROM mesas_votacion WHERE activa = 1")
        mesas = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'municipios': municipios,
            'puestos': puestos,
            'mesas': mesas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_api.route('/api/admin/generate-users', methods=['POST'])
def generate_users_auto():
    """Generar usuarios automáticamente desde DIVIPOLA"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created = 0
        skipped = 0
        errors = 0
        details = []
        
        default_password = data.get('default_password', 'Electoral2024!')
        skip_existing = data.get('skip_existing', True)
        password_hash = generate_password_hash(default_password)
        
        # 1. Generar Coordinadores Municipales
        if data.get('coordinadores_municipales', False):
            cursor.execute("""
                SELECT id, codigo, nombre, codigo_dd, codigo_mm
                FROM municipios
                WHERE activo = 1
                ORDER BY nombre
            """)
            
            municipios = cursor.fetchall()
            
            for mun in municipios:
                cedula = f"CM{mun['codigo_dd']}{mun['codigo_mm']}"
                username = f"coord_mun_{mun['codigo']}"
                
                # Verificar si existe
                if skip_existing:
                    cursor.execute("SELECT id FROM users WHERE cedula = ?", (cedula,))
                    if cursor.fetchone():
                        skipped += 1
                        details.append({
                            'status': 'skipped',
                            'message': f"Coordinador Municipal {mun['nombre']} ya existe"
                        })
                        continue
                
                try:
                    cursor.execute("""
                        INSERT INTO users (
                            username, cedula, nombre_completo, email, telefono,
                            password_hash, rol, departamento, municipio_id,
                            activo, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        username,
                        cedula,
                        f"Coordinador Municipal {mun['nombre']}",
                        f"{username}@electoral.gov.co",
                        "3000000000",
                        password_hash,
                        'coordinador_municipal',
                        'Caquetá',
                        mun['id'],
                        1,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    created += 1
                    details.append({
                        'status': 'created',
                        'message': f"✅ Coordinador Municipal {mun['nombre']}"
                    })
                except Exception as e:
                    errors += 1
                    details.append({
                        'status': 'error',
                        'message': f"❌ Error en {mun['nombre']}: {str(e)}"
                    })
        
        # 2. Generar Coordinadores de Puesto
        if data.get('coordinadores_puesto', False):
            cursor.execute("""
                SELECT p.id, p.nombre, p.codigo_divipola, p.municipio_id,
                       m.nombre as municipio_nombre, m.codigo_dd, m.codigo_mm
                FROM puestos_votacion p
                LEFT JOIN municipios m ON p.municipio_id = m.id
                WHERE p.activo = 1
                ORDER BY m.nombre, p.nombre
            """)
            
            puestos = cursor.fetchall()
            
            for puesto in puestos:
                cedula = f"CP{puesto['codigo_divipola']}"
                username = f"coord_puesto_{puesto['codigo_divipola']}"
                
                if skip_existing:
                    cursor.execute("SELECT id FROM users WHERE cedula = ?", (cedula,))
                    if cursor.fetchone():
                        skipped += 1
                        details.append({
                            'status': 'skipped',
                            'message': f"Coordinador Puesto {puesto['nombre']} ya existe"
                        })
                        continue
                
                try:
                    cursor.execute("""
                        INSERT INTO users (
                            username, cedula, nombre_completo, email, telefono,
                            password_hash, rol, departamento, municipio_id, puesto_id,
                            activo, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        username,
                        cedula,
                        f"Coordinador {puesto['nombre']}",
                        f"{username}@electoral.gov.co",
                        "3000000000",
                        password_hash,
                        'coordinador_puesto',
                        'Caquetá',
                        puesto['municipio_id'],
                        puesto['id'],
                        1,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    created += 1
                    details.append({
                        'status': 'created',
                        'message': f"✅ Coordinador {puesto['nombre']} - {puesto['municipio_nombre']}"
                    })
                except Exception as e:
                    errors += 1
                    details.append({
                        'status': 'error',
                        'message': f"❌ Error en {puesto['nombre']}: {str(e)}"
                    })
        
        # 3. Generar Testigos de Mesa
        if data.get('testigos', False):
            cursor.execute("""
                SELECT mv.id, mv.numero, mv.puesto_id, mv.municipio_id,
                       p.nombre as puesto_nombre, p.codigo_divipola,
                       m.nombre as municipio_nombre
                FROM mesas_votacion mv
                LEFT JOIN puestos_votacion p ON mv.puesto_id = p.id
                LEFT JOIN municipios m ON mv.municipio_id = m.id
                WHERE mv.activa = 1
                ORDER BY m.nombre, p.nombre, mv.numero
            """)
            
            mesas = cursor.fetchall()
            
            for mesa in mesas:
                cedula = f"TM{mesa['codigo_divipola']}{mesa['numero']:03d}"
                username = f"testigo_{mesa['codigo_divipola']}_{mesa['numero']:03d}"
                
                if skip_existing:
                    cursor.execute("SELECT id FROM users WHERE cedula = ?", (cedula,))
                    if cursor.fetchone():
                        skipped += 1
                        continue
                
                try:
                    cursor.execute("""
                        INSERT INTO users (
                            username, cedula, nombre_completo, email, telefono,
                            password_hash, rol, departamento, municipio_id, puesto_id, mesa_id,
                            activo, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        username,
                        cedula,
                        f"Testigo Mesa {mesa['numero']} - {mesa['puesto_nombre']}",
                        f"{username}@electoral.gov.co",
                        "3000000000",
                        password_hash,
                        'testigo_mesa',
                        'Caquetá',
                        mesa['municipio_id'],
                        mesa['puesto_id'],
                        mesa['id'],
                        1,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    created += 1
                    if created % 10 == 0:  # Log cada 10 testigos
                        details.append({
                            'status': 'created',
                            'message': f"✅ {created} testigos creados..."
                        })
                except Exception as e:
                    errors += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'created': created,
            'skipped': skipped,
            'errors': errors,
            'details': details[:50]  # Limitar a 50 detalles
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def register_auth_api(app):
    """Registrar el blueprint de autenticación"""
    app.register_blueprint(auth_api)
    print("✅ API de autenticación y registro registrada exitosamente")
