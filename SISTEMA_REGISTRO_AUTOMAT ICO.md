# Sistema de Registro Automático - Sistema Electoral Caquetá

## ✅ Implementación Completada

Se ha implementado exitosamente un sistema de registro automático para testigos electorales y coordinadores de puesto.

## 🎯 Características Implementadas

### 1. Página de Login/Registro Unificada
- **URL**: http://127.0.0.1:5000/login
- Interfaz moderna con tabs para Login y Registro
- Diseño responsive y amigable
- Validación en tiempo real

### 2. Formulario de Registro Inteligente

#### Selección de Rol
- **Testigo Electoral** (testigo_mesa)
- **Coordinador de Puesto** (coordinador_puesto)

#### Datos Personales Requeridos
- Cédula (6-10 dígitos)
- Nombre completo
- Email
- Teléfono (10 dígitos)
- Contraseña (mínimo 6 caracteres)

#### Selección de Ubicación con Listas Desplegables
1. **Municipio**: Lista de todos los municipios del Caquetá
2. **Puesto de Votación**: Se carga dinámicamente según el municipio seleccionado
3. **Mesa**: Se carga dinámicamente según el puesto seleccionado (solo para testigos)

### 3. APIs Implementadas

#### API de Ubicación
- `GET /api/ubicacion/municipios` - Obtener lista de municipios
- `GET /api/ubicacion/puestos/{municipio_id}` - Obtener puestos de un municipio
- `GET /api/ubicacion/mesas/{puesto_id}` - Obtener mesas de un puesto

#### API de Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión (ya existente)

## 📋 Flujo de Registro

### Paso 1: Seleccionar Rol
El usuario selecciona si es:
- Testigo Electoral
- Coordinador de Puesto

### Paso 2: Ingresar Datos Personales
- Cédula
- Nombre completo
- Email
- Teléfono

### Paso 3: Seleccionar Ubicación
1. Seleccionar **Municipio** de la lista desplegable
2. Seleccionar **Puesto de Votación** (se carga automáticamente)
3. Seleccionar **Mesa** (solo para testigos, se carga automáticamente)

### Paso 4: Crear Contraseña
- Ingresar contraseña (mínimo 6 caracteres)
- Confirmar contraseña

### Paso 5: Registro Automático
- El sistema crea el usuario automáticamente
- Genera un username: `user_{cedula}`
- Asigna el rol seleccionado
- Vincula con la ubicación seleccionada

### Paso 6: Login Automático
- Después del registro, el usuario puede hacer login inmediatamente
- Es redirigido a su dashboard correspondiente

## 🔐 Seguridad

### Validaciones Implementadas
- ✅ Cédula única (no se permite duplicados)
- ✅ Email único (no se permite duplicados)
- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Validación de formato de cédula (6-10 dígitos)
- ✅ Validación de formato de teléfono (10 dígitos)
- ✅ Validación de formato de email
- ✅ Contraseña mínima de 6 caracteres
- ✅ Confirmación de contraseña

### Roles Permitidos para Auto-Registro
- `testigo_mesa` - Testigo Electoral
- `coordinador_puesto` - Coordinador de Puesto
- `coordinador_municipal` - Coordinador Municipal

**Nota**: Los roles administrativos (super_admin, admin_departamental, etc.) NO pueden ser auto-registrados por seguridad.

## 📊 Datos de Prueba

### Municipios Disponibles
- Florencia (18001)
- San Vicente del Caguán (18029)
- Puerto Rico (18592)
- El Paujil (18479)
- Curillo (18205)
- Valparaíso (18860)

### Puestos en Florencia
- Escuela Central
- Colegio San José
- Universidad de la Amazonia

### Mesas por Puesto
- Cada puesto tiene múltiples mesas (001-A, 001-B, 002-A, etc.)
- Capacidad típica: 350 votantes por mesa

## 🧪 Pruebas Realizadas

Se ejecutó el script `test_registro_sistema.py` con los siguientes resultados:

```
✅ TEST 1: Obtener Municipios - 6 municipios
✅ TEST 2: Obtener Puestos - 3 puestos en Florencia
✅ TEST 3: Obtener Mesas - 5 mesas en Colegio San José
✅ TEST 4: Registrar Usuario - Usuario creado exitosamente
✅ TEST 5: Login - Login exitoso con token JWT
```

### Usuario de Prueba Creado
- **Cédula**: 1234567890
- **Username**: user_1234567890
- **Nombre**: Juan Pérez Testigo
- **Rol**: testigo_mesa
- **Municipio**: Florencia
- **Puesto**: Colegio San José
- **Mesa**: 002-A

## 🌐 URLs de Acceso

### Producción
- **Login/Registro**: http://127.0.0.1:5000/login
- **Login Simple (Legacy)**: http://127.0.0.1:5000/login-simple

### Red Local
- **Login/Registro**: http://192.168.20.61:5000/login

## 📱 Interfaz de Usuario

### Características de la UI
- ✅ Diseño moderno con gradientes
- ✅ Tabs para cambiar entre Login y Registro
- ✅ Tarjetas de selección de rol con iconos
- ✅ Listas desplegables dinámicas
- ✅ Validación en tiempo real
- ✅ Mensajes de error y éxito claros
- ✅ Loading spinner durante procesamiento
- ✅ Responsive (funciona en móviles y tablets)
- ✅ Iconos de Font Awesome
- ✅ Animaciones suaves

### Flujo Visual
1. Usuario ve tabs: "Iniciar Sesión" | "Registrarse"
2. Click en "Registrarse"
3. Selecciona rol (Testigo o Coordinador) con tarjetas visuales
4. Completa formulario con validación en tiempo real
5. Listas desplegables se cargan dinámicamente
6. Click en "Registrarse"
7. Mensaje de éxito y redirección a login
8. Login automático con las credenciales

## 🔧 Archivos Creados/Modificados

### Nuevos Archivos
1. `templates/login_registro.html` - Página de login/registro unificada
2. `api/auth_api.py` - API de autenticación y ubicación
3. `test_registro_sistema.py` - Script de pruebas
4. `check_mesas_structure.py` - Script de verificación

### Archivos Modificados
1. `app.py` - Agregada ruta `/login` y registro de API
2. `templates/login.html` - Mantenido como legacy en `/login-simple`

## 📚 Documentación de API

### POST /api/auth/register

**Request Body:**
```json
{
  "cedula": "1234567890",
  "nombre_completo": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "3001234567",
  "municipio_id": 1,
  "puesto_id": 2,
  "mesa_id": 6,
  "rol": "testigo_mesa",
  "password": "mipassword"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user_id": 7,
  "username": "user_1234567890"
}
```

**Errores Posibles:**
- 400: Campo requerido faltante
- 400: Cédula ya registrada
- 400: Email ya registrado
- 400: Rol no permitido
- 500: Error del servidor

### GET /api/ubicacion/municipios

**Response (200):**
```json
{
  "success": true,
  "municipios": [
    {
      "id": 1,
      "codigo": "18001",
      "nombre": "Florencia",
      "departamento": "Caquetá"
    }
  ]
}
```

### GET /api/ubicacion/puestos/{municipio_id}

**Response (200):**
```json
{
  "success": true,
  "puestos": [
    {
      "id": 1,
      "nombre": "Escuela Central",
      "direccion": "Carrera 11 # 15-20",
      "codigo": "PV001"
    }
  ]
}
```

### GET /api/ubicacion/mesas/{puesto_id}

**Response (200):**
```json
{
  "success": true,
  "mesas": [
    {
      "id": 1,
      "numero": "001-A",
      "capacidad": 350
    }
  ]
}
```

## 🚀 Próximos Pasos Sugeridos

### Mejoras Opcionales
1. **Validación de Cédula**: Integrar con API de Registraduría para validar cédulas reales
2. **Verificación de Email**: Enviar email de confirmación
3. **Verificación de Teléfono**: Enviar SMS con código de verificación
4. **Foto de Perfil**: Permitir subir foto durante el registro
5. **Términos y Condiciones**: Agregar checkbox de aceptación
6. **Recuperación de Contraseña**: Implementar "Olvidé mi contraseña"
7. **Captcha**: Agregar reCAPTCHA para prevenir bots
8. **Auditoría**: Registrar todos los intentos de registro

### Funcionalidades Adicionales
1. **Dashboard de Bienvenida**: Mostrar tutorial al primer login
2. **Perfil de Usuario**: Permitir editar datos personales
3. **Notificaciones**: Sistema de notificaciones push
4. **Chat de Soporte**: Chat en vivo para ayuda

## ✅ Estado Actual

- ✅ Sistema de registro funcionando al 100%
- ✅ APIs probadas y operativas
- ✅ Interfaz de usuario completa
- ✅ Validaciones implementadas
- ✅ Seguridad implementada
- ✅ Documentación completa
- ✅ Tests exitosos

## 📞 Uso del Sistema

### Para Testigos Electorales
1. Ir a http://127.0.0.1:5000/login
2. Click en "Registrarse"
3. Seleccionar "Testigo Electoral"
4. Completar datos personales
5. Seleccionar Municipio, Puesto y Mesa
6. Crear contraseña
7. Click en "Registrarse"
8. Hacer login con cédula y contraseña

### Para Coordinadores
1. Ir a http://127.0.0.1:5000/login
2. Click en "Registrarse"
3. Seleccionar "Coordinador"
4. Completar datos personales
5. Seleccionar Municipio y Puesto (Mesa es opcional)
6. Crear contraseña
7. Click en "Registrarse"
8. Hacer login con cédula y contraseña

---

**Última actualización**: 7 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Operativo y probado
