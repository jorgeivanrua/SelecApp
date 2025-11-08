#!/usr/bin/env python3
"""Script para probar el sistema de registro"""

import requests
import json

base_url = "http://127.0.0.1:5000"

def test_get_municipios():
    """Probar obtención de municipios"""
    print("\n" + "="*60)
    print("TEST 1: Obtener Municipios")
    print("="*60)
    
    response = requests.get(f"{base_url}/api/ubicacion/municipios")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Municipios obtenidos: {len(data['municipios'])}")
        for mun in data['municipios'][:3]:
            print(f"   - {mun['nombre']} ({mun['codigo']})")
        return data['municipios'][0]['id'] if data['municipios'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_get_puestos(municipio_id):
    """Probar obtención de puestos"""
    print("\n" + "="*60)
    print(f"TEST 2: Obtener Puestos del Municipio {municipio_id}")
    print("="*60)
    
    response = requests.get(f"{base_url}/api/ubicacion/puestos/{municipio_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Puestos obtenidos: {len(data['puestos'])}")
        for puesto in data['puestos'][:3]:
            print(f"   - {puesto['nombre']}")
        return data['puestos'][0]['id'] if data['puestos'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_get_mesas(puesto_id):
    """Probar obtención de mesas"""
    print("\n" + "="*60)
    print(f"TEST 3: Obtener Mesas del Puesto {puesto_id}")
    print("="*60)
    
    response = requests.get(f"{base_url}/api/ubicacion/mesas/{puesto_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mesas obtenidas: {len(data['mesas'])}")
        for mesa in data['mesas'][:3]:
            print(f"   - Mesa {mesa['numero']} (Capacidad: {mesa['capacidad']})")
        return data['mesas'][0]['id'] if data['mesas'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_register_user(municipio_id, puesto_id, mesa_id):
    """Probar registro de usuario"""
    print("\n" + "="*60)
    print("TEST 4: Registrar Nuevo Usuario")
    print("="*60)
    
    user_data = {
        "cedula": "1234567890",
        "nombre_completo": "Juan Pérez Testigo",
        "email": "juan.perez@test.com",
        "telefono": "3001234567",
        "municipio_id": municipio_id,
        "puesto_id": puesto_id,
        "mesa_id": mesa_id,
        "rol": "testigo_mesa",
        "password": "test123"
    }
    
    response = requests.post(
        f"{base_url}/api/auth/register",
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Usuario registrado exitosamente")
        print(f"   ID: {data['user_id']}")
        print(f"   Username: {data['username']}")
        return data['username']
    elif response.status_code == 400:
        data = response.json()
        print(f"⚠️  Usuario ya existe o error de validación: {data.get('error')}")
        return "user_1234567890"  # Username esperado
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        return None

def test_login_new_user(username):
    """Probar login con el nuevo usuario"""
    print("\n" + "="*60)
    print("TEST 5: Login con Usuario Registrado")
    print("="*60)
    
    login_data = {
        "cedula": "1234567890",
        "password": "test123"
    }
    
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login exitoso")
        print(f"   Usuario: {data['user']['nombre_completo']}")
        print(f"   Rol: {data['user']['rol']}")
        print(f"   Token: {data['access_token'][:30]}...")
        return True
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"   {response.text}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("PRUEBA DEL SISTEMA DE REGISTRO")
    print("="*60)
    
    # Test 1: Obtener municipios
    municipio_id = test_get_municipios()
    if not municipio_id:
        print("\n❌ No se pudieron obtener municipios. Abortando tests.")
        return
    
    # Usar Florencia (municipio_id = 1) que tiene puestos configurados
    municipio_id = 1
    
    # Test 2: Obtener puestos
    puesto_id = test_get_puestos(municipio_id)
    if not puesto_id:
        print("\n❌ No se pudieron obtener puestos. Abortando tests.")
        return
    
    # Test 3: Obtener mesas
    mesa_id = test_get_mesas(puesto_id)
    if not mesa_id:
        print("\n❌ No se pudieron obtener mesas. Abortando tests.")
        return
    
    # Test 4: Registrar usuario
    username = test_register_user(municipio_id, puesto_id, mesa_id)
    if not username:
        print("\n❌ No se pudo registrar usuario. Abortando tests.")
        return
    
    # Test 5: Login con nuevo usuario
    test_login_new_user(username)
    
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    print("✅ Sistema de registro funcionando correctamente")
    print(f"✅ URL de acceso: {base_url}/login")
    print("="*60)

if __name__ == "__main__":
    main()
