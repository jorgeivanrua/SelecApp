#!/usr/bin/env python3
"""
Script de verificación rápida de la corrección del OCR
"""

import os
import sys

def verificar_archivo_modificado():
    """Verificar que el archivo fue modificado correctamente"""
    print("=" * 60)
    print("VERIFICACIÓN: Archivo Modificado")
    print("=" * 60)
    
    archivo = "templates/roles/testigo_mesa/dashboard.html"
    
    if not os.path.exists(archivo):
        print(f"❌ ERROR: No se encuentra el archivo {archivo}")
        return False
    
    print(f"✅ Archivo encontrado: {archivo}")
    
    # Leer el archivo
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar que contiene la corrección
    if 'lastElementChild' in contenido:
        print("✅ Corrección implementada: lastElementChild encontrado")
    else:
        print("❌ ERROR: No se encuentra lastElementChild en el código")
        return False
    
    # Verificar que NO contiene el código antiguo problemático
    if 'setTimeout(() => {' in contenido and 'inputs[index].value' in contenido:
        print("⚠️  ADVERTENCIA: Aún contiene código antiguo con setTimeout e inputs[index]")
        print("   Esto podría indicar que hay múltiples versiones del código")
    else:
        print("✅ Código antiguo problemático eliminado")
    
    # Verificar función específica
    if 'function llenarFormularioConOCR' in contenido:
        print("✅ Función llenarFormularioConOCR encontrada")
    else:
        print("❌ ERROR: No se encuentra la función llenarFormularioConOCR")
        return False
    
    return True


def verificar_estructura_proyecto():
    """Verificar que la estructura del proyecto está correcta"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Estructura del Proyecto")
    print("=" * 60)
    
    archivos_requeridos = [
        "app.py",
        "services/ocr_e14_service.py",
        "api/testigo_api.py",
        "templates/roles/testigo_mesa/dashboard.html",
        "caqueta_electoral.db"
    ]
    
    todos_ok = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    return todos_ok


def verificar_documentacion():
    """Verificar que la documentación fue creada"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Documentación")
    print("=" * 60)
    
    documentos = [
        "CORRECCION_CARGA_OCR.md",
        "RESUMEN_CORRECCION_OCR.md",
        "INSTRUCCIONES_PRUEBA_OCR.md",
        "test_ocr_carga_datos.py"
    ]
    
    todos_ok = True
    for doc in documentos:
        if os.path.exists(doc):
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} - NO ENCONTRADO")
            todos_ok = False
    
    return todos_ok


def verificar_sintaxis_python():
    """Verificar que los archivos Python no tienen errores de sintaxis"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN: Sintaxis Python")
    print("=" * 60)
    
    archivos_python = [
        "app.py",
        "services/ocr_e14_service.py",
        "api/testigo_api.py",
        "test_ocr_carga_datos.py"
    ]
    
    todos_ok = True
    for archivo in archivos_python:
        if not os.path.exists(archivo):
            print(f"⚠️  {archivo} - No encontrado, saltando")
            continue
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                compile(f.read(), archivo, 'exec')
            print(f"✅ {archivo} - Sintaxis correcta")
        except SyntaxError as e:
            print(f"❌ {archivo} - ERROR DE SINTAXIS: {e}")
            todos_ok = False
    
    return todos_ok


def mostrar_resumen():
    """Mostrar resumen de la corrección"""
    print("\n" + "=" * 60)
    print("RESUMEN DE LA CORRECCIÓN")
    print("=" * 60)
    
    print("\n📝 Cambio Principal:")
    print("   Archivo: templates/roles/testigo_mesa/dashboard.html")
    print("   Función: llenarFormularioConOCR(datos)")
    
    print("\n🔧 Modificación:")
    print("   ANTES: setTimeout + inputs[index]")
    print("   DESPUÉS: lastElementChild + querySelector")
    
    print("\n✅ Beneficios:")
    print("   • Carga inmediata de votos")
    print("   • Sin problemas de sincronización")
    print("   • Totales calculados correctamente")
    print("   • Mejor experiencia de usuario")
    
    print("\n📚 Documentación Creada:")
    print("   • CORRECCION_CARGA_OCR.md (detallada)")
    print("   • RESUMEN_CORRECCION_OCR.md (breve)")
    print("   • INSTRUCCIONES_PRUEBA_OCR.md (para probar)")
    print("   • test_ocr_carga_datos.py (tests)")


def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETA DE LA CORRECCIÓN DEL OCR")
    print("=" * 60)
    print()
    
    resultados = []
    
    # Verificación 1: Archivo modificado
    resultados.append(("Archivo Modificado", verificar_archivo_modificado()))
    
    # Verificación 2: Estructura del proyecto
    resultados.append(("Estructura del Proyecto", verificar_estructura_proyecto()))
    
    # Verificación 3: Documentación
    resultados.append(("Documentación", verificar_documentacion()))
    
    # Verificación 4: Sintaxis Python
    resultados.append(("Sintaxis Python", verificar_sintaxis_python()))
    
    # Mostrar resumen
    mostrar_resumen()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} - {nombre}")
    
    print("\n" + "=" * 60)
    if todos_ok:
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("=" * 60)
        print("\n🚀 Próximos pasos:")
        print("   1. Reiniciar el servidor: python app.py")
        print("   2. Abrir: http://127.0.0.1:5000/login")
        print("   3. Login: 1000000001 / Demo2024!")
        print("   4. Capturar foto del E14")
        print("   5. Verificar que los votos se cargan correctamente")
        print("\n📖 Ver instrucciones completas en: INSTRUCCIONES_PRUEBA_OCR.md")
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("=" * 60)
        print("\n⚠️  Revisar los errores arriba y corregir antes de continuar")
        return 1


if __name__ == '__main__':
    sys.exit(main())
