#!/usr/bin/env python3
"""
Test del OCR con imagen real del E14
"""

from services.ocr_e14_service import ocr_service
import os

print("=" * 70)
print("TEST OCR CON IMAGEN REAL E14")
print("=" * 70)

# Buscar imágenes E14 en el proyecto
imagenes_e14 = [
    'E14_basico_001.png',
    'E14_basico_002.png',
    'uploads/e14/test.png'
]

for imagen in imagenes_e14:
    if os.path.exists(imagen):
        print(f"\n📷 Procesando: {imagen}")
        print("-" * 70)
        
        resultado = ocr_service.procesar_imagen_e14(imagen, 'senado')
        
        if resultado['success']:
            print(f"✅ OCR Exitoso")
            print(f"Confianza: {resultado['confianza'] * 100}%")
            
            if resultado['candidatos']:
                print(f"\n📋 Candidatos Extraídos: {len(resultado['candidatos'])}")
                for i, cand in enumerate(resultado['candidatos'], 1):
                    print(f"  {i}. {cand['nombre']}")
                    print(f"     Partido: {cand['partido']}")
                    print(f"     Votos: {cand['votos']}")
                    print()
            else:
                print("⚠️  No se encontraron candidatos")
            
            if resultado['votos_especiales']:
                print(f"📊 Votos Especiales:")
                ve = resultado['votos_especiales']
                print(f"  Votos en blanco: {ve.get('votos_blanco', 0)}")
                print(f"  Votos nulos: {ve.get('votos_nulos', 0)}")
                print(f"  Tarjetas no marcadas: {ve.get('tarjetas_no_marcadas', 0)}")
            
            if resultado['totales']:
                print(f"\n🔢 Totales:")
                t = resultado['totales']
                print(f"  Total votos candidatos: {t.get('total_votos_candidatos', 0)}")
                print(f"  Total votos: {t.get('total_votos', 0)}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
        
        print("\n" + "=" * 70)
        break
else:
    print("\n⚠️  No se encontraron imágenes E14 para probar")
    print("Imágenes buscadas:")
    for img in imagenes_e14:
        print(f"  - {img}")
