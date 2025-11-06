#!/usr/bin/env python3
"""
Test rápido de las correcciones aplicadas
"""

import requests
from pathlib import Path

def test_correcciones():
    """Probar las correcciones aplicadas"""
    
    print("🔧 Probando correcciones aplicadas...")
    
    base_url = "http://localhost:5000"
    
    # Test 1: Dashboard principal
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        print(f"  ✅ Dashboard principal: {'Funcionando' if response.status_code == 200 else 'Error ' + str(response.status_code)}")
    except Exception as e:
        print(f"  ❌ Dashboard principal: Error - {e}")
    
    # Test 2: Archivos de testigo
    testigo_css = Path("static/css/roles/testigo.css")
    testigo_js = Path("static/js/roles/testigo.js")
    
    print(f"  ✅ CSS Testigo: {'Existe' if testigo_css.exists() else 'No existe'}")
    print(f"  ✅ JS Testigo: {'Existe' if testigo_js.exists() else 'No existe'}")
    
    # Test 3: Login y token
    try:
        response = requests.post(f"{base_url}/api/auth/login", json={
            "cedula": "12345678",
            "password": "admin123"
        }, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"  ✅ Login funcionando: Token obtenido")
            
            # Test con token
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{base_url}/api/auth/me", headers=headers, timeout=5)
            print(f"  ✅ Token válido: {'Sí' if response.status_code == 200 else 'No'}")
            
        else:
            print(f"  ❌ Login: Error {response.status_code}")
    except Exception as e:
        print(f"  ❌ Login: Error - {e}")
    
    # Test 4: Páginas principales
    pages = [
        ('/', 'Inicio'),
        ('/login', 'Login'),
        ('/test-login', 'Test Login')
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ Error {response.status_code}"
            print(f"  {status} Página {name}")
        except Exception as e:
            print(f"  ❌ Página {name}: Error - {e}")

if __name__ == "__main__":
    test_correcciones()