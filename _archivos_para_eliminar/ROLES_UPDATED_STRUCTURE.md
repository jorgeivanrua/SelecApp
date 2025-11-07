# 📋 Estructura Actualizada de Roles

## 🎯 Cambios Realizados

### ❌ Roles Eliminados:
1. **Jurado de Votación** - Funcionalidad integrada en Testigo

### 🔄 Roles Unificados:
- **Testigo de Mesa** + **Testigo Electoral** = **Testigo Electoral Unificado**

---

## 👁️ Nuevo Rol: Testigo Electoral (Unificado)

### 📊 Estructura del Dashboard:

#### **SECCIÓN PRINCIPAL: Captura de Datos**
Ubicación: Panel central principal

**Funcionalidades:**
1. **Registro de Votos**
   - Selección de candidato
   - Número de votos
   - Observaciones opcionales
   - Botón: "Registrar Voto"

2. **Formulario E14** (Acta de Escrutinio de Mesa)
   - Total votos válidos
   - Votos en blanco
   - Votos nulos
   - Tarjetas no marcadas
   - Botón: "Generar Formulario E14"

3. **Formulario E24** (Acta de Escrutinio General)
   - Total mesas escrutadas
   - Total votos consolidados
   - Observaciones generales
   - Botón: "Generar Formulario E24"

**Panel Lateral:**
- Abrir Mesa
- Cerrar Mesa
- Ver Resumen
- Exportar Datos
- Resumen de votos en tiempo real

---

#### **SECCIÓN SECUNDARIA: Observaciones e Incidencias**
Ubicación: Panel inferior (accesible por botones)

**Funcionalidades:**
1. **Registrar Observación**
   - Ruta: `/testigo/observaciones`
   - Observaciones del proceso electoral
   - Icono: 📋

2. **Reportar Incidencia**
   - Ruta: `/testigo/incidencias`
   - Incidencias que requieren atención
   - Icono: ⚠️

3. **Ver Reportes**
   - Ruta: `/testigo/reportes`
   - Historial de observaciones e incidencias
   - Icono: 📄

4. **Ver Resultados**
   - Ruta: `/testigo/resultados`
   - Resultados preliminares de la mesa
   - Icono: 📊

---

## 📊 Estadísticas del Dashboard Testigo

**Métricas Principales:**
- Votos Registrados: 0 (actualizado en tiempo real)
- Votantes Habilitados: 350
- Participación: 0% (calculado automáticamente)
- Estado Mesa: En Proceso / Abierta / Cerrada

**Barra de Progreso:**
- Visual del porcentaje de participación
- Actualización automática al registrar votos

---

## 🎨 Diseño Visual

**Colores del Rol Testigo:**
- Primary: #06b6d4 (Cyan)
- Secondary: #0891b2 (Cyan oscuro)
- Accent: #10b981 (Verde)

**Características:**
- Cards con borde izquierdo de color
- Botones con gradiente
- Efectos hover suaves
- Tabs para organizar formularios
- Panel secundario claramente separado

---

## 🔗 Rutas y Endpoints

### Rutas del Dashboard:
- `/dashboard/testigo_mesa` - Dashboard principal
- `/testigo/observaciones` - Página de observaciones
- `/testigo/incidencias` - Página de incidencias
- `/testigo/reportes` - Página de reportes
- `/testigo/resultados` - Página de resultados

### Endpoints API:
- `GET /api/testigo/mesa-asignada` - Datos de la mesa
- `POST /api/testigo/registrar-voto` - Registrar voto
- `POST /api/testigo/formulario-e14` - Generar E14
- `POST /api/testigo/formulario-e24` - Generar E24
- `POST /api/testigo/observacion` - Nueva observación
- `POST /api/testigo/incidencia` - Nueva incidencia
- `GET /api/testigo/exportar-datos` - Exportar datos

---

## 📋 Roles Finales del Sistema (10 roles)

1. ✅ Super Administrador
2. ✅ Administrador Departamental
3. ✅ Administrador Municipal
4. ✅ Coordinador Electoral
5. ✅ Coordinador Departamental
6. ✅ Coordinador Municipal
7. ✅ Coordinador de Puesto
8. ✅ **Testigo Electoral** (Unificado)
9. ✅ Auditor Electoral
10. ✅ Observador Internacional

**Total: 10 roles operativos**

---

## 🔄 Aliases Actualizados

```
testigo → testigo_mesa
witness → testigo_mesa
auditor → auditor_electoral
observador → observador_internacional
admin → super_admin
coordinator → coordinador_municipal
```

---

## ✅ Ventajas de la Unificación

1. **Simplicidad:** Un solo dashboard para testigos
2. **Eficiencia:** Captura de datos como prioridad
3. **Organización:** Observaciones e incidencias separadas pero accesibles
4. **Usabilidad:** Interfaz clara con secciones bien definidas
5. **Funcionalidad completa:** Todas las capacidades en un solo lugar

---

## 🎯 Flujo de Trabajo del Testigo

1. **Inicio:** Abrir mesa
2. **Durante:** Registrar votos continuamente
3. **Observar:** Acceder a observaciones/incidencias cuando sea necesario
4. **Cierre:** Generar formularios E14/E24
5. **Finalizar:** Cerrar mesa y exportar datos

---

## 📱 Optimización Móvil

- Tabs responsivos
- Botones grandes para táctil
- Formularios optimizados
- Estadísticas visibles
- Acceso rápido a funciones secundarias

---

## 🔐 Seguridad

- Autenticación JWT requerida
- Validación de mesa asignada
- Registro de todas las acciones
- Exportación segura de datos
