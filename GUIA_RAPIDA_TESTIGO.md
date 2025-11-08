# 📱 Guía Rápida - Dashboard Testigo Electoral

## 🎯 Acceso al Sistema

**URL:** http://127.0.0.1:5000

**Credenciales de Prueba:**
- **Cédula:** 1000000001 (o cualquier testigo demo)
- **Contraseña:** Demo2024!

---

## 🔄 Nuevo Flujo de Trabajo

### ✅ PASO 1: Seleccionar Mesa y Tipo de Elección

```
┌─────────────────────────────────────┐
│ Mesa: [Seleccionar mesa ▼]         │  ← NUEVO: Puede cambiar de mesa
│ Tipo: [Senado ▼]                   │  ← NUEVO: Puede cambiar tipo
└─────────────────────────────────────┘
```

**Opciones de Tipo de Elección:**
- Senado
- Cámara de Representantes
- Concejo Municipal
- Alcaldía
- Gobernación
- Asamblea Departamental

---

### ✅ PASO 2: Capturar Foto del Formulario E14

```
┌─────────────────────────────────────┐
│     📷                              │
│  Click para tomar foto              │
│  o subir imagen                     │
│                                     │
│  El OCR se activará                 │
│  automáticamente                    │
└─────────────────────────────────────┘
```

**Recomendaciones:**
- ✓ Buena iluminación
- ✓ Foto nítida y enfocada
- ✓ Formulario completo visible
- ✓ Sin sombras ni reflejos

---

### ✅ PASO 3: Verificar Datos (OCR Automático)

El sistema llenará automáticamente:
- Votos por candidato
- Votos en blanco
- Votos nulos
- Tarjetas no marcadas
- Información del acta

**⚠️ IMPORTANTE:** Siempre verifique y corrija los datos del OCR

---

### ✅ PASO 4: Guardar Temporal (Opcional)

```
┌─────────────────────────────────────┐
│  [💾 Guardar Temporal]              │  ← NUEVO
└─────────────────────────────────────┘
```

**¿Cuándo usar?**
- Cuando va a reportar varias mesas
- Para guardar la foto sin enviar
- Para continuar después

**Ventajas:**
- Los datos se guardan en su navegador
- Puede cambiar de mesa y volver después
- No pierde el trabajo realizado

---

### ✅ PASO 5: Validar Datos (OBLIGATORIO)

```
┌─────────────────────────────────────┐
│  [⚠️ Validar Datos]                 │  ← NUEVO: Obligatorio
└─────────────────────────────────────┘
```

**El sistema verificará:**

#### ❌ Errores (Rojo) - Deben corregirse
- Foto no capturada
- Mesa no seleccionada
- Sin votos registrados
- Total excede votantes habilitados
- Candidatos incompletos

#### ⚠️ Advertencias (Amarillo) - Recomendaciones
- Total menor que votantes habilitados
- Número de acta faltante
- Jurado presidente faltante

#### ✅ Éxitos (Verde) - Todo correcto
- Foto capturada
- Mesa seleccionada
- Totales coinciden
- Candidatos completos

---

### ✅ PASO 6: Revisar Alertas de Validación

```
┌─────────────────────────────────────┐
│ ❌ Errores que deben corregirse:    │
│  • Candidato 2: falta partido       │
│  • Total excede votantes            │
│                                     │
│ ⚠️ Advertencias:                    │
│  • Número de acta no especificado   │
│                                     │
│ ✅ Validación exitosa:              │
│  • Foto capturada                   │
│  • 3 candidatos registrados         │
│  • Totales coinciden                │
└─────────────────────────────────────┘
```

**Campos se colorean:**
- 🟢 Verde = Correcto
- 🔴 Rojo = Error
- 🟡 Amarillo = Advertencia

---

### ✅ PASO 7: Enviar Formulario

```
┌─────────────────────────────────────┐
│  [✅ Enviar E14]                    │  ← Solo habilitado después de validar
└─────────────────────────────────────┘
```

**Confirmación:**
```
¿Está seguro de enviar el formulario E14?

Mesa: Mesa 777
Tipo: Senado

Esta acción informará al resto del sistema.

[Cancelar]  [Aceptar]
```

---

## 🔄 Reportar Múltiples Mesas

### Método 1: Guardado Temporal

1. **Mesa 1:**
   - Seleccionar Mesa 1
   - Capturar foto
   - Llenar datos
   - **Guardar Temporal** ← No enviar todavía

2. **Mesa 2:**
   - Cambiar a Mesa 2
   - Capturar foto
   - Llenar datos
   - **Guardar Temporal**

3. **Mesa 3:**
   - Cambiar a Mesa 3
   - Capturar foto
   - Llenar datos
   - **Guardar Temporal**

4. **Enviar Todo:**
   - Volver a Mesa 1
   - Validar y Enviar
   - Volver a Mesa 2
   - Validar y Enviar
   - Volver a Mesa 3
   - Validar y Enviar

### Método 2: Envío Inmediato

1. **Mesa 1:**
   - Seleccionar Mesa 1
   - Capturar foto
   - Validar
   - **Enviar**

2. **Continuar:**
   - Sistema pregunta: "¿Desea reportar otra mesa?"
   - Clic en "Sí"
   - Seleccionar Mesa 2
   - Repetir proceso

---

## 🎨 Indicadores Visuales

### Estados de los Campos

```
┌─────────────────────────────────────┐
│ Candidato: [Juan Pérez          ]  │  🟢 Verde = Válido
│ Partido:   [Partido Liberal     ]  │  🟢 Verde = Válido
│ Votos:     [45                  ]  │  🟢 Verde = Válido
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Candidato: [                     ]  │  🔴 Rojo = Error
│ Partido:   [                     ]  │  🔴 Rojo = Error
│ Votos:     [0                    ]  │  🟡 Amarillo = Advertencia
└─────────────────────────────────────┘
```

### Estado de Validación de Totales

```
┌─────────────────────────────────────┐
│ Total Votos: 350                    │
│ Validación: ✅ Correcto             │  🟢 Verde = Coincide
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Total Votos: 380                    │
│ Validación: ⚠️ Excede               │  🔴 Rojo = Excede
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Total Votos: 320                    │
│ Validación: ⏰ Incompleto           │  🟡 Amarillo = Falta
└─────────────────────────────────────┘
```

### Badge de Guardado

```
┌─────────────────────────────────────┐
│  [Foto del E14]        💾 Guardado  │  ← Aparece al guardar temporal
│                                     │
└─────────────────────────────────────┘
```

---

## ⚡ Atajos y Tips

### Tips de Eficiencia

1. **Use Guardado Temporal** si tiene muchas mesas
2. **Valide siempre** antes de enviar
3. **Verifique el OCR** - puede tener errores
4. **Tome fotos claras** - mejor OCR
5. **Complete todos los campos** - menos advertencias

### Datos que se Guardan Temporalmente

✅ Foto del formulario
✅ Votos por candidato
✅ Votos especiales (blanco, nulos)
✅ Información del acta
✅ Observaciones

### Datos que NO se Guardan

❌ Selección de mesa (debe seleccionar cada vez)
❌ Tipo de elección (debe seleccionar cada vez)

---

## 🆘 Solución de Problemas

### "No puedo enviar el formulario"
✓ ¿Capturó la foto?
✓ ¿Seleccionó la mesa?
✓ ¿Validó los datos?
✓ ¿Hay errores en rojo?

### "Los totales no coinciden"
✓ Verifique votos por candidato
✓ Verifique votos en blanco
✓ Verifique votos nulos
✓ Verifique tarjetas no marcadas

### "Perdí mis datos"
✓ ¿Usó Guardar Temporal?
✓ ¿Está en la misma mesa?
✓ ¿Está en el mismo tipo de elección?
✓ ¿Usó el mismo navegador?

### "El OCR no funciona bien"
✓ Tome foto más clara
✓ Mejor iluminación
✓ Corrija manualmente los datos
✓ Use Validar Datos para verificar

---

## 📊 Estadísticas del Dashboard

```
┌─────────────────────────────────────┐
│ Votantes Habilitados: 350           │
│ Votos Registrados: 0                │
│ Participación: 0%                   │
│ Capturas E14: 0                     │
└─────────────────────────────────────┘
```

Se actualizan automáticamente al:
- Cambiar de mesa
- Registrar votos
- Enviar formularios

---

## ✅ Checklist Antes de Enviar

- [ ] Foto del E14 capturada y clara
- [ ] Mesa correcta seleccionada
- [ ] Tipo de elección correcto
- [ ] Todos los candidatos con nombre y partido
- [ ] Votos registrados para cada candidato
- [ ] Votos especiales completados
- [ ] Totales coinciden con votantes habilitados
- [ ] Número de acta registrado
- [ ] Jurado presidente registrado
- [ ] Validación ejecutada y aprobada (verde)
- [ ] Sin errores en rojo

---

**¿Necesita ayuda?**  
Contacte al coordinador de puesto o coordinador municipal

**Versión:** 2.0  
**Última actualización:** 7 de noviembre de 2025
