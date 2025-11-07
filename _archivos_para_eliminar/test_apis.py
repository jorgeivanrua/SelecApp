#!/usr/bin/env python3
"""
Script para probar las APIs RESTful del Sistema Electoral
"""

import requests
import json
from datetime import datetime

def test_apis():
    """Probar todas las APIs implementadas"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 PROBANDO APIs RESTful DEL SISTEMA ELECTORAL")
    print("=" * 60)
    
    # Test 1: Crear observación
    print("\n📝 Test 1: Crear observación")
    observacion_data = {
        "testigo_id": 5,  # Laura González - Testigo Electoral
        "mesa_id": 1,
        "puesto_id": 1,
        "tipo_observacion": "apertura",
        "descripcion": "Mesa abierta correctamente a las 8:00 AM. Todos los materiales presentes.",
        "severidad": "normal",
        "calificacion_proceso": "excelente",
        "ubicacion_gps_lat": 1.6143,
        "ubicacion_gps_lng": -75.6062
    }
    
    try:
        response = requests.post(f"{base_url}/api/observaciones", 
                               json=observacion_data, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Observación creada: ID {result.get('observacion_id')}")
        else:
            print(f"❌ Error creando observación: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 2: Obtener observaciones
    print("\n📋 Test 2: Obtener observaciones")
    try:
        response = requests.get(f"{base_url}/api/observaciones?testigo_id=5", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Observaciones obtenidas: {result.get('total')} registros")
            if result.get('data'):
                obs = result['data'][0]
                print(f"   Primera observación: {obs.get('tipo_observacion')} - {obs.get('descripcion')[:50]}...")
        else:
            print(f"❌ Error obteniendo observaciones: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Crear incidencia
    print("\n⚠️  Test 3: Crear incidencia")
    incidencia_data = {
        "reportado_por": 4,  # Miguel Torres - Coordinador de Puesto
        "puesto_id": 1,
        "tipo_incidencia": "falta_material",
        "descripcion": "Faltan 2 urnas en el puesto. Se requiere reposición urgente.",
        "severidad": "alta",
        "ubicacion_gps_lat": 1.6143,
        "ubicacion_gps_lng": -75.6062
    }
    
    try:
        response = requests.post(f"{base_url}/api/incidencias", 
                               json=incidencia_data, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Incidencia creada: ID {result.get('incidencia_id')}")
        else:
            print(f"❌ Error creando incidencia: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 4: Crear asignación de personal
    print("\n👥 Test 4: Crear asignación de personal")
    asignacion_data = {
        "usuario_id": 6,  # Juan Pérez - Testigo de Mesa
        "puesto_id": 1,
        "mesa_id": 1,
        "rol_asignado": "testigo_mesa",
        "fecha_asignacion": "2024-11-10",
        "turno": "completo",
        "asignado_por": 4,  # Miguel Torres
        "notas": "Asignación para elecciones municipales"
    }
    
    try:
        response = requests.post(f"{base_url}/api/personal/asignaciones", 
                               json=asignacion_data, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Asignación creada: ID {result.get('asignacion_id')}")
        else:
            print(f"❌ Error creando asignación: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 5: Crear solicitud de material
    print("\n📦 Test 5: Crear solicitud de material")
    material_data = {
        "puesto_id": 1,
        "tipo_material": "urnas",
        "descripcion": "Urnas de votación estándar",
        "cantidad_requerida": 2,
        "prioridad": "alta",
        "solicitado_por": 4,  # Miguel Torres
        "notas": "Reposición urgente por faltantes detectados"
    }
    
    try:
        response = requests.post(f"{base_url}/api/inventario", 
                               json=material_data, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Solicitud de material creada: ID {result.get('solicitud_id')}")
        else:
            print(f"❌ Error creando solicitud: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 6: Obtener notificaciones
    print("\n🔔 Test 6: Obtener notificaciones")
    try:
        # Obtener notificaciones del coordinador departamental (debería tener notificaciones por las incidencias)
        response = requests.get(f"{base_url}/api/notificaciones/2", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Notificaciones obtenidas: {result.get('total')} registros")
            if result.get('data'):
                notif = result['data'][0]
                print(f"   Primera notificación: {notif.get('titulo')} - {notif.get('mensaje')[:50]}...")
        else:
            print(f"❌ Error obteniendo notificaciones: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 7: Obtener inventario
    print("\n📋 Test 7: Obtener inventario")
    try:
        response = requests.get(f"{base_url}/api/inventario?puesto_id=1", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Inventario obtenido: {result.get('total')} registros")
            if result.get('data'):
                item = result['data'][0]
                print(f"   Primer item: {item.get('tipo_material')} - {item.get('estado')}")
        else:
            print(f"❌ Error obteniendo inventario: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas de APIs completadas!")

if __name__ == "__main__":
    try:
        test_apis()
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"❌ Error general: {e}")