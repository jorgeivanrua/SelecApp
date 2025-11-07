#!/usr/bin/env python3
"""
Pruebas comprehensivas del sistema de login
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import requests
import json

def test_login_without_data():
    """Probar login sin datos"""
    print("🧪 Probando login sin datos...")
    try:
        response = requests.post("http://127.0.0.1:5000/api/users/auth/login")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_login_invalid_credentials():
    """Probar login con credenciales inválidas"""
    print("\n🧪 Probando login con credenciales inválidas...")
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/users/auth/login",
            json={"username": "invalid", "password": "invalid"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_validate_without_token():
    """Probar validación sin token"""
    print("\n🧪 Probando validación sin token...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/users/auth/validate")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_validate_invalid_token():
    """Probar validación con token inválido"""
    print("\n🧪 Probando validación con token inválido...")
    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/users/auth/validate",
            headers={"Authorization": "Bearer invalid_token"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_validate_malformed_header():
    """Probar validación con header malformado"""
    print("\n🧪 Probando validación con header malformado...")
    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/users/auth/validate",
            headers={"Authorization": "InvalidFormat token"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_complete_flow():
    """Probar flujo completo de login y validación"""
    print("\n🧪 Probando flujo completo...")
    try:
        # 1. Login
        login_response = requests.post(
            "http://127.0.0.1:5000/api/users/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('token')
            print(f"✅ Login exitoso, token obtenido")
            
            # 2. Validar token
            validate_response = requests.get(
                "http://127.0.0.1:5000/api/users/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Validación - Status: {validate_response.status_code}")
            print(f"Validación - Response: {validate_response.json()}")
            
            # 3. Probar logout
            logout_response = requests.post(
                "http://127.0.0.1:5000/api/users/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Logout - Status: {logout_response.status_code}")
            print(f"Logout - Response: {logout_response.json()}")
            
        else:
            print(f"❌ Login falló: {login_response.json()}")
            
    except Exception as e:
        print(f"Error en flujo completo: {e}")

def test_dashboard_endpoint():
    """Probar endpoint de dashboard que puede requerir autenticación"""
    print("\n🧪 Probando endpoint de dashboard...")
    try:
        # Sin token
        response = requests.get("http://127.0.0.1:5000/api/dashboard/overview")
        print(f"Dashboard sin token - Status: {response.status_code}")
        print(f"Dashboard sin token - Response: {response.json()}")
        
        # Con token
        login_response = requests.post(
            "http://127.0.0.1:5000/api/users/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            
            response_with_token = requests.get(
                "http://127.0.0.1:5000/api/dashboard/overview?user_id=1",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"Dashboard con token - Status: {response_with_token.status_code}")
            print(f"Dashboard con token - Response: {response_with_token.json()}")
            
    except Exception as e:
        print(f"Error probando dashboard: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS COMPREHENSIVAS DEL SISTEMA DE LOGIN")
    print("=" * 60)
    
    test_login_without_data()
    test_login_invalid_credentials()
    test_validate_without_token()
    test_validate_invalid_token()
    test_validate_malformed_header()
    test_complete_flow()
    test_dashboard_endpoint()
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")

if __name__ == '__main__':
    main()