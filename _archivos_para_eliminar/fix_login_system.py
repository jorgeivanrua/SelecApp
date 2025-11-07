#!/usr/bin/env python3
"""
Script para corregir el sistema de login y crear usuarios demo
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def fix_login_system():
    """Corregir sistema de login y crear usuarios demo"""
    
    print("🔧 Corrigiendo sistema de login...")
    
    # Conectar a la base de datos
    db_path = 'caqueta_electoral.db'
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar estructura de tabla users
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"✅ Columnas en tabla users: {columns}")
        
        # Crear usuarios demo si no existen
        demo_users = [
            {
                'nombre_completo': 'Super Administrador Demo',
                'cedula': '12345678',
                'telefono': '3001234567',
                'email': 'super.admin@caqueta.gov.co',
                'username': '12345678',  # Usar cédula como username
                'password': 'admin123',
                'rol': 'super_admin',
                'municipio_id': None,
                'puesto_id': None,
                'activo': 1
            },
            {
                'nombre_completo': 'Administrador Departamental Demo',
                'cedula': '87654321',
                'telefono': '3007654321',
                'email': 'admin.depto@caqueta.gov.co',
                'username': '87654321',
                'password': 'admin123',
                'rol': 'admin_departamental',
                'municipio_id': None,
                'puesto_id': None,
                'activo': 1
            },
            {
                'nombre_completo': 'Administrador Municipal Demo',
                'cedula': '11111111',
                'telefono': '3001111111',
                'email': 'admin.municipal@caqueta.gov.co',
                'username': '11111111',
                'password': 'admin123',
                'rol': 'admin_municipal',
                'municipio_id': 1,
                'puesto_id': None,
                'activo': 1
            },
            {
                'nombre_completo': 'Testigo de Mesa Demo',
                'cedula': '22222222',
                'telefono': '3002222222',
                'email': 'testigo@caqueta.gov.co',
                'username': '22222222',
                'password': 'testigo123',
                'rol': 'testigo',
                'municipio_id': 1,
                'puesto_id': 1,
                'activo': 1
            },
            {
                'nombre_completo': 'Coordinador Electoral Demo',
                'cedula': '33333333',
                'telefono': '3003333333',
                'email': 'coordinador@caqueta.gov.co',
                'username': '33333333',
                'password': 'coord123',
                'rol': 'coordinador_electoral',
                'municipio_id': 1,
                'puesto_id': None,
                'activo': 1
            },
            {
                'nombre_completo': 'Jurado de Votación Demo',
                'cedula': '44444444',
                'telefono': '3004444444',
                'email': 'jurado@caqueta.gov.co',
                'username': '44444444',
                'password': 'jurado123',
                'rol': 'jurado_votacion',
                'municipio_id': 1,
                'puesto_id': 1,
                'activo': 1
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in demo_users:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM users WHERE cedula = ?", (user_data['cedula'],))
            existing_user = cursor.fetchone()
            
            password_hash = generate_password_hash(user_data['password'])
            
            if existing_user:
                # Actualizar usuario existente
                cursor.execute("""
                    UPDATE users SET 
                        nombre_completo = ?,
                        telefono = ?,
                        email = ?,
                        username = ?,
                        password_hash = ?,
                        rol = ?,
                        municipio_id = ?,
                        puesto_id = ?,
                        activo = ?,
                        fecha_actualizacion = ?
                    WHERE cedula = ?
                """, (
                    user_data['nombre_completo'],
                    user_data['telefono'],
                    user_data['email'],
                    user_data['username'],
                    password_hash,
                    user_data['rol'],
                    user_data['municipio_id'],
                    user_data['puesto_id'],
                    user_data['activo'],
                    datetime.now().isoformat(),
                    user_data['cedula']
                ))
                updated_count += 1
                print(f"  ✅ Actualizado: {user_data['nombre_completo']} ({user_data['rol']})")
            else:
                # Crear nuevo usuario
                cursor.execute("""
                    INSERT INTO users (
                        nombre_completo, cedula, telefono, email, username, 
                        password_hash, rol, municipio_id, puesto_id, activo,
                        fecha_creacion, fecha_actualizacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['nombre_completo'],
                    user_data['cedula'],
                    user_data['telefono'],
                    user_data['email'],
                    user_data['username'],
                    password_hash,
                    user_data['rol'],
                    user_data['municipio_id'],
                    user_data['puesto_id'],
                    user_data['activo'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                created_count += 1
                print(f"  ✅ Creado: {user_data['nombre_completo']} ({user_data['rol']})")
        
        conn.commit()
        
        print(f"\n📊 Resumen:")
        print(f"  - Usuarios creados: {created_count}")
        print(f"  - Usuarios actualizados: {updated_count}")
        print(f"  - Total usuarios demo: {len(demo_users)}")
        
        # Verificar usuarios creados
        cursor.execute("SELECT cedula, username, rol FROM users WHERE cedula IN ('12345678', '87654321', '11111111', '22222222', '33333333', '44444444')")
        users = cursor.fetchall()
        
        print(f"\n🔑 Usuarios demo verificados:")
        for user in users:
            print(f"  - Cédula: {user[0]}, Username: {user[1]}, Rol: {user[2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_login_fix_route():
    """Crear archivo para corregir la ruta de login"""
    
    print("🔧 Creando corrección para ruta de login...")
    
    login_fix_content = '''
# Agregar esta función al archivo app.py para soportar login con cédula

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de autenticación con cédula"""
    try:
        data = request.get_json()
        cedula = data.get('cedula') or data.get('username')  # Soportar ambos
        password = data.get('password')
        
        if not cedula or not password:
            return jsonify({'error': 'Cédula and password required'}), 400
        
        # Buscar usuario por cédula o username
        conn = sqlite3.connect('caqueta_electoral.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, nombre_completo, password_hash, rol, activo
            FROM users 
            WHERE (cedula = ? OR username = ?) AND activo = 1
        """, (cedula, cedula))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verificar password
        if not check_password_hash(user_data[3], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Crear token JWT
        access_token = create_access_token(
            identity=user_data[0],
            additional_claims={
                'username': user_data[1],
                'role': user_data[4]
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user_data[0],
                'username': user_data[1],
                'nombre_completo': user_data[2],
                'rol': user_data[4]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
    
    with open('login_fix.py', 'w', encoding='utf-8') as f:
        f.write(login_fix_content)
    
    print("✅ Archivo login_fix.py creado")

def main():
    """Función principal"""
    print("🚀 CORRECCIÓN DEL SISTEMA DE LOGIN")
    print("="*50)
    
    # Corregir sistema de login
    if fix_login_system():
        print("✅ Sistema de login corregido")
        
        # Crear archivo de corrección
        create_login_fix_route()
        
        print("\n" + "="*60)
        print("🎉 CORRECCIÓN COMPLETADA")
        print("="*60)
        
        print("\n🔑 CREDENCIALES DE ACCESO:")
        print("Usar CÉDULA como username:")
        
        credentials = [
            ("Super Admin", "12345678", "admin123"),
            ("Admin Depto", "87654321", "admin123"),
            ("Admin Municipal", "11111111", "admin123"),
            ("Testigo Mesa", "22222222", "testigo123"),
            ("Coordinador", "33333333", "coord123"),
            ("Jurado", "44444444", "jurado123")
        ]
        
        for rol, cedula, password in credentials:
            print(f"  • {rol}: {cedula} / {password}")
        
        print("\n📝 INSTRUCCIONES:")
        print("1. Reiniciar el servidor: Ctrl+C y luego 'uv run python app.py'")
        print("2. Abrir http://localhost:5000")
        print("3. Usar CÉDULA como username en el login")
        print("4. Cada rol tendrá su interfaz específica")
        
    else:
        print("❌ Error corrigiendo el sistema de login")

if __name__ == "__main__":
    main()