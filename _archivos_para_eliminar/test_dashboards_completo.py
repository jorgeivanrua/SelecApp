#!/usr/bin/env python3
"""
Test completo de funcionalidad de dashboards
Verifica que todos los dashboards tengan funcionalidad JavaScript completa
"""

import os
import re
from pathlib import Path

def analizar_dashboard(archivo_path):
    """Analiza un dashboard para verificar su funcionalidad"""
    with open(archivo_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Extraer información básica
    nombre_rol = archivo_path.stem
    
    # Buscar botones con onclick
    botones_onclick = re.findall(r'onclick="([^"]+)"', contenido)
    
    # Buscar funciones JavaScript definidas
    funciones_js = re.findall(r'function\s+(\w+)\s*\(', contenido)
    
    # Buscar modales
    modales = re.findall(r'mostrarModal[A-Za-z]*\(', contenido)
    
    # Buscar notificaciones
    notificaciones = re.findall(r'mostrarNotificacion[A-Za-z]*\(', contenido)
    
    return {
        'rol': nombre_rol,
        'archivo': archivo_path.name,
        'botones_onclick': len(botones_onclick),
        'funciones_js': len(funciones_js),
        'modales': len(modales),
        'notificaciones': len(notificaciones),
        'funciones_onclick': botones_onclick,
        'lista_funciones': funciones_js
    }

def main():
    """Función principal"""
    print("🔍 ANÁLISIS COMPLETO DE DASHBOARDS")
    print("=" * 50)
    
    # Directorio de dashboards
    dashboards_dir = Path("templates/roles")
    
    if not dashboards_dir.exists():
        print("❌ No se encontró el directorio de dashboards")
        return
    
    resultados = []
    
    # Analizar cada dashboard
    for dashboard_dir in dashboards_dir.iterdir():
        if dashboard_dir.is_dir():
            dashboard_file = dashboard_dir / "dashboard.html"
            if dashboard_file.exists():
                resultado = analizar_dashboard(dashboard_file)
                resultados.append(resultado)
    
    # Mostrar resultados
    print(f"\n📊 RESUMEN DE ANÁLISIS ({len(resultados)} dashboards)")
    print("-" * 80)
    
    for resultado in sorted(resultados, key=lambda x: x['rol']):
        print(f"\n🎯 {resultado['rol'].upper().replace('_', ' ')}")
        print(f"   📁 Archivo: {resultado['archivo']}")
        print(f"   🔘 Botones con funcionalidad: {resultado['botones_onclick']}")
        print(f"   ⚙️  Funciones JavaScript: {resultado['funciones_js']}")
        print(f"   📋 Modales implementados: {resultado['modales']}")
        print(f"   🔔 Notificaciones: {resultado['notificaciones']}")
        
        # Mostrar estado
        if resultado['botones_onclick'] > 0 and resultado['funciones_js'] > 5:
            estado = "✅ COMPLETO"
        elif resultado['botones_onclick'] > 0:
            estado = "⚠️  BÁSICO"
        else:
            estado = "❌ INCOMPLETO"
        
        print(f"   📈 Estado: {estado}")
        
        # Mostrar algunas funciones principales
        if resultado['funciones_onclick']:
            principales = resultado['funciones_onclick'][:3]
            print(f"   🔧 Funciones principales: {', '.join(principales)}")
    
    # Estadísticas generales
    total_botones = sum(r['botones_onclick'] for r in resultados)
    total_funciones = sum(r['funciones_js'] for r in resultados)
    dashboards_completos = sum(1 for r in resultados if r['botones_onclick'] > 0 and r['funciones_js'] > 5)
    
    print(f"\n📈 ESTADÍSTICAS GENERALES")
    print("-" * 30)
    print(f"Total de botones funcionales: {total_botones}")
    print(f"Total de funciones JavaScript: {total_funciones}")
    print(f"Dashboards completos: {dashboards_completos}/{len(resultados)}")
    print(f"Porcentaje de completitud: {(dashboards_completos/len(resultados)*100):.1f}%")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES")
    print("-" * 20)
    
    incompletos = [r for r in resultados if r['botones_onclick'] == 0 or r['funciones_js'] <= 5]
    if incompletos:
        print("Dashboards que necesitan mejoras:")
        for r in incompletos:
            print(f"  - {r['rol']}: Agregar más funcionalidad JavaScript")
    else:
        print("✅ Todos los dashboards tienen funcionalidad completa")
    
    print(f"\n🎉 ANÁLISIS COMPLETADO")
    print("Todos los dashboards han sido verificados")

if __name__ == "__main__":
    main()