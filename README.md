# Sistema de Recolección Inicial de Votaciones - Caquetá

## Descripción

Sistema electoral especializado para la recolección inicial de información de votaciones en el departamento de Caquetá, Colombia. Este sistema permite la captura, validación y consolidación de datos electorales desde las mesas de votación hasta los niveles de consolidación municipal y departamental.

## Estado Actual: ✅ Tarea 1 Completada

### ✅ Configuración Inicial y Base de Datos DIVIPOLA

**Implementado:**
- ✅ Base de datos SQLite con estructura completa para Caquetá
- ✅ Modelos de datos optimizados para el proceso electoral
- ✅ Carga automática de datos DIVIPOLA específicos de Caquetá
- ✅ Validación de integridad geográfica
- ✅ Coordenadas GPS para todos los puestos electorales

**Estadísticas de la Base de Datos:**
- **Departamento:** 1 (Caquetá)
- **Municipios:** 16
- **Puestos electorales:** 150
- **Mesas electorales:** 144
- **Total votantes habilitados:** 225,368
- **Cobertura GPS:** 100% de los puestos

**Municipios incluidos:**
1. Florencia (capital) - 51 puestos, 28 mesas
2. San Vicente del Caguán - 25 puestos, 21 mesas
3. Solano - 12 puestos, 13 mesas
4. Puerto Rico - 9 puestos, 12 mesas
5. Cartagena del Chairá - 7 puestos, 11 mesas
6. El Doncello - 7 puestos, 10 mesas
7. Milán - 7 puestos, 7 mesas
8. San José del Fragua - 6 puestos, 7 mesas
9. La Montañita - 5 puestos, 6 mesas
10. Morelia - 4 puestos, 4 mesas
11. Valparaíso - 4 puestos, 5 mesas
12. Belén de los Andaquíes - 3 puestos, 5 mesas
13. Curillo - 3 puestos, 4 mesas
14. El Paujil - 3 puestos, 5 mesas
15. Albania - 2 puestos, 3 mesas
16. Solita - 2 puestos, 3 mesas

## Archivos Implementados

### Modelos de Datos
- **`models.py`** - Modelos SQLAlchemy para toda la estructura electoral
  - `Location` - Ubicaciones geográficas (departamento, municipios, puestos)
  - `MesaElectoral` - Mesas electorales con datos de votantes
  - `User` - Usuarios del sistema (testigos, coordinadores, administradores)
  - `ElectionType` - Tipos de elecciones
  - `ElectoralJourney` - Jornadas electorales
  - `ElectoralProcess` - Procesos electorales específicos

### Servicios
- **`initialization_service.py`** - Servicio de inicialización y carga de datos
  - Carga automática de datos DIVIPOLA
  - Creación de estructura jerárquica
  - Validación de integridad geográfica
  - Generación de reportes de inicialización

### Configuración
- **`config.py`** - Configuración específica para Caquetá
- **`requirements.txt`** - Dependencias del proyecto

### Utilidades
- **`query_database.py`** - Script para consultar y verificar la base de datos
- **`muestra_mesas_caqueta.json`** - Muestra de datos exportados

## Estructura de la Base de Datos

```
caqueta_electoral.db (SQLite)
├── locations (Ubicaciones geográficas)
│   ├── Departamento: Caquetá
│   ├── 16 Municipios
│   └── 150 Puestos electorales
├── mesas_electorales (144 mesas)
├── users (Sistema de usuarios)
├── election_types (Tipos de elecciones)
├── electoral_journeys (Jornadas electorales)
└── electoral_processes (Procesos específicos)
```

## Cómo Usar

### 1. Instalación de Dependencias
```bash
pip install SQLAlchemy==1.4.53
```

### 2. Inicializar la Base de Datos
```bash
python initialization_service.py
```

### 3. Consultar la Base de Datos
```bash
python query_database.py
```

### 4. Verificar Configuración
```bash
python config.py
```

## Características Técnicas

### Coordenadas GPS
- **100% de cobertura** - Todos los puestos tienen coordenadas GPS
- **Centro geográfico:** Florencia (1.6143, -75.6061)
- **Preparado para mapas interactivos** con OpenStreetMap

### Códigos de Mesa
- **Formato:** `{dept}{municipio}{puesto}{mesa}`
- **Ejemplo:** `181.00101` = Caquetá (18), Florencia (1), Puesto 01, Mesa 01

### Validaciones Implementadas
- ✅ Integridad de jerarquía geográfica
- ✅ Códigos DIVIPOLA válidos
- ✅ Coordenadas GPS completas
- ✅ Distribución equitativa de votantes por mesa

## Próximos Pasos

### Tarea 2: Gestión de Tipos de Elecciones
- Implementar modelos para múltiples elecciones simultáneas
- Crear plantillas E-14 dinámicas
- Configurar OCR específico por tipo de elección

### Tarea 3: Plantillas de Formularios E-14
- Crear plantillas para diferentes tipos de elecciones
- Configurar validaciones específicas
- Implementar generación dinámica de formularios

## Tecnologías Utilizadas

- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **ORM:** SQLAlchemy 1.4.53
- **Lenguaje:** Python 3.13
- **Datos:** DIVIPOLA oficial de Colombia

## Contacto y Soporte

Este sistema está diseñado específicamente para el departamento de Caquetá y sigue las especificaciones técnicas del Sistema de Recolección Inicial de Información de Votaciones.

---

**Estado:** ✅ Tarea 1 Completada - Base de datos inicializada y validada
**Siguiente:** Implementar gestión de tipos de elecciones y plantillas E-14