# Instrucciones para Probar la Corrección del OCR

**Fecha:** 7 de noviembre de 2025

---

## ✅ Corrección Implementada

Se ha corregido el error que impedía que los votos de los candidatos se cargaran correctamente desde el OCR.

---

## 🚀 Pasos para Probar

### 1. Reiniciar el Servidor

Abrir una terminal y ejecutar:

```bash
python app.py
```

Esperar a ver:
```
 * Running on http://127.0.0.1:5000
```

---

### 2. Abrir el Navegador

Ir a: **http://127.0.0.1:5000/login**

---

### 3. Iniciar Sesión

**Credenciales de prueba:**
- **Cédula:** `1000000001`
- **Contraseña:** `Demo2024!`

Click en "Iniciar Sesión"

---

### 4. Verificar Carga Automática de Datos

Deberías ver inmediatamente:
- ✅ Municipio: Curillo
- ✅ Zona: Zona 00
- ✅ Puesto: PUESTO CABECERA MUNICIPAL
- ✅ Mesa: Mesa 001 (seleccionada)

---

### 5. Capturar Foto del E14

1. **Click** en el área de captura (donde dice "Click para tomar foto")
2. **Seleccionar** una imagen del formulario E14
3. **Esperar** a que aparezca el mensaje "Procesando OCR automáticamente..."

---

### 6. Verificar Carga de Datos del OCR

Después de procesar el OCR, deberías ver:

#### ✅ Candidatos Cargados
```
Candidato 1: Juan Pérez García
Partido: Partido Liberal
Votos: 145  ← ESTO DEBE APARECER AUTOMÁTICAMENTE

Candidato 2: María López Ruiz
Partido: Partido Conservador
Votos: 132  ← ESTO DEBE APARECER AUTOMÁTICAMENTE

... y así sucesivamente
```

#### ✅ Votos Especiales Cargados
```
Votos en Blanco: 15
Votos Nulos: 8
Tarjetas No Marcadas: 5
```

#### ✅ Totales Calculados
```
Total Votos: 451 (o el total correspondiente)
```

---

## 🎯 Qué Verificar

### ✅ CORRECTO (Después de la corrección)

1. Los candidatos aparecen con sus nombres
2. Los partidos están asignados
3. **Los votos aparecen en los campos** ← ESTO ES LO IMPORTANTE
4. Los votos especiales están cargados
5. El total se calcula automáticamente
6. La validación funciona

### ❌ INCORRECTO (Antes de la corrección)

1. Los candidatos aparecían con 0 votos
2. Había que ingresar los votos manualmente
3. Los totales no se calculaban bien

---

## 🔍 Debugging

Si algo no funciona, abrir la **Consola del Navegador** (F12) y buscar:

```javascript
Llenando formulario con datos del OCR: {...}
Agregando 4 candidatos del OCR
Voto asignado a Juan Pérez García: 145
Voto asignado a María López Ruiz: 132
...
```

Estos mensajes confirman que la carga está funcionando correctamente.

---

## 📊 Ejemplo de Resultado Esperado

### Antes de Capturar Foto:
```
┌─────────────────────────────────────┐
│ Candidatos                          │
├─────────────────────────────────────┤
│ Capture la foto del formulario E14 │
│ para extraer automáticamente los    │
│ candidatos con OCR                  │
└─────────────────────────────────────┘
```

### Después de Capturar Foto (CON LA CORRECCIÓN):
```
┌─────────────────────────────────────────────────────┐
│ Candidato 1                                         │
│ Nombre: Juan Pérez García                           │
│ Partido: Partido Liberal                            │
│ Votos: [145] ← CARGADO AUTOMÁTICAMENTE             │
├─────────────────────────────────────────────────────┤
│ Candidato 2                                         │
│ Nombre: María López Ruiz                            │
│ Partido: Partido Conservador                        │
│ Votos: [132] ← CARGADO AUTOMÁTICAMENTE             │
├─────────────────────────────────────────────────────┤
│ ...                                                 │
└─────────────────────────────────────────────────────┘

Total Votos: 451 ← CALCULADO AUTOMÁTICAMENTE
```

---

## 🎉 Resultado Esperado

Después de capturar la foto:
1. ✅ Los candidatos se cargan automáticamente
2. ✅ Los votos aparecen en los campos
3. ✅ Los totales se calculan correctamente
4. ✅ El usuario solo necesita verificar y ajustar si es necesario
5. ✅ Puede hacer click en "Validar Datos" y luego "Enviar E14"

---

## 📝 Notas

- **Modo Simulación**: Si no tienes Tesseract instalado, el sistema usará datos de ejemplo
- **Edición Manual**: Puedes editar cualquier campo después de la carga automática
- **Validación**: El botón "Validar Datos" verifica que todo esté correcto antes de enviar

---

## 🆘 Soporte

Si encuentras algún problema:

1. Verificar que el servidor esté corriendo
2. Revisar la consola del navegador (F12)
3. Ejecutar el test: `python test_ocr_carga_datos.py`
4. Revisar la documentación completa en `CORRECCION_CARGA_OCR.md`

---

**¡Listo para probar!** 🚀
