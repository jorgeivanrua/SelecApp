# 📋 Requerimientos Dashboard Testigo Electoral

## 🎯 Funcionalidades Requeridas

### 1. **Selección de Mesa** (Primera acción)
El testigo debe poder:
- Ver lista de mesas de su puesto asignado
- Seleccionar la mesa donde está trabajando
- Ver información de la mesa (número, puesto, votantes habilitados)
- Cambiar de mesa si es necesario

**Datos a mostrar:**
- Número de mesa
- Puesto de votación
- Dirección del puesto
- Votantes habilitados en la mesa
- Estado de la mesa (abierta/cerrada)

---

### 2. **Datos Precargados del Admin**
El sistema debe cargar automáticamente:

#### A. Tipo de Elección
- Presidencial
- Congreso
- Gobernación
- Alcaldía
- Consultas
- Plebiscito
- Referendo

#### B. Partidos Políticos
- Nombre del partido
- Logo
- Color representativo
- Número en tarjetón

#### C. Coaliciones
- Nombre de la coalición
- Partidos que la conforman
- Candidatos de la coalición

#### D. Candidatos
- Nombre completo
- Partido/Coalición
- Número en tarjetón
- Foto
- Cargo al que aspira

**Endpoint:** `GET /api/admin/datos-electorales`
**Respuesta:**
```json
{
  "tipo_eleccion": "Alcaldía",
  "partidos": [...],
  "coaliciones": [...],
  "candidatos": [...]
}
```

---

### 3. **Registro de Votos**
Con los datos precargados, el testigo puede:
- Seleccionar candidato de lista dinámica
- Ver foto y partido del candidato
- Registrar número de votos
- Agregar observaciones
- Ver resumen en tiempo real

**Campos del formulario:**
- Candidato (select con datos de BD)
- Número de votos
- Observaciones (opcional)

---

### 4. **Carga de Fotos E14** (NUEVO - Prioridad Alta)

#### Funcionalidad:
El testigo debe poder subir fotos de los formularios E14 físicos diligenciados en la mesa.

#### Características:
- **Múltiples fotos:** Permitir subir varias fotos del mismo formulario
- **Vista previa:** Mostrar miniatura antes de subir
- **Compresión:** Optimizar tamaño de imagen
- **Metadatos:** Asociar foto con mesa y timestamp
- **Galería:** Ver todas las fotos subidas

#### Tipos de fotos a subir:
1. **E14 - Acta de Escrutinio**
   - Foto frontal del formulario
   - Foto de firmas
   - Foto de observaciones (si hay)

2. **Documentos adicionales:**
   - Actas de incidencias
   - Documentos de soporte
   - Fotos del proceso

#### Interfaz de carga:
```
┌─────────────────────────────────────┐
│  📸 Cargar Fotos Formulario E14     │
├─────────────────────────────────────┤
│                                     │
│  [Arrastrar archivos aquí]          │
│  o                                  │
│  [Seleccionar archivos]             │
│                                     │
│  Formatos: JPG, PNG, PDF            │
│  Tamaño máximo: 5MB por archivo     │
│                                     │
├─────────────────────────────────────┤
│  Fotos cargadas:                    │
│  ┌────┐ ┌────┐ ┌────┐              │
│  │ 📷 │ │ 📷 │ │ 📷 │              │
│  └────┘ └────┘ └────┘              │
│  E14-1  E14-2  E14-3                │
│                                     │
│  [Subir todas las fotos]            │
└─────────────────────────────────────┘
```

**Endpoint:** `POST /api/testigo/subir-foto-e14`
**Datos:**
```json
{
  "mesa_id": 123,
  "tipo_documento": "E14",
  "archivo": "base64_image_data",
  "descripcion": "Acta de escrutinio - página 1",
  "timestamp": "2025-11-07T00:30:00"
}
```

---

### 5. **Ver Mesas del Puesto**

El testigo puede ver todas las mesas de su puesto:

**Tabla de mesas:**
```
┌──────┬─────────────┬──────────┬─────────┐
│ Mesa │ Votantes    │ Estado   │ Acción  │
├──────┼─────────────┼──────────┼─────────┤
│ 001  │ 350         │ Abierta  │ [Ver]   │
│ 002  │ 345         │ Abierta  │ [Ver]   │
│ 003  │ 360         │ Cerrada  │ [Ver]   │
└──────┴─────────────┴──────────┴─────────┘
```

**Endpoint:** `GET /api/testigo/mesas-puesto/:puesto_id`

---

### 6. **Formulario E14 Digital**

Además de las fotos, permitir llenar el E14 digitalmente:

**Campos:**
- Total votos por candidato (calculado automáticamente)
- Votos en blanco
- Votos nulos
- Tarjetas no marcadas
- Total votantes que sufragaron
- Observaciones
- Firmas digitales (opcional)

**Botones:**
- Generar PDF
- Enviar a servidor
- Imprimir

---

## 🔄 Flujo de Trabajo del Testigo

```
1. Login → Dashboard Testigo
2. Seleccionar Mesa Asignada
3. Sistema carga:
   - Tipo de elección
   - Candidatos disponibles
   - Partidos y coaliciones
4. Registrar votos durante el día
5. Al finalizar:
   - Subir fotos E14 físico
   - Llenar E14 digital
   - Cerrar mesa
6. Exportar datos
```

---

## 📊 Estructura de Base de Datos Necesaria

### Tabla: `mesas_votacion`
```sql
- id
- numero_mesa
- puesto_id
- votantes_habilitados
- estado (abierta/cerrada)
- testigo_asignado_id
```

### Tabla: `fotos_e14`
```sql
- id
- mesa_id
- testigo_id
- tipo_documento (E14, E24, incidencia)
- ruta_archivo
- descripcion
- timestamp
- estado (pendiente/aprobado/rechazado)
```

### Tabla: `candidatos`
```sql
- id
- nombre_completo
- partido_id
- coalicion_id
- numero_tarjeton
- foto_url
- cargo
- tipo_eleccion_id
```

### Tabla: `votos_registrados`
```sql
- id
- mesa_id
- candidato_id
- numero_votos
- testigo_id
- timestamp
- observaciones
```

---

## 🎨 Diseño de Interfaz

### Sección 1: Selección de Mesa (Top)
```
┌─────────────────────────────────────────┐
│ 📍 Mesa Asignada: [Seleccionar ▼]      │
│    Puesto: Colegio Nacional             │
│    Votantes: 350                        │
└─────────────────────────────────────────┘
```

### Sección 2: Registro de Votos (Centro)
```
┌─────────────────────────────────────────┐
│ 🗳️ Registro de Votos                    │
├─────────────────────────────────────────┤
│ Candidato: [Seleccionar ▼]              │
│ Votos: [___]                            │
│ [Registrar Voto]                        │
└─────────────────────────────────────────┘
```

### Sección 3: Carga de Fotos E14 (Centro-Derecha)
```
┌─────────────────────────────────────────┐
│ 📸 Fotos Formulario E14                 │
├─────────────────────────────────────────┤
│ [Subir Foto]                            │
│ Fotos: 3 archivos                       │
│ [Ver Galería]                           │
└─────────────────────────────────────────┘
```

### Sección 4: Mesas del Puesto (Inferior)
```
┌─────────────────────────────────────────┐
│ 📋 Mesas del Puesto                     │
├─────────────────────────────────────────┤
│ Mesa 001 | Mesa 002 | Mesa 003          │
│ [Ver detalles de cada mesa]             │
└─────────────────────────────────────────┘
```

---

## 🔧 APIs Necesarias

### Admin (Precarga de datos):
- `POST /api/admin/tipo-eleccion` - Crear tipo de elección
- `POST /api/admin/partido` - Crear partido
- `POST /api/admin/coalicion` - Crear coalición
- `POST /api/admin/candidato` - Crear candidato
- `GET /api/admin/datos-electorales` - Obtener todos los datos

### Testigo:
- `GET /api/testigo/mesas-disponibles` - Mesas del puesto
- `POST /api/testigo/seleccionar-mesa` - Asignar mesa
- `GET /api/testigo/datos-eleccion` - Candidatos, partidos, etc.
- `POST /api/testigo/registrar-voto` - Registrar voto
- `POST /api/testigo/subir-foto-e14` - Subir foto
- `GET /api/testigo/fotos-e14/:mesa_id` - Ver fotos subidas
- `DELETE /api/testigo/foto-e14/:id` - Eliminar foto
- `POST /api/testigo/formulario-e14` - Guardar E14 digital

---

## ✅ Prioridades de Implementación

1. **Alta:** Selección de mesa
2. **Alta:** Carga de datos del admin (candidatos, partidos)
3. **Alta:** Carga de fotos E14
4. **Media:** Ver mesas del puesto
5. **Media:** Formulario E14 digital
6. **Baja:** Galería de fotos con zoom
