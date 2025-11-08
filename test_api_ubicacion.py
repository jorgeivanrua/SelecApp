#!/usr/bin/env python3
import requests

base_url = 'http://127.0.0.1:5000'

print("=== PROBANDO API DE UBICACIÓN ===\n")

# Test 1: Municipios
print("1. GET /api/ubicacion/municipios")
response = requests.get(f'{base_url}/api/ubicacion/municipios')
if response.ok:
    data = response.json()
    print(f"   ✅ {len(data['municipios'])} municipios")
    for mun in data['municipios'][:5]:
        print(f"      - {mun['nombre']} (ID: {mun['id']})")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 2: Zonas de Florencia (ID 7)
print("\n2. GET /api/ubicacion/zonas/7")
response = requests.get(f'{base_url}/api/ubicacion/zonas/7')
if response.ok:
    data = response.json()
    print(f"   ✅ {len(data['zonas'])} zonas")
    for zona in data['zonas']:
        print(f"      - {zona['nombre']} - {zona['descripcion']} (ID: {zona['id']})")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 3: Puestos de Zona 01 (ID 20)
print("\n3. GET /api/ubicacion/puestos/20")
response = requests.get(f'{base_url}/api/ubicacion/puestos/20')
if response.ok:
    data = response.json()
    print(f"   ✅ {len(data['puestos'])} puestos")
    for puesto in data['puestos']:
        print(f"      - {puesto['nombre']} (ID: {puesto['id']})")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test 4: Mesas del Puesto 4
print("\n4. GET /api/ubicacion/mesas/4")
response = requests.get(f'{base_url}/api/ubicacion/mesas/4')
if response.ok:
    data = response.json()
    print(f"   ✅ {len(data['mesas'])} mesas")
    for mesa in data['mesas'][:5]:
        print(f"      - Mesa {mesa['numero']} ({mesa['votantes_habilitados']} votantes, ID: {mesa['id']})")
else:
    print(f"   ❌ Error: {response.status_code}")
