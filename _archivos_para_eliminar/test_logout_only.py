#!/usr/bin/env python3
"""
Prueba específica del logout
"""

import requests
import json

def test_logout():
    """Probar solo el logout"""
    try:
        # 1. Login
        print("1. Haciendo login...")
        login_response = requests.post(
            "http://127.0.0.1:5000/api/users/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.json()}")
            return
        
        login_data = login_response.json()
        token = login_data.get('token')
        print(f"✅ Login exitoso, token: {token[:50]}...")
        
        # 2. Logout
        print("\n2. Haciendo logout...")
        logout_response = requests.post(
            "http://127.0.0.1:5000/api/users/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {logout_response.status_code}")
        print(f"Response: {logout_response.json()}")
        
        # 3. Verificar que el token ya no es válido
        print("\n3. Verificando que el token ya no es válido...")
        validate_response = requests.get(
            "http://127.0.0.1:5000/api/users/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Validación después del logout - Status: {validate_response.status_code}")
        print(f"Validación después del logout - Response: {validate_response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_logout()