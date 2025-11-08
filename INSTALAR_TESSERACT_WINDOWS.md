# Instalación de Tesseract OCR en Windows

**Problema Actual:** El sistema usa datos de ejemplo porque Tesseract no está instalado

---

## 📥 Paso 1: Descargar Tesseract

1. Ir a: https://github.com/UB-Mannheim/tesseract/wiki
2. Descargar el instalador para Windows (64-bit):
   - **tesseract-ocr-w64-setup-5.3.3.20231005.exe** (o versión más reciente)

---

## 🔧 Paso 2: Instalar Tesseract

1. Ejecutar el instalador descargado
2. **IMPORTANTE:** Durante la instalación:
   - Marcar la opción **"Spanish"** en idiomas adicionales
   - Ruta de instalación recomendada: `C:\Program Files\Tesseract-OCR`
3. Completar la instalación

---

## 🌐 Paso 3: Agregar al PATH

### Opción A: Automático (Recomendado)
El instalador debería agregar Tesseract al PATH automáticamente.

### Opción B: Manual
Si no funciona automáticamente:

1. Abrir **Panel de Control** → **Sistema** → **Configuración avanzada del sistema**
2. Click en **Variables de entorno**
3. En **Variables del sistema**, buscar **Path**
4. Click en **Editar**
5. Click en **Nuevo**
6. Agregar: `C:\Program Files\Tesseract-OCR`
7. Click en **Aceptar** en todas las ventanas

---

## 📦 Paso 4: Instalar Paquetes Python

Abrir PowerShell o CMD en la carpeta del proyecto y ejecutar:

```bash
pip install pytesseract
pip install opencv-python
pip install Pillow
```

---

## ✅ Paso 5: Verificar Instalación

Ejecutar el script de prueba:

```bash
python test_ocr.py
```

**Resultado esperado:**
```
✅ pytesseract importado correctamente
✅ Pillow importado correctamente
✅ OpenCV importado correctamente
✅ Tesseract versión: 5.3.3
✅ OCR funcionando correctamente!
✅ Sistema OCR completamente funcional
✅ Listo para procesar formularios E14
```

---

## 🔄 Paso 6: Reiniciar Aplicación

```bash
# Detener la aplicación actual (Ctrl+C)
# Iniciar nuevamente
python app.py
```

---

## 🧪 Paso 7: Probar con Imagen Real

1. Ir a http://127.0.0.1:5000/dashboard/testigo_mesa
2. Capturar foto de un E14 real
3. El sistema ahora procesará la imagen real con OCR
4. Los candidatos y votos se extraerán de la imagen

---

## ⚠️ Si Tesseract No Se Detecta

Si después de instalar sigue sin funcionar, configurar manualmente la ruta en el código:

### Editar `services/ocr_e14_service.py`

Agregar al inicio de la clase, después de `def __init__(self)`:

```python
def __init__(self):
    self.db_path = 'caqueta_electoral.db'
    
    # Configurar ruta de Tesseract manualmente
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    except:
        pass
```

---

## 🎯 Alternativa Temporal: Mejorar la Simulación

Si no puedes instalar Tesseract ahora, puedo mejorar la simulación para que al menos permita editar los datos manualmente de forma más fácil.

¿Quieres que:
1. **Instales Tesseract** (recomendado para OCR real)
2. **Mejore la simulación** para que sea más fácil editar manualmente

---

## 📝 Notas Importantes

- **Tesseract es GRATIS** y open source
- La instalación toma **5-10 minutos**
- Una vez instalado, el OCR funcionará **automáticamente**
- El sistema detectará Tesseract y dejará de usar simulación
- La precisión del OCR depende de la **calidad de la foto**

---

## 🆘 Problemas Comunes

### "Tesseract not found"
- Verificar que está en el PATH
- Reiniciar PowerShell/CMD
- Configurar ruta manualmente en el código

### "No module named 'pytesseract'"
```bash
pip install pytesseract
```

### OCR extrae texto incorrecto
- Tomar foto más clara
- Mejor iluminación
- Formulario completo en la imagen
- Sin sombras ni reflejos

---

**Siguiente paso:** ¿Quieres instalar Tesseract o prefieres que mejore la interfaz para edición manual?
