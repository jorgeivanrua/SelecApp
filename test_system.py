#!/usr/bin/env python3
"""
Script de prueba del Sistema Electoral ERP
Verifica que todos los módulos y endpoints funcionen correctamente
"""

import requests
import json
import sys
from datetime import datetime

class SystemTester:
    """Clase para probar el sistema electoral"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
    def test_system_info(self):
        """Probar endpoint de información del sistema"""
        print("🔍 Testing system info...")
        try:
            response = requests.get(f"{self.base_url}/api/system/info")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System: {data['name']} v{data['version']}")
                print(f"   Modules: {', '.join(data['modules'])}")
                return True
            else:
                print(f"❌ System info failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ System info error: {e}")
            return False
    
    def test_authentication(self):
        """Probar autenticación"""
        print("\n🔐 Testing authentication...")
        try:
            # Intentar login con usuario por defecto
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers=self.headers,
                data=json.dumps(login_data)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.headers['Authorization'] = f'Bearer {self.token}'
                print(f"✅ Login successful for user: {data['user']['username']}")
                print(f"   Role: {data['user']['rol']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_electoral_module(self):
        """Probar módulo electoral"""
        print("\n🗳️  Testing electoral module...")
        try:
            # Test electoral processes
            response = requests.get(
                f"{self.base_url}/api/electoral/processes",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Electoral processes: {len(data.get('data', []))} found")
                
                # Test election types
                response = requests.get(
                    f"{self.base_url}/api/electoral/types",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    types_data = response.json()
                    print(f"✅ Election types: {len(types_data.get('data', []))} found")
                    return True
                else:
                    print(f"❌ Election types failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Electoral processes failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Electoral module error: {e}")
            return False
    
    def test_candidates_module(self):
        """Probar módulo de candidatos"""
        print("\n👥 Testing candidates module...")
        try:
            # Test candidates
            response = requests.get(
                f"{self.base_url}/api/candidates/candidates",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Candidates: {len(data.get('data', []))} found")
                
                # Test political parties
                response = requests.get(
                    f"{self.base_url}/api/candidates/parties",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    parties_data = response.json()
                    print(f"✅ Political parties: {len(parties_data.get('data', []))} found")
                    return True
                else:
                    print(f"❌ Political parties failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Candidates failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Candidates module error: {e}")
            return False
    
    def test_users_module(self):
        """Probar módulo de usuarios"""
        print("\n👤 Testing users module...")
        try:
            # Test users list
            response = requests.get(
                f"{self.base_url}/api/users/users",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Users: {len(data.get('data', []))} found")
                
                # Test roles
                response = requests.get(
                    f"{self.base_url}/api/users/roles",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    roles_data = response.json()
                    print(f"✅ Roles: {len(roles_data.get('data', []))} available")
                    return True
                else:
                    print(f"❌ Roles failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Users failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Users module error: {e}")
            return False
    
    def test_reports_module(self):
        """Probar módulo de reportes"""
        print("\n📊 Testing reports module...")
        try:
            # Test electoral summary
            response = requests.get(
                f"{self.base_url}/api/reports/electoral-summary",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Electoral summary generated successfully")
                
                # Test report templates
                response = requests.get(
                    f"{self.base_url}/api/reports/templates",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    templates_data = response.json()
                    print(f"✅ Report templates: {len(templates_data.get('data', []))} available")
                    return True
                else:
                    print(f"❌ Report templates failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Electoral summary failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Reports module error: {e}")
            return False
    
    def test_dashboard_module(self):
        """Probar módulo de dashboard"""
        print("\n📈 Testing dashboard module...")
        try:
            # Test dashboard overview
            response = requests.get(
                f"{self.base_url}/api/dashboard/overview",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Dashboard overview loaded successfully")
                
                # Test electoral progress widget
                response = requests.get(
                    f"{self.base_url}/api/dashboard/widgets/electoral-progress",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    widget_data = response.json()
                    print("✅ Electoral progress widget working")
                    return True
                else:
                    print(f"❌ Electoral progress widget failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Dashboard overview failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Dashboard module error: {e}")
            return False
    
    def test_database_integrity(self):
        """Probar integridad de la base de datos"""
        print("\n🗄️  Testing database integrity...")
        try:
            # Test system audit
            response = requests.get(
                f"{self.base_url}/api/reports/system-audit",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                integrity = data.get('data', {}).get('data_integrity', {})
                status = integrity.get('status', 'UNKNOWN')
                issues = integrity.get('issues', [])
                
                if status == 'OK':
                    print("✅ Database integrity: OK")
                    return True
                elif status == 'WARNING':
                    print(f"⚠️  Database integrity: WARNING")
                    for issue in issues:
                        print(f"   - {issue}")
                    return True
                else:
                    print(f"❌ Database integrity: {status}")
                    return False
            else:
                print(f"❌ System audit failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Database integrity error: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("=" * 60)
        print("🚀 SISTEMA ELECTORAL ERP - PRUEBAS INTEGRALES")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Base URL: {self.base_url}")
        
        tests = [
            ("System Info", self.test_system_info),
            ("Authentication", self.test_authentication),
            ("Electoral Module", self.test_electoral_module),
            ("Candidates Module", self.test_candidates_module),
            ("Users Module", self.test_users_module),
            ("Reports Module", self.test_reports_module),
            ("Dashboard Module", self.test_dashboard_module),
            ("Database Integrity", self.test_database_integrity)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
        
        # Resumen de resultados
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 Resultados: {passed} exitosas, {failed} fallidas")
        
        if failed == 0:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("✅ El sistema está funcionando correctamente")
            return True
        else:
            print(f"⚠️  {failed} pruebas fallaron")
            print("❌ El sistema requiere atención")
            return False

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Probar Sistema Electoral ERP')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='URL base del sistema (default: http://localhost:5000)')
    parser.add_argument('--module', choices=['all', 'auth', 'electoral', 'candidates', 'users', 'reports', 'dashboard'],
                       default='all', help='Módulo específico a probar')
    
    args = parser.parse_args()
    
    tester = SystemTester(args.url)
    
    if args.module == 'all':
        success = tester.run_all_tests()
    else:
        # Probar módulo específico
        test_methods = {
            'auth': tester.test_authentication,
            'electoral': tester.test_electoral_module,
            'candidates': tester.test_candidates_module,
            'users': tester.test_users_module,
            'reports': tester.test_reports_module,
            'dashboard': tester.test_dashboard_module
        }
        
        if args.module in test_methods:
            # Primero autenticar
            if tester.test_authentication():
                success = test_methods[args.module]()
            else:
                success = False
        else:
            print(f"❌ Módulo desconocido: {args.module}")
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()