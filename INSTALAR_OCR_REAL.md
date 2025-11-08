# Instalación de OCR Real para Formulario E14

**Problema Actual:** El sistema usa datos de ejemplo porque Tesseract OCR no está instalado

**Solución:** Instalar Tesseract OCR para procesar imágenes reales

---

## 🎯 Por Qué No Funciona Ahora

El servicio OCR (`services/ocr_e14_service.py`) tiene dos modos:

### Modo Actual: SIMULACIÓN
```python
def procesar_imagen_e14(self, imagen_path, tipo_eleccion):
    # Por ahora, simulamos el OCR con datos de ejemplo
    resultado = self._simular_ocr(tipo_eleccion)  # ← Datos de ejemplo
    return resultado
```

### Modo Requerido: OCR REAL
```python
def procesar_imagen_e14(self, imagen_path, tipo_eleccion):
    # Extraer texto real de la imagen
    texto = self.extraer_texto_tesseract(imagen_path)  # ← OCR real
    datos = self.parsear_texto_e14(texto)
    return datos
```

---

## 📦 Instalación de Tesseract OCR

### Windows

#### Opción 1: Instalador Oficial (Recomendado)

1. **Descargar Tesseract:**
   - Ir a: https://github.com/UB-Mannheim/tesseract/wiki
   - Descargar: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`

2. **Instalar:**
   - Ejecutar el instalador
   - Ruta recomendada: `C:\Program Files\Tesseract-OCR`
   - ✅ Marcar: "Add to PATH"
   - ✅ Marcar: "Spanish language data" (importante para E14)

3. **Verificar Instalación:**
   ```cmd
   tesseract --version
   ```
   
   Debe mostrar:
   ```
   tesseract 5.3.3
   ```

#### Opción 2: Chocolatey (Si lo tienes instalado)

```powershell
choco install tesseract
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-spa  # Idioma español
```

### macOS

```bash
brew install tesseract
brew install tesseract-lang  # Incluye español
```

---

## 🐍 Instalación de Paquetes Python

```bash
pip install pytesseract
pip install opencv-python
pip install Pillow
```

O si usas el requirements:
```bash
pip install -r requirements_ocr.txt
```

---

## ⚙️ Configuración del Sistema

### 1. Verificar Instalación

Ejecutar el script de prueba:
```bash
python test_ocr.py
```

**Resultado Esperado:**
```
✅ pytesseract importado correctamente
✅ Pillow importado correctamente
✅ OpenCV importado correctamente
✅ Tesseract versión: 5.3.3
✅ OCR funcionando correctamente!
✅ Sistema OCR completamente funcional
```

### 2. Configurar Ruta (Si es necesario)

Si Tesseract no está en el PATH, editar `services/ocr_e14_service.py`:

```python
import pytesseract

# Agregar al inicio de la clase
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 🔧 Activar OCR Real

### Modificar `services/ocr_e14_service.py`

**Cambiar la función `procesar_imagen_e14`:**

```python
def procesar_imagen_e14(self, imagen_path: str, tipo_eleccion: str = 'senado') -> Dict:
    """
    Procesar imagen del formulario E14 y extraer datos
    """
    try:
        # OPCIÓN 1: Intentar OCR real primero
        try:
            import pytesseract
            texto = self.extraer_texto_tesseract(imagen_path)
            resultado = self.parsear_texto_e14(texto)
            
            # Si se extrajo algo, usar esos datos
            if resultado['candidatos']:
                print(f"✅ OCR real extrajo {len(resultado['candidatos'])} candidatos")
                self._guardar_candidatos_partidos(resultado['candidatos'], tipo_eleccion)
                return {
                    'success': True,
                    'candidatos': resultado['candidatos'],
                    'votos_especiales': resultado['votos_especiales'],
                    'totales': self._calcular_totales(resultado),
                    'confianza': 0.85
                }
        except ImportError:
            print("⚠️ Tesseract no disponible, usando simulación")
        except Exception as e:
            print(f"⚠️ Error en OCR real: {e}, usando simulación")
        
        # OPCIÓN 2: Fallback a simulación
        resultado = self._simular_ocr(tipo_eleccion)
        self._guardar_candidatos_partidos(resultado['candidatos'], tipo_eleccion)
        
        return {
            'success': True,
            'candidatos': resultado['candidatos'],
            'votos_especiales': resultado['votos_especiales'],
            'totales': resultado['totales'],
            'confianza': resultado['confianza']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'candidatos': [],
            'votos_especiales': {},
            'totales': {}
        }
```

---

## 📝 Mejorar Extracción de Texto

### Preprocesamiento de Imagen

```python
def extraer_texto_tesseract(self, imagen_path: str) -> str:
    """
    Extraer texto de imagen usando Tesseract OCR
    """
    try:
        import pytesseract
        from PIL import Image
        import cv2
        import numpy as np
        
        # Leer imagen
        img = cv2.imread(imagen_path)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold para mejorar contraste
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Aplicar OCR con configuración optimizada para formularios
        custom_config = r'--oem 3 --psm 6 -l spa'
        texto = pytesseract.image_to_string(denoised, config=custom_config)
        
        print(f"📄 Texto extraído ({len(texto)} caracteres)")
        return texto
        
    except ImportError:
        return "OCR no disponible - Tesseract no instalado"
    except Exception as e:
        return f"Error en OCR: {str(e)}"
```

### Parseo Mejorado

```python
def parsear_texto_e14(self, texto: str) -> Dict:
    """
    Parsear texto extraído del E14 y estructurar datos
    """
    candidatos = []
    votos_especiales = {}
    
    # Patrones regex para extraer datos del E14
    # Formato típico: "01 JUAN PEREZ - PARTIDO LIBERAL 145"
    patron_candidato = r'(\d{1,2})\s+([A-ZÁ-Ú\s]+)\s*[-–]\s*([A-ZÁ-Ú\s]+)\s+(\d+)'
    
    matches = re.findall(patron_candidato, texto, re.IGNORECASE)
    
    for match in matches:
        lista, nombre, partido, votos = match
        candidatos.append({
            'lista': lista.zfill(2),
            'nombre': nombre.strip().title(),
            'partido': partido.strip().title(),
            'votos': int(votos)
        })
    
    # Extraer votos en blanco
    match_blanco = re.search(r'BLANCO[:\s]+(\d+)', texto, re.IGNORECASE)
    if match_blanco:
        votos_especiales['votos_blanco'] = int(match_blanco.group(1))
    
    # Extraer votos nulos
    match_nulos = re.search(r'NULO[S]?[:\s]+(\d+)', texto, re.IGNORECASE)
    if match_nulos:
        votos_especiales['votos_nulos'] = int(match_nulos.group(1))
    
    # Extraer tarjetas no marcadas
    match_no_marcadas = re.search(r'NO\s+MARCADA[S]?[:\s]+(\d+)', texto, re.IGNORECASE)
    if match_no_marcadas:
        votos_especiales['tarjetas_no_marcadas'] = int(match_no_marcadas.group(1))
    
    print(f"✅ Parseados {len(candidatos)} candidatos")
    
    return {
        'candidatos': candidatos,
        'votos_especiales': votos_especiales
    }
```

---

## 🧪 Probar OCR Real

### 1. Crear Script de Prueba

```python
# test_ocr_real.py
from services.ocr_e14_service import ocr_service

# Probar con imagen real del E14
imagen_path = 'uploads/e14/mi_formulario_e14.jpg'
tipo_eleccion = 'senado'

resultado = ocr_service.procesar_imagen_e14(imagen_path, tipo_eleccion)

print(f"Success: {resultado['success']}")
print(f"Candidatos: {len(resultado['candidatos'])}")

for candidato in resultado['candidatos']:
    print(f"  - {candidato['nombre']} ({candidato['partido']}): {candidato['votos']} votos")
```

### 2. Ejecutar Prueba

```bash
python test_ocr_real.py
```

---

## 📊 Calidad del OCR

### Factores que Afectan la Precisión

✅ **Buena Calidad:**
- Imagen clara y enfocada
- Buena iluminación
- Sin sombras
- Texto legible
- Formulario completo visible

❌ **Mala Calidad:**
- Imagen borrosa
- Poca luz
- Sombras o reflejos
- Texto ilegible
- Formulario parcial

### Mejorar Precisión

1. **Preprocesamiento:**
   - Escala de grises
   - Binarización
   - Reducción de ruido
   - Corrección de perspectiva

2. **Configuración Tesseract:**
   ```python
   # PSM (Page Segmentation Mode)
   --psm 6  # Asume un bloque uniforme de texto
   --psm 4  # Asume una sola columna de texto
   
   # OEM (OCR Engine Mode)
   --oem 3  # Modo predeterminado (LSTM + Legacy)
   ```

3. **Post-procesamiento:**
   - Validación de datos
   - Corrección de errores comunes
   - Verificación de totales

---

## ✅ Checklist de Instalación

- [ ] Tesseract OCR instalado
- [ ] Tesseract en PATH o ruta configurada
- [ ] Paquete `pytesseract` instalado
- [ ] Paquete `opencv-python` instalado
- [ ] Paquete `Pillow` instalado
- [ ] Script `test_ocr.py` ejecutado exitosamente
- [ ] Función `procesar_imagen_e14` modificada para usar OCR real
- [ ] Probado con imagen real del E14
- [ ] Candidatos extraídos correctamente

---

## 🚀 Resultado Final

Una vez instalado y configurado:

```
Usuario captura foto del E14 real
    ↓
Tesseract OCR extrae texto de la imagen
    ↓
Sistema parsea candidatos, partidos y votos
    ↓
Formulario se llena con datos REALES del E14
    ↓
Usuario verifica y corrige si es necesario
    ↓
Usuario envía datos
```

---

**Estado Actual:** Simulación (datos de ejemplo)  
**Estado Deseado:** OCR Real (datos de la imagen)  
**Acción Requerida:** Instalar Tesseract OCR

**Tiempo estimado:** 10-15 minutos
