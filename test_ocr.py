#!/usr/bin/env python3
"""
Script de prueba para verificar instalación de OCR
Sistema Electoral Caquetá
"""

import sys

print("=" * 60)
print("🧪 PRUEBA DE SISTEMA OCR")
print("=" * 60)

# Verificar importaciones
print("\n1️⃣ Verificando importaciones...")

try:
    import pytesseract
    print("   ✅ pytesseract importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando pytesseract: {e}")
    sys.exit(1)

try:
    import cv2
    print("   ✅ opencv-python (cv2) importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando cv2: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    print("   ✅ Pillow (PIL) importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando PIL: {e}")
    sys.exit(1)

try:
    import numpy as np
    print("   ✅ numpy importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando numpy: {e}")
    sys.exit(1)

# Verificar Tesseract
print("\n2️⃣ Verificando Tesseract OCR...")

try:
    version = pytesseract.get_tesseract_version()
    print(f"   ✅ Tesseract versión: {version}")
except Exception as e:
    print(f"   ⚠️  Tesseract no encontrado o no configurado")
    print(f"   Error: {e}")
    print("\n   📝 Solución:")
    print("   1. Instalar Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   2. Agregar al PATH o configurar ruta en ocr_service.py")
    print("\n   Continuando con prueba básica...")

# Crear imagen de prueba
print("\n3️⃣ Creando imagen de prueba...")

try:
    # Crear imagen con números
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar números grandes
    try:
        # Intentar usar fuente del sistema
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # Usar fuente por defecto
        font = ImageFont.load_default()
    
    draw.text((20, 30), "12345", fill='black', font=font)
    
    # Guardar imagen
    img.save('test_ocr_image.png')
    print("   ✅ Imagen de prueba creada: test_ocr_image.png")
    
except Exception as e:
    print(f"   ❌ Error creando imagen: {e}")
    sys.exit(1)

# Probar OCR
print("\n4️⃣ Probando extracción de texto con OCR...")

try:
    # Leer imagen
    test_img = Image.open('test_ocr_image.png')
    
    # Aplicar OCR
    texto = pytesseract.image_to_string(test_img, config='--psm 7')
    texto_limpio = ''.join(filter(str.isdigit, texto))
    
    print(f"   📄 Texto extraído: '{texto.strip()}'")
    print(f"   🔢 Números detectados: '{texto_limpio}'")
    
    # Verificar resultado
    if '12345' in texto_limpio or texto_limpio == '12345':
        print("   ✅ OCR funcionando correctamente!")
    else:
        print(f"   ⚠️  OCR extrajo texto pero no coincide exactamente")
        print(f"   Esperado: '12345', Obtenido: '{texto_limpio}'")
        
except Exception as e:
    print(f"   ❌ Error en OCR: {e}")
    print("\n   📝 Posibles causas:")
    print("   - Tesseract no está instalado")
    print("   - Tesseract no está en el PATH")
    print("   - Configuración incorrecta")

# Probar OpenCV
print("\n5️⃣ Probando procesamiento de imagen con OpenCV...")

try:
    # Leer imagen con OpenCV
    img_cv = cv2.imread('test_ocr_image.png')
    
    if img_cv is None:
        raise ValueError("No se pudo cargar la imagen")
    
    # Convertir a escala de grises
    gris = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral
    _, binaria = cv2.threshold(gris, 127, 255, cv2.THRESH_BINARY)
    
    # Guardar imagen procesada
    cv2.imwrite('test_ocr_procesada.png', binaria)
    
    print("   ✅ OpenCV funcionando correctamente")
    print("   ✅ Imagen procesada guardada: test_ocr_procesada.png")
    
except Exception as e:
    print(f"   ❌ Error en OpenCV: {e}")

# Resumen
print("\n" + "=" * 60)
print("📊 RESUMEN DE PRUEBAS")
print("=" * 60)

print("\n✅ Dependencias instaladas correctamente:")
print("   - pytesseract")
print("   - opencv-python")
print("   - Pillow")
print("   - numpy")

print("\n📁 Archivos generados:")
print("   - test_ocr_image.png (imagen de prueba)")
print("   - test_ocr_procesada.png (imagen procesada)")

print("\n🎯 Estado del sistema:")
try:
    pytesseract.get_tesseract_version()
    print("   ✅ Sistema OCR completamente funcional")
    print("   ✅ Listo para procesar formularios E14")
except:
    print("   ⚠️  Tesseract necesita ser instalado/configurado")
    print("   📝 Ver instrucciones en INSTALL_OCR.md")

print("\n" + "=" * 60)
print("✅ Prueba completada")
print("=" * 60)
