# Datos Cargados en el Sistema Electoral de Caquetá

## Resumen de Inicialización Completada

El sistema de recolección inicial de votaciones para el departamento de Caquetá ha sido inicializado exitosamente con todos los datos necesarios para su operación.

## 📊 Estadísticas Generales

- **Total ubicaciones**: 167
- **Total mesas electorales**: 148
- **Total votantes habilitados**: 237,524
- **Total tipos de elección**: 5
- **Total jornadas electorales**: 3
- **Total procesos electorales**: 3
- **Total usuarios**: 4

## 🗺️ Estructura Geográfica

### Departamento
- **Caquetá** (Código: 44)

### Municipios (16 total)
1. **FLORENCIA** - 51 puestos, 32 mesas
2. **ALBANIA** - 2 puestos, 3 mesas
3. **CARTAGENA DEL CHAIRA** - 7 puestos, 11 mesas
4. **BELEN DE LOS ANDAQUIES** - 3 puestos, 5 mesas
5. **EL DONCELLO** - 7 puestos, 10 mesas
6. **EL PAUJIL** - 3 puestos, 5 mesas
7. **LA MONTAÑITA** - 5 puestos, 6 mesas
8. **PUERTO RICO** - 9 puestos, 12 mesas
9. **SAN VICENTE DEL CAGUAN** - 25 puestos, 21 mesas
10. **CURILLO** - 3 puestos, 4 mesas
11. **MILAN** - 7 puestos, 7 mesas
12. **MORELIA** - 4 puestos, 4 mesas
13. **SAN JOSE DEL FRAGUA** - 6 puestos, 7 mesas
14. **SOLANO** - 12 puestos, 13 mesas
15. **SOLITA** - 2 puestos, 3 mesas
16. **VALPARAISO** - 4 puestos, 5 mesas

### Puestos Electorales
- **150 puestos** distribuidos en los 16 municipios
- Incluye instituciones educativas, centros comunitarios y sedes especiales
- Cada puesto tiene coordenadas GPS, dirección y información de contacto

### Mesas Electorales
- **148 mesas** distribuidas en los puestos
- Códigos únicos generados automáticamente
- Distribución equitativa de votantes por mesa
- Estado inicial: "pendiente"

## 🗳️ Tipos de Elecciones Configurados

### 1. Concejos de Juventudes (CJ)
- **Candidatos**: 3 listas + votos blancos/nulos
- **Configuración**: Elección de listas cerradas
- **Validación**: Suma de votos debe coincidir

### 2. Senado de la República (SEN)
- **Candidatos**: Partidos políticos principales
- **Configuración**: Sistema de representación proporcional
- **Validación**: Control de votos por partido

### 3. Cámara de Representantes (CAM)
- **Candidatos**: 4 candidatos individuales + votos blancos/nulos
- **Configuración**: Elección uninominal
- **Validación**: Un voto por candidato

### 4. Gobernación de Caquetá (GOB)
- **Candidatos**: 3 candidatos + votos blancos/nulos
- **Configuración**: Elección directa
- **Validación**: Mayoría simple

### 5. Asamblea Departamental (ASA)
- **Candidatos**: 4 listas + votos blancos/nulos
- **Configuración**: Sistema de listas
- **Validación**: Distribución proporcional

## 📅 Jornadas Electorales

### 1. Concejos de Juventudes 2024
- **Fecha**: 5 de diciembre de 2025
- **Estado**: Activa
- **Descripción**: Elección de Concejos Municipales de Juventudes

### 2. Elecciones Territoriales 2027
- **Fecha**: 3 de febrero de 2026
- **Estado**: Programada
- **Descripción**: Gobernadores, Alcaldes, Diputados, Concejales y Ediles

### 3. Elecciones Congreso 2026
- **Fecha**: 3 de junio de 2026
- **Estado**: En configuración
- **Descripción**: Senado y Cámara de Representantes

## ⚙️ Procesos Electorales Activos

### 1. Concejos de Juventudes - Caquetá 2024
- **Estado**: Activo
- **Período**: 5 nov 2025 - 20 dic 2025
- **Configuración**: 
  - Captura múltiple: No
  - Validación manual: Sí
  - Tiempo límite: 1 hora

### 2. Gobernación Caquetá - Territoriales 2027
- **Estado**: En configuración
- **Período**: 5 dic 2025 - 3 feb 2026
- **Configuración**:
  - Captura múltiple: Sí
  - Validación manual: Sí
  - Tiempo límite: 2 horas

### 3. Asamblea Departamental - Territoriales 2027
- **Estado**: En configuración
- **Período**: 5 dic 2025 - 3 feb 2026
- **Configuración**:
  - Captura múltiple: Sí
  - Validación manual: Sí
  - Tiempo límite: 2 horas

## 👥 Usuarios del Sistema

### 1. Administrador del Sistema
- **Usuario**: admin
- **Rol**: Administrador
- **Acceso**: Completo al sistema

### 2. Coordinador Municipal Florencia
- **Usuario**: coord_florencia
- **Rol**: Coordinador Municipal
- **Municipio**: Florencia
- **Acceso**: Gestión municipal

### 3. Testigo Electoral 001
- **Usuario**: testigo001
- **Rol**: Testigo
- **Municipio**: Florencia
- **Acceso**: Captura de datos

### 4. Testigo Electoral 002
- **Usuario**: testigo002
- **Rol**: Testigo
- **Municipio**: Albania
- **Acceso**: Captura de datos

## 🔧 Configuraciones Técnicas

### Base de Datos
- **Tipo**: SQLite
- **Archivo**: `caqueta_electoral.db`
- **Esquema**: Completamente inicializado
- **Integridad**: Validada exitosamente

### Códigos de Mesa
- **Formato**: `44[municipio][zona][puesto][mesa]`
- **Ejemplo**: `441.00101` (Caquetá, Florencia, zona 1, puesto 1, mesa 1)
- **Únicos**: Sí, generados automáticamente

### Coordenadas GPS
- **Cobertura**: Mayoría de puestos tienen coordenadas
- **Formato**: Decimal (latitud, longitud)
- **Uso**: Geolocalización y mapas

## ✅ Estado del Sistema

El sistema está **completamente operativo** y listo para:

1. **Captura de imágenes** de formularios E-14
2. **Procesamiento OCR** de datos electorales
3. **Validación manual** de resultados
4. **Consolidación** de votaciones
5. **Generación de reportes** en tiempo real

## 📋 Próximos Pasos

1. Configurar usuarios adicionales según necesidades
2. Asignar testigos a mesas específicas
3. Configurar procesos de captura
4. Realizar pruebas del sistema
5. Capacitar usuarios finales

---

**Fecha de inicialización**: 5 de noviembre de 2025  
**Sistema**: Recolección Inicial de Votaciones - Caquetá  
**Estado**: ✅ Operativo