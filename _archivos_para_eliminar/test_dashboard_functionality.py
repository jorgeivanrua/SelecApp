#!/usr/bin/env python3
"""
Script para verificar que todos los botones de los dashboards tienen funciones JavaScript implementadas.
"""

import re
import os
from pathlib import Path

def extract_onclick_functions(file_path):
    """Extrae todas las funciones onclick de un archivo HTML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todos los onclick="functionName()"
    onclick_pattern = r'onclick="([^"]*\(\))"'
    onclick_matches = re.findall(onclick_pattern, content)
    
    # Limpiar y extraer solo los nombres de función
    functions = []
    for match in onclick_matches:
        # Extraer el nombre de la función (antes del primer paréntesis)
        func_name = match.split('(')[0].strip()
        if func_name:
            functions.append(func_name)
    
    return functions

def extract_implemented_functions(file_path):
    """Extrae todas las funciones JavaScript implementadas en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las definiciones de función
    function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    function_matches = re.findall(function_pattern, content)
    
    return function_matches

def verify_dashboard_functionality(dashboard_path):
    """Verifica que todas las funciones onclick estén implementadas en un dashboard."""
    print(f"\n=== Verificando {dashboard_path} ===")
    
    onclick_functions = extract_onclick_functions(dashboard_path)
    implemented_functions = extract_implemented_functions(dashboard_path)
    
    print(f"Funciones onclick encontradas: {len(onclick_functions)}")
    print(f"Funciones implementadas: {len(implemented_functions)}")
    
    missing_functions = []
    for func in onclick_functions:
        if func not in implemented_functions:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ FUNCIONES FALTANTES ({len(missing_functions)}):")
        for func in missing_functions:
            print(f"  - {func}()")
        return False
    else:
        print("✅ TODAS LAS FUNCIONES ESTÁN IMPLEMENTADAS")
        return True

def main():
    """Función principal."""
    print("🔍 VERIFICACIÓN DE FUNCIONALIDAD DE DASHBOARDS")
    print("=" * 50)
    
    # Dashboards a verificar
    dashboards = [
        "templates/roles/testigo_electoral/dashboard.html",
        "templates/roles/coordinador_puesto/dashboard.html", 
        "templates/roles/coordinador_municipal/dashboard.html",
        "templates/roles/coordinador_departamental/dashboard.html"
    ]
    
    all_passed = True
    
    for dashboard in dashboards:
        if os.path.exists(dashboard):
            passed = verify_dashboard_functionality(dashboard)
            all_passed = all_passed and passed
        else:
            print(f"❌ ARCHIVO NO ENCONTRADO: {dashboard}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS LOS DASHBOARDS PASARON LA VERIFICACIÓN")
    else:
        print("⚠️  ALGUNOS DASHBOARDS TIENEN PROBLEMAS")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)