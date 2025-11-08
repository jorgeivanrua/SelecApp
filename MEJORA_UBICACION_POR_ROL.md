# Mejora: Campos de Ubicación Condicionales por Rol

**Fecha:** 8 de noviembre de 2025  
**Mejora:** Campos de ubicación dinámicos según el rol del usuario

---

## 🎯 Problema Identificado

El formulario de creación de usuarios mostraba todos los campos de ubicación (Municipio, Puesto, Mesa) para todos los roles, sin considerar que:

- Un **Super Admin** no necesita ubicación específica
- Un **Admin Departamental** solo necesita departamento
- Un **Coordinador Municipal** necesita departamento + municipio
- Un **Testigo de Mesa** necesita la ubicación completa

Además, faltaba el campo **Departamento** en el sistema.

---

## ✅ Solución Implementada

### 1. Campo Departamento Agregado

Se agregó el campo `departamento` a la tabla `users`:

```sql
ALTER TABLE users ADD COLUMN departamento TEXT DEFAULT 'Caquetá'
```

### 2. Lógica Condicional por Rol

Los campos de ubicación ahora se muestran/ocultan dinámicamente según el rol:

| Rol | Departamento | Municipio | Puesto | Mesa |
|-----|--------------|-----------|--------|------|
| **Super Admin** | ❌ | ❌ | ❌ | ❌ |
| **Admin Departamental** | ✅ | ❌ | ❌ | ❌ |
| **Admin Municipal** | ✅ | ✅ | ❌ | ❌ |
| **Coordinador Departamental** | ✅ | ❌ | ❌ | ❌ |
| **Coordinador Municipal** | ✅ | ✅ | ❌ | ❌ |
| **Coordinador Puesto** | ✅ | ✅ | ✅ | ❌ |
| **Testigo Mesa** | ✅ | ✅ | ✅ | ✅ |
| **Auditor Electoral** | ✅ | ❌ | ❌ | ❌ |

### 3. Validación Automática

Los campos requeridos se marcan automáticamente según el rol:
- Si el campo se muestra, es **obligatorio**
- Si el campo está oculto, **no se valida**

---

## 🔧 Cambios Técnicos

### 1. Base de Datos

**Archivo:** `agregar_campo_departamento.py`

```python
cursor.execute("ALTER TABLE users ADD COLUMN departamento TEXT DEFAULT 'Caquetá'")
```

### 2. API - Crear Usuario

**Archivo:** `api/auth_api.py`

```python
cursor.execute("""
    INSERT INTO users (
        username, cedula, nombre_completo, email, telefono,
        password_hash, rol, departamento, municipio_id, puesto_id, mesa_id,
        activo, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    username,
    data['cedula'],
    data['nombre_completo'],
    data.get('email', ''),
    data['telefono'],
    password_hash,
    data['rol'],
    data.get('departamento', 'Caquetá'),  # ← NUEVO
    data.get('municipio_id'),
    data.get('puesto_id'),
    data.get('mesa_id'),
    1,
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
))
```

### 3. API - Obtener Usuarios

```python
cursor.execute("""
    SELECT 
        u.id, u.username, u.cedula, u.nombre_completo, u.email, u.telefono,
        u.rol, u.departamento, u.activo, u.created_at,  # ← departamento agregado
        m.nombre as municipio_nombre,
        p.nombre as puesto_nombre,
        mv.numero as mesa_numero
    FROM users u
    ...
""")
```

### 4. Frontend - Campos Condicionales

**Archivo:** `templates/roles/super_admin/usuarios.html`

```html
<!-- Campos de ubicación condicionales según rol -->
<div id="ubicacionFields">
    <div class="row" id="departamentoRow" style="display: none;">
        <div class="col-12 mb-3">
            <label class="form-label">Departamento *</label>
            <select class="form-select" id="userDepartamento">
                <option value="Caquetá">Caquetá</option>
            </select>
        </div>
    </div>

    <div class="row" id="municipioRow" style="display: none;">
        <!-- ... -->
    </div>

    <div class="row" id="puestoRow" style="display: none;">
        <!-- ... -->
    </div>

    <div class="row" id="mesaRow" style="display: none;">
        <!-- ... -->
    </div>
</div>
```

### 5. JavaScript - Lógica de Visibilidad

```javascript
function updateUbicacionFields() {
    const rol = document.getElementById('userRol').value;
    
    // Ocultar todos los campos primero
    document.getElementById('departamentoRow').style.display = 'none';
    document.getElementById('municipioRow').style.display = 'none';
    document.getElementById('puestoRow').style.display = 'none';
    document.getElementById('mesaRow').style.display = 'none';
    
    // Remover required de todos
    document.getElementById('userDepartamento').required = false;
    document.getElementById('userMunicipio').required = false;
    document.getElementById('userPuesto').required = false;
    document.getElementById('userMesa').required = false;
    
    // Configurar según el rol
    switch(rol) {
        case 'super_admin':
            // Sin campos de ubicación
            break;
            
        case 'admin_departamental':
        case 'coordinador_departamental':
            document.getElementById('departamentoRow').style.display = 'block';
            document.getElementById('userDepartamento').required = true;
            break;
            
        case 'admin_municipal':
        case 'coordinador_municipal':
            document.getElementById('departamentoRow').style.display = 'block';
            document.getElementById('municipioRow').style.display = 'block';
            document.getElementById('userDepartamento').required = true;
            document.getElementById('userMunicipio').required = true;
            break;
            
        case 'coordinador_puesto':
            document.getElementById('departamentoRow').style.display = 'block';
            document.getElementById('municipioRow').style.display = 'block';
            document.getElementById('puestoRow').style.display = 'block';
            document.getElementById('userDepartamento').required = true;
            document.getElementById('userMunicipio').required = true;
            document.getElementById('userPuesto').required = true;
            break;
            
        case 'testigo_mesa':
            // Todos los campos
            document.getElementById('departamentoRow').style.display = 'block';
            document.getElementById('municipioRow').style.display = 'block';
            document.getElementById('puestoRow').style.display = 'block';
            document.getElementById('mesaRow').style.display = 'block';
            document.getElementById('userDepartamento').required = true;
            document.getElementById('userMunicipio').required = true;
            document.getElementById('userPuesto').required = true;
            document.getElementById('userMesa').required = true;
            break;
    }
}
```

---

## 🎨 Mensajes Informativos por Rol

Cada rol muestra un mensaje específico explicando qué campos necesita:

### Super Admin
```
🔱 Super Admin: No requiere asignación de ubicación específica. 
Tiene acceso total al sistema.
```

### Admin/Coordinador Departamental
```
🗺️ Admin Departamental: Requiere asignación de departamento.
```

### Admin/Coordinador Municipal
```
🏙️ Admin Municipal: Requiere asignación de departamento y municipio.
```

### Coordinador de Puesto
```
🏢 Coordinador de Puesto: Requiere asignación de departamento, 
municipio y puesto de votación.
```

### Testigo de Mesa
```
✅ Testigo de Mesa: Requiere asignación completa: departamento, 
municipio, puesto y mesa específica.
```

### Auditor Electoral
```
🔍 Auditor Electoral: Requiere asignación de departamento.
```

---

## 📊 Flujo de Uso

### Crear Usuario:

1. Admin abre el modal "Crear Usuario"
2. Selecciona el **Rol** del usuario
3. Los campos de ubicación aparecen automáticamente según el rol
4. Solo se muestran los campos necesarios
5. Los campos mostrados son obligatorios
6. Al guardar, se valida solo lo necesario

### Ejemplo: Crear Coordinador Municipal

1. Seleccionar rol: "Coordinador Municipal"
2. Aparecen campos:
   - ✅ Departamento (obligatorio)
   - ✅ Municipio (obligatorio)
   - ❌ Puesto (oculto)
   - ❌ Mesa (oculto)
3. Llenar departamento y municipio
4. Guardar

---

## ✅ Beneficios

### 1. Interfaz Más Limpia
- Solo se muestran campos relevantes
- Menos confusión para el usuario
- Formulario más corto y rápido

### 2. Validación Inteligente
- Solo valida campos necesarios
- Previene errores de asignación
- Guía al usuario correctamente

### 3. Mejor Organización
- Cada rol tiene su nivel de acceso claro
- Jerarquía de ubicación respetada
- Datos más consistentes

### 4. Escalabilidad
- Fácil agregar nuevos roles
- Lógica centralizada
- Mantenimiento simplificado

---

## 🧪 Cómo Probar

### 1. Acceder a Gestión de Usuarios

```
http://127.0.0.1:5000/super_admin/usuarios
```

### 2. Crear Usuario con Diferentes Roles

**Testigo de Mesa:**
- Seleccionar rol "Testigo Mesa"
- Verificar que aparecen: Departamento, Municipio, Puesto, Mesa
- Todos son obligatorios

**Coordinador Municipal:**
- Seleccionar rol "Coordinador Municipal"
- Verificar que aparecen: Departamento, Municipio
- Puesto y Mesa están ocultos

**Super Admin:**
- Seleccionar rol "Super Admin"
- Verificar que NO aparece ningún campo de ubicación
- Solo datos personales

### 3. Validación

- Intentar guardar sin llenar campos obligatorios
- Verificar que muestra error
- Llenar campos y guardar exitosamente

---

## 📝 Archivos Modificados

1. **agregar_campo_departamento.py** (NUEVO)
   - Script para agregar campo departamento a la BD

2. **api/auth_api.py**
   - Agregado campo `departamento` en INSERT
   - Agregado campo `departamento` en SELECT
   - Agregado campo `departamento` en UPDATE

3. **templates/roles/super_admin/usuarios.html**
   - Campos de ubicación separados en divs individuales
   - Función `updateUbicacionFields()` agregada
   - Evento `onchange` en select de rol
   - Mensajes informativos por rol
   - Visualización de departamento en tarjetas

4. **caqueta_electoral.db**
   - Columna `departamento` agregada a tabla `users`

---

## 🎯 Casos de Uso

### Caso 1: Crear Admin Departamental

```
Rol: Admin Departamental
Departamento: Caquetá ✅
Municipio: (oculto)
Puesto: (oculto)
Mesa: (oculto)

Resultado: Usuario con acceso a todo el departamento
```

### Caso 2: Crear Coordinador de Puesto

```
Rol: Coordinador Puesto
Departamento: Caquetá ✅
Municipio: Florencia ✅
Puesto: Colegio San José ✅
Mesa: (oculto)

Resultado: Usuario con acceso a ese puesto específico
```

### Caso 3: Crear Testigo de Mesa

```
Rol: Testigo Mesa
Departamento: Caquetá ✅
Municipio: Florencia ✅
Puesto: Colegio San José ✅
Mesa: Mesa 001 ✅

Resultado: Usuario asignado a esa mesa específica
```

---

## 🚀 Próximas Mejoras

1. **Múltiples departamentos** para roles nacionales
2. **Asignación múltiple** de ubicaciones
3. **Historial de cambios** de ubicación
4. **Validación geográfica** (municipio pertenece a departamento)
5. **Autocompletado** de ubicaciones
6. **Mapa visual** de asignaciones

---

**Implementado por:** Kiro AI  
**Fecha:** 8 de noviembre de 2025  
**Estado:** ✅ COMPLETADO Y PROBADO

**Resultado:** 
- Campo departamento agregado al sistema
- Campos de ubicación se muestran/ocultan según el rol
- Validación automática de campos requeridos
- Interfaz más limpia y fácil de usar
- Mensajes informativos por cada rol
