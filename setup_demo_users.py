#!/usr/bin/env python3
"""
Script para crear usuarios de demostración
Sistema Electoral Caquetá
"""

import sqlite3
import hashlib
from datetime import datetime

def hash_password(password):
    """Hashear contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_demo_users():
    """Crear usuarios de demostración"""
    
    print("🔧 Configurando usuarios de demostración...")
    print("=" * 50)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('electoral_system_prod.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios si no existe
    # La tabla ya existe, no necesitamos crearla
    
    # Usuarios de demostración
    demo_users = [
        {
            'username': 'admin',
            'password_hash': hash_password('demo123'),
            'nombre_completo': 'Administrador del Sistema',
            'cedula': '12345678',
            'email': 'admin@caqueta.gov.co',
            'telefono': '3001234567',
            'rol': 'super_admin'
        },
        {
            'username': 'coord1',
            'password_hash': hash_password('demo123'),
            'nombre_completo': 'Coordinador Municipal',
            'cedula': '23456789',
            'email': 'coordinador@caqueta.gov.co',
            'telefono': '3002345678',
            'rol': 'coordinador_municipal'
        },
        {
            'username': 'testigo1',
            'password_hash': hash_password('demo123'),
            'nombre_completo': 'Testigo Electoral',
            'cedula': '34567890',
            'email': 'testigo@caqueta.gov.co',
            'telefono': '3003456789',
            'rol': 'testigo_mesa'
        }
    ]
    
    # Insertar usuarios
    for user in demo_users:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (username, password_hash, nombre_completo, cedula, email, telefono, rol, activo, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['username'],
                user['password_hash'],
                user['nombre_completo'],
                user['cedula'],
                user['email'],
                user['telefono'],
                user['rol'],
                True,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            print(f"✅ Usuario creado: {user['username']} ({user['rol']})")
        except Exception as e:
            print(f"❌ Error creando usuario {user['username']}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Usuarios de demostración configurados")
    print("\n📋 CREDENCIALES DE ACCESO:")
    print("-" * 50)
    print("👤 Admin:       admin / demo123")
    print("👤 Coordinador: coord1 / demo123")
    print("👤 Testigo:     testigo1 / demo123")
    print("-" * 50)

if __name__ == "__main__":
    setup_demo_users()
