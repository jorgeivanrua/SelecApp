#!/usr/bin/env python3
"""
Script para crear usuarios demo en la base de datos SQLite
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_demo_users():
    """Crear usuarios demo en la base de datos"""
    
    print("🔄 Creando usuarios demo...")
    
    # Conectar a la base de datos
    db_path = 'caqueta_electoral.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Usuarios demo
    demo_users = [
        {
            'username': 'superadmin',
            'cedula': '12345678',
            'nombre_completo': 'Super Administrador',
            'email': 'superadmin@caqueta.gov.co',
            'password': 'demo123',
            'rol': 'super_admin'
        },
        {
            'username': 'coord_dept',
            'cedula': '87654321',
            'nombre_completo': 'Carlos Mendoza - Coordinador Departamental',
            'email': 'coord.dept@caqueta.gov.co',
            'password': 'demo123',
            'rol': 'coordinador_departamental'
        },
        {
            'username': 'coord_mun',
            'cedula': '11111111',
            'nombre_completo': 'Ana Patricia Ruiz - Coordinadora Municipal',
            'email': 'coord.mun@florencia.gov.co',
            'password': 'demo123',
            'rol': 'coordinador_municipal'
        },
        {
            'username': 'coord_puesto',
            'cedula': '22222222',
            'nombre_completo': 'Miguel Torres - Coordinador de Puesto',
            'email': 'coord.puesto@florencia.gov.co',
            'password': 'demo123',
            'rol': 'coordinador_puesto'
        },
        {
            'username': 'testigo_electoral',
            'cedula': '33333333',
            'nombre_completo': 'Laura González - Testigo Electoral',
            'email': 'testigo.electoral@partido.com',
            'password': 'demo123',
            'rol': 'testigo_electoral'
        },
        {
            'username': 'testigo_mesa',
            'cedula': '44444444',
            'nombre_completo': 'Juan Pérez - Testigo de Mesa',
            'email': 'testigo.mesa@partido.com',
            'password': 'demo123',
            'rol': 'testigo_mesa'
        },
        {
            'username': 'jurado',
            'cedula': '55555555',
            'nombre_completo': 'María Rodríguez - Jurado de Votación',
            'email': 'jurado@registraduria.gov.co',
            'password': 'demo123',
            'rol': 'jurado_votacion'
        },
        {
            'username': 'auditor',
            'cedula': '66666666',
            'nombre_completo': 'Roberto Silva - Auditor Electoral',
            'email': 'auditor@contraloria.gov.co',
            'password': 'demo123',
            'rol': 'auditor_electoral'
        }
    ]
    
    # Insertar usuarios
    for user in demo_users:
        try:
            password_hash = generate_password_hash(user['password'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (username, cedula, nombre_completo, email, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                user['username'],
                user['cedula'],
                user['nombre_completo'],
                user['email'],
                password_hash,
                user['rol']
            ))
            
            print(f"✅ Usuario creado: {user['nombre_completo']} ({user['rol']})")
            
        except sqlite3.IntegrityError as e:
            print(f"⚠️  Usuario ya existe: {user['username']}")
        except Exception as e:
            print(f"❌ Error creando usuario {user['username']}: {e}")
    
    # Crear tabla de municipios si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS municipios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            departamento TEXT DEFAULT 'Caquetá',
            activo INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insertar municipios del Caquetá
    municipios = [
        ('18001', 'Florencia'),
        ('18029', 'San Vicente del Caguán'),
        ('18592', 'Puerto Rico'),
        ('18479', 'El Paujil'),
        ('18410', 'La Montañita'),
        ('18205', 'Curillo'),
        ('18247', 'El Doncello'),
        ('18256', 'Belén de los Andaquíes'),
        ('18150', 'Cartagena del Chairá'),
        ('18460', 'Morelia'),
        ('18753', 'San José del Fragua'),
        ('18610', 'Albania'),
        ('18785', 'Solano'),
        ('18550', 'Milán'),
        ('18756', 'Solita'),
        ('18685', 'Valparaíso')
    ]
    
    for codigo, nombre in municipios:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO municipios (codigo, nombre)
                VALUES (?, ?)
            """, (codigo, nombre))
        except Exception as e:
            print(f"❌ Error insertando municipio {nombre}: {e}")
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos inicializada con usuarios demo")
    print("\n📋 USUARIOS DEMO CREADOS:")
    print("=" * 50)
    for user in demo_users:
        print(f"👤 {user['nombre_completo']}")
        print(f"   Cédula: {user['cedula']}")
        print(f"   Contraseña: {user['password']}")
        print(f"   Rol: {user['rol']}")
        print()

if __name__ == "__main__":
    try:
        create_demo_users()
        print("🎉 Usuarios demo creados exitosamente!")
    except Exception as e:
        print(f"❌ Error: {e}")