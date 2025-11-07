#!/usr/bin/env python3
"""
Script de prueba para verificar dashboards específicos por rol
"""

import requests
import time

def test_dashboard_routes():
    """Probar todas las rutas de dashboards por rol"""
    base_url = "http://localhost:5000"
    
    # Roles a probar
    roles_to_test = [
        'super_admin',
        'admin_departamental', 
        'admin_municipal',
        'coordinador_electoral',
        'jurado_votacion',
        'testigo_mesa',
        'testigo',  # Alias
        'auditor',  # Alias
        'auditor_electoral',
        'observador',  # Alias
        'observador_internacional'
    ]
    
    print("🔍 Probando dashboards específicos por rol...")
    print("=" * 50)
    
    for role in roles_to_test:
        try:
            url = f"{base_url}/dashboard/{role}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {role}: OK (200)")
            elif response.status_code == 404:
                print(f"❌ {role}: Template no encontrado (404)")
            else:
                print(f"⚠️  {role}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {role}: Error de conexión - {e}")
    
    print("\n" + "=" * 50)
    
    # Probar rutas adicionales
    additional_routes = [
        '/dashboard',
        '/audit/start',
        '/observation/new',
        '/users',
        '/municipalities',
        '/tables',
        '/voting/register',
        '/observations/new'
    ]
    
    print("🔍 Probando rutas adicionales...")
    print("=" * 50)
    
    for route in additional_routes:
        try:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {route}: OK (200)")
            else:
                print(f"⚠️  {route}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {route}: Error de conexión - {e}")
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas!")

def test_role_mapping():
    """Probar el mapeo de roles y aliases"""
    print("\n🔍 Probando mapeo de roles y aliases...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Probar aliases específicos
    aliases = {
        'testigo': 'testigo_mesa',
        'auditor': 'auditor_electoral', 
        'observador': 'observador_internacional'
    }
    
    for alias, expected_role in aliases.items():
        try:
            url = f"{base_url}/dashboard/{alias}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Alias '{alias}' -> '{expected_role}': OK")
            else:
                print(f"❌ Alias '{alias}' -> '{expected_role}': Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Alias '{alias}': Error - {e}")

def test_invalid_roles():
    """Probar roles inválidos"""
    print("\n🔍 Probando roles inválidos...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    invalid_roles = ['invalid_role', 'fake_admin', 'test_user', '']
    
    for role in invalid_roles:
        try:
            url = f"{base_url}/dashboard/{role}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 404:
                print(f"✅ '{role}': Correctamente rechazado (404)")
            else:
                print(f"⚠️  '{role}': Status inesperado {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ '{role}': Error - {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de dashboards...")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
    print()
    
    # Esperar un momento para que el servidor esté listo
    time.sleep(2)
    
    try:
        # Verificar que el servidor esté disponible
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor disponible")
            
            test_dashboard_routes()
            test_role_mapping()
            test_invalid_roles()
            
        else:
            print("❌ Servidor no disponible")
            
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose?")