# 📦 Instalación del Sistema OCR

## 🎯 Requisitos Previos

### 1. Instalar Tesseract OCR

#### Windows:
1. Descargar instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar instalador (recomendado: `tesseract-ocr-w64-setup-5.3.3.exe`)
3. Instalar en: `C:\Program Files\Tesseract-OCR\`
4. Agregar al PATH del sistema

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

#### macOS:
```bash
brew install tesseract
```

### 2. Verificar Instalación de Tesseract
```bash
tesseract --version
```

Debería mostrar algo como:
```
tesseract 5.3.3
```

---

## 📦 Instalar Dependencias Python

### Opción 1: Instalar todas las dependencias
```bash
pip install -r requirements_ocr.txt
```

### Opción 2: Instalar individualmente
```bash
pip install pytesseract==0.3.10
pip install opencv-python==4.8.1.78
pip install Pillow==10.1.0
pip install numpy==1.24.3
pip install pdf2image==1.16.3
pip install scikit-image==0.22.0
```

---

## ⚙️ Configuración

### 1. Configurar ruta de Tesseract (Windows)

Editar `modules/testigo/services/ocr_service.py`:

```python
import pytesseract

# Descomentar y ajustar la ruta si es necesario
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 2. Crear directorios necesarios

```bash
mkdir -p uploads/e14
mkdir -p uploads/e14/procesadas
mkdir -p uploads/e14/originales
```

### 3. Configurar permisos (Linux/macOS)

```bash
chmod 755 uploads/e14
chmod 755 uploads/e14/procesadas
chmod 755 uploads/e14/originales
```

---

## 🧪 Probar Instalación

### Script de prueba:

```python
# test_ocr.py
import pytesseract
from PIL import Image
import cv2

print("Probando OCR...")

# Crear imagen de prueba
img = Image.new('RGB', (200, 50), color='white')
from PIL import ImageDraw, ImageFont
draw = ImageDraw.Draw(img)
draw.text((10, 10), "12345", fill='black')
img.save('test_ocr.png')

# Probar OCR
texto = pytesseract.image_to_string(Image.open('test_ocr.png'))
print(f"Texto extraído: {texto}")

if '12345' in texto:
    print("✅ OCR funcionando correctamente")
else:
    print("❌ OCR no está funcionando correctamente")
```

Ejecutar:
```bash
python test_ocr.py
```

---

## 🚀 Iniciar Sistema con OCR

```bash
python start_production.py
```

El sistema ahora incluye:
- ✅ Endpoint `/api/testigo/subir-e14-ocr`
- ✅ Procesamiento automático de imágenes
- ✅ Extracción de datos con OCR
- ✅ Validación de resultados

---

## 🔧 Solución de Problemas

### Error: "Tesseract not found"
**Solución:** Agregar Tesseract al PATH o configurar ruta manualmente

### Error: "Failed to load image"
**Solución:** Verificar formato de imagen (JPG, PNG) y permisos

### Error: "Low confidence results"
**Solución:** 
- Mejorar calidad de imagen
- Aumentar resolución
- Mejor iluminación
- Imagen más nítida

### Error: "Module not found: cv2"
**Solución:** 
```bash
pip install opencv-python
```

---

## 📊 Optimización del OCR

### Mejorar Precisión:
1. **Resolución mínima:** 1200x1600px
2. **Iluminación:** Uniforme, sin sombras
3. **Enfoque:** Nítido, sin desenfoque
4. **Contraste:** Alto contraste entre texto y fondo
5. **Rotación:** Imagen derecha, sin inclinación

### Configuración Avanzada de Tesseract:
```python
# Para números solamente
config = '--psm 7 -c tessedit_char_whitelist=0123456789'

# Para mejor precisión
config = '--psm 6 --oem 3'

# Para documentos con múltiples columnas
config = '--psm 3'
```

---

## 📝 Notas Importantes

1. **Rendimiento:** El OCR puede tardar 2-5 segundos por imagen
2. **Memoria:** Imágenes grandes requieren más RAM
3. **Precisión:** Depende de la calidad de la imagen
4. **Idioma:** Tesseract soporta español por defecto
5. **Formatos:** JPG, PNG, TIFF, PDF (con pdf2image)

---

## ✅ Checklist de Instalación

- [ ] Tesseract OCR instalado
- [ ] Tesseract en PATH o ruta configurada
- [ ] Dependencias Python instaladas
- [ ] Directorios de uploads creados
- [ ] Permisos configurados
- [ ] Test de OCR exitoso
- [ ] Sistema iniciado correctamente

---

## 📞 Soporte

Si encuentras problemas:
1. Verificar logs en `electoral_system.log`
2. Revisar versión de Tesseract
3. Verificar permisos de archivos
4. Consultar documentación de Tesseract: https://tesseract-ocr.github.io/
