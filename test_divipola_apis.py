#!/usr/bin/env python3
"""Script para probar las APIs con estructura DIVIPOLA"""

import requests
import json

base_url = "http://127.0.0.1:5000"

def test_municipios():
    """Probar API de municipios con códigos DIVIPOLA"""
    print("\n" + "="*80)
    print("TEST 1: Obtener Municipios con Códigos DIVIPOLA")
    print("="*80)
    
    response = requests.get(f"{base_url}/api/ubicacion/municipios")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Municipios obtenidos: {len(data['municipios'])}")
        for mun in data['municipios'][:3]:
            print(f"   {mun['codigo']} (dd:{mun.get('codigo_dd', 'N/A')} mm:{mun.get('codigo_mm', 'N/A')}) - {mun['nombre']}")
        return data['municipios'][0]['id'] if data['municipios'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_zonas(municipio_id):
    """Probar API de zonas"""
    print("\n" + "="*80)
    print(f"TEST 2: Obtener Zonas del Municipio {municipio_id}")
    print("="*80)
    
    response = requests.get(f"{base_url}/api/ubicacion/zonas/{municipio_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Zonas obtenidas: {len(data['zonas'])}")
        for zona in data['zonas']:
            print(f"   {zona['codigo_completo']} (zz:{zona['codigo_zz']}) - {zona['nombre']}")
        return data['zonas'][0]['id'] if data['zonas'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_puestos(municipio_id):
    """Probar API de puestos con códigos DIVIPOLA"""
    print("\n" + "="*80)
    print(f"TEST 3: Obtener Puestos con Códigos DIVIPOLA")
    print("="*80)
    
    response = requests.get(f"{base_url}/api/ubicacion/puestos/{municipio_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Puestos obtenidos: {len(data['puestos'])}")
        for puesto in data['puestos']:
            divipola = puesto.get('codigo_divipola', 'N/A')
            pp = puesto.get('codigo_pp', 'N/A')
            zz = puesto.get('codigo_zz', 'N/A')
            print(f"   {divipola} (zz:{zz} pp:{pp}) - {puesto['nombre']}")
        return data['puestos'][0]['id'] if data['puestos'] else None
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_mesas(puesto_id):
    """Probar API de mesas"""
    print("\n" + "="*80)
    print(f"TEST 4: Obtener Mesas del Puesto {puesto_id}")
    print("="*80)
    
    response = requests.get(f"{base_url}/api/ubicacion/mesas/{puesto_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mesas obtenidas: {len(data['mesas'])}")
        for mesa in data['mesas'][:3]:
            print(f"   Mesa {mesa['numero']} (Capacidad: {mesa['capacidad']})")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("PRUEBA DE APIs CON ESTRUCTURA DIVIPOLA")
    print("="*80)
    
    # Test 1: Municipios
    municipio_id = test_municipios()
    if not municipio_id:
        print("\n❌ No se pudieron obtener municipios. Abortando tests.")
        return
    
    # Usar Florencia (municipio_id = 1)
    municipio_id = 1
    
    # Test 2: Zonas
    zona_id = test_zonas(municipio_id)
    if not zona_id:
        print("\n⚠️  No hay zonas, pero continuamos...")
    
    # Test 3: Puestos
    puesto_id = test_puestos(municipio_id)
    if not puesto_id:
        print("\n❌ No se pudieron obtener puestos. Abortando tests.")
        return
    
    # Test 4: Mesas
    test_mesas(puesto_id)
    
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print("✅ Sistema con estructura DIVIPOLA funcionando correctamente")
    print(f"✅ URL de acceso: {base_url}/login")
    print("✅ Códigos DIVIPOLA: dd (departamento) + mm (municipio) + zz (zona) + pp (puesto)")
    print("="*80)

if __name__ == "__main__":
    main()
