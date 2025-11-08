#!/usr/bin/env python3
"""Script para probar el login del super admin"""

import requests
import json

def test_login():
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 80)
    print("PRUEBA DE LOGIN - SUPER ADMIN")
    print("=" * 80)
    
    # Intentar login con diferentes contraseñas comunes
    passwords_to_try = [
        "admin123",
        "demo123", 
        "superadmin",
        "admin",
        "123456"
    ]
    
    for password in passwords_to_try:
        print(f"\n🔐 Intentando login con: superadmin / {password}")
        
        try:
            # Crear sesión
            session = requests.Session()
            
            # Obtener la página de login primero (para cookies)
            response = session.get(f"{base_url}/login")
            
            # Intentar login usando la API
            login_data = {
                "cedula": "superadmin",  # Puede ser username o cédula
                "password": password
            }
            
            response = session.post(
                f"{base_url}/api/auth/login",
                json=login_data,
                allow_redirects=False
            )
            
            if response.status_code == 200:  # API devuelve 200 con JSON
                result = response.json()
                if result.get('access_token'):  # Login exitoso devuelve access_token
                    print(f"   ✅ LOGIN EXITOSO con contraseña: {password}")
                    print(f"   Usuario: {result.get('user', {}).get('nombre_completo', 'N/A')}")
                    print(f"   Rol: {result.get('user', {}).get('rol', 'N/A')}")
                    print(f"   Token: {result.get('access_token', 'N/A')[:20]}...")
                    
                    # Intentar acceder al dashboard
                    dashboard_response = session.get(f"{base_url}/dashboard/super_admin")
                    if dashboard_response.status_code == 200:
                        print(f"   ✅ Acceso al dashboard exitoso")
                    else:
                        print(f"   ⚠️  Dashboard responde con código: {dashboard_response.status_code}")
                    
                    return True
                else:
                    print(f"   ❌ Login fallido: {result.get('error', 'Error desconocido')}")
            else:
                try:
                    error_msg = response.json().get('error', 'Error desconocido')
                    print(f"   ❌ Login fallido: {error_msg}")
                except:
                    print(f"   ❌ Login fallido (código: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("❌ No se pudo hacer login con ninguna contraseña común")
    print("=" * 80)
    return False

if __name__ == "__main__":
    test_login()
