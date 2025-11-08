# Nuevas Funcionalidades - Dashboard Testigo

**Fecha:** 7 de noviembre de 2025  
**Funcionalidades Agregadas:**
1. Cambio automático de candidatos según tipo de elección
2. Zoom en imagen capturada del formulario E14

---

## 🎯 Funcionalidad 1: Candidatos por Tipo de Elección

### Descripción
Cuando el testigo cambia el tipo de elección, la lista de candidatos se actualiza automáticamente con los candidatos correspondientes a ese tipo.

### Tipos de Elección y Candidatos

#### 1. Senado
```
- Candidato Senado 1 (Partido Liberal)
- Candidato Senado 2 (Partido Conservador)
- Candidato Senado 3 (Partido Verde)
- Candidato Senado 4 (Polo Democrático)
```

#### 2. Cámara de Representantes
```
- Candidato Cámara 1 (Partido Liberal)
- Candidato Cámara 2 (Partido Conservador)
- Candidato Cámara 3 (Cambio Radical)
```

#### 3. Concejo Municipal
```
- Candidato Concejo 1 (Movimiento Cívico)
- Candidato Concejo 2 (Partido Liberal)
- Candidato Concejo 3 (Partido Conservador)
- Candidato Concejo 4 (Independiente)
- Candidato Concejo 5 (Partido Verde)
```

#### 4. Alcaldía
```
- Candidato Alcalde 1 (Partido Liberal)
- Candidato Alcalde 2 (Partido Conservador)
- Candidato Alcalde 3 (Movimiento Cívico)
```

#### 5. Gobernación
```
- Candidato Gobernador 1 (Partido Liberal)
- Candidato Gobernador 2 (Partido Conservador)
- Candidato Gobernador 3 (Cambio Radical)
```

#### 6. Asamblea Departamental
```
- Candidato Asamblea 1 (Partido Liberal)
- Candidato Asamblea 2 (Partido Conservador)
- Candidato Asamblea 3 (Partido Verde)
- Candidato Asamblea 4 (Polo Democrático)
```

### Funcionamiento

```javascript
function cargarCandidatosPorTipo(tipoEleccion) {
    // 1. Limpiar candidatos actuales
    document.getElementById('candidatos-container').innerHTML = '';
    
    // 2. Obtener candidatos del tipo seleccionado
    const candidatos = candidatosPorTipo[tipoEleccion];
    
    // 3. Agregar candidatos al formulario
    candidatos.forEach(candidato => {
        agregarCandidatoRow(candidato.nombre, candidato.partido);
    });
    
    // 4. Recalcular totales
    calcularTotales();
}
```

### Flujo de Usuario

```
1. Usuario selecciona "Tipo de Elección"
   ↓
2. onChange dispara cambiarTipoEleccion()
   ↓
3. Se llama cargarCandidatosPorTipo(tipo)
   ↓
4. Lista de candidatos se actualiza automáticamente
   ↓
5. Campos de votos en 0
   ↓
6. Usuario puede ingresar votos
```

### Ejemplo Visual

```
┌─────────────────────────────────────────────┐
│ Tipo de Elección: [Senado ▼]                │
├─────────────────────────────────────────────┤
│ Votos por Candidato                         │
│                                             │
│ Candidato Senado 1 | Partido Liberal | [0] │
│ Candidato Senado 2 | P. Conservador  | [0] │
│ Candidato Senado 3 | Partido Verde   | [0] │
│ Candidato Senado 4 | Polo Democrático| [0] │
└─────────────────────────────────────────────┘

Usuario cambia a "Concejo Municipal"
        ↓

┌─────────────────────────────────────────────┐
│ Tipo de Elección: [Concejo Municipal ▼]     │
├─────────────────────────────────────────────┤
│ Votos por Candidato                         │
│                                             │
│ Candidato Concejo 1 | Movimiento Cívico| [0]│
│ Candidato Concejo 2 | Partido Liberal  | [0]│
│ Candidato Concejo 3 | P. Conservador   | [0]│
│ Candidato Concejo 4 | Independiente    | [0]│
│ Candidato Concejo 5 | Partido Verde    | [0]│
└─────────────────────────────────────────────┘
```

---

## 🔍 Funcionalidad 2: Zoom en Imagen Capturada

### Descripción
El testigo puede hacer zoom en la imagen del formulario E14 capturado para verificar mejor los datos antes de digitarlos.

### Controles de Zoom

#### Botones de Control
```
┌─────────────────────────────────────────┐
│  [🔍+] [🔍-] [⊡]    ← Controles        │
│                                         │
│     [Imagen del E14]                    │
│                                         │
│  Click en la imagen para zoom           │
└─────────────────────────────────────────┘
```

**Botones:**
- 🔍+ **Acercar:** Aumenta el zoom en 0.5x
- 🔍- **Alejar:** Reduce el zoom en 0.5x
- ⊡ **Restablecer:** Vuelve al tamaño original

#### Zoom por Click
- **Click en la imagen:** Alterna entre zoom 2x y tamaño original
- **Cursor:** Cambia a zoom-in/zoom-out según el estado

### Niveles de Zoom

```
Nivel 1.0x: Tamaño original (default)
Nivel 1.5x: Zoom ligero
Nivel 2.0x: Zoom medio
Nivel 2.5x: Zoom alto
Nivel 3.0x: Zoom muy alto
Nivel 3.5x: Zoom máximo
Nivel 4.0x: Zoom extremo (máximo permitido)
```

### Funciones JavaScript

```javascript
// Toggle zoom con click
function toggleZoom() {
    if (zoomed) {
        resetZoom();
    } else {
        zoomLevel = 2;
        aplicarZoom();
    }
}

// Acercar
function zoomIn() {
    zoomLevel = Math.min(zoomLevel + 0.5, 4);
    aplicarZoom();
}

// Alejar
function zoomOut() {
    zoomLevel = Math.max(zoomLevel - 0.5, 1);
    aplicarZoom();
}

// Restablecer
function resetZoom() {
    zoomLevel = 1;
    aplicarZoom();
}
```

### Estilos CSS

```css
#preview-container {
    max-height: 500px;
    overflow: auto;  /* Permite scroll cuando hay zoom */
}

#preview-container img {
    cursor: zoom-in;
    transition: transform 0.3s;
}

#preview-container.zoomed img {
    cursor: zoom-out;
    transform: scale(2);
}

.zoom-controls {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 10;
}

.zoom-btn {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
```

### Flujo de Usuario

```
1. Usuario captura foto del E14
   ↓
2. Imagen se muestra con controles de zoom
   ↓
3. Usuario puede:
   - Click en imagen → Zoom 2x
   - Botón [+] → Aumentar zoom
   - Botón [-] → Reducir zoom
   - Botón [⊡] → Tamaño original
   ↓
4. Con zoom activo:
   - Scroll para ver diferentes partes
   - Verificar datos con detalle
   ↓
5. Restablecer zoom para continuar
```

### Casos de Uso

#### Caso 1: Verificar Números Borrosos
```
1. Foto capturada tiene números poco claros
2. Usuario hace click en la imagen (zoom 2x)
3. Verifica el número con detalle
4. Ingresa el dato correcto
5. Click nuevamente para volver al tamaño normal
```

#### Caso 2: Revisar Firmas
```
1. Usuario necesita verificar firmas del acta
2. Usa botón [+] varias veces (zoom 3x o 4x)
3. Hace scroll para ver toda la firma
4. Confirma que está firmada
5. Usa botón [⊡] para restablecer
```

#### Caso 3: Comparar Totales
```
1. Usuario quiere verificar suma de votos
2. Zoom 2x con click
3. Compara con los datos digitados
4. Confirma que coinciden
5. Restablecer zoom
```

---

## 🎨 Interfaz Mejorada

### Vista Completa

```
┌─────────────────────────────────────────────────────────┐
│ 1. Captura del Formulario E14                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  [🔍+] [🔍-] [⊡]                               │    │
│  │                                                 │    │
│  │         [Imagen del E14 - Click para zoom]     │    │
│  │                                                 │    │
│  │  ✅ Foto cargada - Click en la imagen para zoom│    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2. Datos del Formulario E14                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Tipo de Elección: [Senado ▼]  ← Cambia candidatos     │
│                                                          │
│  📋 Votos por Candidato                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │ Candidato Senado 1 | Partido Liberal    | [45]│    │
│  │ Candidato Senado 2 | P. Conservador     | [38]│    │
│  │ Candidato Senado 3 | Partido Verde      | [27]│    │
│  │ Candidato Senado 4 | Polo Democrático   | [15]│    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Beneficios

### Candidatos por Tipo
1. **Precisión:** Candidatos correctos para cada elección
2. **Eficiencia:** No hay que borrar/agregar candidatos manualmente
3. **Menos Errores:** Imposible mezclar candidatos de diferentes elecciones
4. **Rapidez:** Cambio instantáneo de lista

### Zoom en Imagen
1. **Verificación:** Puede verificar datos borrosos o poco claros
2. **Precisión:** Reduce errores de digitación
3. **Confianza:** El testigo puede confirmar visualmente
4. **Accesibilidad:** Útil para personas con problemas de visión
5. **Flexibilidad:** Múltiples niveles de zoom

---

## 🧪 Pruebas

### Test 1: Cambio de Tipo de Elección
```
1. Abrir dashboard testigo
2. Tipo inicial: Senado (4 candidatos)
3. Cambiar a "Concejo Municipal"
4. ✅ Lista se actualiza a 5 candidatos de concejo
5. Cambiar a "Alcaldía"
6. ✅ Lista se actualiza a 3 candidatos de alcalde
```

### Test 2: Zoom con Click
```
1. Capturar foto del E14
2. Click en la imagen
3. ✅ Zoom 2x aplicado
4. Click nuevamente
5. ✅ Vuelve a tamaño original
```

### Test 3: Zoom con Botones
```
1. Capturar foto del E14
2. Click en botón [+]
3. ✅ Zoom 1.5x
4. Click en botón [+] nuevamente
5. ✅ Zoom 2.0x
6. Click en botón [-]
7. ✅ Zoom 1.5x
8. Click en botón [⊡]
9. ✅ Zoom 1.0x (original)
```

### Test 4: Zoom Máximo
```
1. Capturar foto
2. Click [+] múltiples veces
3. ✅ Zoom aumenta hasta 4.0x (máximo)
4. Click [+] nuevamente
5. ✅ Se mantiene en 4.0x (no excede)
```

---

## 📝 Archivos Modificados

1. **templates/roles/testigo_mesa/dashboard.html**
   - Función `cambiarTipoEleccion()` mejorada
   - Nueva función `cargarCandidatosPorTipo()`
   - Función `procesarFoto()` con controles de zoom
   - Nuevas funciones: `toggleZoom()`, `zoomIn()`, `zoomOut()`, `resetZoom()`
   - Estilos CSS para zoom y controles

---

## 🚀 Próximas Mejoras

### Para Candidatos
1. Cargar candidatos reales desde la base de datos
2. API `/api/candidatos/por-tipo/{tipo}`
3. Fotos de candidatos
4. Números de lista

### Para Zoom
1. Zoom con rueda del mouse
2. Pan (arrastrar) cuando hay zoom
3. Zoom en área específica (selección)
4. Modo pantalla completa

---

**Implementado por:** Kiro AI  
**Fecha:** 7 de noviembre de 2025  
**Estado:** ✅ COMPLETADO Y FUNCIONANDO

**Prueba ahora:**
1. Ir a http://127.0.0.1:5000/dashboard/testigo_mesa
2. Cambiar tipo de elección → Ver candidatos cambiar
3. Capturar foto → Probar controles de zoom
