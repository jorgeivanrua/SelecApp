#!/usr/bin/env python3
"""
Test para crear candidato usando las APIs administrativas
"""

import requests
import json

def test_create_candidate():
    """Probar creación de candidato"""
    
    base_url = "http://localhost:5000/api/admin"
    
    # Datos del candidato de prueba
    candidate_data = {
        "cedula": "11223344",
        "nombre_completo": "Juan Carlos Pérez García",
        "fecha_nacimiento": "1980-05-15",
        "lugar_nacimiento": "Florencia, Caquetá",
        "profesion": "Abogado",
        "telefono": "3001234567",
        "email": "juan.perez@email.com",
        "direccion": "Calle 10 # 15-20, Florencia",
        "partido_id": 1,  # Partido Liberal Colombiano
        "cargo_id": 1,    # Alcalde Municipal
        "municipio_id": 1, # Florencia (asumiendo que existe)
        "numero_lista": 1,
        "estado": "inscrito",
        "observaciones": "Candidato de prueba creado por el sistema administrativo"
    }
    
    print("🔄 Creando candidato de prueba...")
    print(f"Datos: {json.dumps(candidate_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Crear candidato
        response = requests.post(
            f"{base_url}/candidatos",
            json=candidate_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Candidato creado exitosamente!")
            candidate_id = result.get('candidate_id') or result.get('candidato_id')
            print(f"ID del candidato: {candidate_id}")
            
            # Obtener lista de candidatos para verificar
            print("\n🔄 Verificando lista de candidatos...")
            response = requests.get(f"{base_url}/candidatos")
            
            if response.status_code == 200:
                candidates = response.json()
                print(f"Total candidatos: {candidates['total']}")
                
                if candidates['data']:
                    candidate = candidates['data'][0]
                    print(f"Candidato creado: {candidate['nombre_completo']} - {candidate['partido_nombre']}")
                
                return True
            else:
                print(f"❌ Error obteniendo candidatos: {response.status_code}")
                return False
        else:
            print(f"❌ Error creando candidato: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_create_candidate()
    if success:
        print("\n🎉 Test completado exitosamente!")
    else:
        print("\n💥 Test falló!")