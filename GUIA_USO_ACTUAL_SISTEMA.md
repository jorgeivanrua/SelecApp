# Guía de Uso Actual del Sistema

**Estado Actual:** MODO SIMULACIÓN (Tesseract OCR no instalado)

---

## ⚠️ IMPORTANTE: Modo Simulación Activo

El sistema actualmente está en **MODO SIMULACIÓN** porque Tesseract OCR no está instalado.

### ¿Qué significa esto?

Cuando capturas una foto del formulario E14:
- ❌ **NO** extrae datos reales de la imagen
- ✅ **SÍ** carga datos de ejemplo para que pruebes el sistema
- ✅ **SÍ** puedes editar manualmente todos los campos
- ✅ **SÍ** puedes enviar los datos al sistema

---

## 📝 Cómo Usar el Sistema Ahora

### Opción 1: Edición Manual (Actual)

```
1. Capturar foto del E14 real
   ↓
2. Sistema carga datos de ejemplo
   ↓
3. EDITAR MANUALMENTE cada campo:
   - Nombre del candidato
   - Partido
   - Votos
   ↓
4. Editar votos especiales:
   - Votos en blanco
   - Votos nulos
   - Tarjetas no marcadas
   ↓
5. Validar datos
   ↓
6. Enviar formulario
```

### Pasos Detallados

#### 1. Capturar Foto
```
- Click en "Click para tomar foto"
- Seleccionar imagen del E14
- Aparece mensaje: "MODO SIMULACIÓN: Datos de ejemplo cargados"
```

#### 2. Editar Candidatos
```
Para cada candidato:
┌─────────────────────────────────────────────┐
│ Candidato: [Editar nombre real]            │
│ Partido:   [Editar partido real]           │
│ Votos:     [Editar votos reales]           │
└─────────────────────────────────────────────┘
```

**Ejemplo:**
- Cambiar "Juan Pérez García" → "Nombre real del E14"
- Cambiar "Partido Liberal" → "Partido real del E14"
- Cambiar "145" → "Votos reales del E14"

#### 3. Agregar/Eliminar Candidatos
```
- Botón [+ Agregar Candidato]: Agregar más candidatos
- Botón [🗑️]: Eliminar candidato específico
- Botón [Limpiar Todo]: Borrar todos y empezar de cero
```

#### 4. Editar Votos Especiales
```
Votos en Blanco:        [Editar con dato real]
Votos Nulos:            [Editar con dato real]
Tarjetas No Marcadas:   [Editar con dato real]
```

#### 5. Validar y Enviar
```
1. Click en [Validar Datos]
2. Revisar alertas (rojo = error, amarillo = advertencia)
3. Corregir errores
4. Click en [Enviar E14]
```

---

## 🚀 Opción 2: Instalar OCR Real (Recomendado)

Para que el sistema extraiga automáticamente los datos de las imágenes reales:

### Instalación Rápida

```bash
# 1. Descargar Tesseract
https://github.com/UB-Mannheim/tesseract/wiki

# 2. Instalar (marcar idioma Spanish)

# 3. Instalar paquetes Python
pip install pytesseract opencv-python Pillow

# 4. Verificar
python test_ocr.py

# 5. Reiniciar aplicación
python app.py
```

**Tiempo estimado:** 10 minutos

**Después de instalar:**
- ✅ OCR real activado automáticamente
- ✅ Extrae datos reales de las imágenes
- ✅ Candidatos, partidos y votos automáticos
- ✅ Solo verificar y corregir si es necesario

---

## 📊 Comparación

### Modo Actual (Simulación)
```
Capturar foto → Datos de ejemplo → Editar TODO manualmente → Enviar
```
**Tiempo:** ~5 minutos por formulario

### Con Tesseract Instalado
```
Capturar foto → OCR extrae datos → Verificar → Enviar
```
**Tiempo:** ~30 segundos por formulario

---

## 🎯 Recomendación

### Para Pruebas y Desarrollo
✅ **Modo actual está bien** - Puedes probar todas las funcionalidades

### Para Uso en Producción
⚠️ **Instalar Tesseract** - Ahorra 90% del tiempo de captura

---

## 📝 Instrucciones de Uso Manual

### Flujo Completo Paso a Paso

1. **Login**
   - Cédula: 1000000001
   - Password: Demo2024!

2. **Seleccionar Mesa y Tipo**
   - Mesa: Seleccionar de la lista
   - Tipo: Seleccionar tipo de elección

3. **Capturar Foto**
   - Click en área de captura
   - Seleccionar imagen del E14
   - Aparece mensaje de simulación

4. **Editar Candidatos** (IMPORTANTE)
   - Ver la imagen capturada (usar zoom si es necesario)
   - Para cada candidato en el E14:
     * Editar nombre del candidato
     * Editar partido
     * Editar número de votos

5. **Agregar/Eliminar Candidatos**
   - Si faltan candidatos: Click en [+ Agregar Candidato]
   - Si sobran: Click en [🗑️] del candidato

6. **Editar Votos Especiales**
   - Votos en blanco: Ingresar dato del E14
   - Votos nulos: Ingresar dato del E14
   - Tarjetas no marcadas: Ingresar dato del E14

7. **Verificar Totales**
   - El sistema suma automáticamente
   - Debe coincidir con votantes habilitados
   - Verde = Correcto, Rojo = Error

8. **Validar**
   - Click en [Validar Datos]
   - Revisar alertas
   - Corregir errores en rojo

9. **Enviar**
   - Click en [Enviar E14]
   - Confirmar envío
   - Datos se guardan en el sistema

---

## 💡 Tips para Edición Manual

1. **Usa el Zoom** en la imagen para ver mejor los datos
2. **Verifica los totales** antes de validar
3. **Guarda temporal** si vas a reportar varias mesas
4. **Usa Tab** para moverte rápido entre campos
5. **Copia y pega** nombres largos para evitar errores

---

## 🔗 Enlaces Útiles

- **Dashboard:** http://127.0.0.1:5000/dashboard/testigo_mesa
- **Credenciales:** Ver USUARIOS_DEMO.txt
- **Instalar Tesseract:** Ver INSTALAR_TESSERACT_WINDOWS.md
- **Documentación:** Ver IMPLEMENTACION_OCR_E14.md

---

**Estado:** ✅ Sistema funcionando en modo simulación  
**Próximo paso:** Instalar Tesseract para OCR real
