# 📋 Análisis de Brechas: HTML vs Requerimientos del Sistema

## 🎯 Requerimientos del Sistema Electoral

### Módulos Principales (6):
1. **Candidatos** - Gestión de candidatos y partidos
2. **Coordinación** - Coordinación municipal y testigos
3. **Administración** - Panel admin y gestión de usuarios
4. **Usuarios** - Autenticación JWT y perfiles
5. **Reportes** - Generación de reportes (CSV, JSON, Excel, PDF)
6. **Dashboard** - Widgets y estadísticas en tiempo real

### Funcionalidades Clave:
- 130 endpoints REST
- Autenticación JWT
- Dashboards por rol (12 roles diferentes)
- Reportes avanzados
- Gestión de mesas y puestos de votación
- Coordinación territorial

---

## ❌ Problemas Identificados en los HTML Actuales

### 1. **Login (login.html)**
**Problemas:**
- ❌ No muestra información real del sistema
- ❌ Selector de roles simplificado (solo 3: admin, coordinator, witness)
- ❌ No refleja los 12 roles reales del sistema
- ⚠️ Credenciales de demo hardcodeadas en el HTML

**Debería tener:**
- ✅ Selector con los 12 roles reales
- ✅ Información dinámica del sistema
- ✅ Validación contra la BD real
- ✅ Redirección correcta según rol

### 2. **Página de Inicio (index_home.html)**
**Problemas:**
- ❌ Datos estáticos (16 municipios, 180 puestos, 720 mesas)
- ❌ No consulta datos reales de la BD
- ❌ Features genéricas sin conexión a módulos reales
- ❌ No muestra estado real del sistema

**Debería tener:**
- ✅ Estadísticas dinámicas desde la BD
- ✅ Estado real de los 6 módulos
- ✅ Información actualizada de municipios/puestos/mesas
- ✅ Links funcionales a cada módulo

### 3. **Dashboard (dashboard_home.html)**
**Problemas:**
- ❌ Mapa estático con datos hardcodeados
- ❌ Estadísticas ficticias
- ❌ No consulta APIs reales
- ❌ Cards de roles sin funcionalidad real
- ❌ No muestra widgets del sistema

**Debería tener:**
- ✅ Datos en tiempo real desde APIs
- ✅ Integración con los 8 widgets disponibles
- ✅ Mapa con datos reales de municipios
- ✅ Estadísticas actualizadas automáticamente
- ✅ Acceso real a dashboards por rol

---

## 🔧 Correcciones Necesarias

### Prioridad ALTA:

#### 1. **Login - Integración Real**
```javascript
// Necesita:
- Consultar /api/users/roles para obtener roles disponibles
- Validar contra BD real (ya funciona)
- Mostrar información del sistema desde /api/info
- Redirigir correctamente según rol del usuario
```

#### 2. **Dashboard - Datos Dinámicos**
```javascript
// Necesita:
- Consultar /api/dashboard/widgets para widgets
- Obtener estadísticas desde /api/dashboard/stats
- Cargar mapa con datos de /api/coordination/municipios
- Mostrar estado de módulos desde /api/info
```

#### 3. **Página Inicio - Información Real**
```javascript
// Necesita:
- Consultar /api/info para módulos y endpoints
- Obtener estadísticas desde /api/dashboard/stats
- Mostrar estado del sistema desde /health
- Links funcionales a cada módulo
```

---

## 📊 Endpoints Disponibles que Deberíamos Usar

### Información del Sistema:
- `GET /api/info` - Info de módulos y endpoints
- `GET /health` - Estado del sistema
- `GET /api` - Info general de la API

### Dashboard y Estadísticas:
- `GET /api/dashboard/widgets` - Widgets disponibles
- `GET /api/dashboard/stats` - Estadísticas generales
- `GET /api/dashboard/widget/<widget_id>` - Datos de widget específico

### Coordinación:
- `GET /api/coordination/municipios` - Lista de municipios
- `GET /api/coordination/puestos` - Puestos de votación
- `GET /api/coordination/mesas` - Mesas electorales
- `GET /api/coordination/dashboard/<coordinator_id>` - Dashboard coordinador

### Candidatos:
- `GET /api/candidates` - Lista de candidatos
- `GET /api/candidates/stats` - Estadísticas de candidatos

### Reportes:
- `GET /api/reports/types` - Tipos de reportes disponibles
- `POST /api/reports/generate` - Generar reporte

### Usuarios:
- `GET /api/users/roles` - Roles disponibles
- `GET /api/users/profile` - Perfil del usuario

---

## ✅ Plan de Acción

### Fase 1: Corregir Login
1. Agregar consulta a `/api/users/roles` para roles dinámicos
2. Mostrar info del sistema desde `/api/info`
3. Mejorar validación y redirección

### Fase 2: Actualizar Dashboard
1. Integrar widgets desde `/api/dashboard/widgets`
2. Cargar estadísticas reales desde `/api/dashboard/stats`
3. Mapa con datos de `/api/coordination/municipios`
4. Estado de módulos desde `/api/info`

### Fase 3: Mejorar Página Inicio
1. Estadísticas dinámicas desde `/api/dashboard/stats`
2. Módulos desde `/api/info`
3. Estado del sistema desde `/health`
4. Links funcionales a cada módulo

---

## 🎯 Resultado Esperado

### Login:
- ✅ Selector con 12 roles reales
- ✅ Información del sistema actualizada
- ✅ Validación contra BD
- ✅ Redirección correcta

### Dashboard:
- ✅ 8 widgets funcionales
- ✅ Estadísticas en tiempo real
- ✅ Mapa con datos reales
- ✅ Acceso a dashboards por rol

### Página Inicio:
- ✅ Estadísticas actualizadas
- ✅ Estado de 6 módulos
- ✅ 130 endpoints disponibles
- ✅ Links funcionales

---

## 📝 Notas Importantes

1. **No eliminar el diseño visual** - Mantener colores y animaciones
2. **Agregar funcionalidad** - Conectar con APIs reales
3. **Datos dinámicos** - Reemplazar hardcoded por consultas
4. **Mantener responsive** - Optimización móvil
5. **Seguridad** - Validar tokens JWT en cada consulta
