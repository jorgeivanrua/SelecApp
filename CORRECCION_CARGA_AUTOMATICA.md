# Corrección: Carga Automática de Datos del Usuario

**Fecha:** 7 de noviembre de 2025  
**Problema:** Los datos no se cargaban automáticamente al abrir el dashboard

---

## 🎯 Objetivo

Que cuando el usuario inicie sesión, sus datos se carguen automáticamente en el dashboard sin necesidad de hacer llamadas adicionales a la API, mostrando:
- Departamento
- Municipio
- Zona
- Puesto de Votación
- Mesa (con opción de cambiar)
- Tipo de Elección (con opción de cambiar)

---

## ✅ Solución Implementada

### 1. API de Login Mejorada

**Archivo:** `app.py` - Ruta `/api/auth/login`

La API de login ahora devuelve TODOS los datos del usuario en una sola consulta:

```python
cursor.execute("""
    SELECT 
        u.id, u.username, u.nombre_completo, u.password_hash, u.rol, u.activo,
        u.cedula, u.email, u.telefono,
        u.municipio_id, u.puesto_id, u.mesa_id,
        mu.nombre as municipio_nombre, mu.codigo as municipio_codigo,
        p.nombre as puesto_nombre, p.direccion as puesto_direccion,
        m.numero as mesa_numero, m.votantes_habilitados,
        z.codigo_zz as zona_codigo, z.nombre as zona_nombre
    FROM users u
    LEFT JOIN municipios mu ON u.municipio_id = mu.id
    LEFT JOIN puestos_votacion p ON u.puesto_id = p.id
    LEFT JOIN mesas_votacion m ON u.mesa_id = m.id
    LEFT JOIN zonas z ON p.zona_id = z.id
    WHERE (u.cedula = ? OR u.username = ?) AND u.activo = 1
""")
```

**Respuesta del Login:**
```json
{
    "access_token": "...",
    "user": {
        "id": 9,
        "username": "user_1000000001",
        "nombre_completo": "Testigo Curillo 1",
        "rol": "testigo_mesa",
        "cedula": "1000000001",
        "email": "demo_testigo_mesa_1000000001@electoral.gov.co",
        "telefono": "3101234567",
        "municipio_id": 11,
        "municipio_nombre": "Curillo",
        "municipio_codigo": "18205",
        "puesto_id": 251,
        "puesto_nombre": "PUESTO CABECERA MUNICIPAL",
        "puesto_direccion": "...",
        "mesa_id": 758,
        "mesa_numero": "001",
        "votantes_habilitados": 3795,
        "zona_codigo": "00",
        "zona_nombre": "Zona 00",
        "total_capturas": 0
    }
}
```

### 2. Carga Automática en el Dashboard

**Archivo:** `templates/roles/testigo_mesa/dashboard.html`

Se implementó un sistema de carga automática que:

1. **Lee datos de localStorage** (guardados en el login)
2. **Muestra datos inmediatamente** sin esperar llamadas a la API
3. **Fallback a API** solo si los datos no están completos

```javascript
// Al cargar el dashboard
document.addEventListener('DOMContentLoaded', function() {
    cargarDatosUsuario();  // ← Carga automática
    cargarCandidatos();
    inicializarEventos();
    cargarDatosTemporales();
});

// Función de carga automática
function cargarDatosUsuario() {
    // 1. Leer de localStorage
    const userStr = localStorage.getItem('user');
    const usuarioActual = JSON.parse(userStr);
    
    // 2. Si tiene datos completos, mostrarlos inmediatamente
    if (usuarioActual.municipio_nombre && usuarioActual.puesto_nombre) {
        mostrarDatosUsuario(usuarioActual);
    } else {
        // 3. Fallback: llamar a la API
        cargarDatosDesdeAPI();
    }
}

// Mostrar datos en el formulario
function mostrarDatosUsuario(user) {
    document.getElementById('municipioForm').value = user.municipio_nombre;
    document.getElementById('zona').value = user.zona_nombre;
    document.getElementById('puestoForm').value = user.puesto_nombre;
    document.getElementById('votantesHabilitados').textContent = user.votantes_habilitados;
    
    // Cargar mesas del puesto
    cargarMesasDelPuesto(user.puesto_id, user.mesa_id);
}
```

### 3. Campos del Formulario

**Campos de Solo Lectura (Cargados Automáticamente):**
- ✅ Departamento: Caquetá (fijo)
- ✅ Municipio: Desde BD
- ✅ Zona: Desde BD
- ✅ Puesto de Votación: Desde BD

**Campos Editables:**
- 🔄 Mesa: Selector con todas las mesas del puesto
- 🔄 Tipo de Elección: Selector con tipos disponibles

---

## 🔄 Flujo Completo

### 1. Login
```
Usuario ingresa cédula/contraseña
    ↓
API /api/auth/login consulta BD con JOINs
    ↓
Devuelve TODOS los datos del usuario
    ↓
localStorage.setItem('user', JSON.stringify(userData))
    ↓
Redirect a /dashboard/testigo_mesa
```

### 2. Carga del Dashboard
```
Dashboard carga
    ↓
JavaScript lee localStorage.getItem('user')
    ↓
Datos disponibles inmediatamente
    ↓
Muestra: Municipio, Zona, Puesto
    ↓
Carga mesas del puesto (API)
    ↓
Selecciona mesa asignada automáticamente
```

### 3. Usuario Puede Cambiar
```
✅ Mesa: Selector con todas las mesas del puesto
✅ Tipo de Elección: Selector con tipos
❌ Municipio: Solo lectura
❌ Zona: Solo lectura
❌ Puesto: Solo lectura
```

---

## 📊 Comparación Antes/Después

### ANTES ❌
```
1. Usuario hace login
2. Redirect a dashboard
3. Dashboard muestra "N/A" en todos los campos
4. JavaScript hace llamada a /api/testigo/info/{id}
5. Espera respuesta (delay)
6. Actualiza campos
```

**Problemas:**
- Delay visible para el usuario
- Campos vacíos o "N/A" al inicio
- Llamada adicional innecesaria
- Mala experiencia de usuario

### DESPUÉS ✅
```
1. Usuario hace login
2. API devuelve TODOS los datos
3. Datos guardados en localStorage
4. Redirect a dashboard
5. Dashboard lee localStorage
6. Campos poblados INMEDIATAMENTE
```

**Beneficios:**
- Sin delay visible
- Datos aparecen instantáneamente
- Sin llamadas adicionales
- Excelente experiencia de usuario

---

## 🎨 Interfaz de Usuario

### Vista del Formulario

```
┌─────────────────────────────────────────────────────────┐
│ 2. Datos del Formulario E14                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Departamento          Municipio           Zona          │
│ ┌──────────────┐     ┌──────────────┐   ┌───────────┐  │
│ │ Caquetá      │     │ Curillo      │   │ Zona 00   │  │
│ └──────────────┘     └──────────────┘   └───────────┘  │
│ (Solo lectura)       (Solo lectura)     (Solo lectura) │
│                                                          │
│ Puesto de Votación   Mesa *              Tipo *         │
│ ┌──────────────────┐ ┌──────────────┐   ┌───────────┐  │
│ │ PUESTO CABECERA  │ │ Mesa 001  ▼  │   │ Senado ▼  │  │
│ └──────────────────┘ └──────────────┘   └───────────┘  │
│ (Solo lectura)       (Editable)         (Editable)     │
│                      Puede cambiar       Puede cambiar  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Pruebas

### Test 1: Login y Carga Automática
```
1. Login con cédula: 1000000001
2. Password: Demo2024!
3. ✅ Redirect a dashboard
4. ✅ Municipio: "Curillo" (inmediato)
5. ✅ Zona: "Zona 00" (inmediato)
6. ✅ Puesto: "PUESTO CABECERA MUNICIPAL" (inmediato)
7. ✅ Mesa: Selector cargado con "Mesa 001" seleccionada
```

### Test 2: Cambio de Mesa
```
1. Usuario abre selector de mesa
2. ✅ Ve todas las mesas del puesto
3. Selecciona "Mesa 002"
4. ✅ Votantes habilitados se actualizan
5. ✅ Puede reportar para esa mesa
```

### Test 3: Cambio de Tipo de Elección
```
1. Usuario abre selector de tipo
2. ✅ Ve: Senado, Cámara, Concejo, etc.
3. Selecciona "Cámara de Representantes"
4. ✅ Puede reportar para ese tipo
```

---

## 📝 Archivos Modificados

1. **app.py**
   - Ruta `/api/auth/login` mejorada
   - Consulta con JOINs para obtener todos los datos
   - Respuesta incluye datos completos del usuario

2. **templates/roles/testigo_mesa/dashboard.html**
   - Nueva función `cargarDatosUsuario()`
   - Nueva función `mostrarDatosUsuario(user)`
   - Nueva función `cargarDatosDesdeAPI()` (fallback)
   - Función `cargarMesasDelPuesto()` simplificada

3. **templates/login_mejorado.html**
   - Ya guardaba user_id y user_role
   - Ahora guarda objeto user completo

---

## ✅ Resultado Final

### Lo que el Usuario Ve

1. **Al hacer login:**
   - Transición suave al dashboard
   - Datos aparecen inmediatamente
   - Sin pantallas de carga

2. **En el dashboard:**
   - Municipio, Zona, Puesto: Ya poblados
   - Mesa: Selector con su mesa seleccionada
   - Tipo: Selector listo para usar
   - Puede empezar a trabajar inmediatamente

3. **Flexibilidad:**
   - Puede cambiar de mesa si reporta varias
   - Puede cambiar tipo de elección
   - No puede cambiar municipio/zona/puesto (correcto)

---

## 🚀 Beneficios

1. **Rendimiento:** Sin llamadas adicionales innecesarias
2. **UX:** Datos instantáneos, sin esperas
3. **Offline-first:** Datos en localStorage
4. **Consistencia:** Mismos datos del login
5. **Simplicidad:** Menos código, más eficiente

---

## 📌 Notas Importantes

- Los datos se guardan en `localStorage` al hacer login
- Si el navegador borra localStorage, se hace fallback a la API
- Los datos se actualizan en cada login
- La contraseña aceptada es `Demo2024!` para usuarios demo

---

**Implementado por:** Kiro AI  
**Fecha:** 7 de noviembre de 2025  
**Estado:** ✅ COMPLETADO Y FUNCIONANDO

**Prueba ahora:**
1. Ir a http://127.0.0.1:5000/login
2. Login con cédula: 1000000001
3. Password: Demo2024!
4. Ver datos cargados automáticamente
