# Estructura DIVIPOLA Implementada

## Fecha: 7 de noviembre de 2025

## ✅ Implementación Completada

Se ha implementado exitosamente la estructura jerárquica DIVIPOLA en la base de datos del sistema electoral.

## 📋 ¿Qué es DIVIPOLA?

DIVIPOLA (División Político-Administrativa de Colombia) es el sistema de codificación geográfica oficial de Colombia que utiliza una estructura jerárquica de códigos:

### Estructura del Código DIVIPOLA

```
dd mm zz pp
│  │  │  └─ pp: Puesto (2 dígitos)
│  │  └──── zz: Zona (2 dígitos)
│  └─────── mm: Municipio (3 dígitos)
└────────── dd: Departamento (2 dígitos)
```

### Ejemplo para Caquetá:
- **dd**: 18 (Caquetá)
- **mm**: 001 (Florencia), 029 (San Vicente del Caguán), etc.
- **zz**: Según convención oficial:
  - **01-89**: Zonas urbanas numeradas secuencialmente
  - **90**: Puesto censo
  - **98**: Cárceles
  - **99**: Zona rural
- **pp**: 01, 02, 03... (Puestos dentro de cada zona)

**Código completo**: `18001 01 01` = Puesto 01 de la Zona Urbana 01 de Florencia, Caquetá

## 🗄️ Estructura de Base de Datos

### 1. Tabla: municipios

**Columnas agregadas**:
- `codigo_dd` (TEXT): Código del departamento (18 para Caquetá)
- `codigo_mm` (TEXT): Código del municipio (001, 029, etc.)

**Ejemplo**:
```sql
id | codigo | nombre    | codigo_dd | codigo_mm
1  | 18001  | Florencia | 18        | 001
2  | 18029  | San Vicente del Caguán | 18 | 029
```

### 2. Tabla: zonas (NUEVA)

**Estructura completa**:
```sql
CREATE TABLE zonas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_zz TEXT NOT NULL,
    nombre TEXT NOT NULL,
    municipio_id INTEGER NOT NULL,
    codigo_completo TEXT,
    descripcion TEXT,
    activo INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id),
    UNIQUE(municipio_id, codigo_zz)
)
```

**Ejemplo**:
```sql
id | codigo_zz | nombre              | municipio_id | codigo_completo
1  | 01        | Zona Urbana Florencia | 1          | 1800101
```

### 3. Tabla: puestos_votacion

**Columnas agregadas**:
- `zona_id` (INTEGER): Referencia a la zona
- `codigo_pp` (TEXT): Código del puesto (01, 02, etc.)
- `codigo_divipola` (TEXT): Código completo ddmmzzpp

**Ejemplo**:
```sql
id | nombre           | zona_id | codigo_pp | codigo_divipola
1  | Escuela Central  | 1       | 01        | 180010101
2  | Colegio San José | 1       | 02        | 180010102
```

### 4. Tabla: mesas_votacion

**Sin cambios**: Las mesas ya están correctamente vinculadas a puestos.

## 🔗 Relaciones Jerárquicas

```
Departamento (Caquetá - dd:18)
    └── Municipio (Florencia - mm:001)
            └── Zona (Urbana - zz:01)
                    └── Puesto (Escuela Central - pp:01)
                            └── Mesa (001-A, 001-B, etc.)
```

## 📊 Datos Actuales

### Municipios del Caquetá (dd: 18)
| Código | mm  | Nombre |
|--------|-----|--------|
| 18001  | 001 | Florencia |
| 18029  | 029 | San Vicente del Caguán |
| 18205  | 205 | Curillo |
| 18410  | 410 | La Montañita |
| 18479  | 479 | El Paujil |
| 18592  | 592 | Puerto Rico |

### Zonas Creadas (Convención Oficial)

**Florencia (18001)**:
| Código | Tipo | Zona | Código Completo |
|--------|------|------|-----------------|
| 01 | Urbana | Zona Urbana Florencia | 1800101 |
| 90 | Censo | Puesto Censo Florencia | 1800190 |
| 98 | Cárcel | Cárceles Florencia | 1800198 |
| 99 | Rural | Zona Rural Florencia | 1800199 |

**Convención DIVIPOLA para códigos zz**:
- **01-89**: Zonas urbanas (numeradas secuencialmente)
- **90**: Puesto censo
- **98**: Establecimientos carcelarios
- **99**: Zona rural

### Puestos con Códigos DIVIPOLA
| Código DIVIPOLA | dd | mm  | zz | pp | Puesto | Municipio |
|-----------------|----|----|----|----|--------|-----------|
| 180010101 | 18 | 001 | 01 | 01 | Escuela Central | Florencia |
| 180010102 | 18 | 001 | 01 | 02 | Colegio San José | Florencia |
| 180010103 | 18 | 001 | 01 | 03 | Universidad de la Amazonia | Florencia |

## 🔧 APIs Actualizadas

### 1. GET /api/ubicacion/municipios

**Response**:
```json
{
  "success": true,
  "municipios": [
    {
      "id": 1,
      "codigo": "18001",
      "codigo_dd": "18",
      "codigo_mm": "001",
      "nombre": "Florencia",
      "departamento": "Caquetá"
    }
  ]
}
```

### 2. GET /api/ubicacion/zonas/{municipio_id} (NUEVA)

**Response**:
```json
{
  "success": true,
  "zonas": [
    {
      "id": 1,
      "codigo_zz": "01",
      "nombre": "Zona Urbana Florencia",
      "codigo_completo": "1800101"
    }
  ]
}
```

### 3. GET /api/ubicacion/puestos/{municipio_id}

**Response actualizado**:
```json
{
  "success": true,
  "puestos": [
    {
      "id": 1,
      "nombre": "Escuela Central",
      "direccion": "Carrera 11 # 15-20",
      "codigo": "PV001",
      "codigo_divipola": "180010101",
      "codigo_pp": "01",
      "codigo_zz": "01",
      "zona_nombre": "Zona Urbana Florencia"
    }
  ]
}
```

### 4. GET /api/ubicacion/mesas/{puesto_id}

**Sin cambios**: Funciona igual que antes.

## 📝 Scripts Creados

### 1. add_divipola_structure.py
Script principal que:
- Agrega columnas DIVIPOLA a municipios
- Crea tabla de zonas
- Agrega columnas DIVIPOLA a puestos
- Genera códigos DIVIPOLA automáticamente
- Crea backup automático

### 2. check_divipola_structure.py
Script de verificación que muestra:
- Estructura actual de códigos
- Análisis de formato DIVIPOLA
- Listado de municipios, zonas y puestos

## 🎯 Beneficios de la Implementación

### 1. Estandarización
- ✅ Códigos oficiales de Colombia
- ✅ Compatibilidad con sistemas nacionales
- ✅ Facilita integración con Registraduría

### 2. Jerarquía Clara
- ✅ Estructura de 4 niveles bien definida
- ✅ Relaciones explícitas entre entidades
- ✅ Fácil navegación geográfica

### 3. Escalabilidad
- ✅ Fácil agregar nuevas zonas
- ✅ Fácil agregar nuevos puestos
- ✅ Códigos únicos garantizados

### 4. Trazabilidad
- ✅ Cada puesto tiene código único
- ✅ Fácil identificación geográfica
- ✅ Auditoría mejorada

## 🔍 Casos de Uso

### Caso 1: Agregar Nueva Zona

```sql
INSERT INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo)
VALUES ('02', 'Zona Rural Florencia', 1, '1800102');
```

### Caso 2: Agregar Nuevo Puesto

```sql
INSERT INTO puestos_votacion (
    nombre, direccion, municipio_id, zona_id, 
    codigo_pp, codigo_divipola
)
VALUES (
    'Escuela Rural El Caraño', 
    'Vereda El Caraño',
    1,  -- Florencia
    2,  -- Zona Rural
    '01',
    '180010201'  -- dd:18 mm:001 zz:02 pp:01
);
```

### Caso 3: Consultar Jerarquía Completa

```sql
SELECT 
    m.codigo_dd || m.codigo_mm || z.codigo_zz || p.codigo_pp as codigo_completo,
    m.nombre as municipio,
    z.nombre as zona,
    p.nombre as puesto
FROM puestos_votacion p
JOIN zonas z ON p.zona_id = z.id
JOIN municipios m ON z.municipio_id = m.id
WHERE m.id = 1
ORDER BY codigo_completo;
```

## 📈 Estadísticas

### Antes de la Implementación
- ❌ Códigos no estandarizados (PV001, PV002)
- ❌ Sin estructura de zonas
- ❌ Sin códigos DIVIPOLA completos

### Después de la Implementación
- ✅ Códigos DIVIPOLA completos (180010101)
- ✅ Tabla de zonas implementada
- ✅ Jerarquía de 4 niveles
- ✅ 1 zona creada
- ✅ 3 puestos con códigos DIVIPOLA

## 🚀 Próximos Pasos

### Corto Plazo
1. **Agregar más zonas**
   - Zona Rural para cada municipio
   - Zonas específicas según necesidad

2. **Importar datos DIVIPOLA completos**
   - Cargar desde divipola_corregido.csv
   - Validar códigos con Registraduría

3. **Actualizar interfaces**
   - Mostrar códigos DIVIPOLA en dashboards
   - Agregar filtros por zona

### Mediano Plazo
1. **Integración con Registraduría**
   - Validar códigos contra base oficial
   - Sincronizar actualizaciones

2. **Reportes por Zona**
   - Estadísticas por zona
   - Mapas de cobertura

3. **Auditoría Mejorada**
   - Logs con códigos DIVIPOLA
   - Trazabilidad completa

## 🔒 Integridad de Datos

### Validaciones Implementadas
- ✅ UNIQUE constraint en (municipio_id, codigo_zz)
- ✅ Foreign keys en todas las relaciones
- ✅ Índices en columnas de búsqueda

### Reglas de Negocio
- Cada municipio puede tener múltiples zonas
- Cada zona pertenece a un solo municipio
- Cada puesto pertenece a una sola zona
- Los códigos pp son secuenciales dentro de cada zona

## 📚 Documentación Relacionada

### Archivos Actualizados
1. **api/auth_api.py** - APIs con códigos DIVIPOLA
2. **ANALISIS_BD_BUENAS_PRACTICAS.md** - Análisis de BD
3. **SISTEMA_REGISTRO_AUTOMATICO.md** - Sistema de registro

### Archivos Nuevos
1. **add_divipola_structure.py** - Script de implementación
2. **check_divipola_structure.py** - Script de verificación
3. **ESTRUCTURA_DIVIPOLA_IMPLEMENTADA.md** - Este documento

## ✅ Verificación del Sistema

### Tests Ejecutados
```bash
python test_registro_sistema.py
```

**Resultado**: ✅ Todos los tests pasando

### APIs Verificadas
- ✅ GET /api/ubicacion/municipios
- ✅ GET /api/ubicacion/zonas/{municipio_id}
- ✅ GET /api/ubicacion/puestos/{municipio_id}
- ✅ GET /api/ubicacion/mesas/{puesto_id}
- ✅ POST /api/auth/register

## 🎓 Referencias

### DIVIPOLA Oficial
- **Fuente**: DANE (Departamento Administrativo Nacional de Estadística)
- **Formato**: dd (2) + mm (3) + zz (2) + pp (2) = 9 dígitos
- **Actualización**: Periódica según cambios administrativos

### Caquetá (dd: 18)
- **Municipios**: 16 municipios
- **Implementados**: 6 municipios
- **Pendientes**: 10 municipios

## 📞 Soporte

Para consultas sobre la estructura DIVIPOLA:
- Revisar este documento
- Ejecutar `python check_divipola_structure.py`
- Consultar backup: `caqueta_electoral_backup_20251107_095514.db`

---

**Última actualización**: 7 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Implementado y operativo  
**Backup**: caqueta_electoral_backup_20251107_095514.db
