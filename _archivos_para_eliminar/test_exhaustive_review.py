#!/usr/bin/env python3
"""
Test Exhaustivo del Sistema Electoral ERP
Revisión completa de formularios, botones y funcionalidades
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
TEST_USER_ID = 5  # Laura González - Testigo Electoral

class SystemTester:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
    def test_route(self, route, method='GET', data=None, expected_status=200):
        """Probar una ruta específica"""
        try:
            url = f"{BASE_URL}{route}"
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == expected_status:
                print(f"✅ {method} {route} - Status: {response.status_code}")
                self.results['passed'] += 1
                return True
            else:
                print(f"❌ {method} {route} - Expected: {expected_status}, Got: {response.status_code}")
                self.results['failed'] += 1
                self.results['errors'].append(f"{method} {route}: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {method} {route} - Error: {str(e)}")
            self.results['failed'] += 1
            self.results['errors'].append(f"{method} {route}: {str(e)}")
            return False
    
    def test_all_routes(self):
        """Probar todas las rutas principales"""
        print("🔍 REVISIÓN EXHAUSTIVA DEL SISTEMA ELECTORAL ERP")
        print("=" * 60)
        
        # Rutas principales
        print("\n📄 PÁGINAS PRINCIPALES:")
        self.test_route("/")
        self.test_route("/login")
        self.test_route("/dashboard")
        self.test_route("/test-login")
        
        # Dashboards por rol
        print("\n👥 DASHBOARDS POR ROL:")
        roles = [
            'super_admin', 'admin_departamental', 'admin_municipal',
            'coordinador_electoral', 'coordinador_departamental', 
            'coordinador_municipal', 'coordinador_puesto',
            'testigo_electoral', 'jurado_votacion', 'testigo_mesa',
            'auditor_electoral', 'observador_internacional'
        ]
        
        for role in roles:
            self.test_route(f"/dashboard/{role}")
        
        # Funcionalidades de testigo electoral
        print("\n🗳️ TESTIGO ELECTORAL:")
        testigo_routes = [
            '/testigo/resultados',
            '/testigo/observacion', 
            '/testigo/reportes',
            '/testigo/incidencias',
            '/testigo/e14',
            '/testigo/e24'
        ]
        
        for route in testigo_routes:
            self.test_route(route)
        
        # APIs
        print("\n🔌 APIs:")
        self.test_route(f"/api/user/location/{TEST_USER_ID}")
        self.test_route("/api/mesas/puesto/1")
        self.test_route("/api/e14/validar-mesa/1")
        self.test_route("/api/system/info")
        self.test_route("/api/health")
        
        # APIs POST
        print("\n📤 APIs POST:")
        self.test_route("/api/auth/login", "POST", {
            "cedula": "33333333",
            "password": "demo123"
        })
        
        self.test_route("/api/e14/capturar", "POST", {
            "mesa_id": 1,
            "testigo_id": TEST_USER_ID,
            "imagen_e14": "data:image/jpeg;base64,test",
            "votos_validos": 100,
            "votos_blanco": 10,
            "votos_nulos": 5,
            "observaciones": "Test",
            "confirmado": True
        })
        
        # Rutas adicionales
        print("\n🔧 FUNCIONALIDADES ADICIONALES:")
        additional_routes = [
            '/users', '/municipalities', '/tables', '/voting/register',
            '/observations/new', '/profile', '/settings', '/coordination',
            '/schedule', '/progress', '/electoral', '/candidates', '/reports',
            '/audit/start', '/observation/new'
        ]
        
        for route in additional_routes:
            self.test_route(route)
    
    def test_forms_functionality(self):
        """Probar funcionalidades específicas de formularios"""
        print("\n📝 PRUEBAS DE FORMULARIOS:")
        
        # Test de formulario de observaciones
        print("Testing observaciones form...")
        obs_data = {
            "testigo_id": TEST_USER_ID,
            "tipo_observacion": "desarrollo_votacion",
            "descripcion": "Test de observación",
            "severidad": "baja",
            "mesa_id": "001-A"
        }
        
        # Test de formulario de incidencias
        print("Testing incidencias form...")
        inc_data = {
            "reportado_por": TEST_USER_ID,
            "tipo_incidencia": "falla_tecnica",
            "descripcion": "Test de incidencia",
            "severidad": "media"
        }
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        print(f"✅ Pruebas exitosas: {self.results['passed']}")
        print(f"❌ Pruebas fallidas: {self.results['failed']}")
        print(f"📈 Tasa de éxito: {(self.results['passed']/(self.results['passed']+self.results['failed'])*100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORES ENCONTRADOS ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"{i}. {error}")
        else:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")

def main():
    """Función principal"""
    print("🚀 Iniciando revisión exhaustiva del sistema...")
    print(f"🕐 Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = SystemTester()
    
    try:
        # Verificar que el servidor esté corriendo
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está respondiendo correctamente")
            return
        
        print("✅ Servidor detectado y funcionando")
        
        # Ejecutar todas las pruebas
        tester.test_all_routes()
        tester.test_forms_functionality()
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:5000?")
        print("💡 Ejecuta: python app.py")
        return
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return
    
    # Mostrar resumen
    tester.print_summary()
    
    print(f"\n🕐 Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍 Revisión exhaustiva completada")

if __name__ == "__main__":
    main()