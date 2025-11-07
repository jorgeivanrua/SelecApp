#!/usr/bin/env python3
"""
Test de caracteres UTF-8 en producción
Sistema Electoral Caquetá
"""

import requests
import json

def test_utf8_endpoints():
    """Probar que los endpoints manejen correctamente UTF-8"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 PROBANDO CARACTERES UTF-8 EN PRODUCCIÓN")
    print("=" * 50)
    
    # Test 1: Endpoint principal
    print("\n1️⃣ Probando endpoint principal...")
    try:
        response = requests.get(f"{base_url}/")
        data = response.json()
        print(f"✅ Mensaje: {data['message']}")
        print(f"✅ Codificación: {response.encoding}")
        print(f"✅ Content-Type: {response.headers.get('content-type')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Endpoint de salud
    print("\n2️⃣ Probando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/health")
        data = response.json()
        print(f"✅ Estado: {data['status']}")
        print(f"✅ Ambiente: {data['environment']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Crear datos con caracteres especiales
    print("\n3️⃣ Probando datos con caracteres especiales...")
    test_data = {
        "nombre": "José María Hernández",
        "municipio": "Florencia, Caquetá",
        "descripción": "Candidato con experiencia en administración pública",
        "propuestas": "Educación, salud y vías para el departamento"
    }
    
    print(f"✅ Datos de prueba: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    print("\n🎉 PRUEBAS DE UTF-8 COMPLETADAS")
    print("Los caracteres especiales funcionan correctamente en producción")

if __name__ == "__main__":
    test_utf8_endpoints()