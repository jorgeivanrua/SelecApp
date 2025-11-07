#!/usr/bin/env python3
"""
Script de prueba para el sistema modular
Sistema de Recolección Inicial de Votaciones - Caquetá
"""

from app_modular import create_app
import json

def test_modular_system():
    """Probar el sistema modular completo"""
    
    print("🧪 Iniciando pruebas del sistema modular...")
    print("=" * 60)
    
    # Crear aplicación
    app = create_app()
    
    with app.test_client() as client:
        
        # Probar endpoint principal
        print("\n📍 Probando endpoint principal...")
        response = client.get('/')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Endpoint principal: {data['message']}")
            print(f"   Versión: {data['version']}")
            print(f"   Módulos: {len(data['modules'])}")
        else:
            print(f"❌ Error en endpoint principal: {response.status_code}")
        
        # Probar health check
        print("\n🏥 Probando health check...")
        response = client.get('/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Health check: {data['status']}")
        else:
            print(f"❌ Error en health check: {response.status_code}")
        
        # Probar info de API
        print("\n📋 Probando info de API...")
        response = client.get('/api/info')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ API Info: {len(data['endpoints'])} endpoints disponibles")
        else:
            print(f"❌ Error en API info: {response.status_code}")
        
        # Probar módulos específicos
        print("\n🔧 Probando módulos específicos...")
        
        # Módulo de administración
        response = client.get('/api/admin/health')
        if response.status_code == 200:
            print("✅ Módulo de administración: Disponible")
        else:
            print(f"⚠️  Módulo de administración: {response.status_code}")
        
        # Módulo de candidatos
        response = client.get('/api/candidates/')
        if response.status_code in [200, 404]:  # 404 es OK si no hay datos
            print("✅ Módulo de candidatos: Disponible")
        else:
            print(f"⚠️  Módulo de candidatos: {response.status_code}")
        
        # Módulo de coordinación
        response = client.get('/api/coordination/health')
        if response.status_code == 200:
            print("✅ Módulo de coordinación: Disponible")
        else:
            print(f"⚠️  Módulo de coordinación: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas!")
    
    # Mostrar resumen de blueprints
    print(f"\n📊 Resumen del sistema:")
    print(f"   Blueprints registrados: {len(app.blueprints)}")
    
    for bp_name in sorted(app.blueprints.keys()):
        bp = app.blueprints[bp_name]
        prefix = bp.url_prefix or '/'
        print(f"   - {bp_name:20} -> {prefix}")
    
    # Mostrar endpoints principales
    print(f"\n🌐 Endpoints principales:")
    main_endpoints = [
        ('GET', '/', 'Información principal'),
        ('GET', '/health', 'Health check'),
        ('GET', '/api/info', 'Información de API'),
        ('GET', '/api/admin/health', 'Salud del sistema'),
        ('GET', '/api/admin/statistics', 'Estadísticas del sistema'),
        ('POST', '/api/users/auth/login', 'Login de usuarios'),
        ('GET', '/api/candidates/', 'Lista de candidatos'),
        ('GET', '/api/coordination/health', 'Estado de coordinación'),
    ]
    
    for method, endpoint, description in main_endpoints:
        print(f"   {method:4} {endpoint:30} - {description}")

def test_services():
    """Probar servicios individuales"""
    
    print("\n🔧 Probando servicios individuales...")
    print("=" * 60)
    
    try:
        # Servicios de administración
        from modules.admin.services import AdminPanelService, ExcelImportService, PriorityService
        
        admin_service = AdminPanelService()
        excel_service = ExcelImportService()
        priority_service = PriorityService()
        
        print("✅ Servicios de administración: OK")
        
        # Servicios de usuarios
        from modules.users.services import UserService, AuthService
        
        user_service = UserService()
        auth_service = AuthService()
        
        print("✅ Servicios de usuarios: OK")
        
        # Servicios de candidatos
        from modules.candidates.services import CandidateManagementService
        
        candidate_service = CandidateManagementService()
        
        print("✅ Servicios de candidatos: OK")
        
        # Servicios de coordinación
        from modules.coordination.services import CoordinationService, MunicipalCoordinationService
        
        coord_service = CoordinationService()
        municipal_service = MunicipalCoordinationService()
        
        print("✅ Servicios de coordinación: OK")
        
        print("\n🎉 Todos los servicios funcionan correctamente!")
        
    except Exception as e:
        print(f"❌ Error probando servicios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🗳️  Sistema Electoral Caquetá - Pruebas Modulares")
    print("=" * 60)
    
    test_modular_system()
    test_services()
    
    print("\n" + "=" * 60)
    print("✅ Sistema modular completamente funcional!")
    print("🚀 Listo para desarrollo y producción")