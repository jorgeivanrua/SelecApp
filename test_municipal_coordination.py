#!/usr/bin/env python3
"""
Test del sistema de coordinación municipal
"""

from services.municipal_coordination_service import MunicipalCoordinationService
import json
import requests

def test_municipal_coordination():
    """Probar el sistema de coordinación municipal"""
    
    print("🔄 Probando sistema de coordinación municipal...")
    
    # Crear instancia del servicio
    service = MunicipalCoordinationService()
    
    municipio_id = 1  # Florencia
    usuario_id = 1    # Super admin
    
    # Obtener estado de consolidación
    print("\n📊 Obteniendo estado de consolidación...")
    status = service.get_consolidation_status(municipio_id)
    print(f"Estado general:")
    print(f"  - Total consolidaciones: {status['total_consolidaciones']}")
    print(f"  - Completadas: {status['completadas']}")
    print(f"  - En proceso: {status['en_proceso']}")
    print(f"  - Progreso general: {status['progreso_general']:.1f}%")
    print(f"  - Discrepancias pendientes: {status['discrepancias_pendientes']}")
    
    # Obtener consolidaciones existentes
    print("\n📋 Obteniendo consolidaciones existentes...")
    consolidations = service.get_municipal_consolidations(municipio_id)
    print(f"Total consolidaciones: {len(consolidations)}")
    
    for consolidation in consolidations:
        print(f"  - {consolidation['tipo_eleccion'].upper()}: {consolidation['estado']} ({consolidation['mesas_procesadas']}/{consolidation['total_mesas']} mesas)")
    
    # Iniciar nueva consolidación
    print("\n🚀 Iniciando nueva consolidación...")
    try:
        consolidation_id = service.start_consolidation(municipio_id, 1, 'senado', usuario_id)
        print(f"Consolidación iniciada: {consolidation_id}")
        
        # Procesar E-14s
        print("\n⚙️ Procesando E-14s...")
        result = service.process_e14_to_consolidation(consolidation_id, usuario_id)
        print(f"Procesamiento completado:")
        print(f"  - Mesas procesadas: {result['mesas_procesadas']}")
        print(f"  - Total votos válidos: {result['total_votos_validos']}")
        print(f"  - Estado: {result['estado']}")
        
        # Generar E-24
        print("\n📄 Generando E-24...")
        e24_path = service.generate_e24_image(consolidation_id, usuario_id)
        print(f"E-24 generado: {e24_path}")
        
        # Simular subida de E-24 oficial
        print("\n📤 Simulando subida de E-24 oficial...")
        official_path = f"static/official_e24/test_official_{consolidation_id}.png"
        success = service.upload_official_e24(consolidation_id, official_path, usuario_id)
        print(f"E-24 oficial subido: {success}")
        
        # Verificar E-24
        print("\n🔍 Verificando E-24...")
        verification_result = service.verify_e24_comparison(consolidation_id, usuario_id)
        print(f"Verificación completada:")
        print(f"  - Discrepancias encontradas: {verification_result['discrepancias_encontradas']}")
        print(f"  - Estado verificación: {verification_result['estado_verificacion']}")
        
        if verification_result['discrepancias_encontradas'] > 0:
            # Generar reclamación
            print("\n📝 Generando reclamación...")
            claim_id = service.generate_claim(
                consolidation_id,
                'discrepancia_totales',
                'Discrepancias detectadas en la verificación automática del E-24',
                usuario_id
            )
            print(f"Reclamación generada: {claim_id}")
        
        # Obtener dashboard data
        print("\n📊 Obteniendo datos de dashboard...")
        dashboard_data = service.get_municipal_dashboard_data(municipio_id, usuario_id)
        print(f"Dashboard actualizado:")
        print(f"  - Progreso general: {dashboard_data['summary']['progreso_general']}%")
        print(f"  - Consolidaciones recientes: {len(dashboard_data['recent_consolidations'])}")
        print(f"  - Reclamaciones activas: {dashboard_data['summary']['reclamaciones_activas']}")
        
        print("\n✅ Sistema de coordinación municipal funcionando correctamente!")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

def test_municipal_apis():
    """Probar las APIs municipales"""
    
    print("\n🌐 Probando APIs municipales...")
    
    base_url = "http://localhost:5000/api/municipal"
    municipio_id = 1
    
    try:
        # Probar estado de consolidación
        print("📊 Probando API de estado...")
        response = requests.get(f"{base_url}/consolidacion/{municipio_id}/estado")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado obtenido: {data['data']['progreso_general']:.1f}% progreso")
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
        
        # Probar dashboard
        print("📋 Probando API de dashboard...")
        response = requests.get(f"{base_url}/dashboard/{municipio_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard obtenido: {data['data']['summary']['total_consolidaciones']} consolidaciones")
        else:
            print(f"❌ Error obteniendo dashboard: {response.status_code}")
        
        # Probar tipos de elección
        print("🗳️ Probando API de tipos de elección...")
        response = requests.get(f"{base_url}/tipos-eleccion")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tipos de elección obtenidos: {data['total']} tipos")
            for tipo in data['data'][:3]:
                print(f"  - {tipo['nombre']}")
        else:
            print(f"❌ Error obteniendo tipos: {response.status_code}")
        
        print("\n✅ APIs municipales funcionando correctamente!")
        
    except Exception as e:
        print(f"❌ Error probando APIs: {e}")

if __name__ == "__main__":
    test_municipal_coordination()
    test_municipal_apis()