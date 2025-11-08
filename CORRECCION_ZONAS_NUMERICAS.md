# Corrección de Zonas a Formato Numérico

## 📅 Fecha: 7 de noviembre de 2025

## 🎯 Objetivo
Corregir la nomenclatura de zonas en la base de datos de nombres descriptivos (Urbana, Rural, Cárceles, Censo) a formato numérico estándar (Zona 01, Zona 02, Zona 03, etc.).

## ❌ Problema Identificado

### Antes (Incorrecto):
```
- Zona Urbana Florencia
- Zona Rural Florencia
- Cárceles Florencia
- Puesto Censo Florencia
```

### Después (Correcto):
```
- Zona 01 (Descripción: Zona Urbana)
- Zona 02 (Descripción: Zona Rural)
- Zona 03 (Descripción: Cárceles)
- Zona 04 (Descripción: Puesto de Censo)
```

## ✅ Cambios Realizados

### 1. Base de Datos

**Script**: `fix_zonas_numericas.py`

**Cambios en tabla `zonas`**:
- `codigo_zz`: Actualizado a formato numérico (01, 02, 03, etc.)
- `nombre`: Cambiado a "Zona XX" donde XX es el número
- `descripcion`: Mantiene el tipo original (Zona Urbana, Zona Rural, Cárceles, Puesto de Censo)
- `tipo_zona`: Se mantiene sin cambios (urbana, rural, carcel, censo)

**Ejemplo de actualización**:
```sql
-- Antes
codigo_zz: '01'
nombre: 'Zona Urbana Florencia'
descripcion: NULL
tipo_zona: 'urbana'

-- Después
codigo_zz: '01'
nombre: 'Zona 01'
descripcion: 'Zona Urbana'
tipo_zona: 'urbana'
```

### 2. Dashboard Testigo

**Archivo**: `templates/roles/testigo_mesa/dashboard.html`

**Cambio**:
```html
<!-- Antes -->
<input type="text" class="form-control" id="zona" value="Urbana" readonly>

<!-- Después -->
<input type="text" class="form-control" id="zona" value="Zona 01" readonly>
```

## 📊 Resultados por Municipio

### Florencia (4 zonas)
- Zona 01 - Zona Urbana
- Zona 02 - Zona Rural
- Zona 03 - Cárceles
- Zona 04 - Puesto de Censo

### San Vicente del Caguán (3 zonas)
- Zona 01 - Zona Rural
- Zona 02 - Cárceles
- Zona 03 - Puesto de Censo

### Puerto Rico (3 zonas)
- Zona 01 - Zona Rural
- Zona 02 - Cárceles
- Zona 03 - Puesto de Censo

### El Paujil (3 zonas)
- Zona 01 - Zona Rural
- Zona 02 - Cárceles
- Zona 03 - Puesto de Censo

### La Montañita (3 zonas)
- Zona 01 - Zona Rural
- Zona 02 - Cárceles
- Zona 03 - Puesto de Censo

### Curillo (3 zonas)
- Zona 01 - Zona Rural
- Zona 02 - Cárceles
- Zona 03 - Puesto de Censo

**Total**: 19 zonas actualizadas en 6 municipios

## 🔧 Estructura de Datos

### Tabla `zonas`
```sql
CREATE TABLE zonas (
    id INTEGER PRIMARY KEY,
    codigo_zz TEXT NOT NULL,           -- '01', '02', '03', etc.
    nombre TEXT NOT NULL,               -- 'Zona 01', 'Zona 02', etc.
    municipio_id INTEGER NOT NULL,
    codigo_completo TEXT,               -- Código DIVIPOLA completo
    descripcion TEXT,                   -- 'Zona Urbana', 'Zona Rural', etc.
    tipo_zona TEXT,                     -- 'urbana', 'rural', 'carcel', 'censo'
    activo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📝 Convención de Numeración

### Regla General:
Cada municipio tiene sus propias zonas numeradas secuencialmente desde 01.

### Orden de Numeración:
1. **Zona Urbana** (si existe) → Zona 01
2. **Zona Rural** → Siguiente número disponible
3. **Cárceles** → Siguiente número disponible
4. **Puesto de Censo** → Siguiente número disponible

### Ejemplos:

**Municipio con zona urbana** (Florencia):
```
Zona 01 → Zona Urbana
Zona 02 → Zona Rural
Zona 03 → Cárceles
Zona 04 → Puesto de Censo
```

**Municipio sin zona urbana** (San Vicente del Caguán):
```
Zona 01 → Zona Rural
Zona 02 → Cárceles
Zona 03 → Puesto de Censo
```

## 🔍 Verificación

### Consulta SQL para verificar:
```sql
SELECT 
    z.id,
    z.codigo_zz,
    z.nombre,
    z.descripcion,
    z.tipo_zona,
    m.nombre as municipio
FROM zonas z
JOIN municipios m ON z.municipio_id = m.id
ORDER BY m.nombre, z.codigo_zz;
```

### Script de verificación:
```bash
python check_zonas.py
```

## 🚀 Impacto en el Sistema

### Componentes Afectados:
1. ✅ **Base de datos** - Tabla `zonas` actualizada
2. ✅ **Dashboard Testigo** - Campo zona actualizado
3. ⏳ **APIs** - Deben retornar zona en formato numérico
4. ⏳ **Reportes** - Deben mostrar zona en formato numérico
5. ⏳ **Formularios** - Deben usar zona en formato numérico

### Componentes NO Afectados:
- Tabla `municipios` - Sin cambios
- Tabla `puestos_votacion` - Sin cambios
- Tabla `mesas_votacion` - Sin cambios
- Usuarios y roles - Sin cambios

## 📋 Tareas Pendientes

### Corto Plazo:
- [ ] Actualizar APIs para retornar zona en formato numérico
- [ ] Actualizar formularios de creación/edición de zonas
- [ ] Actualizar reportes que muestran zonas
- [ ] Verificar que todos los dashboards usen el formato correcto

### Mediano Plazo:
- [ ] Agregar validación en frontend para formato de zona
- [ ] Documentar convención de zonas en manual de usuario
- [ ] Crear interfaz de administración para gestionar zonas

## 🔒 Consideraciones

### Migración de Datos:
- ✅ Los datos existentes fueron migrados automáticamente
- ✅ Se mantiene la información original en el campo `descripcion`
- ✅ El campo `tipo_zona` se mantiene para filtros y consultas

### Retrocompatibilidad:
- El campo `descripcion` mantiene el nombre original
- El campo `tipo_zona` permite filtrar por tipo
- Las relaciones con otras tablas se mantienen intactas

### Validación:
- Cada zona debe tener un código único dentro de su municipio
- El formato debe ser siempre "Zona XX" donde XX es 01-99
- La descripción es opcional pero recomendada

## 📞 Archivos Relacionados

- **Script de corrección**: `fix_zonas_numericas.py`
- **Script de verificación**: `check_zonas.py`
- **Dashboard actualizado**: `templates/roles/testigo_mesa/dashboard.html`
- **Convención DIVIPOLA**: `CONVENCION_ZONAS_DIVIPOLA.md`
- **Estructura DIVIPOLA**: `ESTRUCTURA_DIVIPOLA_IMPLEMENTADA.md`

---

**Estado**: ✅ Completado  
**Zonas Actualizadas**: 19 zonas en 6 municipios  
**Última Actualización**: 7 de noviembre de 2025
