#!/usr/bin/env python3
"""
Pruebas para el módulo de candidatos
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
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo candidatos: {e}")

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

def main():
    """Función principal de pruebas"""
    print("🗳️  PRUEBAS DEL MÓDULO DE CANDIDATOS")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    print()
    
    try:
        # Ejecutar pruebas
        test_political_parties()
        test_candidates()
        test_candidate_search()
        
        print("\n" + "=" * 70)
        print("🎉 PRUEBAS DEL MÓDULO DE CANDIDATOS COMPLETADAS")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error general en las pruebas: {e}")

if __name__ == "__main__":
    main()