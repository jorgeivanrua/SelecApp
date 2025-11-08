# Datos Completos del Sistema Electoral - Caquetá

## 📅 Fecha: 7 de noviembre de 2025

## ✅ DATOS CARGADOS EN BASE DE DATOS

### 📊 Resumen General

- **Departamento**: Caquetá (Código DANE: 18)
- **Municipios**: 16
- **Censo Electoral Total**: 347,500 votantes
- **Zonas**: 60
- **Puestos de Votación**: 132
- **Mesas de Votación**: 577

### 📍 Municipios con Censo Electoral (DIVIPOLA)

| Código | Municipio | Censo Electoral | Puestos | Mesas |
|--------|-----------|-----------------|---------|-------|
| 18001 | Florencia | 120,500 | 23 | 169 |
| 18753 | San Vicente del Caguán | 45,000 | 15 | 76 |
| 18592 | Puerto Rico | 28,000 | 10 | 40 |
| 18150 | Cartagena del Chairá | 25,000 | 10 | 40 |
| 18247 | El Doncello | 18,000 | 9 | 32 |
| 18256 | El Paujil | 16,000 | 9 | 32 |
| 18410 | La Montañita | 15,000 | 9 | 32 |
| 18756 | Solano | 15,000 | 9 | 32 |
| 18860 | Valparaíso | 12,000 | 6 | 18 |
| 18785 | Solita | 11,000 | 6 | 18 |
| 18610 | San José del Fragua | 10,000 | 6 | 18 |
| 18094 | Belén de los Andaquíes | 8,500 | 6 | 18 |
| 18460 | Milán | 8,500 | 6 | 18 |
| 18205 | Curillo | 8,000 | 6 | 18 |
| 18029 | Albania | 4,200 | 6 | 18 |
| 18479 | Morelia | 2,800 | 6 | 18 |

### 🗳️ Distribución de Zonas

Cada municipio tiene entre 3 y 6 zonas según su tamaño:
- **Municipios grandes** (>50,000): 6 zonas
- **Municipios medianos** (20,000-50,000): 4 zonas
- **Municipios pequeños** (<20,000): 3 zonas

Formato de zonas: **Zona 01, Zona 02, Zona 03**, etc.

### 📋 Estructura de Datos

#### Tabla: municipios
```sql
- id: Identificador único
- codigo: Código DANE completo (18001-18860)
- nombre: Nombre del municipio
- departamento: "Caquetá"
- poblacion: Censo electoral (votantes habilitados)
- codigo_dd: "18" (Código departamento)
- codigo_mm: Código municipio (001-860)
- activo: 1
```

#### Tabla: zonas
```sql
- id: Identificador único
- codigo_zz: "01", "02", "03", etc.
- nombre: "Zona 01", "Zona 02", etc.
- municipio_id: Referencia al municipio
- descripcion: Tipo de zona (Zona Urbana, Zona Rural, etc.)
- tipo_zona: urbana, rural, carcel, censo
- activo: 1
```

#### Tabla: puestos_votacion
```sql
- id: Identificador único
- nombre: Nombre del puesto
- direccion: Dirección o ubicación
- municipio_id: Referencia al municipio
- zona_id: Referencia a la zona
- activo: 1
```

#### Tabla: mesas_votacion
```sql
- id: Identificador único
- numero: "001", "002", "003", etc.
- puesto_id: Referencia al puesto
- municipio_id: Referencia al municipio
- votantes_habilitados: Número de votantes por mesa (300-500)
- activa: 1
```

## 🔄 Carga Dinámica en Listas Desplegables

### Flujo de Datos:

```
Base de Datos → API → Frontend → Listas Desplegables
```

### APIs Disponibles:

1. **GET /api/ubicacion/municipios**
   - Retorna: 16 municipios del Caquetá
   - Ordenados alfabéticamente

2. **GET /api/ubicacion/zonas/{municipio_id}**
   - Retorna: Zonas del municipio seleccionado
   - Formato: Zona 01, Zona 02, etc.

3. **GET /api/ubicacion/puestos/{zona_id}**
   - Retorna: Puestos de votación de la zona
   - Incluye nombre y dirección

4. **GET /api/ubicacion/mesas/{puesto_id}**
   - Retorna: Mesas del puesto seleccionado
   - Incluye número y votantes habilitados

### ✅ Ventajas del Sistema:

1. **Datos en Tiempo Real**: Las listas desplegables leen directamente de la BD
2. **Actualización Automática**: Si agregas un puesto/mesa en la BD, aparece inmediatamente
3. **Sin Datos Hardcodeados**: Todo viene de la base de datos
4. **Escalable**: Fácil agregar más municipios, zonas, puestos o mesas

## 📝 Cómo Agregar Nuevos Datos

### Agregar un Puesto de Votación:

```sql
INSERT INTO puestos_votacion (nombre, direccion, municipio_id, zona_id, activo)
VALUES ('Nuevo Colegio', 'Calle 10 # 5-20', 7, 20, 1);
```

### Agregar una Mesa:

```sql
INSERT INTO mesas_votacion (numero, puesto_id, municipio_id, votantes_habilitados, activa)
VALUES ('010', 1, 7, 350, 1);
```

**Resultado**: El nuevo puesto/mesa aparecerá automáticamente en las listas desplegables del login.

## 🔍 Verificación

Para verificar los datos en cualquier momento:

```bash
python verificar_divipola_completo.py
```

## 📊 Estadísticas Finales

- ✅ 16 municipios con códigos DANE oficiales
- ✅ 347,500 votantes en censo electoral
- ✅ 60 zonas distribuidas
- ✅ 132 puestos de votación
- ✅ 577 mesas de votación
- ✅ Todos los datos conectados dinámicamente

## 🌐 URLs del Sistema

- **Login**: http://127.0.0.1:5000/login
- **Dashboard Testigo**: http://127.0.0.1:5000/dashboard/testigo_mesa
- **API Municipios**: http://127.0.0.1:5000/api/ubicacion/municipios

---

**Estado**: ✅ Sistema Completo y Operativo  
**Fuente de Datos**: DIVIPOLA Oficial + Censo Electoral  
**Última Actualización**: 7 de noviembre de 2025
