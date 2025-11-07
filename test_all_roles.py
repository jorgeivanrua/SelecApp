#!/usr/bin/env python3
"""
Script para verificar el funcionamiento de todos los roles y sus dashboards
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"

# Lista de todos los roles del sistema
ROLES = [
    'super_admin',
    'admin_departamental',
    'admin_municipal',
    'coordinador_electoral',
    'coordinador_departamental',
    'coordinador_municipal',
    'coordinador_puesto',
    'testigo_mesa',
    'auditor_electoral',
    'observador_internacional'
]

# Aliases de roles
ROLE_ALIASES = {
    'testigo': 'testigo_mesa',
    'auditor': 'auditor_electoral',
    'observador': 'observador_internacional'
}

def test_dashboard(role):
    """Probar el dashboard de un rol específico"""
    url = f"{BASE_URL}/dashboard/{role}"
    try:
        response = requests.get(url, timeout=5)
        return {
            'role': role,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'content_length': len(response.content),
            'has_html': 'html' in response.text.lower()
        }
    except Exception as e:
        return {
            'role': role,
            'status_code': 0,
            'success': False,
            'error': str(e)
        }

def test_role_alias(alias, expected_role):
    """Probar que un alias funcione correctamente"""
    url = f"{BASE_URL}/dashboard/{alias}"
    try:
        response = requests.get(url, timeout=5)
        return {
            'alias': alias,
            'expected_role': expected_role,
            'status_code': response.status_code,
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'alias': alias,
            'expected_role': expected_role,
            'status_code': 0,
            'success': False,
            'error': str(e)
        }

def test_health():
    """Probar el endpoint de health check"""
    url = f"{BASE_URL}/api/health"
    try:
        response = requests.get(url, timeout=5)
        return {
            'success': response.status_code == 200,
            'data': response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Función principal"""
    print("=" * 80)
    print("🧪 VERIFICACIÓN DE ROLES Y DASHBOARDS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    print()
    
    # 1. Verificar health check
    print("1️⃣ Verificando Health Check...")
    health = test_health()
    if health['success']:
        print("   ✅ Sistema saludable")
        if health.get('data'):
            print(f"   📊 Versión: {health['data'].get('version')}")
            print(f"   📊 Estado BD: {health['data'].get('database')}")
    else:
        print(f"   ❌ Error: {health.get('error')}")
    print()
    
    # 2. Verificar dashboards de roles
    print("2️⃣ Verificando Dashboards de Roles...")
    print()
    
    results = []
    for role in ROLES:
        result = test_dashboard(role)
        results.append(result)
        
        status_icon = "✅" if result['success'] else "❌"
        print(f"   {status_icon} {role:30} | Status: {result['status_code']} | Size: {result.get('content_length', 0):,} bytes")
        
        if not result['success'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print()
    
    # 3. Verificar aliases
    print("3️⃣ Verificando Aliases de Roles...")
    print()
    
    alias_results = []
    for alias, expected_role in ROLE_ALIASES.items():
        result = test_role_alias(alias, expected_role)
        alias_results.append(result)
        
        status_icon = "✅" if result['success'] else "❌"
        print(f"   {status_icon} {alias:15} → {expected_role:30} | Status: {result['status_code']}")
        
        if not result['success'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print()
    
    # 4. Resumen
    print("=" * 80)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    
    successful_roles = sum(1 for r in results if r['success'])
    total_roles = len(results)
    success_rate = (successful_roles / total_roles * 100) if total_roles > 0 else 0
    
    print(f"✅ Roles funcionando: {successful_roles}/{total_roles} ({success_rate:.1f}%)")
    
    successful_aliases = sum(1 for r in alias_results if r['success'])
    total_aliases = len(alias_results)
    alias_success_rate = (successful_aliases / total_aliases * 100) if total_aliases > 0 else 0
    
    print(f"✅ Aliases funcionando: {successful_aliases}/{total_aliases} ({alias_success_rate:.1f}%)")
    
    # Roles con problemas
    failed_roles = [r['role'] for r in results if not r['success']]
    if failed_roles:
        print()
        print("⚠️  Roles con problemas:")
        for role in failed_roles:
            print(f"   - {role}")
    
    # Aliases con problemas
    failed_aliases = [r['alias'] for r in alias_results if not r['success']]
    if failed_aliases:
        print()
        print("⚠️  Aliases con problemas:")
        for alias in failed_aliases:
            print(f"   - {alias}")
    
    print()
    print("=" * 80)
    
    # Estado final
    if successful_roles == total_roles and successful_aliases == total_aliases:
        print("🎉 ¡TODOS LOS ROLES Y DASHBOARDS FUNCIONAN CORRECTAMENTE!")
    else:
        print("⚠️  Algunos roles o dashboards requieren atención")
    
    print("=" * 80)
    
    # Guardar resultados en JSON
    report = {
        'timestamp': datetime.now().isoformat(),
        'base_url': BASE_URL,
        'health_check': health,
        'roles': results,
        'aliases': alias_results,
        'summary': {
            'total_roles': total_roles,
            'successful_roles': successful_roles,
            'success_rate': success_rate,
            'total_aliases': total_aliases,
            'successful_aliases': successful_aliases,
            'alias_success_rate': alias_success_rate
        }
    }
    
    with open('role_verification_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("📄 Reporte guardado en: role_verification_report.json")
    print()

if __name__ == '__main__':
    main()
