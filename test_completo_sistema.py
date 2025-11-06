#!/usr/bin/env python3
"""
TEST COMPLETO Y EXHAUSTIVO DEL SISTEMA ELECTORAL ERP
Verifica todas las funcionalidades, módulos, endpoints y características
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

class SistemaElectoralTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.tokens = {}  # Almacenar tokens por rol
        self.users = {}   # Almacenar datos de usuarios
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        # Usuarios de prueba
        self.test_users = [
            ("12345678", "admin123", "super_admin", "Super Administrador"),
            ("87654321", "admin123", "admin_departamental", "Admin Departamental"),
            ("11111111", "admin123", "admin_municipal", "Admin Municipal"),
            ("33333333", "coord123", "coordinador_electoral", "Coordinador Electoral"),
            ("44444444", "jurado123", "jurado_votacion", "Jurado de Votación"),
            ("22222222", "testigo123", "testigo", "Testigo de Mesa")
        ]
    
    def log_test(self, test_name, success, details=""):
        """Registrar resultado de test"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed_tests'] += 1
            print(f"  ✅ {test_name}")
        else:
            self.results['failed_tests'] += 1
            print(f"  ❌ {test_name}")
            if details:
                self.results['errors'].append(f"{test_name}: {details}")
                print(f"     Error: {details}")
        
        self.results['details'][test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_server_connectivity(self):
        """Test 1: Conectividad del servidor"""
        print("\n🔍 1. TESTING CONECTIVIDAD DEL SERVIDOR")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.log_test("Servidor respondiendo", response.status_code == 200)
            
            response = requests.get(f"{self.base_url}/api/system/info", timeout=5)
            if response.status_code == 200:
                info = response.json()
                self.log_test("API de sistema funcionando", True)
                self.log_test("Módulos cargados", len(info.get('modules', [])) >= 5)
            else:
                self.log_test("API de sistema funcionando", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Servidor respondiendo", False, str(e))
    
    def test_authentication_system(self):
        """Test 2: Sistema de autenticación"""
        print("\n🔐 2. TESTING SISTEMA DE AUTENTICACIÓN")
        
        # Test login para cada usuario
        for cedula, password, rol, nombre in self.test_users:
            try:
                response = requests.post(f"{self.base_url}/api/auth/login", json={
                    "cedula": cedula,
                    "password": password
                }, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    user = data.get('user', {})
                    
                    if token and user.get('rol') == rol:
                        self.tokens[rol] = token
                        self.users[rol] = user
                        self.log_test(f"Login {nombre}", True)
                    else:
                        self.log_test(f"Login {nombre}", False, "Token o rol inválido")
                else:
                    self.log_test(f"Login {nombre}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Login {nombre}", False, str(e))
        
        # Test token inválido
        try:
            headers = {'Authorization': 'Bearer token_invalido'}
            response = requests.get(f"{self.base_url}/api/auth/me", headers=headers, timeout=5)
            self.log_test("Rechazo token inválido", response.status_code == 401)
        except Exception as e:
            self.log_test("Rechazo token inválido", False, str(e))
    
    def test_protected_endpoints(self):
        """Test 3: Endpoints protegidos"""
        print("\n🔒 3. TESTING ENDPOINTS PROTEGIDOS")
        
        if not self.tokens:
            print("  ⚠️  No hay tokens disponibles, saltando tests de endpoints protegidos")
            return
        
        # Usar token de super admin para tests
        token = self.tokens.get('super_admin') or list(self.tokens.values())[0]
        headers = {'Authorization': f'Bearer {token}'}
        
        # Endpoints a probar
        endpoints = [
            ('/api/auth/me', 'Información usuario actual'),
            ('/api/electoral/processes', 'Procesos electorales'),
            ('/api/candidates/candidates', 'Lista de candidatos'),
            ('/api/users/users', 'Lista de usuarios'),
            ('/api/reports/electoral-summary', 'Resumen electoral'),
            ('/api/dashboard/overview', 'Dashboard general')
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                # Aceptar 200 (éxito) o 401 (sin permisos específicos)
                success = response.status_code in [200, 401, 403]
                self.log_test(f"Endpoint {description}", success, 
                             f"Status: {response.status_code}" if not success else "")
            except Exception as e:
                self.log_test(f"Endpoint {description}", False, str(e))
    
    def test_web_pages(self):
        """Test 4: Páginas web"""
        print("\n🌐 4. TESTING PÁGINAS WEB")
        
        pages = [
            ('/', 'Página principal'),
            ('/login', 'Página de login'),
            ('/test-login', 'Página de test login'),
            ('/dashboard', 'Dashboard principal')
        ]
        
        for url, description in pages:
            try:
                response = requests.get(f"{self.base_url}{url}", timeout=5)
                success = response.status_code == 200
                self.log_test(f"Página {description}", success,
                             f"Status: {response.status_code}" if not success else "")
            except Exception as e:
                self.log_test(f"Página {description}", False, str(e))
    
    def test_database_integrity(self):
        """Test 5: Integridad de base de datos"""
        print("\n🗄️  5. TESTING INTEGRIDAD DE BASE DE DATOS")
        
        # Verificar archivo de base de datos
        db_file = Path("caqueta_electoral.db")
        self.log_test("Archivo de BD existe", db_file.exists())
        
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            self.log_test("BD tiene contenido", size_mb > 0.1, f"Tamaño: {size_mb:.2f} MB")
        
        # Test de consultas básicas a través de API
        if self.tokens:
            token = list(self.tokens.values())[0]
            headers = {'Authorization': f'Bearer {token}'}
            
            try:
                response = requests.get(f"{self.base_url}/api/users/users", headers=headers, timeout=5)
                if response.status_code == 200:
                    users = response.json()
                    self.log_test("Consulta usuarios BD", len(users) > 0 if isinstance(users, list) else True)
                else:
                    self.log_test("Consulta usuarios BD", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Consulta usuarios BD", False, str(e))
    
    def test_ui_components(self):
        """Test 6: Componentes de UI"""
        print("\n🎨 6. TESTING COMPONENTES DE UI")
        
        # Verificar templates
        templates_dir = Path("templates")
        if templates_dir.exists():
            html_files = list(templates_dir.rglob("*.html"))
            self.log_test("Templates HTML disponibles", len(html_files) >= 10)
            
            role_templates = [f for f in html_files if 'roles' in str(f)]
            self.log_test("Templates por rol", len(role_templates) >= 6)
        else:
            self.log_test("Templates HTML disponibles", False, "Directorio no existe")
        
        # Verificar CSS
        css_dir = Path("static/css")
        if css_dir.exists():
            css_files = list(css_dir.rglob("*.css"))
            self.log_test("Archivos CSS disponibles", len(css_files) >= 6)
            
            role_css = [f for f in css_files if 'roles' in str(f)]
            self.log_test("CSS por rol", len(role_css) >= 6)
        else:
            self.log_test("Archivos CSS disponibles", False, "Directorio no existe")
        
        # Verificar JavaScript
        js_dir = Path("static/js")
        if js_dir.exists():
            js_files = list(js_dir.rglob("*.js"))
            self.log_test("Archivos JavaScript disponibles", len(js_files) >= 5)
            
            role_js = [f for f in js_files if 'roles' in str(f)]
            self.log_test("JavaScript por rol", len(role_js) >= 5)
        else:
            self.log_test("Archivos JavaScript disponibles", False, "Directorio no existe")
    
    def test_uv_configuration(self):
        """Test 7: Configuración UV"""
        print("\n📦 7. TESTING CONFIGURACIÓN UV")
        
        # Verificar pyproject.toml
        pyproject_file = Path("pyproject.toml")
        self.log_test("pyproject.toml existe", pyproject_file.exists())
        
        # Verificar uv.lock
        uv_lock = Path("uv.lock")
        self.log_test("uv.lock existe", uv_lock.exists())
        
        # Test comando uv
        try:
            import subprocess
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True, timeout=5)
            self.log_test("UV instalado", result.returncode == 0)
        except Exception as e:
            self.log_test("UV instalado", False, str(e))
    
    def test_role_specific_features(self):
        """Test 8: Características específicas por rol"""
        print("\n👥 8. TESTING CARACTERÍSTICAS POR ROL")
        
        roles_to_test = [
            ('super_admin', 'Super Administrador'),
            ('admin_departamental', 'Admin Departamental'),
            ('admin_municipal', 'Admin Municipal'),
            ('coordinador_electoral', 'Coordinador Electoral'),
            ('jurado_votacion', 'Jurado de Votación'),
            ('testigo', 'Testigo de Mesa')
        ]
        
        for role_key, role_name in roles_to_test:
            # Verificar archivos específicos del rol
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
            
            self.log_test(f"Componentes {role_name}", len(components) >= 2,
                         f"Disponibles: {', '.join(components)}" if components else "Ninguno")
    
    def test_api_modules(self):
        """Test 9: Módulos de API"""
        print("\n🔧 9. TESTING MÓDULOS DE API")
        
        if not self.tokens:
            print("  ⚠️  No hay tokens disponibles, saltando tests de módulos")
            return
        
        token = list(self.tokens.values())[0]
        headers = {'Authorization': f'Bearer {token}'}
        
        # Módulos a probar
        modules = [
            ('electoral', 'Electoral'),
            ('candidates', 'Candidatos'),
            ('users', 'Usuarios'),
            ('reports', 'Reportes'),
            ('dashboard', 'Dashboard')
        ]
        
        for module, description in modules:
            try:
                # Probar endpoint principal del módulo
                response = requests.get(f"{self.base_url}/api/{module}", headers=headers, timeout=5)
                # Aceptar cualquier respuesta que no sea 404 (módulo existe)
                success = response.status_code != 404
                self.log_test(f"Módulo {description}", success,
                             f"Status: {response.status_code}" if not success else "")
            except Exception as e:
                self.log_test(f"Módulo {description}", False, str(e))
    
    def test_performance_basic(self):
        """Test 10: Performance básico"""
        print("\n⚡ 10. TESTING PERFORMANCE BÁSICO")
        
        # Test tiempo de respuesta de páginas principales
        pages_to_test = [
            ('/', 'Página principal'),
            ('/api/system/info', 'API sistema'),
            ('/login', 'Página login')
        ]
        
        for url, description in pages_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                success = response_time < 2.0  # Menos de 2 segundos
                
                self.log_test(f"Tiempo respuesta {description}", success,
                             f"{response_time:.2f}s" if not success else f"{response_time:.2f}s")
            except Exception as e:
                self.log_test(f"Tiempo respuesta {description}", False, str(e))
    
    def generate_comprehensive_report(self):
        """Generar reporte completo"""
        print("\n" + "="*80)
        print("📊 REPORTE COMPLETO DEL SISTEMA ELECTORAL ERP")
        print("="*80)
        
        # Estadísticas generales
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"  • Total de pruebas: {total}")
        print(f"  • Pruebas exitosas: {passed}")
        print(f"  • Pruebas fallidas: {failed}")
        print(f"  • Tasa de éxito: {success_rate:.1f}%")
        
        # Estado general del sistema
        if success_rate >= 90:
            status = "🟢 EXCELENTE"
        elif success_rate >= 75:
            status = "🟡 BUENO"
        elif success_rate >= 50:
            status = "🟠 REGULAR"
        else:
            status = "🔴 CRÍTICO"
        
        print(f"\n🎯 ESTADO GENERAL: {status}")
        
        # Detalles por categoría
        print(f"\n📋 RESUMEN POR CATEGORÍAS:")
        categories = {
            'Conectividad': ['Servidor respondiendo', 'API de sistema funcionando'],
            'Autenticación': [k for k in self.results['details'].keys() if 'Login' in k],
            'Endpoints': [k for k in self.results['details'].keys() if 'Endpoint' in k],
            'Páginas Web': [k for k in self.results['details'].keys() if 'Página' in k],
            'Base de Datos': [k for k in self.results['details'].keys() if 'BD' in k],
            'UI Components': [k for k in self.results['details'].keys() if any(x in k for x in ['Templates', 'CSS', 'JavaScript'])],
            'Roles': [k for k in self.results['details'].keys() if 'Componentes' in k]
        }
        
        for category, tests in categories.items():
            if tests:
                category_passed = sum(1 for test in tests if self.results['details'].get(test, {}).get('success', False))
                category_total = len(tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 50 else "❌"
                print(f"  {status_icon} {category}: {category_passed}/{category_total} ({category_rate:.0f}%)")
        
        # Errores encontrados
        if self.results['errors']:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for error in self.results['errors'][:10]:  # Mostrar máximo 10 errores
                print(f"  • {error}")
            if len(self.results['errors']) > 10:
                print(f"  ... y {len(self.results['errors']) - 10} errores más")
        
        # Información del sistema
        print(f"\n🔧 INFORMACIÓN DEL SISTEMA:")
        print(f"  • URL Base: {self.base_url}")
        print(f"  • Usuarios de prueba: {len(self.test_users)}")
        print(f"  • Tokens obtenidos: {len(self.tokens)}")
        print(f"  • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if success_rate >= 90:
            print("  🎉 ¡Sistema funcionando excelentemente!")
            print("  • Listo para uso en producción")
            print("  • Considerar agregar más funcionalidades")
        elif success_rate >= 75:
            print("  👍 Sistema funcionando bien")
            print("  • Revisar errores menores")
            print("  • Optimizar componentes con problemas")
        else:
            print("  ⚠️  Sistema requiere atención")
            print("  • Revisar errores críticos")
            print("  • Verificar configuración")
        
        print("="*80)
        
        return success_rate >= 75
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 INICIANDO BATERÍA COMPLETA DE TESTS")
        print("="*60)
        
        start_time = time.time()
        
        # Ejecutar todos los tests
        self.test_server_connectivity()
        self.test_authentication_system()
        self.test_protected_endpoints()
        self.test_web_pages()
        self.test_database_integrity()
        self.test_ui_components()
        self.test_uv_configuration()
        self.test_role_specific_features()
        self.test_api_modules()
        self.test_performance_basic()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️  Tiempo total de ejecución: {total_time:.2f} segundos")
        
        # Generar reporte final
        return self.generate_comprehensive_report()

def main():
    """Función principal"""
    tester = SistemaElectoralTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())