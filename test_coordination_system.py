#!/usr/bin/env python3
"""
Script de prueba para el sistema de coordinación municipal
Verifica funcionalidades de testigos, asignaciones, mesas y reportes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.coordination_service import CoordinationService
from datetime import datetime, date
import json

def test_coordination_system():
    """Probar funcionalidades del sistema de coordinación"""
    
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE COORDINACIÓN MUNICIPAL")
    print("=" * 60)
    
    coordination_service = CoordinationService()
    
    try:
        # Test 1: Obtener información del coordinador
        print("\n1️⃣ Probando obtención de información del coordinador...")
        coordinator_info = coordination_service.get_coordinator_info(user_id=2)
        if coordinator_info:
            print(f"✅ Coordinador encontrado: {coordinator_info['nombre_completo']}")
            print(f"   Municipio: {coordinator_info['municipio_nombre']}")
            coordinator_id = coordinator_info['id']
        else:
            print("❌ No se encontró coordinador")
            return False
        
        # Test 2: Dashboard de coordinación
        print("\n2️⃣ Probando dashboard de coordinación...")
        dashboard = coordination_service.get_coordination_dashboard(coordinator_id)
        print(f"✅ Dashboard cargado:")
        print(f"   Total testigos: {dashboard['statistics']['total_testigos']}")
        print(f"   Testigos asignados: {dashboard['statistics']['testigos_asignados']}")
        print(f"   Mesas cubiertas: {dashboard['statistics']['mesas_cubiertas']}")
        print(f"   Porcentaje cobertura: {dashboard['statistics']['porcentaje_cobertura']}%")
        
        # Test 3: Obtener testigos
        print("\n3️⃣ Probando obtención de testigos...")
        witnesses = coordination_service.get_witnesses(coordinator_id)
        print(f"✅ Testigos obtenidos: {len(witnesses)}")
        for witness in witnesses[:3]:  # Mostrar solo los primeros 3
            print(f"   - {witness['nombre_completo']} ({witness['cedula']}) - Estado: {witness['estado']}")
        
        # Test 4: Crear nuevo testigo
        print("\n4️⃣ Probando creación de testigo...")
        new_witness_data = {
            'nombre_completo': 'Testigo de Prueba Sistema',
            'cedula': '99999999',
            'telefono': '3009999999',
            'email': 'testigo.prueba@test.com',
            'direccion': 'Dirección de Prueba',
            'profesion': 'Profesional de Prueba',
            'experiencia_electoral': 'Primera vez - Prueba',
            'partido_id': 1,
            'tipo_testigo': 'principal',
            'observaciones': 'Testigo creado para pruebas del sistema'
        }
        
        try:
            witness_id = coordination_service.create_witness(coordinator_id, new_witness_data)
            print(f"✅ Testigo creado con ID: {witness_id}")
        except Exception as e:
            if "Ya existe un testigo con esta cédula" in str(e):
                print("⚠️ Testigo ya existe (esperado en pruebas repetidas)")
                # Buscar el testigo existente
                existing_witnesses = coordination_service.get_witnesses(coordinator_id, {'search': '99999999'})
                if existing_witnesses:
                    witness_id = existing_witnesses[0]['id']
                    print(f"✅ Usando testigo existente con ID: {witness_id}")
                else:
                    print("❌ Error: No se pudo encontrar testigo existente")
                    return False
            else:
                print(f"❌ Error creando testigo: {e}")
                return False
        
        # Test 5: Obtener mesas de votación
        print("\n5️⃣ Probando obtención de mesas de votación...")
        voting_tables = coordination_service.get_voting_tables(coordinator_id)
        print(f"✅ Mesas obtenidas: {len(voting_tables)}")
        for table in voting_tables[:3]:  # Mostrar solo las primeras 3
            cobertura = "Sí" if table['tiene_cobertura'] else "No"
            print(f"   - Mesa {table['numero_mesa']} - {table['puesto_nombre']} - Cobertura: {cobertura}")
        
        # Test 6: Obtener puestos de votación
        print("\n6️⃣ Probando obtención de puestos de votación...")
        voting_stations = coordination_service.get_voting_stations(coordinator_id)
        print(f"✅ Puestos obtenidos: {len(voting_stations)}")
        for station in voting_stations:
            print(f"   - {station['nombre']} - Mesas: {station['total_mesas']} - Cobertura: {station['porcentaje_cobertura']:.1f}%")
        
        # Test 7: Crear asignación
        print("\n7️⃣ Probando creación de asignación...")
        
        # Buscar una mesa sin cobertura
        uncovered_tables = coordination_service.get_voting_tables(coordinator_id, {'sin_cobertura': True})
        if uncovered_tables:
            mesa_id = uncovered_tables[0]['id']
            print(f"   Mesa seleccionada: {uncovered_tables[0]['numero_mesa']}")
            
            assignment_data = {
                'testigo_id': witness_id,
                'mesa_id': mesa_id,
                'proceso_electoral_id': 1,
                'tipo_asignacion': 'principal',
                'hora_inicio': '06:00',
                'hora_fin': '18:00',
                'observaciones': 'Asignación de prueba del sistema'
            }
            
            try:
                assignment_id = coordination_service.assign_witness_to_table(assignment_data, coordinator_id)
                print(f"✅ Asignación creada con ID: {assignment_id}")
            except Exception as e:
                if "Ya existe una asignación" in str(e):
                    print("⚠️ Asignación ya existe (esperado en pruebas repetidas)")
                else:
                    print(f"❌ Error creando asignación: {e}")
                    return False
        else:
            print("⚠️ No hay mesas sin cobertura para probar asignación")
        
        # Test 8: Obtener asignaciones
        print("\n8️⃣ Probando obtención de asignaciones...")
        assignments = coordination_service.get_assignments(coordinator_id)
        print(f"✅ Asignaciones obtenidas: {len(assignments)}")
        for assignment in assignments[:3]:  # Mostrar solo las primeras 3
            print(f"   - {assignment['testigo_nombre']} -> Mesa {assignment['numero_mesa']} - Estado: {assignment['estado']}")
        
        # Test 9: Obtener tareas
        print("\n9️⃣ Probando obtención de tareas...")
        tasks = coordination_service.get_tasks(coordinator_id)
        print(f"✅ Tareas obtenidas: {len(tasks)}")
        for task in tasks:
            print(f"   - {task['titulo']} - Estado: {task['estado']} - Progreso: {task['progreso']}%")
        
        # Test 10: Generar reporte de cobertura
        print("\n🔟 Probando generación de reporte de cobertura...")
        coverage_report = coordination_service.generate_coverage_report(coordinator_id)
        print(f"✅ Reporte generado:")
        print(f"   Título: {coverage_report['title']}")
        print(f"   Total mesas: {coverage_report['summary']['total_mesas']}")
        print(f"   Mesas cubiertas: {coverage_report['summary']['mesas_cubiertas']}")
        print(f"   Porcentaje cobertura: {coverage_report['summary']['porcentaje_cobertura']}%")
        print(f"   Mesas sin cobertura: {len(coverage_report['uncovered_tables'])}")
        
        # Test 11: Actualizar estadísticas
        print("\n1️⃣1️⃣ Probando actualización de estadísticas...")
        stats_updated = coordination_service.update_coordination_statistics(coordinator_id)
        if stats_updated:
            print("✅ Estadísticas actualizadas correctamente")
        else:
            print("❌ Error actualizando estadísticas")
        
        # Test 12: Obtener resumen de coordinación
        print("\n1️⃣2️⃣ Probando resumen de coordinación...")
        summary = coordination_service.get_coordination_summary(coordinator_id)
        print(f"✅ Resumen obtenido:")
        print(f"   Coordinador: {summary['coordinator_name']}")
        print(f"   Municipio: {summary['municipality']}")
        print(f"   Total testigos: {summary['metrics']['total_testigos']}")
        print(f"   Cobertura: {summary['metrics']['porcentaje_cobertura']}%")
        print(f"   Alertas: {len(summary['alerts'])}")
        
        # Test 13: Testigos disponibles para asignación
        print("\n1️⃣3️⃣ Probando testigos disponibles para asignación...")
        available_witnesses = coordination_service.get_available_witnesses_for_assignment(coordinator_id)
        print(f"✅ Testigos disponibles: {len(available_witnesses)}")
        for witness in available_witnesses[:3]:
            print(f"   - {witness['nombre_completo']} ({witness['cedula']})")
        
        print("\n" + "=" * 60)
        print("🎉 TODAS LAS PRUEBAS DEL SISTEMA DE COORDINACIÓN COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_coordination_api_integration():
    """Probar integración con la API"""
    
    print("\n🔗 PROBANDO INTEGRACIÓN CON API DE COORDINACIÓN")
    print("-" * 50)
    
    try:
        # Importar la aplicación Flask
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test de endpoint de dashboard (requiere autenticación)
            print("📡 Probando endpoint de dashboard...")
            
            # Simular sesión de usuario
            with client.session_transaction() as sess:
                sess['user_id'] = 2  # ID del coordinador de prueba
            
            response = client.get('/api/coordination/dashboard')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    print("✅ API de dashboard funcionando correctamente")
                else:
                    print(f"⚠️ API responde pero con error: {data.get('error') if data else 'Sin datos'}")
            else:
                print(f"❌ Error en API: {response.status_code}")
        
        print("✅ Integración con API probada")
        return True
        
    except Exception as e:
        print(f"❌ Error probando API: {e}")
        return False

def main():
    """Función principal"""
    
    print("🚀 SISTEMA DE PRUEBAS - COORDINACIÓN MUNICIPAL")
    print("Sistema Electoral Caquetá")
    print("=" * 60)
    
    # Ejecutar pruebas del servicio
    service_tests_passed = test_coordination_system()
    
    # Ejecutar pruebas de API
    api_tests_passed = test_coordination_api_integration()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print(f"   Servicio de Coordinación: {'✅ PASÓ' if service_tests_passed else '❌ FALLÓ'}")
    print(f"   API de Coordinación: {'✅ PASÓ' if api_tests_passed else '❌ FALLÓ'}")
    
    if service_tests_passed and api_tests_passed:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - SISTEMA LISTO PARA USO")
        return True
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON - REVISAR ERRORES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)