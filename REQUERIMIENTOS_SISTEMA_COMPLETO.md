# 📋 Requerimientos del Sistema Electoral - Documento Consolidado

**Versión:** 2.0  
**Fecha:** 2025-11-07  
**Estado:** Consolidado y Actualizado

---

## 📑 Índice

1. [Introducción](#introducción)
2. [Glosario](#glosario)
3. [Requerimientos Generales del Sistema](#requerimientos-generales-del-sistema)
4. [Requerimientos del Testigo Electoral](#requerimientos-del-testigo-electoral)
5. [Requerimientos de OCR (Opcional)](#requerimientos-de-ocr-opcional)
6. [Estructura de Base de Datos](#estructura-de-base-de-datos)
7. [APIs Requeridas](#apis-requeridas)
8. [Prioridades de Implementación](#prioridades-de-implementación)

---

## Introducción

El Sistema Electoral es una aplicación web integral para la gestión y supervisión de procesos electorales en Colombia. El sistema permitirá el registro, validación y consolidación de resultados electorales a través de una jerarquía de usuarios que incluye testigos electorales, coordinadores de puesto, coordinadores municipales y coordinadores departamentales.

### Objetivos Principales:
1. Facilitar la captura rápida y precisa de resultados electorales
2. Mantener trazabilidad completa desde mesas individuales hasta consolidaciones departamentales
3. Garantizar la seguridad e integridad de los datos electorales
4. Proporcionar herramientas de supervisión y auditoría en tiempo real

---

## Glosario

### Términos del Sistema
- **Sistema_Electoral**: La aplicación web completa para gestión electoral
- **Testigo_Electoral**: Usuario que captura resultados del formulario E14 físico mediante foto y digitación
- **Coordinador_Puesto**: Usuario que supervisa múltiples mesas en un puesto de votación
- **Coordinador_Municipal**: Usuario que supervisa todos los puestos en un municipio y consolida E24
- **Coordinador_Departamental**: Usuario que supervisa todos los municipios en un departamento
- **Admin**: Usuario administrador con acceso completo al sistema

### Términos Electorales
- **Formulario_E14**: Acta física de escrutinio de mesa electoral (llenada por jurados)
- **Formulario_E24**: Consolidación digital de resultados por municipio (creada por coordinadores)
- **Mesa_Electoral**: Unidad básica de votación
- **Puesto_Votacion**: Conjunto de mesas en una ubicación física
- **DIVIPOLA**: División Político-Administrativa de Colombia

### Términos Técnicos
- **JWT**: JSON Web Token para autenticación
- **API_REST**: Interfaz de programación de aplicaciones RESTful
- **OCR**: Optical Character Recognition (Reconocimiento Óptico de Caracteres)
- **Zona_OCR**: Área rectangular definida en el formulario E14 donde se extraerá texto
- **Confianza**: Porcentaje de certeza del OCR sobre el texto extraído (0-100%)

---

## Requerimientos Generales del Sistema

### REQ-SYS-001: Configuración Inicial del Proyecto

**User Story:** Como desarrollador, quiero establecer la estructura base del proyecto Flask, para que pueda desarrollar el sistema electoral sobre una base sólida y escalable.

**Criterios de Aceptación:**
1. EL Sistema_Electoral DEBERÁ usar Flask como framework web principal con estructura modular
2. EL Sistema_Electoral DEBERÁ implementar SQLAlchemy como ORM para gestión de base de datos
3. EL Sistema_Electoral DEBERÁ usar SQLite para desarrollo y PostgreSQL para producción
4. EL Sistema_Electoral DEBERÁ implementar migraciones de base de datos con Flask-Migrate
5. EL Sistema_Electoral DEBERÁ incluir configuraciones separadas para desarrollo, testing y producción

---

### REQ-SYS-002: Gestión de Usuarios y Autenticación

**User Story:** Como administrador del sistema, quiero gestionar usuarios con diferentes roles y niveles de acceso, para que cada usuario pueda realizar solo las funciones autorizadas según su rol.

**Criterios de Aceptación:**
1. EL Sistema_Electoral DEBERÁ permitir la creación de usuarios con roles específicos:
   - Super Administrador
   - Administrador Departamental
   - Administrador Municipal
   - Coordinador Electoral
   - Coordinador Departamental
   - Coordinador Municipal
   - Coordinador de Puesto
   - Testigo Electoral (rol unificado)
   - Auditor Electoral
   - Observador Internacional
2. WHEN un usuario intente iniciar sesión, EL Sistema_Electoral DEBERÁ validar las credenciales contra la base de datos
3. EL Sistema_Electoral DEBERÁ generar tokens JWT válidos para usuarios autenticados exitosamente
4. EL Sistema_Electoral DEBERÁ bloquear usuarios después de 5 intentos fallidos de inicio de sesión por 30 minutos
5. MIENTRAS un usuario esté autenticado, EL Sistema_Electoral DEBERÁ mantener la sesión activa mediante cookies seguras
6. EL Sistema_Electoral DEBERÁ basar todos los datos en la base de datos, sus botones desplegables y sus conexiones

---

### REQ-SYS-003: Jerarquía Geográfica y Permisos

**User Story:** Como coordinador de cualquier nivel, quiero acceder solo a las ubicaciones bajo mi jurisdicción, para que pueda supervisar eficientemente mi área asignada sin acceso no autorizado.

**Criterios de Aceptación:**
1. EL Sistema_Electoral DEBERÁ implementar la estructura jerárquica DIVIPOLA (Departamento → Municipio → Comuna → Puesto → Mesa)
2. WHEN un Coordinador_Departamental acceda al sistema, EL Sistema_Electoral DEBERÁ mostrar todos los municipios, comunas, puestos y mesas de su departamento
3. WHEN un Coordinador_Municipal acceda al sistema, EL Sistema_Electoral DEBERÁ mostrar solo las comunas, los puestos y mesas de su municipio
4. WHEN un Coordinador_Puesto acceda al sistema, EL Sistema_Electoral DEBERÁ mostrar solo las mesas de su puesto
5. WHEN un Testigo_Electoral acceda al sistema, EL Sistema_Electoral DEBERÁ mostrar su mesa asignada como primera y las del puesto como adicionales

---

### REQ-SYS-004: Consolidación y Formularios E-24

**User Story:** Como coordinador municipal, quiero consolidar los resultados de múltiples mesas, para generar reportes agregados de mi jurisdicción.

**Criterios de Aceptación:**
1. WHEN todas las capturas E14 de un puesto estén aprobadas, EL Sistema_Electoral DEBERÁ permitir la creación de un Formulario_E24 de consolidación
2. EL Sistema_Electoral DEBERÁ calcular automáticamente los totales consolidados basados en las capturas E-14 aprobadas
3. EL Sistema_Electoral DEBERÁ detectar y alertar sobre discrepancias entre capturas individuales y consolidados
4. WHEN un Coordinador_Municipal genere un Formulario_E24, EL Sistema_Electoral DEBERÁ incluir datos de todos los puestos bajo su jurisdicción
5. EL Sistema_Electoral DEBERÁ mantener trazabilidad completa desde mesas individuales hasta consolidaciones departamentales

---

### REQ-SYS-005: Seguridad y Protección de Datos

**User Story:** Como administrador del sistema, quiero garantizar la seguridad e integridad de los datos electorales, para proteger la información sensible y mantener la confianza en el proceso.

**Criterios de Aceptación:**
1. EL Sistema_Electoral DEBERÁ encriptar todas las contraseñas usando algoritmos seguros (bcrypt/scrypt)
2. EL Sistema_Electoral DEBERÁ usar conexiones HTTPS en producción para proteger datos en tránsito
3. EL Sistema_Electoral DEBERÁ validar y sanitizar todas las entradas de usuario para prevenir inyecciones
4. EL Sistema_Electoral DEBERÁ implementar tokens JWT con expiración automática
5. EL Sistema_Electoral DEBERÁ registrar intentos de acceso no autorizado y actividad sospechosa
6. EL Sistema_Electoral DEBERÁ prohibir la carga de 2 formularios iguales

---

### REQ-SYS-006: Reportes y Auditoría

**User Story:** Como auditor o coordinador de alto nivel, quiero generar reportes detallados y rastrear cambios en el sistema, para garantizar transparencia y trazabilidad del proceso electoral.

**Criterios de Aceptación:**
1. EL Sistema_Electoral DEBERÁ generar reportes de progreso por departamento, municipio y puesto
2. EL Sistema_Electoral DEBERÁ registrar todas las acciones de usuarios en un log de auditoría
3. WHEN se detecten discrepancias en los datos, EL Sistema_Electoral DEBERÁ generar alertas automáticas
4. EL Sistema_Electoral DEBERÁ permitir la exportación de datos en formatos CSV y JSON
5. EL Sistema_Electoral DEBERÁ proporcionar dashboards con estadísticas en tiempo real del proceso electoral

---

## Requerimientos del Testigo Electoral

### 🎯 Clarificación del Rol

**El Testigo Electoral:**
- ✅ **Fotografía** el formulario E14 físico (ya llenado por jurados en la mesa)
- ✅ **Digita** los datos del formulario en el sistema
- ✅ **Envía** la captura (foto + datos) al servidor
- ✅ **Registra** observaciones del proceso electoral
- ✅ **Reporta** incidencias durante la votación

**El Testigo NO:**
- ❌ Crea formularios E14 (el E14 es físico, llenado por jurados)
- ❌ Crea formularios E24 (consolidación de múltiples mesas)
- ❌ Genera PDFs oficiales
- ❌ Consolida datos de múltiples mesas
- ❌ Valida capturas de otros testigos

---

### REQ-TEST-001: Selección de Mesa

**User Story:** Como testigo electoral, quiero seleccionar la mesa donde estoy trabajando, para poder capturar los resultados de esa mesa específica.

**Criterios de Aceptación:**
1. WHEN el testigo accede al dashboard, THE Sistema SHALL mostrar lista de mesas de su puesto asignado
2. THE Sistema SHALL mostrar información de cada mesa: número, puesto, votantes habilitados, estado
3. WHEN el testigo selecciona una mesa, THE Sistema SHALL cargar los datos de esa mesa
4. THE Sistema SHALL permitir cambiar de mesa si es necesario
5. THE Sistema SHALL mostrar la mesa asignada como primera opción

---

### REQ-TEST-002: Captura de Foto del E14

**User Story:** Como testigo electoral, quiero fotografiar el formulario E14 físico, para tener un respaldo visual de los datos que voy a digitar.

**Criterios de Aceptación:**
1. THE Sistema SHALL permitir tomar foto con cámara del dispositivo
2. THE Sistema SHALL permitir subir archivo desde galería
3. WHEN el testigo selecciona una imagen, THE Sistema SHALL validar que el formato sea JPG, PNG o PDF
4. WHEN el testigo selecciona una imagen, THE Sistema SHALL validar que el tamaño no exceda 10MB
5. THE Sistema SHALL mostrar vista previa de la foto antes de continuar
6. THE Sistema SHALL mostrar recomendaciones de calidad (iluminación, nitidez, formulario completo visible)

---

### REQ-TEST-003: Digitación de Datos del E14

**User Story:** Como testigo electoral, quiero digitar los datos del formulario E14, para registrar oficialmente los resultados en el sistema.

**Criterios de Aceptación:**
1. THE Sistema SHALL mostrar formulario con campos para cada candidato (cargados desde BD)
2. THE Sistema SHALL incluir campos para votos especiales (blanco, nulo, no marcado)
3. WHEN el testigo ingresa datos, THE Sistema SHALL calcular automáticamente el total de votos
4. THE Sistema SHALL validar que los números sean enteros no negativos
5. THE Sistema SHALL comparar el total con votantes habilitados y mostrar advertencia si difiere más del 5%
6. THE Sistema SHALL incluir campo de observaciones opcional

---

### REQ-TEST-004: Envío de Captura E14

**User Story:** Como testigo electoral, quiero enviar la captura completa (foto + datos), para que queden registrados oficialmente los resultados de mi mesa.

**Criterios de Aceptación:**
1. THE Sistema SHALL habilitar botón de envío solo si hay foto Y datos digitados
2. WHEN el testigo hace clic en enviar, THE Sistema SHALL mostrar confirmación antes de enviar
3. THE Sistema SHALL enviar datos a endpoint `POST /api/testigo/captura-e14`
4. THE Sistema SHALL incluir: foto (base64), datos digitados, mesa_id, testigo_id, timestamp
5. WHEN el envío es exitoso, THE Sistema SHALL mostrar mensaje de confirmación
6. WHEN el envío es exitoso, THE Sistema SHALL redirigir al dashboard
7. THE Sistema SHALL actualizar el estado de la mesa a "datos_capturados"

---

### REQ-TEST-005: Observaciones del Proceso

**User Story:** Como testigo electoral, quiero registrar observaciones durante el proceso electoral, para documentar aspectos relevantes del proceso.

**Criterios de Aceptación:**
1. THE Sistema SHALL proporcionar formulario para nueva observación
2. THE Sistema SHALL incluir tipos de observación: procedimiento, participación, seguridad, otro
3. THE Sistema SHALL incluir campo de descripción detallada
4. THE Sistema SHALL registrar timestamp automáticamente
5. THE Sistema SHALL mostrar historial de observaciones registradas

---

### REQ-TEST-006: Reporte de Incidencias

**User Story:** Como testigo electoral, quiero reportar incidencias que requieren atención, para que sean atendidas oportunamente.

**Criterios de Aceptación:**
1. THE Sistema SHALL proporcionar formulario para nueva incidencia
2. THE Sistema SHALL incluir tipos de incidencia: irregularidad, problema técnico, alteración, falta material, otro
3. THE Sistema SHALL incluir niveles de gravedad: baja, media, alta
4. THE Sistema SHALL incluir campo de descripción detallada
5. THE Sistema SHALL registrar timestamp automáticamente
6. THE Sistema SHALL mostrar historial de incidencias reportadas

---

### REQ-TEST-007: Historial de Capturas

**User Story:** Como testigo electoral, quiero ver todas las capturas E14 que he enviado, para poder revisar el historial de mi trabajo.

**Criterios de Aceptación:**
1. THE Sistema SHALL mostrar lista de capturas con fecha/hora
2. THE Sistema SHALL mostrar estado de cada captura: pendiente, aprobada, rechazada
3. WHEN el testigo hace clic en una captura, THE Sistema SHALL mostrar detalles completos
4. THE Sistema SHALL mostrar foto original y datos digitados
5. THE Sistema SHALL permitir ver pero no editar capturas enviadas

---

## Requerimientos de OCR (Opcional)

### 🤖 Procesamiento Automático Asistido

**Nota Importante:** El OCR es una funcionalidad **opcional** que asiste al testigo pre-llenando el formulario. El testigo **SIEMPRE** debe revisar y corregir los datos antes de enviar.

---

### REQ-OCR-001: Configuración de Estructura E14 por Admin

**User Story:** Como administrador, quiero configurar las zonas OCR del formulario E14, para que el sistema sepa dónde extraer los números de votos en las fotos.

**Criterios de Aceptación:**
1. WHEN el admin accede a configuración de E14, THE Sistema SHALL mostrar formulario para definir posiciones y zonas OCR
2. THE Sistema SHALL solicitar para cada posición: posición, tipo, candidato_id, coordenadas (x, y, width, height)
3. WHEN el admin guarda la configuración, THE Sistema SHALL enviar datos a `POST /api/admin/configurar-estructura-e14`
4. THE Sistema SHALL guardar registros en tabla `estructura_e14`
5. THE Sistema SHALL validar que todas las posiciones tengan zonas OCR definidas

---

### REQ-OCR-002: Procesamiento Automático de Imagen

**User Story:** Como testigo electoral, quiero que el sistema procese automáticamente la foto del E14, para ahorrar tiempo en la digitación manual.

**Criterios de Aceptación:**
1. WHEN el servidor recibe una imagen E14, THE Sistema SHALL preprocesar la imagen (escala de grises, mejora de contraste, eliminación de ruido)
2. THE Sistema SHALL obtener la estructura E14 configurada por el admin
3. THE Sistema SHALL extraer texto de cada zona OCR definida usando Tesseract
4. THE Sistema SHALL convertir el texto a número entero y calcular nivel de confianza
5. THE Sistema SHALL retornar datos extraídos con confianza promedio y total de votos
6. IF el OCR falla en una zona, THEN THE Sistema SHALL asignar valor 0 y confianza 0%

---

### REQ-OCR-003: Revisión y Corrección por Testigo

**User Story:** Como testigo electoral, quiero revisar y corregir los datos extraídos por el OCR, para garantizar la precisión de los resultados.

**Criterios de Aceptación:**
1. WHEN el OCR completa el procesamiento, THE Sistema SHALL mostrar tabla con: Posición, Candidato, Votos, Confianza, Acción
2. THE Sistema SHALL resaltar en amarillo las filas con confianza menor a 90%
3. THE Sistema SHALL mostrar confianza promedio general
4. WHEN el testigo hace clic en editar, THE Sistema SHALL convertir el campo en input editable
5. WHEN el testigo modifica un valor, THE Sistema SHALL marcar ese campo como "editado" visualmente
6. THE Sistema SHALL recalcular el total de votos automáticamente

---

### REQ-OCR-004: Manejo de Errores OCR

**User Story:** Como testigo electoral, quiero que el sistema me notifique si el OCR no puede procesar la imagen, para que pueda tomar acciones correctivas.

**Criterios de Aceptación:**
1. IF el OCR falla completamente, THEN THE Sistema SHALL mostrar mensaje de error
2. THE Sistema SHALL ofrecer opciones: "Tomar nueva foto" o "Ingresar manualmente"
3. IF el testigo selecciona "Tomar nueva foto", THEN THE Sistema SHALL volver a pantalla de captura
4. IF el testigo selecciona "Ingresar manualmente", THEN THE Sistema SHALL mostrar formulario vacío
5. THE Sistema SHALL registrar el error en logs con detalles de la imagen y mesa

---

### REQ-OCR-005: Indicadores de Calidad de Imagen

**User Story:** Como testigo electoral, quiero recibir retroalimentación sobre la calidad de la foto, para asegurarme de que el OCR funcionará correctamente.

**Criterios de Aceptación:**
1. WHEN el testigo sube una imagen, THE Sistema SHALL analizar la resolución
2. IF la resolución es menor a 1200x1600px, THEN THE Sistema SHALL mostrar advertencia
3. THE Sistema SHALL detectar si está borrosa usando análisis de varianza de Laplacian
4. IF la imagen está borrosa, THEN THE Sistema SHALL mostrar advertencia y sugerir nueva foto
5. THE Sistema SHALL permitir al testigo continuar o tomar nueva foto

---

## Estructura de Base de Datos

### Tabla: `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    departamento_id INTEGER,
    municipio_id INTEGER,
    puesto_id INTEGER,
    mesa_id INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado_hasta DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: `mesas_votacion`
```sql
CREATE TABLE mesas_votacion (
    id INTEGER PRIMARY KEY,
    numero_mesa VARCHAR(20) NOT NULL,
    puesto_id INTEGER NOT NULL,
    votantes_habilitados INTEGER NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente',
    testigo_asignado_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (puesto_id) REFERENCES puestos_votacion(id),
    FOREIGN KEY (testigo_asignado_id) REFERENCES users(id)
);
```

### Tabla: `capturas_e14`
```sql
CREATE TABLE capturas_e14 (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER NOT NULL,
    testigo_id INTEGER NOT NULL,
    ruta_foto VARCHAR(255) NOT NULL,
    datos_json TEXT NOT NULL,
    total_votos INTEGER,
    observaciones TEXT,
    estado VARCHAR(50) DEFAULT 'pendiente',
    procesado_ocr BOOLEAN DEFAULT FALSE,
    confianza_ocr FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id),
    FOREIGN KEY (testigo_id) REFERENCES users(id)
);
```

### Tabla: `observaciones_testigo`
```sql
CREATE TABLE observaciones_testigo (
    id INTEGER PRIMARY KEY,
    testigo_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    tipo VARCHAR(50),
    descripcion TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (testigo_id) REFERENCES users(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
);
```

### Tabla: `incidencias_testigo`
```sql
CREATE TABLE incidencias_testigo (
    id INTEGER PRIMARY KEY,
    testigo_id INTEGER NOT NULL,
    mesa_id INTEGER NOT NULL,
    tipo VARCHAR(50),
    gravedad VARCHAR(20),
    descripcion TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (testigo_id) REFERENCES users(id),
    FOREIGN KEY (mesa_id) REFERENCES mesas_votacion(id)
);
```

### Tabla: `estructura_e14` (Para OCR)
```sql
CREATE TABLE estructura_e14 (
    id INTEGER PRIMARY KEY,
    tipo_eleccion_id INTEGER,
    posicion INTEGER,
    tipo VARCHAR(50),
    candidato_id INTEGER,
    partido_id INTEGER,
    zona_ocr_x INTEGER,
    zona_ocr_y INTEGER,
    zona_ocr_width INTEGER,
    zona_ocr_height INTEGER
);
```

---

## APIs Requeridas

### APIs de Autenticación
```
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
POST /api/auth/refresh
```

### APIs del Testigo
```
GET  /api/testigo/mesas-disponibles
POST /api/testigo/seleccionar-mesa
POST /api/testigo/captura-e14
GET  /api/testigo/capturas/:mesa_id
POST /api/testigo/observacion
POST /api/testigo/incidencia
GET  /api/testigo/resultados/:mesa_id
```

### APIs de OCR (Opcional)
```
POST /api/admin/configurar-estructura-e14
POST /api/testigo/procesar-ocr-e14
GET  /api/testigo/fotos-e14/:mesa_id
```

### APIs de Coordinación
```
GET  /api/coordinador/capturas-pendientes
POST /api/coordinador/aprobar-captura/:id
POST /api/coordinador/rechazar-captura/:id
POST /api/coordinador/generar-e24
```

### APIs Administrativas
```
GET  /api/admin/datos-electorales
POST /api/admin/candidato
POST /api/admin/partido
GET  /api/admin/reportes
```

---

## Prioridades de Implementación

### 🔴 Fase 1: Funcionalidad Básica (Alta Prioridad)
1. ✅ Autenticación y gestión de usuarios
2. ✅ Estructura jerárquica DIVIPOLA
3. ✅ Dashboards por rol
4. 🔄 Captura E14 básica (foto + digitación manual)
5. 🔄 Almacenamiento en base de datos
6. 🔄 Validación de datos

### 🟡 Fase 2: Funcionalidades Intermedias (Media Prioridad)
1. 🔄 Observaciones e incidencias
2. 🔄 Historial de capturas
3. 🔄 Validación por coordinadores
4. 🔄 Consolidación E24
5. 🔄 Reportes básicos

### 🟢 Fase 3: Funcionalidades Avanzadas (Baja Prioridad)
1. 🔄 OCR asistido
2. 🔄 Configuración de zonas OCR
3. 🔄 Indicadores de calidad de imagen
4. 🔄 Dashboards en tiempo real
5. 🔄 Exportación avanzada de datos

---

## 📊 Resumen Ejecutivo

### Sistema Completo:
- **10 roles** de usuario con permisos específicos
- **Jerarquía geográfica** DIVIPOLA completa
- **Captura E14** mediante foto + digitación
- **OCR opcional** para asistir digitación
- **Consolidación E24** por coordinadores
- **Trazabilidad completa** de datos
- **Auditoría** de todas las acciones

### Flujo Principal:
1. Testigo fotografía E14 físico
2. Testigo digita datos (con o sin asistencia OCR)
3. Testigo envía captura
4. Sistema almacena foto + datos
5. Coordinador valida captura
6. Coordinador consolida en E24
7. Sistema genera reportes

---

**Documento consolidado:** 2025-11-07  
**Próxima revisión:** Según avance del proyecto  
**Mantenido por:** Equipo de desarrollo
