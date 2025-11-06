#!/usr/bin/env python3
"""
Test Final del Sistema Electoral ERP con UV
Verifica todas las funcionalidades y componentes del sistema
"""

import requests
import os
import json
from datetime import datetime
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = {
            'server': False,
            'api': False,
            'templates': 0,
            'css_files': 0,
            'js_files': 0,
            'role_templates': 0,
            'role_css': 0,
            'role_js': 0,
            'modules': [],
            'errors': []
        }
    
    def test_server_connection(self):
        """Test conexión al servidor"""
        print("🔍 Testing server connection...")
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("  ✅ Server: Running on port 5000")
                self.results['server'] = True
                return True
            else:
                print(f"  ❌ Server: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Server: Not responding")
            self.results['errors'].append("Server not running")
            return False
        except Exception as e:
            print(f"  ❌ Server: {e}")
            self.results['errors'].append(f"Server error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("🔍 Testing API endpoints...")
        
        endpoints = [
            ('/api/system/info', 'System Info'),
            ('/api/auth/login', 'Authentication'),
            ('/api/electoral/processes', 'Electoral'),
            ('/api/candidates/candidates', 'Candidates'),
            ('/api/users/users', 'Users'),
            ('/api/reports/electoral-summary', 'Reports'),
            ('/api/dashboard/overview', 'Dashboard')
        ]
        
        working_endpoints = 0
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=3)
                if response.status_code in [200, 401]:  # 401 es esperado sin auth
                    print(f"  ✅ {name}: Available")
                    working_endpoints += 1
                else:
                    print(f"  ❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        if working_endpoints >= 5:
            self.results['api'] = True
            print(f"  📊 API Status: {working_endpoints}/{len(endpoints)} endpoints working")
        
        # Test system info específicamente
        try:
            response = requests.get(f"{self.base_url}/api/system/info", timeout=3)
            if response.status_code == 200:
                info = response.json()
                self.results['modules'] = info.get('modules', [])
                print(f"  ✅ Modules loaded: {', '.join(self.results['modules'])}")
        except:
            pass
    
    def test_ui_components(self):
        """Test componentes de UI"""
        print("🔍 Testing UI components...")
        
        # Test templates
        templates_dir = Path("templates")
        if templates_dir.exists():
            template_files = list(templates_dir.rglob("*.html"))
            self.results['templates'] = len(template_files)
            
            role_templates = [f for f in template_files if 'roles' in str(f)]
            self.results['role_templates'] = len(role_templates)
            
            print(f"  ✅ Templates: {len(template_files)} total, {len(role_templates)} role-specific")
        
        # Test CSS
        css_dir = Path("static/css")
        if css_dir.exists():
            css_files = list(css_dir.rglob("*.css"))
            self.results['css_files'] = len(css_files)
            
            role_css = [f for f in css_files if 'roles' in str(f)]
            self.results['role_css'] = len(role_css)
            
            print(f"  ✅ CSS: {len(css_files)} total, {len(role_css)} role-specific")
        
        # Test JavaScript
        js_dir = Path("static/js")
        if js_dir.exists():
            js_files = list(js_dir.rglob("*.js"))
            self.results['js_files'] = len(js_files)
            
            role_js = [f for f in js_files if 'roles' in str(f)]
            self.results['role_js'] = len(role_js)
            
            print(f"  ✅ JavaScript: {len(js_files)} total, {len(role_js)} role-specific")
    
    def test_uv_configuration(self):
        """Test configuración UV"""
        print("🔍 Testing UV configuration...")
        
        # Test pyproject.toml
        pyproject_file = Path("pyproject.toml")
        if pyproject_file.exists():
            print("  ✅ pyproject.toml: Found")
            try:
                import tomllib
                with open(pyproject_file, 'rb') as f:
                    config = tomllib.load(f)
                    
                project_name = config.get('project', {}).get('name', 'Unknown')
                version = config.get('project', {}).get('version', 'Unknown')
                dependencies = len(config.get('project', {}).get('dependencies', []))
                
                print(f"  ✅ Project: {project_name} v{version}")
                print(f"  ✅ Dependencies: {dependencies} packages")
                
            except ImportError:
                print("  ⚠️  tomllib not available (Python < 3.11)")
            except Exception as e:
                print(f"  ❌ pyproject.toml parse error: {e}")
        
        # Test uv.lock
        uv_lock = Path("uv.lock")
        if uv_lock.exists():
            print("  ✅ uv.lock: Found")
        else:
            print("  ⚠️  uv.lock: Not found")
    
    def test_role_specific_features(self):
        """Test características específicas por rol"""
        print("🔍 Testing role-specific features...")
        
        roles = [
            ('super_admin', 'Super Administrador', '🔴'),
            ('admin_departamental', 'Admin Departamental', '🔵'),
            ('admin_municipal', 'Admin Municipal', '🟠'),
            ('coordinador_electoral', 'Coordinador Electoral', '🟢'),
            ('jurado_votacion', 'Jurado de Votación', '🔵'),
            ('testigo_mesa', 'Testigo de Mesa', '🟣')
        ]
        
        for role_key, role_name, color in roles:
            # Check template
            template_path = Path(f"templates/roles/{role_key}/dashboard.html")
            css_path = Path(f"static/css/roles/{role_key}.css")
            js_path = Path(f"static/js/roles/{role_key}.js")
            
            components = []
            if template_path.exists():
                components.append("HTML")
            if css_path.exists():
                components.append("CSS")
            if js_path.exists():
                components.append("JS")
            
            if components:
                print(f"  ✅ {color} {role_name}: {', '.join(components)}")
            else:
                print(f"  ❌ {color} {role_name}: No components found")
    
    def generate_report(self):
        """Generar reporte final"""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DEL SISTEMA")
        print("="*60)
        
        # Estado general
        if self.results['server'] and self.results['api']:
            status = "🟢 FUNCIONANDO"
        elif self.results['server']:
            status = "🟡 PARCIAL"
        else:
            status = "🔴 NO FUNCIONA"
        
        print(f"Estado General: {status}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Componentes
        print(f"\n📁 Componentes:")
        print(f"  • Templates: {self.results['templates']} ({self.results['role_templates']} por rol)")
        print(f"  • CSS Files: {self.results['css_files']} ({self.results['role_css']} por rol)")
        print(f"  • JS Files: {self.results['js_files']} ({self.results['role_js']} por rol)")
        
        # Módulos
        if self.results['modules']:
            print(f"\n🔧 Módulos Activos: {', '.join(self.results['modules'])}")
        
        # Errores
        if self.results['errors']:
            print(f"\n❌ Errores:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        # Acceso
        print(f"\n🌐 Acceso al Sistema:")
        print(f"  URL: {self.base_url}")
        print(f"  Estado: {'✅ Disponible' if self.results['server'] else '❌ No disponible'}")
        
        # Usuarios demo
        print(f"\n👥 Usuarios Demo:")
        demo_users = [
            ("Super Admin", "12345678", "admin123"),
            ("Admin Depto", "87654321", "admin123"),
            ("Admin Municipal", "11111111", "admin123"),
            ("Testigo Mesa", "22222222", "testigo123")
        ]
        
        for role, cedula, password in demo_users:
            print(f"  • {role}: {cedula} / {password}")
        
        print("="*60)
        
        return status == "🟢 FUNCIONANDO"

def main():
    """Función principal"""
    print("🚀 SISTEMA ELECTORAL ERP - TEST FINAL")
    print("="*50)
    
    tester = SystemTester()
    
    # Ejecutar tests
    tester.test_server_connection()
    tester.test_api_endpoints()
    tester.test_ui_components()
    tester.test_uv_configuration()
    tester.test_role_specific_features()
    
    # Generar reporte
    success = tester.generate_report()
    
    if success:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("Puedes comenzar a usar el Sistema Electoral ERP.")
    else:
        print("\n⚠️  Sistema con problemas. Revisa los errores arriba.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())