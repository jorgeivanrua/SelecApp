#!/usr/bin/env python3
"""
Test final optimizado del Sistema Electoral ERP
Enfocado en las funcionalidades principales
"""

import requests
import time
from pathlib import Path

def test_sistema_completo():
    """Test completo optimizado"""
    
    print("🚀 TEST FINAL OPTIMIZADO - SISTEMA ELECTORAL ERP")
    print("="*60)
    
    base_url = "http://localhost:5000"
    results = {'passed': 0, 'total': 0}
    
    def test_item(name, condition, details=""):
        results['total'] += 1
        if condition:
            results['passed'] += 1
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} - {details}")
    
    # 1. CONECTIVIDAD BÁSICA
    print("\n🔍 1. CONECTIVIDAD Y SERVIDOR")
    try:
        response = requests.get(f"{base_url}/", timeout=3)
        test_item("Servidor respondiendo", response.status_code == 200)
        
        response = requests.get(f"{base_url}/api/system/info", timeout=3)
        test_item("API funcionando", response.status_code == 200)
    except Exception as e:
        test_item("Servidor respondiendo", False, str(e))
        test_item("API funcionando", False, str(e))
    
    # 2. AUTENTICACIÓN
    print("\n🔐 2. SISTEMA DE AUTENTICACIÓN")
    tokens = {}
    users_to_test = [
        ("12345678", "admin123", "Super Admin"),
        ("11111111", "admin123", "Admin Municipal"),
        ("22222222", "testigo123", "Testigo Mesa")
    ]
    
    for cedula, password, name in users_to_test:
        try:
            response = requests.post(f"{base_url}/api/auth/login", json={
                "cedula": cedula,
                "password": password
            }, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                tokens[name] = token
                test_item(f"Login {name}", bool(token))
            else:
                test_item(f"Login {name}", False, f"Status: {response.status_code}")
        except Exception as e:
            test_item(f"Login {name}", False, str(e))
    
    # 3. PÁGINAS WEB
    print("\n🌐 3. PÁGINAS WEB PRINCIPALES")
    pages = [
        ('/', 'Inicio'),
        ('/login', 'Login'),
        ('/test-login', 'Test Login'),
        ('/dashboard', 'Dashboard')
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{base_url}{url}", timeout=3)
            test_item(f"Página {name}", response.status_code == 200)
        except Exception as e:
            test_item(f"Página {name}", False, str(e))
    
    # 4. COMPONENTES UI
    print("\n🎨 4. COMPONENTES DE INTERFAZ")
    
    # Templates
    templates_dir = Path("templates")
    html_files = list(templates_dir.rglob("*.html")) if templates_dir.exists() else []
    test_item("Templates HTML", len(html_files) >= 8, f"Encontrados: {len(html_files)}")
    
    # CSS
    css_dir = Path("static/css")
    css_files = list(css_dir.rglob("*.css")) if css_dir.exists() else []
    test_item("Archivos CSS", len(css_files) >= 6, f"Encontrados: {len(css_files)}")
    
    # JavaScript
    js_dir = Path("static/js")
    js_files = list(js_dir.rglob("*.js")) if js_dir.exists() else []
    test_item("Archivos JavaScript", len(js_files) >= 5, f"Encontrados: {len(js_files)}")
    
    # 5. ROLES Y PERMISOS
    print("\n👥 5. ROLES Y COMPONENTES")
    roles = [
        ('super_admin', 'Super Administrador'),
        ('admin_municipal', 'Admin Municipal'),
        ('testigo_mesa', 'Testigo Mesa'),
        ('testigo', 'Testigo (alternativo)')
    ]
    
    for role_key, role_name in roles:
        template_exists = Path(f"templates/roles/{role_key}/dashboard.html").exists()
        css_exists = Path(f"static/css/roles/{role_key}.css").exists()
        js_exists = Path(f"static/js/roles/{role_key}.js").exists()
        
        components = sum([template_exists, css_exists, js_exists])
        test_item(f"Componentes {role_name}", components >= 2, f"Componentes: {components}/3")
    
    # 6. BASE DE DATOS
    print("\n🗄️  6. BASE DE DATOS")
    db_file = Path("caqueta_electoral.db")
    test_item("Archivo BD existe", db_file.exists())
    
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        test_item("BD con contenido", size_mb > 0.1, f"Tamaño: {size_mb:.2f} MB")
    
    # 7. CONFIGURACIÓN UV
    print("\n📦 7. CONFIGURACIÓN UV")
    test_item("pyproject.toml", Path("pyproject.toml").exists())
    test_item("uv.lock", Path("uv.lock").exists())
    
    # 8. PERFORMANCE BÁSICO
    print("\n⚡ 8. PERFORMANCE")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/", timeout=5)
        response_time = time.time() - start_time
        test_item("Tiempo respuesta < 3s", response_time < 3.0, f"Tiempo: {response_time:.2f}s")
    except Exception as e:
        test_item("Tiempo respuesta < 3s", False, str(e))
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    passed = results['passed']
    total = results['total']
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        status = "🟢 EXCELENTE"
        message = "¡Sistema completamente funcional!"
    elif success_rate >= 80:
        status = "🟡 MUY BUENO"
        message = "Sistema funcionando muy bien con errores menores"
    elif success_rate >= 70:
        status = "🟠 BUENO"
        message = "Sistema funcionando bien, revisar algunos componentes"
    else:
        status = "🔴 REQUIERE ATENCIÓN"
        message = "Sistema con problemas que requieren corrección"
    
    print(f"🎯 Estado: {status}")
    print(f"💬 {message}")
    
    print(f"\n🌐 Acceso al sistema:")
    print(f"   • Principal: http://localhost:5000")
    print(f"   • Login: http://localhost:5000/login")
    print(f"   • Test: http://localhost:5000/test-login")
    
    print(f"\n🔑 Credenciales verificadas:")
    for cedula, password, name in users_to_test:
        if name in tokens:
            print(f"   ✅ {name}: {cedula} / {password}")
        else:
            print(f"   ❌ {name}: {cedula} / {password}")
    
    print("="*60)
    
    return success_rate >= 75

if __name__ == "__main__":
    success = test_sistema_completo()
    exit(0 if success else 1)