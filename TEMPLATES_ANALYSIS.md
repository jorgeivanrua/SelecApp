# Análisis de Templates HTML

## Templates Actualmente en Uso (✅ FUNCIONALES)

### 1. **index_home.html** ✅
- **Ruta:** `/` (página principal)
- **Propósito:** Página de inicio del sistema
- **Estado:** ACTIVO - Se usa en producción
- **Acción:** MANTENER

### 2. **login.html** ✅
- **Ruta:** `/login`
- **Propósito:** Página de inicio de sesión
- **Estado:** ACTIVO - Se usa en producción
- **Acción:** MANTENER y MEJORAR diseño móvil

### 3. **dashboard_home.html** ✅
- **Ruta:** `/dashboard`
- **Propósito:** Dashboard principal con mapa y estadísticas
- **Estado:** ACTIVO - Se usa en producción
- **Acción:** MANTENER y MEJORAR diseño móvil

### 4. **dashboard.html** ✅
- **Ruta:** `/dashboard/<role>` (fallback)
- **Propósito:** Dashboard genérico cuando falla el específico por rol
- **Estado:** ACTIVO - Se usa como fallback
- **Acción:** MANTENER

### 5. **base.html** ✅
- **Propósito:** Template base para herencia
- **Estado:** USADO por otros templates
- **Acción:** MANTENER

---

## Templates Duplicados o No Usados (❌ ELIMINAR)

### 6. **index.html** ❌ DUPLICADO
- **Estado:** NO SE USA - Reemplazado por index_home.html
- **Acción:** ELIMINAR

### 7. **dashboard_generic.html** ❌ DUPLICADO
- **Estado:** NO SE USA - Similar a dashboard.html
- **Acción:** ELIMINAR

### 8. **test_login.html** ❌ TEMPORAL
- **Estado:** Solo para pruebas
- **Acción:** ELIMINAR

### 9. **error.html** ⚠️ REVISAR
- **Estado:** No se usa actualmente pero podría ser útil
- **Acción:** MANTENER para manejo de errores

---

## Templates en Subdirectorios

### templates/roles/ ✅
- Contiene dashboards específicos por rol
- **Acción:** REVISAR y MANTENER los necesarios

### templates/admin/ ⚠️
- **Acción:** REVISAR contenido

### templates/testigo/ ⚠️
- **Acción:** REVISAR contenido

### templates/forms/ ⚠️
- **Acción:** REVISAR contenido

### templates/components/ ⚠️
- **Acción:** REVISAR contenido

---

## Resumen de Acciones

### ELIMINAR (3 archivos):
1. index.html
2. dashboard_generic.html
3. test_login.html

### MANTENER Y MEJORAR (3 archivos principales):
1. index_home.html - Mejorar colores y diseño móvil
2. login.html - Mejorar colores y diseño móvil
3. dashboard_home.html - Mejorar colores y diseño móvil

### MANTENER (2 archivos):
1. base.html
2. dashboard.html (fallback)
3. error.html (manejo de errores)
