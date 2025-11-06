#!/usr/bin/env python3
"""
Script para configurar usuarios demo del Sistema Electoral ERP
Crea usuarios de prueba para cada rol con credenciales conocidas
"""

import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db_connection
from models import User

def create_demo_users():
    """Crear usuarios demo para testing"""
    print("🔧 Configurando usuarios demo...")
    
    # Usuarios demo con credenciales conocidas
    demo_users = [
        {
            'nombre_completo': 'Super Administrador Demo',
            'cedula': '12345678',
            'telefono': '3001234567',
            'email': 'super.admin@caqueta.gov.co',
            'username': 'super_admin',
            'password': 'admin123',
            'rol': 'super_admin',
            'municipio_id': None,
            'puesto_id': None,
            'activo': True
        },
        {
            'nombre_completo': 'Administrador Departamental Demo',
            'cedula': '87654321',
            'telefono': '3007654321',
            'email': 'admin.depto@caqueta.gov.co',
            'username': 'admin_departamental',
            'password': 'admin123',
            'rol': 'admin_departamental',
            'municipio_id': None,
            'puesto_id': None,
            'activo': True
        },
        {
            'nombre_completo': 'Administrador Municipal Demo',
            'cedula': '11111111',
            'telefono': '3001111111',
            'email': 'admin.municipal@caqueta.gov.co',
            'username': 'admin_municipal',
            'password': 'admin123',
            'rol': 'admin_municipal',
            'municipio_id': 1,  # Florencia
            'puesto_id': None,
            'activo': True
        },
        {
            'nombre_completo': 'Coordinador Electoral Demo',
            'cedula': '33333333',
            'telefono': '3003333333',
            'email': 'coordinador@caqueta.gov.co',
            'username': 'coordinador_electoral',
            'password': 'coord123',
            'rol': 'coordinador_electoral',
            'municipio_id': 1,
            'puesto_id': None,
            'activo': True
        },
        {
            'nombre_completo': 'Jurado de Votación Demo',
            'cedula': '44444444',
            'telefono': '3004444444',
            'email': 'jurado@caqueta.gov.co',
            'username': 'jurado_votacion',
            'password': 'jurado123',
            'rol': 'jurado_votacion',
            'municipio_id': 1,
            'puesto_id': 1,
            'activo': True
        },
        {
            'nombre_completo': 'Testigo de Mesa Demo',
            'cedula': '22222222',
            'telefono': '3002222222',
            'email': 'testigo@caqueta.gov.co',
            'username': 'testigo_mesa',
            'password': 'testigo123',
            'rol': 'testigo',
            'municipio_id': 1,
            'puesto_id': 1,
            'activo': True
        },
        {
            'nombre_completo': 'Auditor Electoral Demo',
            'cedula': '55555555',
            'telefono': '3005555555',
            'email': 'auditor@caqueta.gov.co',
            'username': 'auditor_electoral',
            'password': 'auditor123',
            'rol': 'auditor',
            'municipio_id': None,
            'puesto_id': None,
            'activo': True
        },
        {
            'nombre_completo': 'Observador Internacional Demo',
            'cedula': '66666666',
            'telefono': '3006666666',
            'email': 'observador@international.org',
            'username': 'observador_internacional',
            'password': 'observer123',
            'rol': 'observador',
            'municipio_id': None,
            'puesto_id': None,
            'activo': True
        }
    ]
    
    try:
        db = get_db_connection()
        created_count = 0
        updated_count = 0
        
        for user_data in demo_users:
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter_by(cedula=user_data['cedula']).first()
            
            if existing_user:
                # Actualizar usuario existente
                existing_user.nombre_completo = user_data['nombre_completo']
                existing_user.telefono = user_data['telefono']
                existing_user.email = user_data['email']
                existing_user.username = user_data['username']
                existing_user.password_hash = generate_password_hash(user_data['password'])
                existing_user.rol = user_data['rol']
                existing_user.municipio_id = user_data['municipio_id']
                existing_user.puesto_id = user_data['puesto_id']
                existing_user.activo = user_data['activo']
                existing_user.fecha_actualizacion = datetime.utcnow()
                updated_count += 1
                print(f"  ✅ Actualizado: {user_data['nombre_completo']} ({user_data['rol']})")
            else:
                # Crear nuevo usuario
                new_user = User(
                    nombre_completo=user_data['nombre_completo'],
                    cedula=user_data['cedula'],
                    telefono=user_data['telefono'],
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=generate_password_hash(user_data['password']),
                    rol=user_data['rol'],
                    municipio_id=user_data['municipio_id'],
                    puesto_id=user_data['puesto_id'],
                    activo=user_data['activo'],
                    fecha_creacion=datetime.utcnow(),
                    fecha_actualizacion=datetime.utcnow()
                )
                db.add(new_user)
                created_count += 1
                print(f"  ✅ Creado: {user_data['nombre_completo']} ({user_data['rol']})")
        
        db.commit()
        print(f"\n📊 Resumen:")
        print(f"  - Usuarios creados: {created_count}")
        print(f"  - Usuarios actualizados: {updated_count}")
        print(f"  - Total usuarios demo: {len(demo_users)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando usuarios demo: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

def show_demo_credentials():
    """Mostrar credenciales de usuarios demo"""
    print("\n" + "="*60)
    print("🔑 CREDENCIALES DE USUARIOS DEMO")
    print("="*60)
    
    credentials = [
        ("Super Administrador", "12345678", "admin123", "Rojo/Azul"),
        ("Admin Departamental", "87654321", "admin123", "Azul/Cyan"),
        ("Admin Municipal", "11111111", "admin123", "Naranja/Amarillo"),
        ("Coordinador Electoral", "33333333", "coord123", "Verde/Teal"),
        ("Jurado de Votación", "44444444", "jurado123", "Azul/Cyan"),
        ("Testigo de Mesa", "22222222", "testigo123", "Púrpura/Rosa"),
        ("Auditor Electoral", "55555555", "auditor123", "Gris/Negro"),
        ("Observador Internacional", "66666666", "observer123", "Marrón/Beige")
    ]
    
    print(f"{'Rol':<25} {'Cédula':<12} {'Contraseña':<12} {'Colores UI'}")
    print("-" * 60)
    
    for rol, cedula, password, colores in credentials:
        print(f"{rol:<25} {cedula:<12} {password:<12} {colores}")
    
    print("\n📝 INSTRUCCIONES:")
    print("1. Abrir http://localhost:5000")
    print("2. Usar cualquier cédula y contraseña de la tabla")
    print("3. Cada rol tiene su interfaz única con colores específicos")
    print("4. Probar diferentes dashboards y funcionalidades")
    print("="*60)

def test_demo_login():
    """Probar login con usuarios demo"""
    print("\n🧪 Probando login de usuarios demo...")
    
    import requests
    
    base_url = "http://localhost:5000"
    test_users = [
        ("12345678", "admin123", "Super Administrador"),
        ("22222222", "testigo123", "Testigo de Mesa"),
        ("11111111", "admin123", "Admin Municipal")
    ]
    
    for cedula, password, rol in test_users:
        try:
            response = requests.post(f"{base_url}/api/auth/login", json={
                "cedula": cedula,
                "password": password
            })
            
            if response.status_code == 200:
                print(f"  ✅ {rol}: Login exitoso")
            else:
                print(f"  ❌ {rol}: Login falló - {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {rol}: Error de conexión - {e}")

def main():
    """Función principal"""
    print("🚀 CONFIGURADOR DE USUARIOS DEMO")
    print("="*50)
    
    # Crear usuarios demo
    if create_demo_users():
        print("✅ Usuarios demo configurados exitosamente")
        
        # Mostrar credenciales
        show_demo_credentials()
        
        # Probar login
        test_demo_login()
        
        print("\n🎉 ¡Sistema listo para pruebas!")
        print("Puedes acceder a http://localhost:5000 y probar cada rol")
        
    else:
        print("❌ Error configurando usuarios demo")
        sys.exit(1)

if __name__ == "__main__":
    main()