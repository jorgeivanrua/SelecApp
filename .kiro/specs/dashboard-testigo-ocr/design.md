# Design Document - Dashboard Testigo con OCR

## Overview

El dashboard del testigo electoral es una interfaz web integrada que permite capturar, procesar y validar formularios E14 mediante OCR automático. El diseño se enfoca en un flujo lineal y simple: capturar foto → OCR automático → revisar/editar datos → enviar. Todo el proceso ocurre en una sola página sin navegación adicional.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Dashboard Testigo (Single Page)                │ │
│  │  ┌──────────────┐  ┌──────────────────────────────┐  │ │
│  │  │   Captura    │  │    Formulario E14 Completo   │  │ │
│  │  │   de Foto    │  │  (25+ campos editables)      │  │ │
│  │  │              │  │                              │  │ │
│  │  │  [Preview]   │  │  • Ubicación (6 campos)      │  │ │
│  │  │  [OCR Auto]  │  │  • Horarios (2 campos)       │  │ │
│  │  │              │  │  • Candidatos (dinámico)     │  │ │
│  │  │              │  │  • Votos (4 campos)          │  │ │
│  │  │              │  │  • Votantes (3 campos)       │  │ │
│  │  │              │  │  • Acta (5 campos)           │  │ │
│  │  │              │  │  • Observaciones (1 campo)   │  │ │
│  │  └──────────────┘  └──────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Routes                                 │ │
│  │  • POST /api/testigo/enviar-e14                        │ │
│  │  • GET  /api/testigo/mesa-asignada                     │ │
│  │  • GET  /api/testigo/candidatos                        │ │
│  │  • POST /api/testigo/procesar-ocr (futuro)             │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Business Logic                             │ │
│  │  • Validación de datos                                 │ │
│  │  • Cálculo de totales                                  │ │
│  │  • Procesamiento OCR (simulado)                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Data Layer                                 │ │
│  │  • SQLite Database                                      │ │
│  │  • Tablas: capturas_e14, datos_ocr_e14, users, mesas   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **OCR**: Tesseract OCR (futuro)
- **Image Processing**: PIL/Pillow (futuro)

## Components and Interfaces

### 1. Dashboard Component

**Responsabilidad**: Contenedor principal que orquesta la captura y edición del E14

**Subcomponentes**:
- Header con información de la mesa
- Estadísticas rápidas (4 cards)
- Área de captura de foto
- Formulario E14 completo

**Estado**:
```javascript
{
  fotoCapturada: boolean,
  candidatosCount: number,
  datosFormulario: {
    // 25+ campos del E14
  }
}
```

### 2. Captura de Foto Component

**Responsabilidad**: Manejo de captura/subida de imagen y preview

**Interfaz**:
```javascript
// Props
{
  onFotoCapturada: (file: File) => void
}

// Methods
- procesarFoto(file: File): Promise<void>
- mostrarPreview(imageData: string): void
```

**Flujo**:
1. Usuario hace click en área de captura
2. Se abre selector de archivo/cámara
3. Usuario selecciona imagen
4. Se muestra preview
5. Se activa OCR automáticamente

### 3. OCR Processor Component

**Responsabilidad**: Procesamiento automático de la imagen con OCR

**Interfaz**:
```javascript
// Methods
- procesarOCR(file: File): Promise<DatosOCR>
- llenarFormularioConOCR(datos: DatosOCR): void

// Types
interface DatosOCR {
  candidatos: Array<{
    nombre: string,
    partido: string,
    votos: number
  }>,
  votosBlanco: number,
  votosNulos: number,
  tarjetasNoMarcadas: number,
  votantesSufragaron: number,
  certificadosElectorales: number,
  numeroActa: string,
  juradoPresidente: string
}
```

**Flujo**:
1. Recibe archivo de imagen
2. Muestra indicador de procesamiento
3. Simula delay de 2 segundos (OCR real en futuro)
4. Extrae datos simulados
5. Llena formulario automáticamente
6. Muestra mensaje de éxito

### 4. Formulario E14 Component

**Responsabilidad**: Captura y validación de todos los campos del E14

**Secciones**:

**A. Información de Ubicación** (6 campos readonly)
- Departamento, Municipio, Zona
- Puesto, Mesa, Tipo de Elección

**B. Horarios** (2 campos editables)
- Hora de Apertura (time input)
- Hora de Cierre (time input)

**C. Candidatos** (dinámico)
- Nombre (text input)
- Partido (text input)
- Votos (number input)
- Botón eliminar
- Botón agregar nuevo

**D. Votos Especiales** (4 campos)
- Votos en Blanco (number)
- Votos Nulos (number)
- Tarjetas No Marcadas (number)
- Total Tarjetas (readonly, calculado)

**E. Información de Votantes** (3 campos)
- Votantes Habilitados (readonly)
- Votantes que Sufragaron (number)
- Certificados Electorales (number)

**F. Totales y Validación** (2 indicadores)
- Total Votos (calculado automáticamente)
- Estado de Validación (verde/amarillo/rojo)

**G. Información del Acta** (5 campos)
- Número de Acta E14 (text)
- Jurado Presidente (text)
- Testigos del Acta (text)
- Acta Firmada (checkbox)
- Proceso Normal (checkbox)

**H. Observaciones** (1 campo)
- Observaciones (textarea, 4 filas)

**Interfaz**:
```javascript
// Methods
- agregarCandidato(): void
- eliminarCandidato(id: number): void
- calcularTotales(): void
- validarFormulario(): boolean
- enviarFormulario(e: Event): Promise<void>

// Validation Rules
- Foto obligatoria
- Al menos un voto registrado
- Números no negativos
- Total calculado automáticamente
```

### 5. Validación Component

**Responsabilidad**: Validación en tiempo real de totales y consistencia

**Interfaz**:
```javascript
// Methods
- calcularTotales(): number
- validarContraHabilitados(total: number, habilitados: number): ValidationStatus
- actualizarIndicadorVisual(status: ValidationStatus): void

// Types
enum ValidationStatus {
  CORRECTO = 'green',    // Total === Habilitados
  INCOMPLETO = 'yellow', // Total < Habilitados
  EXCEDE = 'red'         // Total > Habilitados
}
```

**Lógica de Validación**:
```javascript
if (totalVotos === votantesHabilitados) {
  return CORRECTO; // Verde
} else if (totalVotos > votantesHabilitados) {
  return EXCEDE; // Rojo
} else {
  return INCOMPLETO; // Amarillo
}
```

## Data Models

### Captura E14
```javascript
{
  id: number,
  testigo_id: number,
  mesa_id: number,
  imagen_path: string,
  
  // Ubicación
  departamento: string,
  municipio: string,
  zona: string,
  puesto: string,
  mesa: string,
  tipo_eleccion: string,
  
  // Horarios
  hora_apertura: string, // HH:MM
  hora_cierre: string,   // HH:MM
  
  // Votos
  total_votos_candidatos: number,
  votos_blanco: number,
  votos_nulos: number,
  tarjetas_no_marcadas: number,
  total_votos: number,
  
  // Votantes
  votantes_habilitados: number,
  votantes_sufragaron: number,
  certificados_electorales: number,
  
  // Acta
  numero_acta: string,
  jurado_presidente: string,
  testigos_acta: string,
  acta_firmada: boolean,
  proceso_normal: boolean,
  
  // Metadata
  observaciones: string,
  estado: string, // 'enviado', 'validado', 'rechazado'
  procesado_ocr: boolean,
  fecha_captura: datetime,
  created_at: datetime,
  updated_at: datetime
}
```

### Datos OCR E14
```javascript
{
  id: number,
  captura_e14_id: number,
  posicion: number,
  tipo: string, // 'candidato', 'voto_blanco', 'voto_nulo', 'no_marcado'
  nombre_candidato: string,
  partido: string,
  votos_detectados: number,
  votos_confirmados: number,
  confianza: number, // 0-100%
  editado: boolean,
  created_at: datetime
}
```

## Error Handling

### Errores de Captura
- **Sin foto**: Deshabilitar botón de envío
- **Formato inválido**: Mostrar alerta y rechazar archivo
- **Tamaño excedido**: Mostrar alerta y sugerir comprimir

### Errores de OCR
- **OCR falla**: Mostrar mensaje de error, permitir entrada manual
- **Baja confianza**: Resaltar campos en amarillo
- **Sin datos**: Mostrar formulario vacío para entrada manual

### Errores de Validación
- **Total excede habilitados**: Mostrar indicador rojo, permitir envío con observaciones
- **Campos vacíos**: Validar antes de envío
- **Números negativos**: Prevenir entrada con min="0"

### Errores de Red
- **Timeout**: Mostrar mensaje, permitir reintentar
- **Error 500**: Mostrar mensaje genérico, guardar datos localmente (futuro)
- **Sin conexión**: Detectar y notificar (futuro)

## Testing Strategy

### Unit Tests
- Validación de totales
- Cálculo de participación
- Lógica de validación (verde/amarillo/rojo)
- Agregar/eliminar candidatos

### Integration Tests
- Flujo completo: captura → OCR → edición → envío
- API endpoints: enviar-e14, mesa-asignada, candidatos
- Persistencia de datos en base de datos

### E2E Tests
- Usuario captura foto
- OCR llena formulario
- Usuario edita datos
- Usuario envía formulario
- Sistema confirma guardado

### Manual Tests
- Calidad de imagen
- Responsive design (mobile/tablet/desktop)
- Accesibilidad (keyboard navigation)
- Performance (tiempo de carga, OCR)

## Performance Considerations

### Frontend
- Lazy loading de imágenes
- Debounce en cálculo de totales
- Optimización de re-renders
- Compresión de imágenes antes de subir

### Backend
- Índices en tablas (mesa_id, testigo_id)
- Caché de candidatos
- Procesamiento asíncrono de OCR
- Límite de tamaño de imagen (10MB)

### Database
- Índices compuestos para queries frecuentes
- Paginación de historial
- Archivado de datos antiguos

## Security Considerations

### Authentication
- JWT tokens para API calls
- Validación de rol de testigo
- Verificación de mesa asignada

### Authorization
- Testigo solo puede ver/editar su mesa
- Validación server-side de permisos
- Rate limiting en endpoints

### Data Validation
- Sanitización de inputs
- Validación de tipos de datos
- Prevención de SQL injection
- Validación de tamaño de archivo

## Deployment

### Development
```bash
python app.py
# Server: http://127.0.0.1:5000
# Dashboard: http://127.0.0.1:5000/dashboard/testigo_mesa
```

### Production
- Usar Gunicorn/uWSGI
- Configurar HTTPS
- Variables de entorno para secrets
- Backup automático de base de datos
- Monitoreo de errores (Sentry)

## Future Enhancements

### Short Term
1. OCR real con Tesseract
2. Validación de calidad de imagen
3. Modo offline con sincronización

### Medium Term
1. Historial de capturas
2. Comparación con otros testigos
3. Notificaciones push
4. Exportación de reportes

### Long Term
1. IA para detección de anomalías
2. Reconocimiento de firmas
3. Blockchain para inmutabilidad
4. Dashboard de análisis en tiempo real
