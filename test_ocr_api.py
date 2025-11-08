#!/usr/bin/env python3
"""
Test de la API OCR
"""

import requests
import io
from PIL import Image

# Crear una imagen de prueba
img = Image.new('RGB', (800, 600), color='white')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

print("=" * 70)
print("TEST API OCR")
print("=" * 70)

try:
    # Preparar datos
    files = {'imagen': ('test.png', img_bytes, 'image/png')}
    data = {'tipo_eleccion': 'senado'}
    
    # Llamar a la API
    response = requests.post(
        'http://127.0.0.1:5000/api/testigo/procesar-ocr',
        files=files,
        data=data
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse:")
    
    if response.ok:
        resultado = response.json()
        print(f"Success: {resultado.get('success')}")
        print(f"Confianza: {resultado.get('confianza', 0) * 100}%")
        
        if resultado.get('candidatos'):
            print(f"\nCandidatos extraídos: {len(resultado['candidatos'])}")
            for i, candidato in enumerate(resultado['candidatos'], 1):
                print(f"  {i}. {candidato['nombre']} ({candidato['partido']}) - {candidato['votos']} votos")
        
        if resultado.get('votos_especiales'):
            print(f"\nVotos Especiales:")
            ve = resultado['votos_especiales']
            print(f"  Votos en blanco: {ve.get('votos_blanco', 0)}")
            print(f"  Votos nulos: {ve.get('votos_nulos', 0)}")
            print(f"  Tarjetas no marcadas: {ve.get('tarjetas_no_marcadas', 0)}")
        
        if resultado.get('totales'):
            print(f"\nTotales:")
            t = resultado['totales']
            print(f"  Total votos candidatos: {t.get('total_votos_candidatos', 0)}")
            print(f"  Total votos: {t.get('total_votos', 0)}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
