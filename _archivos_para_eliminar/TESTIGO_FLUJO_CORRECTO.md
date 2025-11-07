# 📋 Flujo Correcto del Testigo Electoral

## 🎯 Rol del Testigo

El testigo electoral **NO crea** formularios E14 ni E24. Su función es:
1. **Capturar foto** del formulario E14 físico
2. **Digitar los datos** del formulario
3. **Enviar** la información al sistema

---

## 📸 Proceso de Captura E14

### Paso 1: Fotografiar el Formulario Físico
- El testigo toma una foto del formulario E14 que fue llenado físicamente en la mesa
- Puede usar la cámara del dispositivo o subir un archivo
- Requisitos de la foto:
  - Buena iluminación
  - Imagen nítida y enfocada
  - Formulario completo visible
  - Sin sombras ni reflejos

### Paso 2: Digitar los Datos
El testigo transcribe manualmente los datos del formulario:
- Votos por partido o coalision
- Votos por cada candidato
- Votos en blanco
- Votos nulos
- Tarjetas no marcadas
- Observaciones (opcional)

### Paso 3: Validación
- El sistema calcula automáticamente el total de votos
- Compara con votantes habilitados
- Muestra advertencias si hay inconsistencias

### Paso 4: Envío
- El testigo revisa que todo esté correcto
- Envía la captura (foto + datos) al sistema
- El sistema guarda:
  - Imagen del formulario físico
  - Datos digitados
  - Timestamp y testigo que capturó

---

## ❌ Lo que el Testigo NO Hace

### NO Crea E14
- El E14 es un formulario físico oficial
- Se llena manualmente en la mesa de votación
- El testigo solo lo fotografía y transcribe

### NO Crea E24
- El E24 es un formulario de consolidación
- al igual que el E14 no lo crea el sistema, es un documento al cual se le toma la foto fisica
- Consolida múltiples E14 de diferentes mesas
- El testigo NO tiene acceso a esta funcionalidad

### NO Genera PDFs
- El testigo no genera documentos oficiales
- Solo captura y transcribe información
- Los documentos oficiales se generan en otros niveles

---

## 🔄 Flujo Completo del Sistema

```
1. MESA DE VOTACIÓN (Físico)
   ├─ Jurados llenan E14 físico
   └─ Firman y sellan el documento

2. TESTIGO ELECTORAL (Captura)
   ├─ Fotografía el E14 físico
   ├─ Digita los datos en el sistema
   └─ Envía captura al servidor

3. SISTEMA (Almacenamiento)
   ├─ Guarda imagen original
   ├─ Guarda datos digitados
   ├─ Asocia con mesa y testigo
   └─ Marca como "capturado"

4. COORDINADOR/ADMIN (Validación)
   ├─ Revisa capturas de testigos
   ├─ Valida datos vs foto
   ├─ Aprueba o rechaza
   └─ Consolida en E24 (múltiples mesas)

5. REPORTES (Generación)
   ├─ Sistema genera reportes
   ├─ Consolida datos aprobados
   └─ Genera E24 oficial (consolidado)
```

---

## 📱 Interfaz del Testigo

### Dashboard Principal
- **Registro de Votos:** Registro rápido durante el día
- **Captura E14:** Fotografía + digitación al final
- **Observaciones:** Notas del proceso
- **Incidencias:** Reportes de problemas

### Página de Captura E14 (`/testigo/e14`)
```
┌─────────────────────────────────────────┐
│  📸 Paso 1: Fotografía del E14          │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │     [Vista previa de foto]        │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│  [Tomar Foto] [Subir Archivo]           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ⌨️ Paso 2: Digitación de Datos         │
│  Candidato 1: [___]                     │
│  Candidato 2: [___]                     │
│  Candidato 3: [___]                     │
│  Votos Blanco: [___]                    │
│  Votos Nulos: [___]                     │
│  No Marcadas: [___]                     │
│  Total: 0 / 350 votantes                │
│  Observaciones: [____________]          │
└─────────────────────────────────────────┘

        [Enviar Captura E14]
```

---

## 🗂️ Estructura de Archivos

### Templates del Testigo
```
templates/roles/testigo_mesa/
├── dashboard.html          # Dashboard principal
├── e14.html                # Captura E14 (foto + datos)
├── observaciones.html      # Observaciones del proceso
├── incidencias.html        # Reporte de incidencias
├── reportes.html           # Ver reportes generados
└── resultados.html         # Ver resultados preliminares
```

### ❌ Archivos que NO Existen
```
templates/roles/testigo_mesa/
├── e24.html                # ❌ NO EXISTE - Testigo no crea E24
└── generar_pdf.html        # ❌ NO EXISTE - Testigo no genera PDFs
```

---

## 🔗 Rutas del Testigo

### Rutas Activas
```
GET  /dashboard/testigo_mesa    # Dashboard principal
GET  /testigo/e14                # Captura E14 (foto + datos)
GET  /testigo/observaciones      # Observaciones
GET  /testigo/incidencias        # Incidencias
GET  /testigo/reportes           # Reportes
GET  /testigo/resultados         # Resultados
```

### ❌ Rutas que NO Existen
```
GET  /testigo/e24                # ❌ ELIMINADA
GET  /testigo/generar-e14        # ❌ NO EXISTE
GET  /testigo/generar-e24        # ❌ NO EXISTE
```

---

## 📊 APIs del Testigo

### APIs Necesarias (Pendientes)
```
POST /api/testigo/captura-e14
{
  "mesa_id": 123,
  "testigo_id": 456,
  "foto": "base64_image_data",
  "datos": {
    "candidatos": [
      {"id": 1, "votos": 145},
      {"id": 2, "votos": 132}
    ],
    "votos_blanco": 8,
    "votos_nulos": 3,
    "no_marcadas": 12
  },
  "observaciones": "Todo normal"
}
```

### Respuesta
```json
{
  "success": true,
  "captura_id": 789,
  "mensaje": "Captura E14 registrada exitosamente",
  "estado": "pendiente_validacion"
}
```

---

## ✅ Resumen

### El Testigo:
- ✅ Fotografía el E14 físico
- ✅ Digita los datos del E14
- ✅ Envía captura al sistema
- ✅ Registra observaciones
- ✅ Reporta incidencias

### El Testigo NO:
- ❌ Crea formularios E14
- ❌ Crea formularios E24
- ❌ Genera PDFs oficiales
- ❌ Consolida datos de múltiples mesas
- ❌ Valida capturas de otros testigos

---

## 🎯 Próxima Implementación

### Fase 1: Captura Básica
1. Interfaz de captura de foto
2. Formulario de digitación
3. Validación de datos
4. Envío al servidor

### Fase 2: OCR (Opcional)
1. Procesamiento automático de foto
2. Extracción de números con Tesseract
3. Pre-llenado de formulario
4. Testigo revisa y corrige

### Fase 3: Validación
1. Coordinador revisa capturas
2. Compara foto vs datos
3. Aprueba o rechaza
4. Solicita correcciones si es necesario

---

**Documento actualizado:** 2025-11-07  
**Estado:** Flujo clarificado y corregido
