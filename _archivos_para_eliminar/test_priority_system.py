#!/usr/bin/env python3
"""
Test del sistema de priorización
"""

from services.priority_service import PriorityService
import json

def test_priority_system():
    """Probar el sistema de priorización"""
    
    print("🔄 Probando sistema de priorización...")
    
    # Crear instancia del servicio
    service = PriorityService()
    
    # Obtener configuración activa
    print("\n📋 Obteniendo configuración activa...")
    active_config = service.get_active_configuration()
    
    if active_config:
        print(f"Configuración activa: {active_config['nombre']}")
        config_id = active_config['id']
        
        # Obtener prioridades de partidos
        print("\n🏛️ Obteniendo prioridades de partidos...")
        party_priorities = service.get_party_priorities(config_id)
        print(f"Partidos con prioridad configurada: {len(party_priorities)}")
        
        for party in party_priorities[:3]:
            print(f"  - {party['partido_nombre']} ({party['partido_sigla']}): {party['prioridad_texto']}")
        
        # Establecer prioridad de un partido
        print("\n⚙️ Estableciendo prioridad de partido...")
        success = service.set_party_priority(config_id, 1, 1, "Partido de alta importancia para recolección")
        print(f"Prioridad establecida: {success}")
        
        # Obtener resumen de prioridades
        print("\n📊 Obteniendo resumen de prioridades...")
        summary = service.get_priority_summary(config_id)
        print("Resumen:")
        print(f"  Partidos: {summary['partidos']['total']} total ({summary['partidos']['alta']} alta, {summary['partidos']['media']} media, {summary['partidos']['baja']} baja)")
        print(f"  Candidatos: {summary['candidatos']['total']} total ({summary['candidatos']['alta']} alta, {summary['candidatos']['media']} media, {summary['candidatos']['baja']} baja)")
        print(f"  Procesos: {summary['procesos']['total']} total ({summary['procesos']['alta']} alta, {summary['procesos']['media']} media, {summary['procesos']['baja']} baja)")
        
        # Obtener entidades de alta prioridad
        print("\n⭐ Obteniendo entidades de alta prioridad...")
        high_priority = service.get_high_priority_entities(config_id)
        
        print(f"Partidos de alta prioridad: {len(high_priority['partidos'])}")
        for party in high_priority['partidos']:
            print(f"  - {party['nombre']} ({party['sigla']})")
        
        print(f"Candidatos de alta prioridad: {len(high_priority['candidatos'])}")
        for candidate in high_priority['candidatos'][:3]:
            print(f"  - {candidate['nombre_completo']} ({candidate['partido_sigla']})")
        
        print(f"Procesos de alta prioridad: {len(high_priority['procesos'])}")
        for process in high_priority['procesos']:
            print(f"  - {process['nombre']} ({process['tipo']})")
        
        print("\n✅ Sistema de priorización funcionando correctamente!")
        
    else:
        print("❌ No hay configuración activa")
        
        # Crear configuración de prueba
        print("\n🔄 Creando configuración de prueba...")
        config_data = {
            'nombre': 'Configuración de Prueba',
            'descripcion': 'Configuración para pruebas del sistema',
            'activa': True,
            'fecha_inicio': '2024-11-01',
            'fecha_fin': '2024-12-31'
        }
        
        config_id = service.create_configuration(config_data, 1)
        print(f"Configuración creada: {config_id}")
        
        # Establecer algunas prioridades de prueba
        print("\n⚙️ Estableciendo prioridades de prueba...")
        service.set_party_priority(config_id, 1, 1, "Partido Liberal - Alta prioridad")
        service.set_party_priority(config_id, 2, 1, "Partido Conservador - Alta prioridad")
        service.set_party_priority(config_id, 3, 2, "Centro Democrático - Media prioridad")
        
        print("Prioridades de prueba establecidas")
        
        # Obtener resumen
        summary = service.get_priority_summary(config_id)
        print(f"\nResumen después de configurar:")
        print(f"  Partidos: {summary['partidos']['total']} total")

if __name__ == "__main__":
    test_priority_system()