#!/usr/bin/env python3
"""
Script de revisión completa del sistema electoral
Verifica módulos, dashboards, mapas y roles
"""

import os
import requests
import time
from pathlib import Path

def check_file_structure():
    """Verificar estructura de archivos"""
    print("🔍 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    print("=" * 50)
    
    required_files = {
        'app.py': 'Aplicación principal',
        'templates/base.html': 'Template base',
        'templates/dashboard.html': 'Dashboard principal',
        'templates/dashboard_generic.html': 'Dashboard genérico',
        'templates/error.html': 'Página de error',
        'templates/components/electoral_map.html': 'Mapa electoral',
        'templates/components/real_time_stats.html': 'Estadísticas en tiempo real',
        'templates/components/alerts_panel.html': 'Panel de alertas',
        'static/css/base.css': 'Estilos base'
    }
    
    # Verificar archivos principales
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (FALTANTE)")
    
    # Verificar templates de roles
    roles_dir = Path("templates/roles")
    expected_roles = [
        'super_admin', 'admin_departamental', 'admin_municipal',
        'coordinador_electoral', 'jurado_votacion', 'testigo_mesa',
        'auditor_electoral', 'observador_internacional'
    ]
    
    print(f"\n📁 TEMPLATES DE ROLES:")
    for role in expected_roles:
        role_file = roles_dir / role / "dashboard.html"
        if role_file.exists():
            print(f"✅ {role}/dashboard.html")
        else:
            print(f"❌ {role}/dashboard.html (FALTANTE)")
    
    # Verificar CSS de roles
    css_dir = Path("static/css/roles")
    print(f"\n🎨 ARCHIVOS CSS DE ROLES:")
    for role in expected_roles:
        css_file = css_dir / f"{role}.css"
        if css_file.exists():
            print(f"✅ {role}.css")
        else:
            print(f"❌ {role}.css (FALTANTE)")
    
    # Verificar formularios
    forms_dir = Path("templates/forms")
    expected_forms = [
        'audit_form.html', 'observation_form.html', 
        'proceso_electoral_form.html', 'candidate_form.html', 'mesa_form.html'
    ]
    
    print(f"\n📋 FORMULARIOS:")
    for form in expected_forms:
        form_file = forms_dir / form
        if form_file.exists():
            print(f"✅ {form}")
        else:
            print(f"❌ {form} (FALTANTE)")

def check_server_connectivity():
    """Verificar conectividad del servidor"""
    print(f"\n🌐 VERIFICANDO SERVIDOR")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor disponible en http://localhost:5000")
            return True
        else:
            print(f"⚠️  Servidor responde con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

def check_dashboard_functionality():
    """Verificar funcionalidad de dashboards"""
    print(f"\n🎯 VERIFICANDO DASHBOARDS POR ROL")
    print("=" * 50)
    
    roles = {
        'super_admin': 'Super Administrador',
        'admin_departamental': 'Administrador Departamental',
        'admin_municipal': 'Administrador Municipal',
        'coordinador_electoral': 'Coordinador Electoral',
        'jurado_votacion': 'Jurado de Votación',
        'testigo_mesa': 'Testigo de Mesa',
        'auditor_electoral': 'Auditor Electoral',
        'observador_internacional': 'Observador Internacional'
    }
    
    base_url = "http://localhost:5000"
    successful_dashboards = 0
    
    for role, name in roles.items():
        try:
            url = f"{base_url}/dashboard/{role}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {role} ({name})")
                successful_dashboards += 1
            else:
                print(f"❌ {role} ({name}) - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {role} ({name}) - Error: {e}")
    
    print(f"\n📊 Resultado: {successful_dashboards}/{len(roles)} dashboards funcionando")
    return successful_dashboards == len(roles)

def check_aliases():
    """Verificar aliases de roles"""
    print(f"\n🔄 VERIFICANDO ALIASES DE ROLES")
    print("=" * 50)
    
    aliases = {
        'testigo': 'testigo_mesa',
        'auditor': 'auditor_electoral',
        'observador': 'observador_internacional'
    }
    
    base_url = "http://localhost:5000"
    successful_aliases = 0
    
    for alias, target in aliases.items():
        try:
            url = f"{base_url}/dashboard/{alias}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ '{alias}' -> '{target}'")
                successful_aliases += 1
            else:
                print(f"❌ '{alias}' -> '{target}' - Status {response.status_code}")
        except Exception as e:
            print(f"❌ '{alias}' -> '{target}' - Error: {e}")
    
    return successful_aliases == len(aliases)

def check_additional_routes():
    """Verificar rutas adicionales"""
    print(f"\n🛣️  VERIFICANDO RUTAS ADICIONALES")
    print("=" * 50)
    
    routes = {
        '/users': 'Gestión de usuarios',
        '/municipalities': 'Gestión de municipios',
        '/tables': 'Gestión de mesas',
        '/voting/register': 'Registro de votos',
        '/audit/start': 'Formulario de auditoría',
        '/observation/new': 'Observación internacional',
        '/coordination': 'Coordinación de procesos',
        '/schedule': 'Cronograma electoral',
        '/progress': 'Supervisión de avance',
        '/electoral': 'Procesos electorales',
        '/candidates': 'Gestión de candidatos',
        '/reports': 'Reportes del sistema'
    }
    
    base_url = "http://localhost:5000"
    successful_routes = 0
    
    for route, description in routes.items():
        try:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {route} - {description}")
                successful_routes += 1
            else:
                print(f"❌ {route} - {description} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {route} - {description} - Error: {e}")
    
    print(f"\n📊 Resultado: {successful_routes}/{len(routes)} rutas funcionando")
    return successful_routes == len(routes)

def check_error_handling():
    """Verificar manejo de errores"""
    print(f"\n🚫 VERIFICANDO MANEJO DE ERRORES")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    error_tests = [
        '/dashboard/invalid_role',
        '/dashboard/fake_admin',
        '/dashboard/nonexistent',
        '/dashboard/',  # Rol vacío
    ]
    
    successful_errors = 0
    
    for test_url in error_tests:
        try:
            url = f"{base_url}{test_url}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 404:
                print(f"✅ {test_url} - Correctamente rechazado (404)")
                successful_errors += 1
            else:
                print(f"⚠️  {test_url} - Status inesperado {response.status_code}")
        except Exception as e:
            print(f"❌ {test_url} - Error: {e}")
    
    return successful_errors == len(error_tests)

def check_components():
    """Verificar componentes específicos"""
    print(f"\n🧩 VERIFICANDO COMPONENTES")
    print("=" * 50)
    
    components = [
        'templates/components/electoral_map.html',
        'templates/components/real_time_stats.html',
        'templates/components/alerts_panel.html'
    ]
    
    for component in components:
        if os.path.exists(component):
            # Verificar que el archivo no esté vacío
            with open(component, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    print(f"✅ {os.path.basename(component)} - Disponible y con contenido")
                else:
                    print(f"⚠️  {os.path.basename(component)} - Archivo vacío")
        else:
            print(f"❌ {os.path.basename(component)} - No encontrado")

def generate_summary_report():
    """Generar reporte resumen"""
    print(f"\n📋 GENERANDO REPORTE RESUMEN")
    print("=" * 50)
    
    # Ejecutar todas las verificaciones
    server_ok = check_server_connectivity()
    dashboards_ok = check_dashboard_functionality()
    aliases_ok = check_aliases()
    routes_ok = check_additional_routes()
    errors_ok = check_error_handling()
    
    # Calcular puntuación general
    total_checks = 5
    passed_checks = sum([server_ok, dashboards_ok, aliases_ok, routes_ok, errors_ok])
    score = (passed_checks / total_checks) * 100
    
    print(f"\n🎯 PUNTUACIÓN GENERAL: {score:.1f}%")
    print("=" * 50)
    
    if score >= 90:
        print("🎉 EXCELENTE: El sistema está funcionando perfectamente")
        status = "EXCELENTE"
    elif score >= 75:
        print("✅ BUENO: El sistema está funcionando bien con algunos problemas menores")
        status = "BUENO"
    elif score >= 50:
        print("⚠️  REGULAR: El sistema tiene algunos problemas que requieren atención")
        status = "REGULAR"
    else:
        print("❌ CRÍTICO: El sistema tiene problemas graves que requieren corrección inmediata")
        status = "CRÍTICO"
    
    # Generar archivo de reporte
    report_content = f"""# REPORTE DE REVISIÓN COMPLETA - SISTEMA ELECTORAL ERP

## Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
## Estado General: {status} ({score:.1f}%)

### Resultados de Verificación:
- ✅ Servidor: {'OK' if server_ok else 'FALLO'}
- ✅ Dashboards por Rol: {'OK' if dashboards_ok else 'FALLO'}
- ✅ Aliases de Roles: {'OK' if aliases_ok else 'FALLO'}
- ✅ Rutas Adicionales: {'OK' if routes_ok else 'FALLO'}
- ✅ Manejo de Errores: {'OK' if errors_ok else 'FALLO'}

### Componentes Verificados:
- 📁 Estructura de archivos
- 🎯 Dashboards específicos por rol
- 🔄 Sistema de aliases
- 🛣️  Rutas adicionales
- 🚫 Manejo de errores
- 🧩 Componentes visuales
- 🗺️  Mapa electoral interactivo
- 📊 Estadísticas en tiempo real
- 🔔 Panel de alertas

### Recomendaciones:
{get_recommendations(server_ok, dashboards_ok, aliases_ok, routes_ok, errors_ok)}

---
Generado por revision_completa.py
"""
    
    with open('REPORTE_REVISION_COMPLETA.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📄 Reporte guardado en: REPORTE_REVISION_COMPLETA.md")

def get_recommendations(server_ok, dashboards_ok, aliases_ok, routes_ok, errors_ok):
    """Generar recomendaciones basadas en los resultados"""
    recommendations = []
    
    if not server_ok:
        recommendations.append("- Verificar que el servidor Flask esté ejecutándose correctamente")
    
    if not dashboards_ok:
        recommendations.append("- Revisar templates de dashboards por rol y corregir errores")
    
    if not aliases_ok:
        recommendations.append("- Verificar configuración de aliases en app.py")
    
    if not routes_ok:
        recommendations.append("- Agregar rutas faltantes o corregir errores en rutas existentes")
    
    if not errors_ok:
        recommendations.append("- Mejorar manejo de errores para roles inválidos")
    
    if not recommendations:
        recommendations.append("- El sistema está funcionando correctamente")
        recommendations.append("- Considerar agregar más funcionalidades o mejorar la interfaz")
        recommendations.append("- Realizar pruebas de carga y rendimiento")
    
    return '\n'.join(recommendations)

if __name__ == "__main__":
    print("🚀 INICIANDO REVISIÓN COMPLETA DEL SISTEMA ELECTORAL ERP")
    print("=" * 60)
    print("Departamento del Caquetá - Sistema de Gestión Electoral")
    print("=" * 60)
    
    # Verificar estructura de archivos
    check_file_structure()
    
    # Verificar componentes
    check_components()
    
    # Generar reporte completo
    generate_summary_report()
    
    print(f"\n🎉 REVISIÓN COMPLETA FINALIZADA")
    print("Consulta el archivo REPORTE_REVISION_COMPLETA.md para detalles completos")