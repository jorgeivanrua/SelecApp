import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 60)
print("PRUEBA COMPLETA DE APIs DE UBICACIÓN")
print("=" * 60)

# 1. Probar API de municipios
print("\n1. PROBANDO /api/ubicacion/municipios")
print("-" * 60)
response = requests.get(f'{BASE_URL}/api/ubicacion/municipios')
data = response.json()
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
if data.get('success'):
    print(f"Municipios encontrados: {len(data['municipios'])}")
    print("\nPrimeros 3 municipios:")
    for mun in data['municipios'][:3]:
        print(f"  - ID: {mun['id']}, Nombre: {mun['nombre']}, Código: {mun['codigo']}")
    
    # Usar Florencia para las siguientes pruebas
    florencia_id = next((m['id'] for m in data['municipios'] if m['nombre'] == 'Florencia'), None)
    
    if florencia_id:
        # 2. Probar API de zonas
        print(f"\n2. PROBANDO /api/ubicacion/zonas/{florencia_id} (Florencia)")
        print("-" * 60)
        response = requests.get(f'{BASE_URL}/api/ubicacion/zonas/{florencia_id}')
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            print(f"Zonas encontradas: {len(data['zonas'])}")
            print("\nTodas las zonas:")
            for zona in data['zonas']:
                print(f"  - ID: {zona['id']}, Código: {zona.get('codigo', 'N/A')}, Nombre: {zona['nombre']}, Descripción: {zona.get('descripcion', 'N/A')}")
            
            # Usar primera zona para siguiente prueba
            if data['zonas']:
                zona_id = data['zonas'][0]['id']
                
                # 3. Probar API de puestos
                print(f"\n3. PROBANDO /api/ubicacion/puestos/{zona_id}")
                print("-" * 60)
                response = requests.get(f'{BASE_URL}/api/ubicacion/puestos/{zona_id}')
                data = response.json()
                print(f"Status: {response.status_code}")
                print(f"Success: {data.get('success')}")
                if data.get('success'):
                    print(f"Puestos encontrados: {len(data['puestos'])}")
                    print("\nPrimeros 5 puestos:")
                    for puesto in data['puestos'][:5]:
                        print(f"  - ID: {puesto['id']}, Nombre: {puesto['nombre']}, Dirección: {puesto.get('direccion', 'N/A')}")
                    
                    # Usar primer puesto para siguiente prueba
                    if data['puestos']:
                        puesto_id = data['puestos'][0]['id']
                        
                        # 4. Probar API de mesas
                        print(f"\n4. PROBANDO /api/ubicacion/mesas/{puesto_id}")
                        print("-" * 60)
                        response = requests.get(f'{BASE_URL}/api/ubicacion/mesas/{puesto_id}')
                        data = response.json()
                        print(f"Status: {response.status_code}")
                        print(f"Success: {data.get('success')}")
                        if data.get('success'):
                            print(f"Mesas encontradas: {len(data['mesas'])}")
                            print("\nPrimeras 5 mesas:")
                            for mesa in data['mesas'][:5]:
                                print(f"  - ID: {mesa['id']}, Número: {mesa['numero']}, Votantes: {mesa.get('votantes_habilitados', 0)}")

print("\n" + "=" * 60)
print("PRUEBA COMPLETADA")
print("=" * 60)
