# Convención de Zonas DIVIPOLA

## Fecha: 7 de noviembre de 2025

## 📋 Convención Oficial para Códigos de Zona (zz)

Según la estructura DIVIPOLA oficial de Colombia, los códigos de zona (zz) siguen esta convención:

### Rangos de Códigos

| Rango | Tipo | Descripción | Uso |
|-------|------|-------------|-----|
| **01-89** | Urbana | Zonas urbanas numeradas secuencialmente | Áreas urbanas del municipio |
| **90** | Censo | Puesto censo | Puestos especiales para censo |
| **98** | Cárcel | Establecimientos carcelarios | Centros penitenciarios |
| **99** | Rural | Zona rural | Área rural del municipio |

## 🗄️ Implementación en Base de Datos

### Tabla: zonas

**Columnas**:
- `id`: INTEGER PRIMARY KEY
- `codigo_zz`: TEXT (01-99)
- `nombre`: TEXT
- `municipio_id`: INTEGER
- `codigo_completo`: TEXT (ddmmzz)
- `tipo_zona`: TEXT (urbana, censo, carcel, rural)
- `descripcion`: TEXT
- `activo`: INTEGER
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Tabla: tipos_zona (Referencia)

Tabla de referencia que documenta la convención oficial:

```sql
CREATE TABLE tipos_zona (
    codigo_zz TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    rango_inicio INTEGER,
    rango_fin INTEGER
)
```

**Datos**:
| codigo_zz | tipo | descripcion | rango_inicio | rango_fin |
|-----------|------|-------------|--------------|-----------|
| 01-89 | urbana | Zonas urbanas numeradas secuencialmente | 1 | 89 |
| 90 | censo | Puesto censo | 90 | 90 |
| 98 | carcel | Establecimientos carcelarios | 98 | 98 |
| 99 | rural | Zona rural | 99 | 99 |

## 📊 Zonas Creadas por Municipio

### Florencia (18001)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 01 | urbana | Zona Urbana Florencia | 1800101 |
| 90 | censo | Puesto Censo Florencia | 1800190 |
| 98 | carcel | Cárceles Florencia | 1800198 |
| 99 | rural | Zona Rural Florencia | 1800199 |

### San Vicente del Caguán (18029)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 90 | censo | Puesto Censo San Vicente del Caguán | 1802990 |
| 98 | carcel | Cárceles San Vicente del Caguán | 1802998 |
| 99 | rural | Zona Rural San Vicente del Caguán | 1802999 |

### Puerto Rico (18592)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 90 | censo | Puesto Censo Puerto Rico | 1859290 |
| 98 | carcel | Cárceles Puerto Rico | 1859298 |
| 99 | rural | Zona Rural Puerto Rico | 1859299 |

### El Paujil (18479)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 90 | censo | Puesto Censo El Paujil | 1847990 |
| 98 | carcel | Cárceles El Paujil | 1847998 |
| 99 | rural | Zona Rural El Paujil | 1847999 |

### La Montañita (18410)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 90 | censo | Puesto Censo La Montañita | 1841090 |
| 98 | carcel | Cárceles La Montañita | 1841098 |
| 99 | rural | Zona Rural La Montañita | 1841099 |

### Curillo (18205)
| zz | Tipo | Nombre | Código Completo |
|----|------|--------|-----------------|
| 90 | censo | Puesto Censo Curillo | 1820590 |
| 98 | carcel | Cárceles Curillo | 1820598 |
| 99 | rural | Zona Rural Curillo | 1820599 |

## 🎯 Casos de Uso

### Caso 1: Agregar Zona Urbana Adicional

Para municipios con múltiples zonas urbanas:

```sql
INSERT INTO zonas (codigo_zz, nombre, municipio_id, codigo_completo, tipo_zona)
VALUES ('02', 'Zona Urbana 2 Florencia', 1, '1800102', 'urbana');
```

### Caso 2: Agregar Puesto en Zona Rural

```sql
-- Primero obtener la zona rural
SELECT id FROM zonas WHERE municipio_id = 1 AND codigo_zz = '99';

-- Luego crear el puesto
INSERT INTO puestos_votacion (
    nombre, direccion, municipio_id, zona_id,
    codigo_pp, codigo_divipola
)
VALUES (
    'Escuela Rural Vereda El Caraño',
    'Vereda El Caraño',
    1,  -- Florencia
    (SELECT id FROM zonas WHERE municipio_id = 1 AND codigo_zz = '99'),
    '01',
    '180019901'  -- dd:18 mm:001 zz:99 pp:01
);
```

### Caso 3: Agregar Puesto en Cárcel

```sql
INSERT INTO puestos_votacion (
    nombre, direccion, municipio_id, zona_id,
    codigo_pp, codigo_divipola
)
VALUES (
    'Centro Penitenciario Florencia',
    'Km 5 Vía Neiva',
    1,  -- Florencia
    (SELECT id FROM zonas WHERE municipio_id = 1 AND codigo_zz = '98'),
    '01',
    '180019801'  -- dd:18 mm:001 zz:98 pp:01
);
```

### Caso 4: Agregar Puesto Censo

```sql
INSERT INTO puestos_votacion (
    nombre, direccion, municipio_id, zona_id,
    codigo_pp, codigo_divipola
)
VALUES (
    'Puesto Censo Central',
    'Plaza Principal',
    1,  -- Florencia
    (SELECT id FROM zonas WHERE municipio_id = 1 AND codigo_zz = '90'),
    '01',
    '180019001'  -- dd:18 mm:001 zz:90 pp:01
);
```

## 🔍 Consultas Útiles

### Listar todas las zonas por tipo

```sql
SELECT 
    m.nombre as municipio,
    z.codigo_zz,
    z.tipo_zona,
    z.nombre,
    z.codigo_completo
FROM zonas z
JOIN municipios m ON z.municipio_id = m.id
ORDER BY m.nombre, z.codigo_zz;
```

### Contar puestos por tipo de zona

```sql
SELECT 
    z.tipo_zona,
    COUNT(p.id) as total_puestos
FROM zonas z
LEFT JOIN puestos_votacion p ON z.id = p.zona_id
GROUP BY z.tipo_zona;
```

### Validar códigos de zona

```sql
SELECT 
    z.codigo_zz,
    z.tipo_zona,
    CASE 
        WHEN CAST(z.codigo_zz AS INTEGER) BETWEEN 1 AND 89 THEN 'urbana'
        WHEN z.codigo_zz = '90' THEN 'censo'
        WHEN z.codigo_zz = '98' THEN 'carcel'
        WHEN z.codigo_zz = '99' THEN 'rural'
        ELSE 'invalido'
    END as tipo_esperado
FROM zonas z
WHERE z.tipo_zona != CASE 
    WHEN CAST(z.codigo_zz AS INTEGER) BETWEEN 1 AND 89 THEN 'urbana'
    WHEN z.codigo_zz = '90' THEN 'censo'
    WHEN z.codigo_zz = '98' THEN 'carcel'
    WHEN z.codigo_zz = '99' THEN 'rural'
END;
```

## 📈 Estadísticas

### Zonas Totales: 19

**Por Tipo**:
- Urbanas (01-89): 1 zona
- Censo (90): 6 zonas (una por municipio)
- Cárceles (98): 6 zonas (una por municipio)
- Rural (99): 6 zonas (una por municipio)

**Por Municipio**:
- Florencia: 4 zonas (01, 90, 98, 99)
- Otros municipios: 3 zonas cada uno (90, 98, 99)

## 🔒 Validaciones

### Reglas de Negocio

1. **Códigos 01-89**: Solo para zonas urbanas
2. **Código 90**: Solo para puestos censo
3. **Código 98**: Solo para cárceles
4. **Código 99**: Solo para zona rural
5. **Unicidad**: Un municipio no puede tener dos zonas con el mismo código_zz

### Constraints en Base de Datos

```sql
-- Ya implementado en la tabla zonas
UNIQUE(municipio_id, codigo_zz)
```

## 📚 Referencias

### Fuente Oficial
- **DANE**: Departamento Administrativo Nacional de Estadística
- **Registraduría Nacional del Estado Civil**
- **Convención DIVIPOLA**: Estándar nacional de Colombia

### Documentos Relacionados
- ESTRUCTURA_DIVIPOLA_IMPLEMENTADA.md
- ANALISIS_BD_BUENAS_PRACTICAS.md
- SISTEMA_REGISTRO_AUTOMATICO.md

## 🚀 Próximos Pasos

### Corto Plazo
1. Agregar más zonas urbanas según necesidad (02, 03, etc.)
2. Asignar puestos existentes a zonas apropiadas
3. Crear puestos en zonas especiales (censo, cárceles, rural)

### Mediano Plazo
1. Importar datos completos desde divipola_corregido.csv
2. Validar con datos oficiales de la Registraduría
3. Implementar reportes por tipo de zona

## ✅ Scripts Disponibles

1. **update_zonas_convention.py** - Actualiza zonas según convención
2. **test_zonas_convention.py** - Prueba las zonas creadas
3. **check_divipola_structure.py** - Verifica estructura completa

## 📞 Soporte

Para consultas sobre la convención de zonas:
- Revisar este documento
- Ejecutar `python test_zonas_convention.py`
- Consultar tabla `tipos_zona` en la base de datos

---

**Última actualización**: 7 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Implementado según convención oficial  
**Backup**: caqueta_electoral_backup_20251107_100358.db
