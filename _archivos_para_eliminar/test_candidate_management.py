#!/usr/bin/env python3
"""
Pruebas para el Sistema de Gestión de Candidatos, Partidos y Coaliciones
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import requests
import json
import csv
import tempfile
import os
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
TEST_DATA_DIR = "test_data"

def create_test_data_directory():
    """Crear directorio para datos de prueba"""
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR)

def test_political_parties():
    """Probar gestión de partidos políticos"""
    print("🏛️  PROBANDO GESTIÓN DE PARTIDOS POLÍTICOS")
    print("=" * 50)
    
    # Test 1: Obtener partidos existentes
    print("\n1️⃣ Obteniendo partidos políticos existentes:")
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/parties")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                parties = result['data']
                print(f"✅ {len(parties)} partidos encontrados")
                for party in parties[:3]:  # Mostrar solo los primeros 3
                    print(f"   - {party['nombre_oficial']} ({party['siglas']})")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo partidos: {e}")
    
    # Test 2: Crear nuevo partido político
    print("\n2️⃣ Creando nuevo partido político:")
    new_party_data = {
        "nombre_oficial": "Partido de Prueba Electoral",
        "siglas": "PPE",
        "color_representativo": "#FF5733",
        "descripcion": "Partido creado para pruebas del sistema electoral",
        "ideologia": "Centrista",
        "fundacion_year": 2024,
        "activo": True,
        "reconocido_oficialmente": True,
        "created_by": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/candidates/parties", json=new_party_data)
        if response.status_code == 201:
            result = response.json()
            if result['success']:
                print(f"✅ Partido creado exitosamente")
                print(f"   ID: {result.get('party_id', 'N/A')}")
                print(f"   Mensaje: {result.get('message', 'N/A')}")
                return result['party_id']
            else:
                print(f"❌ Error creando partido: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error creando partido: {e}")
    
    return None

def test_coalitions():
    """Probar gestión de coaliciones"""
    print("\n🤝 PROBANDO GESTIÓN DE COALICIONES")
    print("=" * 50)
    
    # Test 1: Obtener coaliciones existentes
    print("\n1️⃣ Obteniendo coaliciones existentes:")
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/coalitions")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                coalitions = result['data']
                print(f"✅ {len(coalitions)} coaliciones encontradas")
                for coalition in coalitions[:3]:
                    print(f"   - {coalition['nombre_coalicion']}")
                    if coalition.get('partidos'):
                        print(f"     Partidos: {len(coalition['partidos'])}")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo coaliciones: {e}")
    
    # Test 2: Crear nueva coalición
    print("\n2️⃣ Creando nueva coalición:")
    new_coalition_data = {
        "nombre_coalicion": "Coalición de Prueba Electoral",
        "descripcion": "Coalición creada para pruebas del sistema electoral",
        "fecha_formacion": datetime.now().isoformat(),
        "partidos_ids": [1, 2],  # IDs de partidos existentes
        "activo": True,
        "created_by": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/candidates/coalitions", json=new_coalition_data)
        if response.status_code == 201:
            result = response.json()
            if result['success']:
                print(f"✅ Coalición creada exitosamente")
                print(f"   ID: {result.get('coalition_id', 'N/A')}")
                print(f"   Mensaje: {result.get('message', 'N/A')}")
                return result['coalition_id']
            else:
                print(f"❌ Error creando coalición: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error creando coalición: {e}")
    
    return None

def test_candidates():
    """Probar gestión de candidatos"""
    print("\n👤 PROBANDO GESTIÓN DE CANDIDATOS")
    print("=" * 50)
    
    # Test 1: Obtener candidatos existentes
    print("\n1️⃣ Obteniendo candidatos existentes:")
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                candidates = result['data']
                print(f"✅ {len(candidates)} candidatos encontrados")
                for candidate in candidates[:3]:
                    print(f"   - {candidate['nombre_completo']} (Tarjetón: {candidate['numero_tarjeton']})")
                    if candidate.get('party_name'):
                        print(f"     Partido: {candidate['party_name']}")
                    elif candidate.get('coalition_name'):
                        print(f"     Coalición: {candidate['coalition_name']}")
                    else:
                        print(f"     Independiente")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo candidatos: {e}")
    
    # Test 2: Crear nuevo candidato
    print("\n2️⃣ Creando nuevo candidato:")
    new_candidate_data = {
        "nombre_completo": "Juan Carlos Pérez García",
        "cedula": "12345678901",
        "numero_tarjeton": 999,
        "cargo_aspirado": "Senador",
        "election_type_id": 1,  # Asumiendo que existe
        "circunscripcion": "Nacional",
        "party_id": 1,  # Asumiendo que existe
        "biografia": "Abogado con 20 años de experiencia en derecho público",
        "propuestas": "Educación gratuita y salud universal",
        "experiencia": "Alcalde de Florencia 2016-2020",
        "activo": True,
        "habilitado_oficialmente": True,
        "created_by": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/candidates/", json=new_candidate_data)
        if response.status_code == 201:
            result = response.json()
            if result['success']:
                print(f"✅ Candidato creado exitosamente")
                print(f"   ID: {result.get('candidate_id', 'N/A')}")
                print(f"   Mensaje: {result.get('message', 'N/A')}")
                return result['candidate_id']
            else:
                print(f"❌ Error creando candidato: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error creando candidato: {e}")
    
    return None

def test_candidate_search():
    """Probar búsqueda avanzada de candidatos"""
    print("\n🔍 PROBANDO BÚSQUEDA AVANZADA DE CANDIDATOS")
    print("=" * 50)
    
    # Test 1: Búsqueda por nombre
    print("\n1️⃣ Búsqueda por nombre:")
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/search?nombre=Juan")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                candidates = result['data']
                print(f"✅ {len(candidates)} candidatos encontrados con 'Juan' en el nombre")
                for candidate in candidates[:2]:
                    print(f"   - {candidate['nombre_completo']}")
            else:
                print(f"❌ Error en búsqueda: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    # Test 2: Búsqueda por partido
    print("\n2️⃣ Búsqueda por partido:")
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/search?party_id=1")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                candidates = result['data']
                print(f"✅ {len(candidates)} candidatos encontrados del partido ID 1")
                for candidate in candidates[:2]:
                    print(f"   - {candidate['nombre_completo']} ({candidate.get('party_name', 'N/A')})")
            else:
                print(f"❌ Error en búsqueda: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

def create_test_csv():
    """Crear archivo CSV de prueba para carga masiva"""
    csv_file_path = os.path.join(TEST_DATA_DIR, "candidatos_prueba.csv")
    
    test_candidates = [
        {
            'nombre_completo': 'María Elena Rodríguez',
            'cedula': '23456789012',
            'numero_tarjeton': '101',
            'cargo_aspirado': 'Senador',
            'circunscripcion': 'Nacional',
            'party_siglas': 'PLC',
            'coalition_name': '',
            'foto_url': 'https://example.com/maria.jpg',
            'biografia': 'Economista especializada en políticas públicas',
            'propuestas': 'Desarrollo rural y equidad de género',
            'experiencia': 'Secretaria de Hacienda Departamental'
        },
        {
            'nombre_completo': 'Carlos Alberto Mendoza',
            'cedula': '34567890123',
            'numero_tarjeton': '102',
            'cargo_aspirado': 'Senador',
            'circunscripcion': 'Nacional',
            'party_siglas': 'CD',
            'coalition_name': '',
            'foto_url': 'https://example.com/carlos.jpg',
            'biografia': 'Ingeniero civil con experiencia en infraestructura',
            'propuestas': 'Vías y conectividad para el Caquetá',
            'experiencia': 'Director de Invías regional'
        },
        {
            'nombre_completo': 'Ana Lucía Vargas',
            'cedula': '45678901234',
            'numero_tarjeton': '103',
            'cargo_aspirado': 'Senador',
            'circunscripcion': 'Nacional',
            'party_siglas': '',
            'coalition_name': 'Coalición de Prueba Electoral',
            'foto_url': 'https://example.com/ana.jpg',
            'biografia': 'Médica especialista en salud pública',
            'propuestas': 'Salud rural y medicina preventiva',
            'experiencia': 'Directora Hospital Regional'
        }
    ]
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = test_candidates[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_candidates)
    
    print(f"✅ Archivo CSV de prueba creado: {csv_file_path}")
    return csv_file_path

def test_bulk_upload():
    """Probar carga masiva de candidatos desde CSV"""
    print("\n📁 PROBANDO CARGA MASIVA DESDE CSV")
    print("=" * 50)
    
    # Crear archivo CSV de prueba
    csv_file_path = create_test_csv()
    
    try:
        with open(csv_file_path, 'rb') as csv_file:
            files = {'file': ('candidatos_prueba.csv', csv_file, 'text/csv')}
            data = {
                'election_type_id': 1,  # Asumiendo que existe
                'created_by': 1
            }
            
            response = requests.post(f"{BASE_URL}/api/candidates/upload-csv", 
                                   files=files, data=data)
            
            if response.status_code == 201:
                result = response.json()
                if result['success']:
                    print(f"✅ Carga masiva exitosa")
                    print(f"   Total procesados: {result.get('total_processed', 0)}")
                    print(f"   Exitosos: {result.get('successful', 0)}")
                    print(f"   Errores: {len(result.get('errors', []))}")
                    
                    if result.get('errors'):
                        print("   Errores encontrados:")
                        for error in result['errors'][:3]:  # Mostrar solo los primeros 3
                            print(f"     - Fila {error.get('row', 'N/A')}: {error.get('error', 'N/A')}")
                else:
                    print(f"❌ Error en carga masiva: {result.get('error', 'N/A')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"   Respuesta: {response.text}")
    
    except Exception as e:
        print(f"❌ Error en carga masiva: {e}")
    
    # Limpiar archivo temporal
    try:
        os.remove(csv_file_path)
        print(f"🧹 Archivo temporal eliminado")
    except:
        pass

def test_candidate_validation():
    """Probar validación de candidatos con tarjetón oficial"""
    print("\n✅ PROBANDO VALIDACIÓN CON TARJETÓN OFICIAL")
    print("=" * 50)
    
    # Datos simulados del tarjetón oficial
    official_ballot_data = [
        {
            'numero_tarjeton': 1,
            'nombre_completo': 'Juan Carlos Pérez García',
            'cedula': '12345678901'
        },
        {
            'numero_tarjeton': 101,
            'nombre_completo': 'María Elena Rodríguez',
            'cedula': '23456789012'
        },
        {
            'numero_tarjeton': 102,
            'nombre_completo': 'Carlos Alberto Mendoza',
            'cedula': '34567890123'
        }
    ]
    
    validation_data = {
        'election_type_id': 1,
        'official_ballot_data': official_ballot_data
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/candidates/validate-ballot", 
                               json=validation_data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Validación completada")
                print(f"   Total oficial: {result.get('total_official', 0)}")
                print(f"   Total sistema: {result.get('total_system', 0)}")
                print(f"   Coincidencias: {len(result.get('matches', []))}")
                print(f"   Faltantes en sistema: {len(result.get('missing_in_system', []))}")
                print(f"   Extras en sistema: {len(result.get('extra_in_system', []))}")
                print(f"   Discrepancias: {len(result.get('discrepancies', []))}")
                print(f"   Porcentaje coincidencia: {result.get('match_percentage', 0):.1f}%")
            else:
                print(f"❌ Error en validación: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    
    except Exception as e:
        print(f"❌ Error en validación: {e}")

def test_candidate_lists():
    """Probar generación de listas organizadas"""
    print("\n📋 PROBANDO LISTAS ORGANIZADAS DE CANDIDATOS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/candidate-lists/1")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                print(f"✅ Listas generadas exitosamente")
                print(f"   Total candidatos: {data['summary']['total_candidates']}")
                print(f"   Total partidos: {data['summary']['total_parties']}")
                print(f"   Total coaliciones: {data['summary']['total_coalitions']}")
                print(f"   Independientes: {data['summary']['total_independents']}")
                
                # Mostrar algunos partidos
                if data['by_party']:
                    print("\n   Partidos con candidatos:")
                    for party_name, party_data in list(data['by_party'].items())[:3]:
                        print(f"     - {party_name}: {len(party_data['candidates'])} candidatos")
                
                # Mostrar coaliciones
                if data['by_coalition']:
                    print("\n   Coaliciones con candidatos:")
                    for coalition_name, coalition_data in data['by_coalition'].items():
                        print(f"     - {coalition_name}: {len(coalition_data['candidates'])} candidatos")
            else:
                print(f"❌ Error generando listas: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error generando listas: {e}")

def test_candidate_stats():
    """Probar estadísticas de candidatos"""
    print("\n📊 PROBANDO ESTADÍSTICAS DE CANDIDATOS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/stats")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                stats = result['data']
                print(f"✅ Estadísticas obtenidas")
                print(f"   Total candidatos: {stats['total_candidates']}")
                print(f"   Habilitados: {stats['enabled']}")
                print(f"   Deshabilitados: {stats['disabled']}")
                print(f"   Independientes: {stats['independents']}")
                
                # Mostrar por tipo de elección
                if stats['by_election_type']:
                    print("\n   Por tipo de elección:")
                    for election_type, count in stats['by_election_type'].items():
                        print(f"     - {election_type}: {count}")
                
                # Mostrar por partido
                if stats['by_party']:
                    print("\n   Por partido (top 5):")
                    sorted_parties = sorted(stats['by_party'].items(), 
                                          key=lambda x: x[1], reverse=True)
                    for party, count in sorted_parties[:5]:
                        print(f"     - {party}: {count}")
            else:
                print(f"❌ Error obteniendo estadísticas: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

def test_csv_template():
    """Probar exportación de plantilla CSV"""
    print("\n📄 PROBANDO PLANTILLA CSV")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/candidates/export-template")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                template_data = result['data']
                print(f"✅ Plantilla CSV obtenida")
                print(f"   Campos: {len(template_data['headers'])}")
                print(f"   Headers: {', '.join(template_data['headers'][:5])}...")
                
                # Mostrar instrucciones
                if template_data.get('instructions'):
                    print("\n   Instrucciones disponibles:")
                    for field, instruction in list(template_data['instructions'].items())[:3]:
                        print(f"     - {field}: {instruction[:50]}...")
            else:
                print(f"❌ Error obteniendo plantilla: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error obteniendo plantilla: {e}")

def main():
    """Función principal de pruebas"""
    print("🗳️  SISTEMA DE PRUEBAS - GESTIÓN DE CANDIDATOS")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    print()
    
    # Crear directorio de datos de prueba
    create_test_data_directory()
    
    # Ejecutar todas las pruebas
    try:
        # Pruebas de partidos políticos
        party_id = test_political_parties()
        
        # Pruebas de coaliciones
        coalition_id = test_coalitions()
        
        # Pruebas de candidatos
        candidate_id = test_candidates()
        
        # Pruebas de búsqueda
        test_candidate_search()
        
        # Pruebas de carga masiva
        test_bulk_upload()
        
        # Pruebas de validación
        test_candidate_validation()
        
        # Pruebas de listas organizadas
        test_candidate_lists()
        
        # Pruebas de estadísticas
        test_candidate_stats()
        
        # Pruebas de plantilla CSV
        test_csv_template()
        
        print("\n" + "=" * 70)
        print("🎉 PRUEBAS COMPLETADAS")
        print("Revise los resultados anteriores para verificar el funcionamiento")
        print("del sistema de gestión de candidatos, partidos y coaliciones.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error general en las pruebas: {e}")

if __name__ == "__main__":
    main()