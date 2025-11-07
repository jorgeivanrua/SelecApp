#!/usr/bin/env python3
"""
Test del servicio administrativo
"""

from services.admin_panel_service import AdminPanelService
import json

def test_admin_service():
    """Probar el servicio administrativo"""
    
    print("🔄 Probando servicio administrativo...")
    
    # Crear instancia del servicio
    service = AdminPanelService()
    
    # Obtener estadísticas
    print("\n📊 Obteniendo estadísticas del sistema...")
    stats = service.get_system_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Obtener candidatos
    print("\n👥 Obteniendo candidatos...")
    candidates = service.get_all_candidates()
    print(f"Total candidatos: {len(candidates)}")
    
    # Obtener partidos
    print("\n🏛️ Obteniendo partidos...")
    parties = service.get_all_parties()
    print(f"Total partidos: {len(parties)}")
    
    for party in parties[:3]:
        nombre = party.get('nombre', 'N/A')
        sigla = party.get('sigla', 'N/A')
        total = party.get('total_candidatos', 0)
        print(f"  - {nombre} ({sigla}) - {total} candidatos")
    
    # Obtener configuración
    print("\n⚙️ Obteniendo configuración del sistema...")
    config = service.get_system_configuration()
    print(f"Categorías de configuración: {list(config.keys())}")
    
    # Generar reporte
    print("\n📋 Generando reporte de candidatos...")
    report = service.generate_admin_report('candidates_summary')
    print(f"Reporte generado: {report['title']}")
    print(f"Total candidatos en reporte: {report['total_candidates']}")
    
    print("\n✅ Servicio administrativo funcionando correctamente!")

if __name__ == "__main__":
    test_admin_service()