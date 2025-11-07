#!/usr/bin/env python3
"""
Script de prueba para el sistema de login
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import requests
import json
from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime

def setup_test_user():
    """Crear usuario de prueba en la base de datos"""
    try:
        conn = sqlite3.connect('electoral_system.db')
        cursor = conn.cursor()
        
        # Crear tabla de usuarios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo VARCHAR(255) NOT NULL,
                cedula VARCHAR(20) UNIQUE NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(255),
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) NOT NULL,
                municipio_id INTEGER,
                puesto_id INTEGER,
                activo BOOLEAN DEFAULT 1,
                ultimo_login DATETIME,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME
            )
        """)
        
        # Verificar si ya existe el usuario de prueba
        cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        if cursor.fetchone():
            print("✅ Usuario de prueba 'admin' ya existe")
            conn.close()
            return
        
        # Crear usuario de prueba
        password_hash = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT INTO users 
            (nombre_completo, cedula, username, password_hash, rol, activo, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'Administrador de Prueba',
            '12345678',
            'admin',
            password_hash,
            'super_admin',
            True,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Usuario de prueba creado:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Rol: super_admin")
        
    except Exception as e:
        print(f"❌ Error creando usuario de prueba: {e}")

def test_login_endpoint():
    """Probar el endpoint de login"""
    try:
        # URL del endpoint de login
        login_url = "http://127.0.0.1:5000/api/users/auth/login"
        
        # Datos de login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print(f"🔍 Probando login en: {login_url}")
        print(f"📝 Datos: {json.dumps(login_data, indent=2)}")
        
        # Realizar petición POST
        response = requests.post(
            login_url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📋 Response Data:")
            print(json.dumps(response_data, indent=2, default=str))
            
            if response.status_code == 200 and response_data.get('success'):
                print("✅ LOGIN EXITOSO!")
                
                # Extraer token para pruebas adicionales
                token = response_data.get('token')
                if token:
                    print(f"🔑 Token JWT obtenido: {token[:50]}...")
                    return token
                    
            else:
                print("❌ LOGIN FALLIDO!")
                print(f"Error: {response_data.get('error', 'Error desconocido')}")
                
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: ¿Está ejecutándose la aplicación en http://127.0.0.1:5000?")
    except requests.exceptions.Timeout:
        print("❌ Timeout: La aplicación no responde")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    return None

def test_protected_endpoint(token):
    """Probar endpoint protegido con token"""
    if not token:
        print("⚠️  No hay token para probar endpoint protegido")
        return
    
    try:
        # Probar endpoint de validación de sesión
        validate_url = "http://127.0.0.1:5000/api/users/auth/validate"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔍 Probando validación de token en: {validate_url}")
        
        response = requests.get(validate_url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📋 Response Data:")
            print(json.dumps(response_data, indent=2, default=str))
            
            if response.status_code == 200:
                print("✅ TOKEN VÁLIDO!")
            else:
                print("❌ TOKEN INVÁLIDO!")
                
        except json.JSONDecodeError:
            print(f"❌ Respuesta no es JSON válido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error probando endpoint protegido: {e}")

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE LOGIN")
    print("=" * 60)
    
    # Paso 1: Configurar usuario de prueba
    print("\n1️⃣ Configurando usuario de prueba...")
    setup_test_user()
    
    # Paso 2: Probar login
    print("\n2️⃣ Probando endpoint de login...")
    token = test_login_endpoint()
    
    # Paso 3: Probar endpoint protegido
    print("\n3️⃣ Probando endpoint protegido...")
    test_protected_endpoint(token)
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")

if __name__ == '__main__':
    main()