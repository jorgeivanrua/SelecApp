#!/usr/bin/env python3
"""
Test de la API de testigo
"""

import requests

# Test con usuario demo testigo (cédula 1000000001)
user_id = 9  # Primer testigo demo creado

print("=" * 70)
print("TEST API TESTIGO")
print("=" * 70)

try:
    response = requests.get(f'http://127.0.0.1:5000/api/testigo/info/{user_id}')
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse:")
    
    if response.ok:
        data = response.json()
        print(f"Success: {data.get('success')}")
        
        if data.get('success'):
            user = data.get('user', {})
            print(f"\nDatos del Usuario:")
            print(f"  ID: {user.get('id')}")
            print(f"  Nombre: {user.get('nombre_completo')}")
            print(f"  Cédula: {user.get('cedula')}")
            print(f"  Rol: {user.get('rol')}")
            print(f"\nUbicación:")
            print(f"  Municipio: {user.get('municipio_nombre')} (ID: {user.get('municipio_id')})")
            print(f"  Puesto: {user.get('puesto_nombre')} (ID: {user.get('puesto_id')})")
            print(f"  Mesa: {user.get('mesa_numero')} (ID: {user.get('mesa_id')})")
            print(f"  Zona: {user.get('zona_nombre')} ({user.get('zona_codigo')})")
            print(f"  Votantes: {user.get('votantes_habilitados')}")
            print(f"\nEstadísticas:")
            print(f"  Capturas E14: {user.get('total_capturas')}")
        else:
            print(f"Error: {data.get('error')}")
    else:
        print(f"Error HTTP: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
