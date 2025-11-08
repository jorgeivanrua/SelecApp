import requests
import json

# Probar la zona 90 de Florencia
print("Probando Zona 90 de Florencia...")

# Primero obtener el ID de la zona 90
response = requests.get('http://127.0.0.1:5000/api/ubicacion/zonas/7')
data = response.json()

print("\nZonas de Florencia:")
zona_90_id = None
for zona in data['zonas']:
    print(f"  ID: {zona['id']}, Nombre: {zona['nombre']}, Codigo: {zona.get('codigo', 'N/A')}")
    if 'Zona 90' in zona['nombre'] or zona.get('codigo') == '90':
        zona_90_id = zona['id']

if zona_90_id:
    print(f"\nZona 90 ID: {zona_90_id}")
    
    # Obtener puestos de la zona 90
    response = requests.get(f'http://127.0.0.1:5000/api/ubicacion/puestos/{zona_90_id}')
    data = response.json()
    
    print(f"\nPuestos de Zona 90:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("\n⚠️ No se encontró la Zona 90")
