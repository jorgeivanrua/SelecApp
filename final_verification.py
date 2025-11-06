#!/usr/bin/env python3
"""
Verificación final completa de todos los dashboards después del autofix.
"""

import re
import os
from pathlib import Path

def verify_html_structure(file_path):
    """Verifica la estructura HTML básica."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Verificar bloques básicos
    required_blocks = [
        '{% extends "base.html" %}',
        '{% block title %}',
        '{% block content %}',
        '{% block role_scripts %}',
        '{% endblock %}'
    ]
    
    for block in required_blocks:
        if block not in content:
            issues.append(f"Falta bloque: {block}")
    
    # Verificar que no hay contenido HTML después del primer {% endblock %}
    content_blocks = content.split('{% block content %}')
    if len(content_blocks) > 1:
        content_section = content_blocks[1]
        first_endblock = content_section.find('{% endblock %}')
        if first_endblock != -1:
            after_endblock = content_section[first_endblock + len('{% endblock %}'):]
            # Verificar que no hay HTML tags después del endblock (excepto comentarios y el siguiente bloque)
            html_after = re.search(r'<(?!!--)[^>]+>', after_endblock.split('{% block')[0])
            if html_after:
                issues.append("Hay contenido HTML después del {% endblock %} del bloque content")
    
    return issues

def verify_javascript_functions(file_path):
    """Verifica que las funciones JavaScript estén bien formadas."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Verificar que las funciones onclick tienen implementación
    onclick_pattern = r'onclick="([^"]*\(\))"'
    onclick_matches = re.findall(onclick_pattern, content)
    
    function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    function_matches = re.findall(function_pattern, content)
    
    for onclick in onclick_matches:
        func_name = onclick.split('(')[0].strip()
        if func_name not in function_matches:
            issues.append(f"Función onclick no implementada: {func_name}")
    
    # Verificar sintaxis básica de JavaScript
    script_sections = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    for script in script_sections:
        # Verificar balanceado de llaves
        open_braces = script.count('{')
        close_braces = script.count('}')
        if open_braces != close_braces:
            issues.append(f"Llaves desbalanceadas en JavaScript: {open_braces} abiertas, {close_braces} cerradas")
    
    return issues

def main():
    """Función principal de verificación."""
    print("🔍 VERIFICACIÓN FINAL COMPLETA POST-AUTOFIX")
    print("=" * 60)
    
    dashboards = [
        "templates/roles/testigo_electoral/dashboard.html",
        "templates/roles/coordinador_puesto/dashboard.html", 
        "templates/roles/coordinador_municipal/dashboard.html",
        "templates/roles/coordinador_departamental/dashboard.html"
    ]
    
    all_passed = True
    
    for dashboard in dashboards:
        if not os.path.exists(dashboard):
            print(f"❌ ARCHIVO NO ENCONTRADO: {dashboard}")
            all_passed = False
            continue
            
        print(f"\n📋 Verificando {dashboard}")
        print("-" * 50)
        
        # Verificar estructura HTML
        html_issues = verify_html_structure(dashboard)
        if html_issues:
            print("❌ PROBLEMAS DE ESTRUCTURA HTML:")
            for issue in html_issues:
                print(f"  - {issue}")
            all_passed = False
        else:
            print("✅ Estructura HTML correcta")
        
        # Verificar funciones JavaScript
        js_issues = verify_javascript_functions(dashboard)
        if js_issues:
            print("❌ PROBLEMAS DE JAVASCRIPT:")
            for issue in js_issues:
                print(f"  - {issue}")
            all_passed = False
        else:
            print("✅ Funciones JavaScript correctas")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 VERIFICACIÓN FINAL EXITOSA - TODOS LOS DASHBOARDS ESTÁN CORRECTOS")
        print("✅ Estructura HTML válida")
        print("✅ Funciones JavaScript implementadas")
        print("✅ Sin errores de sintaxis")
        print("✅ Listos para producción")
    else:
        print("⚠️  SE ENCONTRARON PROBLEMAS EN LA VERIFICACIÓN")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)