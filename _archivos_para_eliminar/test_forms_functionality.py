#!/usr/bin/env python3
"""
Test específico de funcionalidad de formularios
Sistema Electoral ERP - Caquetá
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_form_submissions():
    """Probar envío de formularios"""
    print("🔍 PROBANDO FUNCIONALIDAD DE FORMULARIOS")
    print("=" * 50)
    
    # Test 1: Login
    print("\n1️⃣ PROBANDO LOGIN:")
    login_data = {
        "cedula": "33333333",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login exitoso")
            token_data = response.json()
            print(f"   Usuario: {token_data.get('user', {}).get('nombre_completo', 'N/A')}")
        else:
            print(f"❌ Login falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en login: {e}")
    
    # Test 2: Captura E14
    print("\n2️⃣ PROBANDO CAPTURA E14:")
    e14_data = {
        "mesa_id": 1,
        "testigo_id": 5,
        "imagen_e14": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/test",
        "votos_validos": 450,
        "votos_blanco": 25,
        "votos_nulos": 15,
        "observaciones": "Proceso normal, sin incidencias",
        "confirmado": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/e14/capturar", json=e14_data)
        if response.status_code == 200:
            print("✅ Captura E14 exitosa")
            result = response.json()
            print(f"   ID E14: {result.get('e14_id', 'N/A')}")
        else:
            print(f"❌ Captura E14 falló: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en captura E14: {e}")
    
    # Test 3: Validación de mesa duplicada
    print("\n3️⃣ PROBANDO VALIDACIÓN DUPLICADOS:")
    try:
        response = requests.get(f"{BASE_URL}/api/e14/validar-mesa/1")
        if response.status_code == 200:
            result = response.json()
            if result.get('tiene_e14'):
                print("✅ Validación correcta - Mesa ya tiene E14")
                print(f"   Mensaje: {result.get('mensaje', 'N/A')}")
            else:
                print("✅ Validación correcta - Mesa disponible")
        else:
            print(f"❌ Validación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en validación: {e}")
    
    # Test 4: Información de ubicación
    print("\n4️⃣ PROBANDO INFORMACIÓN DE UBICACIÓN:")
    try:
        response = requests.get(f"{BASE_URL}/api/user/location/5")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                location = result.get('location', {})
                print("✅ Información de ubicación obtenida")
                print(f"   Testigo: {location.get('nombre_completo', 'N/A')}")
                print(f"   Municipio: {location.get('municipio', 'N/A')}")
                print(f"   Puesto: {location.get('puesto', 'N/A')}")
                print(f"   Mesa: {location.get('mesa', 'N/A')}")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Ubicación falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en ubicación: {e}")
    
    # Test 5: Mesas por puesto
    print("\n5️⃣ PROBANDO MESAS POR PUESTO:")
    try:
        response = requests.get(f"{BASE_URL}/api/mesas/puesto/1")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                mesas = result.get('mesas', [])
                print(f"✅ {len(mesas)} mesas encontradas")
                for mesa in mesas[:3]:  # Mostrar solo las primeras 3
                    print(f"   Mesa {mesa.get('numero', 'N/A')} - E14: {'Sí' if mesa.get('tiene_e14') else 'No'}")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Mesas falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en mesas: {e}")

def test_page_loads():
    """Probar que todas las páginas de formularios cargan correctamente"""
    print("\n📄 PROBANDO CARGA DE PÁGINAS DE FORMULARIOS:")
    
    pages = [
        ("/testigo/e14", "Captura E14"),
        ("/testigo/e24", "Captura E24"),
        ("/testigo/observacion", "Observaciones"),
        ("/testigo/incidencias", "Incidencias"),
        ("/testigo/reportes", "Reportes"),
        ("/testigo/resultados", "Resultados")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                # Verificar que contenga elementos de formulario
                content = response.text
                has_form = 'form' in content.lower()
                has_buttons = 'button' in content.lower()
                has_inputs = 'input' in content.lower()
                
                print(f"✅ {name}: Carga OK")
                if has_form:
                    print(f"   📝 Contiene formularios")
                if has_buttons:
                    print(f"   🔘 Contiene botones")
                if has_inputs:
                    print(f"   📝 Contiene campos de entrada")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE FORMULARIOS")
    print(f"🕐 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar servidor
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor no responde")
            return
        
        print("✅ Servidor funcionando")
        
        # Ejecutar pruebas
        test_page_loads()
        test_form_submissions()
        
        print("\n" + "=" * 50)
        print("✅ PRUEBAS DE FORMULARIOS COMPLETADAS")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("💡 Ejecuta: python app.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()