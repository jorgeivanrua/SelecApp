#!/usr/bin/env python3
"""
Test directo de login
"""

import requests
import json

def test_login():
    url = "http://localhost:5000/api/users/auth/login"
    
    # Datos de login
    login_data = {
        "username": "admin",
        "password": "demo123"
    }
    
    print("🧪 Probando login...")
    print(f"URL: {url}")
    print(f"Usuario: {login_data['username']}")
    print(f"Contraseña: {login_data['password']}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=login_data)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"\n📄 Contenido:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
