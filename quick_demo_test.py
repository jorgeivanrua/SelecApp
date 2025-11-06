#!/usr/bin/env python3
"""
Test rápido del Sistema Electoral ERP
Verifica que el sistema esté funcionando y muestra información de acceso
"""

import requests
import json
from datetime import datetime

def test_system_status():
    """Probar estado del sistema"""
    print("🔍 Verificando estado del sistema...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test de conexión básica
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Servidor web: Funcionando")
        else:
            print(f"  ❌ Servidor web: Error {response.status_code}")
            return False
            
        # Test de API
        response = requests.get(f"{base_url}/api/system/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"  ✅ API: {info.get('name', 'Sistema Electoral ERP')}")
            print(f"  ✅ Versión: {info.get('version', '1.0.0')}")
            print(f"  ✅ Módulos: {', '.join(info.get('modules', []))}")
        else:
            print(f"  ❌ API: Error {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ❌ No se puede conectar al servidor")
        print("  💡 Asegúrate de que el servidor esté ejecutándose:")
        print("     uv run python app.py")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def show_access_info():
    """Mostrar información de acceso"""
    print("\n" + "="*60)
    print("🌐 ACCESO AL SISTEMA ELECTORAL ERP")
    print("="*60)
    
    print("📍 URL del Sistema:")
    print("   http://localhost:5000")
    
    print("\n🔑 Usuarios Demo Disponibles:")
    print("   (Si están configurados en la base de datos)")
    
    users = [
        ("Super Administrador", "12345678", "admin123", "🔴 Rojo/Azul"),
        ("Admin Departamental", "87654321", "admin123", "🔵 Azul/Cyan"),
        ("Admin Municipal", "11111111", "admin123", "🟠 Naranja/Amarillo"),
        ("Coordinador Electoral", "33333333", "coord123", "🟢 Verde/Teal"),
        ("Jurado de Votación", "44444444", "jurado123", "🔵 Azul/Cyan"),
        ("Testigo de Mesa", "22222222", "testigo123", "🟣 Púrpura/Rosa"),
    ]
    
    print(f"\n{'Rol':<22} {'Cédula':<10} {'Contraseña':<10} {'UI'}")
    print("-" * 55)
    
    for rol, cedula, password, ui in users:
        print(f"{rol:<22} {cedula:<10} {password:<10} {ui}")
    
    print("\n📱 Características por Rol:")
    print("   • Cada rol tiene colores únicos")
    print("   • Dashboards personalizados")
    print("   • Funcionalidades específicas")
    print("   • Formularios adaptativos")
    
    print("\n🧪 Para Probar:")
    print("   1. Abrir http://localhost:5000 en el navegador")
    print("   2. Usar cualquier cédula/contraseña de la tabla")
    print("   3. Explorar el dashboard específico del rol")
    print("   4. Probar formularios y funcionalidades")
    
    print("\n🔧 Comandos Útiles:")
    print("   uv run python app.py          # Iniciar servidor")
    print("   uv run python demo.py         # Demo completo")
    print("   uv run python test_system.py  # Tests del sistema")
    
    print("="*60)

def test_ui_components():
    """Probar componentes de UI"""
    print("\n🎨 Verificando componentes de UI...")
    
    import os
    
    # Verificar templates
    templates_dir = "templates"
    if os.path.exists(templates_dir):
        template_files = []
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
        
        print(f"  ✅ Templates: {len(template_files)} archivos HTML")
        
        # Verificar templates por rol
        role_templates = [f for f in template_files if 'roles/' in f]
        print(f"  ✅ Templates por rol: {len(role_templates)}")
    
    # Verificar CSS
    css_dir = "static/css"
    if os.path.exists(css_dir):
        css_files = []
        for root, dirs, files in os.walk(css_dir):
            for file in files:
                if file.endswith('.css'):
                    css_files.append(os.path.join(root, file))
        
        print(f"  ✅ Archivos CSS: {len(css_files)}")
        
        # Verificar CSS por rol
        role_css = [f for f in css_files if 'roles/' in f]
        print(f"  ✅ CSS por rol: {len(role_css)}")
    
    # Verificar JavaScript
    js_dir = "static/js"
    if os.path.exists(js_dir):
        js_files = []
        for root, dirs, files in os.walk(js_dir):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
        
        print(f"  ✅ Archivos JavaScript: {len(js_files)}")
        
        # Verificar JS por rol
        role_js = [f for f in js_files if 'roles/' in f]
        print(f"  ✅ JavaScript por rol: {len(role_js)}")

def main():
    """Función principal"""
    print("🚀 TEST RÁPIDO - SISTEMA ELECTORAL ERP")
    print("="*50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test de estado del sistema
    if test_system_status():
        # Test de componentes UI
        test_ui_components()
        
        # Mostrar información de acceso
        show_access_info()
        
        print("\n🎉 ¡Sistema funcionando correctamente!")
        print("Puedes comenzar a probar las interfaces por rol.")
        
    else:
        print("\n❌ El sistema no está funcionando correctamente")
        print("Revisa que el servidor esté ejecutándose:")
        print("   uv run python app.py")

if __name__ == "__main__":
    main()