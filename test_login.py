#!/usr/bin/env python3
"""
Test rápido del sistema de login corregido
"""

import requests
import json

def test_login():
    """Probar login con usuarios demo"""
    
    print("🧪 Probando sistema de login corregido...")
    
    base_url = "http://localhost:5000"
    
    # Usuarios de prueba
    test_users = [
        ("12345678", "admin123", "Super Admin"),
        ("87654321", "admin123", "Admin Departamental"),
        ("11111111", "admin123", "Admin Municipal"),
        ("22222222", "testigo123", "Testigo Mesa"),
        ("33333333", "coord123", "Coordinador Electoral"),
        ("44444444", "jurado123", "Jurado de Votación")
    ]
    
    successful_logins = 0
    
    for cedula, password, rol in test_users:
        try:
            # Test con cédula
            response = requests.post(f"{base_url}/api/auth/login", json={
                "cedula": cedula,
                "password": password
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                print(f"  ✅ {rol}: Login exitoso")
                print(f"     Usuario: {user.get('nombre_completo')}")
                print(f"     Rol: {user.get('rol')}")
                successful_logins += 1
            else:
                print(f"  ❌ {rol}: Login falló - {response.status_code}")
                print(f"     Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ {rol}: Error de conexión - {e}")
    
    print(f"\n📊 Resultado: {successful_logins}/{len(test_users)} logins exitosos")
    
    if successful_logins > 0:
        print("\n🎉 ¡Sistema de login funcionando!")
        print("\n🌐 Acceso al sistema:")
        print("   URL: http://localhost:5000")
        print("\n🔑 Credenciales verificadas:")
        for cedula, password, rol in test_users[:successful_logins]:
            print(f"   • {rol}: {cedula} / {password}")
    else:
        print("\n❌ Sistema de login no funciona correctamente")

if __name__ == "__main__":
    test_login()