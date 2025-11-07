# 📋 Requerimientos Consolidados - Testigo Electoral

## 🎯 Clarificación del Rol del Testigo

### ✅ Lo que el Testigo SÍ Hace:
1. **Fotografía** el formulario E14 físico (ya llenado en la mesa)
2. **Digita** los datos del formulario en el sistema
3. **Envía** la captura (foto + datos) al servidor
4. **Registra** observaciones del proceso electoral
5. **Reporta** incidencias durante la votación

### ❌ Lo que el Testigo NO Hace:
1. **NO crea** formularios E14 (el E14 es físico, llenado por jurados)
2. **NO crea** formularios E24 (consolidación de múltiples mesas)
3. **NO genera** PDFs oficiales
4. **NO consolida** datos de múltiples mesas
5. **NO valida** capturas de otros testigos

---

## 📸 Flujo Principal: Captura E14

### Paso 1: Fotografiar Formulario Físico

**Requerimiento 1.1:** El testigo debe poder capturar foto del E14 físico

**Criterios de Aceptación:**
- Sistema permite tomar foto con cámara del dispositivo
- Sistema permite subir archivo desde galería
- Formatos aceptados: JPG, PNG, PDF
- Tamaño máximo: 10MB
- Resolución mínima recomendada: 1200x1600px
- Vista previa de la foto antes de continuar

**Interfaz:**
```
┌─────────────────────────────────────┐
│  📸 Paso 1: Fotografía del E14      │
├─────────────────────────────────────┤
│  [Vista previa de la foto]          │
│                                     │
│  [📷 Tomar Foto] [📁 Subir Archivo] │
│                                     │
│  Recomendaciones:                   │
│  • Buena iluminación                │
│  • Foto nítida                      │
│  • Formulario completo visible      │
└─────────────────────────────────────┘
```

---

### Paso 2: Digitar Datos del Formulario

**Requerimiento 2.1:** El testigo debe poder digitar manualmente los datos del E14

**Criterios de Aceptación:**
- Formulario con campos para cada candidato
- Campos para votos especiales (blanco, nulo, no marcado)
- Cálculo automático del total de votos
- Validación de números (enteros no negativos)
- Campo de observaciones opcional
- Comparación con votantes habilitados

**Interfaz:**
```
┌─────────────────────────────────────┐
│  ⌨️ Paso 2: Digitación de Datos     │
├─────────────────────────────────────┤
│  Candidato 1: [___] votos           │
│  Candidato 2: [___] votos           │
│  Candidato 3: [___] votos           │
│                                     │
│  Votos en Blanco: [___]             │
│  Votos Nulos: [___]                 │
│  No Marcadas: [___]                 │
│                                     │
│  Total: 0 / 350 votantes            │
│  Observaciones: [____________]      │
└─────────────────────────────────────┘
```

---

### Paso 3: Enviar Captura

**Requerimiento 3.1:** El testigo debe poder enviar la captura completa

**Criterios de Aceptación:**
- Botón de envío habilitado solo si hay foto Y datos
- Confirmación antes de enviar
- Envío a endpoint: `POST /api/testigo/captura-e14`
- Incluye: foto (base64), datos digitados, mesa_id, testigo_id, timestamp
- Mensaje de confirmación al enviar exitosamente
- Redirección al dashboard después de enviar

**Datos Enviados:**
```json
{
  "mesa_id": 123,
  "testigo_id": 456,
  "foto": "base64_image_data",
  "datos": {
    "candidatos": [
      {"id": 1, "votos": 145},
      {"id": 2, "votos": 132},
      {"id": 3, "votos": 20}
    ],
    "votos_blanco": 8,
    "votos_nulos": 3,
    "no_marcadas": 12,
    "total": 320
  },
  "observaciones": "Todo normal",
  "timestamp": "2025-11-07T15:30:00"
}
```

---

## 🔄 Flujo Opcional: OCR Asistido

### Requerimiento OCR.1: Procesamiento Automático (Opcional)

**Descripción:** Si el admin ha configurado zonas OCR, el sistema puede pre-llenar el formulario automáticamente.

**Criterios de Aceptación:**
- Admin configura estructura E14 con zonas OCR
- Sistema procesa foto con Tesseract OCR
- Extrae números de cada zona definida
- Pre-llena formulario con datos extraídos
- Muestra nivel de confianza por campo
- **Testigo SIEMPRE revisa y corrige** antes de enviar

**Flujo con OCR:**
```
1. Testigo sube foto
2. Sistema procesa con OCR (automático)
3. Sistema pre-llena formulario
4. Testigo revisa datos
5. Testigo corrige si es necesario
6. Testigo envía captura
```

**Interfaz con OCR:**
```
┌─────────────────────────────────────┐
│  ✅ OCR Completado                  │
│  Confianza Promedio: 95%            │
├─────────────────────────────────────┤
│  Candidato 1: [145] 98% ✏️          │
│  Candidato 2: [132] 96% ✏️          │
│  Candidato 3: [20]  94% ✏️          │
│                                     │
│  Votos Blanco: [8]  92% ✏️          │
│  Votos Nulos: [3]   89% ⚠️ ✏️       │
│  No Marcadas: [12]  94% ✏️          │
│                                     │
│  ⚠️ Baja confianza en Votos Nulos   │
│                                     │
│  [Corregir] [Aceptar y Enviar]      │
└─────────────────────────────────────┘
```

---

## 📊 Funcionalidades Adicionales

### Requerimiento 4: Observaciones del Proceso

**Descripción:** El testigo puede registrar observaciones durante el proceso electoral.

**Criterios de Aceptación:**
- Formulario para nueva observación
- Tipo de observación (procedimiento, participación, seguridad, otro)
- Descripción detallada
- Timestamp automático
- Historial de observaciones registradas

---

### Requerimiento 5: Reporte de Incidencias

**Descripción:** El testigo puede reportar incidencias que requieren atención.

**Criterios de Aceptación:**
- Formulario para nueva incidencia
- Tipo de incidencia (irregularidad, problema técnico, alteración, falta material, otro)
- Nivel de gravedad (baja, media, alta)
- Descripción detallada
- Timestamp automático
- Historial de incidencias reportadas

---

### Requerimiento 6: Ver Resultados Preliminares

**Descripción:** El testigo puede ver resultados preliminares de su mesa.

**Criterios de Aceptación:**
- Tabla con votos por candidato
- Gráfico de participación
- Total de votos registrados
- Comparación con votantes habilitados

---

### Requerimiento 7: Historial de Capturas

**Descripción:** El testigo puede ver todas las capturas E14 que ha enviado.

**Criterios de Aceptación:**
- Lista de capturas con fecha/hora
- Estado de cada captura (pendiente, aprobada, rechazada)
- Posibilidad de ver detalles de cada captura
- Ver foto original y datos digitados

---

## 🗂️ Estructura de Base de Datos

### Tabla: `capturas_e14`
```sql
CREATE TABLE capturas_e14 (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER NOT NULL,
    testigo_id INTEGER NOT NULL,
    ruta_foto VARCHAR(255) NOT NULL,
    datos_json TEXT NOT NULL,
    total_votos INTEGER,
    observaciones TEXT,
    estado VARCHAR(50) DEFAULT 'pendiente',
    procesado_ocr BOOLEAN DEFAULT FALSE,
    confianza_ocr FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
    FOREIGN KEY (testigo_id) REFERENCES users(id)
);
```

### Tabla: `observaciones_testigo`
```sql
CREATE TABLE observaciones_testigo (
    id INTEGER PRIMARY KEY,
    testigo_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    tipo VARCHAR(50),
    descripcion TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (testigo_id) REFERENCES users(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
);
```

### Tabla: `incidencias_testigo`
```sql
CREATE TABLE incidencias_testigo (
    id INTEGER PRIMARY KEY,
    testigo_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    tipo VARCHAR(50),
    gravedad VARCHAR(20),
    descripcion TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (testigo_id) REFERENCES users(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
);
```

---

## 🔗 APIs Requeridas

### API Principal: Captura E14

```
POST /api/testigo/captura-e14
Content-Type: multipart/form-data

Parámetros:
- mesa_id: integer
- testigo_id: integer
- foto: file (image/jpeg, image/png, application/pdf)
- datos: json string
- observaciones: string (opcional)

Respuesta:
{
  "success": true,
  "captura_id": 789,
  "mensaje": "Captura E14 registrada exitosamente",
  "estado": "pendiente_validacion"
}
```

### API Opcional: OCR Asistido

```
POST /api/testigo/procesar-ocr-e14
Content-Type: multipart/form-data

Parámetros:
- foto: file
- mesa_id: integer

Respuesta:
{
  "success": true,
  "datos_extraidos": {
    "candidatos": [...],
    "votos_blanco": 8,
    "votos_nulos": 3,
    "no_marcadas": 12
  },
  "confianza_promedio": 95,
  "advertencias": [...]
}
```

### APIs Adicionales

```
POST /api/testigo/observacion
POST /api/testigo/incidencia
GET  /api/testigo/capturas/:mesa_id
GET  /api/testigo/resultados/:mesa_id
```

---

## 📱 Páginas del Testigo

### Páginas Requeridas:
1. **dashboard.html** - Dashboard principal
2. **e14.html** - Captura E14 (foto + digitación)
3. **observaciones.html** - Registro de observaciones
4. **incidencias.html** - Reporte de incidencias
5. **reportes.html** - Ver reportes generados
6. **resultados.html** - Ver resultados preliminares

### ❌ Páginas que NO Existen:
- **e24.html** - El testigo NO crea E24
- **generar_pdf.html** - El testigo NO genera PDFs

---

## ✅ Prioridades de Implementación

### Fase 1: Captura Básica (Alta Prioridad)
1. ✅ Interfaz de captura de foto
2. ✅ Formulario de digitación manual
3. ✅ Validación de datos
4. ✅ Envío al servidor
5. ✅ Almacenamiento en BD

### Fase 2: OCR Asistido (Media Prioridad)
1. 🔄 Configuración de zonas OCR por admin
2. 🔄 Procesamiento automático con Tesseract
3. 🔄 Pre-llenado de formulario
4. 🔄 Revisión y corrección por testigo
5. 🔄 Indicadores de confianza

### Fase 3: Funcionalidades Adicionales (Baja Prioridad)
1. 🔄 Observaciones del proceso
2. 🔄 Reporte de incidencias
3. 🔄 Historial de capturas
4. 🔄 Resultados preliminares
5. 🔄 Exportación de datos

---

## 🎯 Resumen Ejecutivo

### El Testigo Electoral:
- **Captura** foto del E14 físico
- **Digita** datos del formulario
- **Envía** captura al sistema
- **Registra** observaciones e incidencias
- **Consulta** resultados preliminares

### El Sistema:
- **Almacena** foto original + datos digitados
- **Valida** totales y consistencia
- **Procesa** con OCR (opcional)
- **Notifica** al coordinador para validación
- **Mantiene** historial de capturas

### El Coordinador/Admin:
- **Revisa** capturas de testigos
- **Valida** datos vs foto
- **Aprueba** o rechaza capturas
- **Consolida** datos en E24 (múltiples mesas)
- **Genera** reportes oficiales

---

**Documento actualizado:** 2025-11-07  
**Estado:** Requerimientos consolidados y clarificados  
**Próximo paso:** Implementar Fase 1 (Captura Básica)
