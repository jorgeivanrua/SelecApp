#!/usr/bin/env python3
"""Script para probar las zonas con la convención oficial"""

import requests

base_url = "http://127.0.0.1:5000"

print("="*80)
print("PRUEBA DE ZONAS CON CONVENCIÓN DIVIPOLA")
print("="*80)

# Probar zonas de Florencia
response = requests.get(f"{base_url}/api/ubicacion/zonas/1")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Zonas de Florencia: {len(data['zonas'])}")
    print("\nConvención:")
    print("  01-89: Zonas urbanas")
    print("  90:    Puesto censo")
    print("  98:    Cárceles")
    print("  99:    Zona rural")
    print("\nZonas encontradas:")
    for zona in data['zonas']:
        codigo = zona['codigo_zz']
        nombre = zona['nombre']
        completo = zona.get('codigo_completo', 'N/A')
        print(f"  {codigo} - {nombre} ({completo})")
else:
    print(f"❌ Error: {response.status_code}")

print("\n" + "="*80)
