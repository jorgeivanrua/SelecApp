#!/usr/bin/env python3
"""
Pruebas para el módulo de coordinación
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"

def test_coordination_dashboard():
    """Probar dashboard de coordinación"""
    print("🏛️  PROBANDO DASHBOARD DE COORDINACIÓN")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/coordination/dashboard?coordinator_id=1")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                print(f"✅ Dashboard obtenido exitosamente")
                print(f"   Coordinador: {data.get('coordinator_info', {}).get('nombre_completo', 'N/A')}")
                print(f"   Estadísticas disponibles: {len(data.get('statistics', {}))}")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo dashboard: {e}")

def test_coordination_statistics():
    """Probar estadísticas de coordinación"""
    print("\n📊 PROBANDO ESTADÍSTICAS DE COORDINACIÓN")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/coordination/statistics?coordinator_id=1")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                stats = result['data']
                print(f"✅ Estadísticas obtenidas")
                print(f"   Total testigos: {stats.get('total_testigos', 0)}")
                print(f"   Mesas cubiertas: {stats.get('mesas_cubiertas', 0)}")
                print(f"   Cobertura: {stats.get('porcentaje_cobertura', 0)}%")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

def test_witnesses_management():
    """Probar gestión de testigos"""
    print("\n👥 PROBANDO GESTIÓN DE TESTIGOS")
    print("=" * 50)
    
    # Test 1: Obtener testigos disponibles
    print("\n1️⃣ Obteniendo testigos disponibles:")
    try:
        response = requests.get(f"{BASE_URL}/api/coordination/witnesses/available")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                witnesses = result['data']
                print(f"✅ {len(witnesses)} testigos disponibles encontrados")
                for witness in witnesses[:2]:
                    print(f"   - {witness['nombre_completo']} ({witness['cedula']})")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo testigos: {e}")

def test_coverage_report():
    """Probar reporte de cobertura"""
    print("\n📋 PROBANDO REPORTE DE COBERTURA")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/coordination/reports/coverage")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                data = result['data']
                summary = data.get('summary', {})
                print(f"✅ Reporte de cobertura generado")
                print(f"   Total mesas: {summary.get('total_mesas', 0)}")
                print(f"   Mesas cubiertas: {summary.get('mesas_cubiertas', 0)}")
                print(f"   Cobertura: {summary.get('porcentaje_cobertura', 0)}%")
            else:
                print(f"❌ Error en respuesta: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")

def main():
    """Función principal de pruebas"""
    print("🗳️  PRUEBAS DEL MÓDULO DE COORDINACIÓN")
    print("Sistema de Recolección Inicial de Votaciones - Caquetá")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    print()
    
    try:
        # Ejecutar pruebas
        test_coordination_dashboard()
        test_coordination_statistics()
        test_witnesses_management()
        test_coverage_report()
        
        print("\n" + "=" * 70)
        print("🎉 PRUEBAS DEL MÓDULO DE COORDINACIÓN COMPLETADAS")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error general en las pruebas: {e}")

if __name__ == "__main__":
    main()