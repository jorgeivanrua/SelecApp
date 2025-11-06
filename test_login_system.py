#!/usr/bin/env python3
"""
Script para probar el sistema de login y roles
"""

import requests
import json

def test_login_system():
    """Probar el sistema de login con diferentes usuarios"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Usuarios de prueba
    test_users = [
        {
            'cedula': '12345678',
            'password': 'demo123',
            'expected_role': 'super_admin',
            'name': 'Super Administrador'
        },
        {
            'cedula': '87654321',
            'password': 'demo123',
            'expected_role': 'coordinador_departamental',
            'name': 'Coordinador Departamental'
        },
        {
            'cedula': '11111111',
            'password': 'demo123',
            'expected_role': 'coordinador_municipal',
            'name': 'Coordinador Municipal'
        },
        {
            'cedula': '22222222',
            'password': 'demo123',
            'expected_role': 'coordinador_puesto',
            'name': 'Coordinador de Puesto'
        },
        {
            'cedula': '33333333',
            'password': 'demo123',
            'expected_role': 'testigo_electoral',
            'name': 'Testigo Electoral'
        }
    ]
    
    print("🔍 PROBANDO SISTEMA DE LOGIN Y ROLES")
    print("=" * 50)
    
    for user in test_users:
        print(f"\n👤 Probando: {user['name']}")
        print(f"   Cédula: {user['cedula']}")
        
        try:
            # Hacer login
            response = requests.post(f"{base_url}/api/auth/login", 
                                   json={
                                       'cedula': user['cedula'],
                                       'password': user['password']
                                   },
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                actual_role = data['user']['rol']
                
                if actual_role == user['expected_role']:
                    print(f"   ✅ Login exitoso - Rol correcto: {actual_role}")
                    
                    # Probar acceso al dashboard del rol
                    dashboard_url = f"{base_url}/dashboard/{actual_role}"
                    dashboard_response = requests.get(dashboard_url, timeout=5)
                    
                    if dashboard_response.status_code == 200:
                        print(f"   ✅ Dashboard accesible: {dashboard_url}")
                    else:
                        print(f"   ❌ Dashboard no accesible: {dashboard_response.status_code}")
                        
                else:
                    print(f"   ❌ Rol incorrecto - Esperado: {user['expected_role']}, Actual: {actual_role}")
            else:
                print(f"   ❌ Login falló: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"      Error: {error_data.get('error', 'Unknown error')}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 PRUEBA DE ACCESO DIRECTO A DASHBOARDS")
    print("=" * 50)
    
    # Probar acceso directo a dashboards
    dashboards_to_test = [
        'testigo_electoral',
        'coordinador_puesto',
        'coordinador_municipal',
        'coordinador_departamental'
    ]
    
    for dashboard in dashboards_to_test:
        try:
            url = f"{base_url}/dashboard/{dashboard}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {dashboard}: Accesible")
            else:
                print(f"❌ {dashboard}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {dashboard}: Error de conexión")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    try:
        test_login_system()
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"❌ Error general: {e}")