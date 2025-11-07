# 📸 Flujo de Trabajo con OCR - Dashboard Testigo

## 🎯 Proceso Completo de Captura con OCR

### Paso 1: Admin Configura Estructura del E14
El administrador debe configurar previamente:

#### A. Estructura del Formulario E14
```json
{
  "tipo_eleccion": "Alcaldía",
  "estructura_e14": {
    "posiciones": [
      {
        "posicion": 1,
        "tipo": "candidato",
        "partido": "Partido A",
        "candidato": "Juan Pérez",
        "zona_ocr": {"x": 100, "y": 200, "width": 50, "height": 30}
      },
      {
        "posicion": 2,
        "tipo": "candidato",
        "partido": "Partido B",
        "candidato": "María García",
        "zona_ocr": {"x": 100, "y": 250, "width": 50, "height": 30}
      },
      {
        "posicion": 99,
        "tipo": "voto_blanco",
        "zona_ocr": {"x": 100, "y": 500, "width": 50, "height": 30}
      },
      {
        "posicion": 100,
        "tipo": "voto_nulo",
        "zona_ocr": {"x": 100, "y": 550, "width": 50, "height": 30}
      },
      {
        "posicion": 101,
        "tipo": "no_marcado",
        "zona_ocr": {"x": 100, "y": 600, "width": 50, "height": 30}
      }
    ]
  }
}
```

**Endpoint Admin:** `POST /api/admin/configurar-estructura-e14`

---

### Paso 2: Testigo Sube Foto del E14

#### Interfaz de Carga:
```
┌─────────────────────────────────────────────┐
│  📸 Cargar Formulario E14 Físico            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────┐       │
│  │                                 │       │
│  │   [Arrastrar foto aquí]         │       │
│  │   o                             │       │
│  │   [📷 Tomar Foto] [📁 Archivo]  │       │
│  │                                 │       │
│  └─────────────────────────────────┘       │
│                                             │
│  ✅ Formatos: JPG, PNG, PDF                │
│  ✅ Tamaño máximo: 10MB                     │
│  ✅ Resolución mínima: 1200x1600px          │
│                                             │
│  [Subir y Procesar con OCR]                │
└─────────────────────────────────────────────┘
```

**Endpoint:** `POST /api/testigo/subir-e14-ocr`

---

### Paso 3: Procesamiento OCR Automático

#### Flujo del Servidor:
```
1. Recibir imagen
2. Preprocesar imagen:
   - Convertir a escala de grises
   - Mejorar contraste
   - Corregir rotación
   - Eliminar ruido
3. Aplicar OCR en zonas definidas
4. Extraer números de cada posición
5. Validar datos extraídos
6. Retornar resultados
```

#### Tecnologías OCR:
- **Tesseract OCR** (Python: pytesseract)
- **Google Cloud Vision API** (opcional, más preciso)
- **Azure Computer Vision** (opcional)

#### Respuesta del OCR:
```json
{
  "success": true,
  "imagen_id": "e14_mesa001_20251107_001",
  "confianza_promedio": 95,
  "datos_extraidos": [
    {
      "posicion": 1,
      "candidato": "Juan Pérez",
      "partido": "Partido A",
      "votos": 145,
      "confianza": 98
    },
    {
      "posicion": 2,
      "candidato": "María García",
      "partido": "Partido B",
      "votos": 132,
      "confianza": 96
    },
    {
      "posicion": 99,
      "tipo": "voto_blanco",
      "votos": 8,
      "confianza": 92
    },
    {
      "posicion": 100,
      "tipo": "voto_nulo",
      "votos": 3,
      "confianza": 89
    },
    {
      "posicion": 101,
      "tipo": "no_marcado",
      "votos": 12,
      "confianza": 94
    }
  ],
  "total_votos": 300,
  "advertencias": [
    "Baja confianza en posición 100 (89%)"
  ]
}
```

---

### Paso 4: Revisión y Corrección por Testigo

#### Interfaz de Revisión:
```
┌─────────────────────────────────────────────────────────┐
│  ✅ OCR Completado - Revisar Datos Extraídos            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Confianza Promedio: 95% ✅                             │
│  Total Votos Detectados: 300                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Vista Previa de Imagen                          │   │
│  │ [Imagen del E14 con zonas marcadas]             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  📊 Datos Extraídos:                                    │
│                                                         │
│  ┌──────┬─────────────────┬────────┬──────┬─────────┐  │
│  │ Pos  │ Candidato       │ Votos  │ Conf │ Acción  │  │
│  ├──────┼─────────────────┼────────┼──────┼─────────┤  │
│  │  1   │ Juan Pérez      │ [145]  │ 98%  │ ✅ ✏️   │  │
│  │  2   │ María García    │ [132]  │ 96%  │ ✅ ✏️   │  │
│  │  3   │ Carlos López    │ [20]   │ 94%  │ ✅ ✏️   │  │
│  │ ...  │ ...             │ ...    │ ...  │ ...     │  │
│  │  99  │ Voto Blanco     │ [8]    │ 92%  │ ✅ ✏️   │  │
│  │ 100  │ Voto Nulo       │ [3]    │ 89%⚠️│ ✅ ✏️   │  │
│  │ 101  │ No Marcado      │ [12]   │ 94%  │ ✅ ✏️   │  │
│  └──────┴─────────────────┴────────┴──────┴─────────┘  │
│                                                         │
│  ⚠️ Advertencias:                                       │
│  • Baja confianza en posición 100 (89%)                │
│                                                         │
│  [Corregir Datos] [Aceptar y Guardar] [Rechazar]      │
└─────────────────────────────────────────────────────────┘
```

#### Funcionalidades de Revisión:
- ✅ Ver imagen original con zonas OCR marcadas
- ✅ Editar cualquier valor manualmente
- ✅ Ver nivel de confianza por campo
- ✅ Alertas en campos con baja confianza (<90%)
- ✅ Validación de totales
- ✅ Comparación con votantes habilitados

---

### Paso 5: Guardar Datos Validados

Una vez el testigo revisa y corrige:

**Endpoint:** `POST /api/testigo/confirmar-datos-e14`

```json
{
  "mesa_id": 123,
  "imagen_e14_id": "e14_mesa001_20251107_001",
  "datos_confirmados": [
    {"posicion": 1, "votos": 145, "editado": false},
    {"posicion": 2, "votos": 132, "editado": false},
    {"posicion": 100, "votos": 5, "editado": true}
  ],
  "total_votos": 300,
  "observaciones": "Corregí voto nulo de 3 a 5",
  "testigo_id": 456,
  "timestamp": "2025-11-07T15:30:00"
}
```

---

## 🔧 Implementación Técnica del OCR

### Backend (Python/Flask):

```python
from PIL import Image
import pytesseract
import cv2
import numpy as np

def procesar_e14_con_ocr(imagen_path, estructura_e14):
    """
    Procesa imagen E14 y extrae datos con OCR
    """
    # 1. Cargar imagen
    imagen = cv2.imread(imagen_path)
    
    # 2. Preprocesar
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY)
    
    # 3. Extraer datos de cada zona
    resultados = []
    for posicion in estructura_e14['posiciones']:
        zona = posicion['zona_ocr']
        
        # Recortar zona
        roi = binaria[
            zona['y']:zona['y']+zona['height'],
            zona['x']:zona['x']+zona['width']
        ]
        
        # Aplicar OCR
        texto = pytesseract.image_to_string(
            roi, 
            config='--psm 7 digits'
        )
        
        # Extraer número
        try:
            votos = int(''.join(filter(str.isdigit, texto)))
            confianza = calcular_confianza(roi, texto)
        except:
            votos = 0
            confianza = 0
        
        resultados.append({
            'posicion': posicion['posicion'],
            'candidato': posicion.get('candidato'),
            'partido': posicion.get('partido'),
            'tipo': posicion.get('tipo'),
            'votos': votos,
            'confianza': confianza
        })
    
    return {
        'datos_extraidos': resultados,
        'confianza_promedio': np.mean([r['confianza'] for r in resultados]),
        'total_votos': sum([r['votos'] for r in resultados])
    }
```

### Endpoint Flask:

```python
@testigo_bp.route('/subir-e14-ocr', methods=['POST'])
def subir_e14_ocr():
    """Subir foto E14 y procesar con OCR"""
    
    # Recibir imagen
    archivo = request.files['imagen']
    mesa_id = request.form['mesa_id']
    
    # Guardar imagen
    ruta = f'uploads/e14/mesa_{mesa_id}_{timestamp}.jpg'
    archivo.save(ruta)
    
    # Obtener estructura E14 del admin
    estructura = obtener_estructura_e14(mesa_id)
    
    # Procesar con OCR
    resultados = procesar_e14_con_ocr(ruta, estructura)
    
    # Guardar en BD (estado: pendiente_revision)
    guardar_datos_ocr_pendientes(mesa_id, resultados)
    
    return jsonify({
        'success': True,
        'imagen_id': ruta,
        'datos_extraidos': resultados['datos_extraidos'],
        'confianza_promedio': resultados['confianza_promedio']
    })
```

---

## 📊 Base de Datos

### Tabla: `estructura_e14`
```sql
CREATE TABLE estructura_e14 (
    id INTEGER PRIMARY KEY,
    tipo_eleccion_id INTEGER,
    posicion INTEGER,
    tipo VARCHAR(50), -- candidato, voto_blanco, voto_nulo, no_marcado
    candidato_id INTEGER,
    partido_id INTEGER,
    zona_ocr_x INTEGER,
    zona_ocr_y INTEGER,
    zona_ocr_width INTEGER,
    zona_ocr_height INTEGER
);
```

### Tabla: `imagenes_e14`
```sql
CREATE TABLE imagenes_e14 (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER,
    testigo_id INTEGER,
    ruta_archivo VARCHAR(255),
    estado VARCHAR(50), -- pendiente_ocr, procesado, confirmado, rechazado
    confianza_promedio FLOAT,
    timestamp DATETIME
);
```

### Tabla: `datos_ocr_e14`
```sql
CREATE TABLE datos_ocr_e14 (
    id INTEGER PRIMARY KEY,
    imagen_e14_id INTEGER,
    posicion INTEGER,
    candidato_id INTEGER,
    votos_detectados INTEGER,
    votos_confirmados INTEGER,
    confianza FLOAT,
    editado BOOLEAN,
    timestamp DATETIME
);
```

---

## 🎯 Ventajas del Sistema OCR

1. ✅ **Velocidad:** Captura en segundos vs minutos manual
2. ✅ **Precisión:** 95%+ de exactitud con buena imagen
3. ✅ **Trazabilidad:** Imagen original + datos extraídos
4. ✅ **Validación:** Testigo revisa antes de confirmar
5. ✅ **Respaldo:** Imagen física + datos digitales
6. ✅ **Auditoría:** Registro de correcciones manuales

---

## ⚠️ Consideraciones

### Calidad de Imagen:
- Buena iluminación
- Sin sombras
- Enfoque nítido
- Resolución mínima 1200x1600px

### Manejo de Errores:
- Baja confianza → Alerta al testigo
- OCR falla → Permitir entrada manual
- Imagen borrosa → Solicitar nueva foto

### Privacidad:
- Imágenes encriptadas
- Acceso solo personal autorizado
- Eliminación automática después de X días
