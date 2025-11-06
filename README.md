# Sistema Electoral ERP - Caquetá

Sistema integral de gestión electoral desarrollado para el departamento del Caquetá, Colombia. Diseñado para facilitar la supervisión, monitoreo y reporte de procesos electorales con funcionalidades específicas para diferentes roles.

## 🚀 Características Principales

### ✅ **Gestión Multi-Rol**
- **Super Administrador**: Control total del sistema
- **Administradores**: Departamental y Municipal
- **Coordinadores**: Electoral, Departamental, Municipal y de Puesto
- **Testigos Electorales**: Observación y reporte
- **Jurados de Votación**: Gestión de mesas
- **Auditores**: Supervisión y control
- **Observadores Internacionales**: Monitoreo externo

### 📱 **Optimización Móvil Completa**
- Diseño responsive mobile-first
- Controles táctiles optimizados
- Funcionalidades offline preparadas
- Rendimiento optimizado para dispositivos móviles

### 📊 **Sistema de Reportes Avanzado**
- Generador de reportes personalizados
- Múltiples formatos: PDF, Excel, Word, HTML
- Gráficos interactivos con Chart.js
- Reportes predefinidos y cronológicos
- Exportación y compartir reportes

### 📸 **Captura de Formularios con Zoom**
- **E14 (Acta de Escrutinio)**: Captura de resultados
- **E24 (Acta de Instalación)**: Documentación de apertura
- Zoom avanzado (0.5x a 5x) con controles táctiles
- Vista en pantalla completa
- Pan y zoom con gestos
- Validación de duplicados por mesa

### 🗺️ **Geolocalización Visual**
- Mapas interactivos en dashboard
- Ubicación GPS en tiempo real
- Cálculo de distancias
- Integración con Google Maps
- Compartir ubicación

### 🔍 **Observaciones e Incidencias**
- Sistema completo de observaciones electorales
- Reporte de incidencias con niveles de urgencia
- Evidencia fotográfica y multimedia
- Notificaciones automáticas a coordinadores
- Seguimiento y resolución de incidencias

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13+**
- **Flask** - Framework web
- **SQLite** - Base de datos
- **Werkzeug** - Utilidades WSGI
- **JWT** - Autenticación (opcional)

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos responsive
- **JavaScript ES6+** - Interactividad
- **Bootstrap 5** - Framework UI
- **Chart.js** - Gráficos interactivos
- **Font Awesome** - Iconografía

### APIs y Servicios
- **Geolocation API** - Ubicación GPS
- **Camera API** - Captura de fotos
- **Canvas API** - Procesamiento de imágenes
- **Web Share API** - Compartir contenido

## 📦 Instalación

### Prerrequisitos
- Python 3.13 o superior
- pip (gestor de paquetes de Python)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-electoral-caqueta.git
cd sistema-electoral-caqueta

# Instalar dependencias
pip install flask werkzeug

# Crear la base de datos
python create_complete_database.py

# Ejecutar la aplicación
python app.py
```

### Instalación con Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos
python create_complete_database.py

# Ejecutar aplicación
python app.py
```

## 🚀 Uso del Sistema

### Acceso al Sistema
1. Abrir navegador en: `http://localhost:5000`
2. Usar las credenciales demo o crear nuevos usuarios

### Usuarios Demo
- **Super Admin**: `superadmin` / `demo123`
- **Testigo Electoral**: `testigo_electoral` / `demo123`
- **Coordinador**: `coord_dept` / `demo123`

### Rutas Principales
- **Dashboard General**: `/dashboard`
- **Dashboard por Rol**: `/dashboard/{rol}`
- **Testigo Electoral**: `/dashboard/testigo_electoral`
- **Captura E14**: `/testigo/e14`
- **Captura E24**: `/testigo/e24`
- **Observaciones**: `/testigo/observacion`
- **Incidencias**: `/testigo/incidencias`
- **Reportes**: `/testigo/reportes`

## 📱 Funcionalidades Móviles

### Controles Táctiles
- Botones optimizados (mínimo 44px)
- Gestos de zoom y pan
- Navegación por swipe
- Formularios mobile-friendly

### Captura de Fotos
- Acceso a cámara del dispositivo
- Zoom con pellizco (pinch-to-zoom)
- Rotación automática
- Compresión optimizada

### Geolocalización
- GPS de alta precisión
- Modo offline preparado
- Cálculo de distancias
- Mapas interactivos

## 🗄️ Estructura de Base de Datos

### Tablas Principales
- `users` - Usuarios del sistema
- `municipios` - Municipios del Caquetá
- `puestos_votacion` - Puestos electorales
- `mesas_votacion` - Mesas de votación
- `observaciones` - Observaciones electorales
- `incidencias` - Incidencias reportadas
- `e14_capturas` - Formularios E14 capturados
- `notificaciones` - Sistema de notificaciones

### Relaciones
- Usuarios asignados a municipios, puestos y mesas
- Observaciones e incidencias vinculadas a ubicaciones
- Sistema de auditoría completo

## 🔧 Configuración

### Variables de Entorno
```bash
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-secreto-aqui
DATABASE_URL=sqlite:///caqueta_electoral.db
FLASK_ENV=development
```

### Configuración de Producción
```python
# Para producción, cambiar en app.py:
app.run(debug=False, host='0.0.0.0', port=80)
```

## 📊 APIs Disponibles

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Usuario actual

### Ubicación
- `GET /api/user/location/{user_id}` - Ubicación del usuario
- `GET /api/mesas/puesto/{puesto_id}` - Mesas por puesto

### Formularios E14
- `GET /api/e14/validar-mesa/{mesa_id}` - Validar duplicados
- `POST /api/e14/capturar` - Capturar E14

### Observaciones e Incidencias
- `GET/POST /api/observaciones` - CRUD observaciones
- `GET/POST /api/incidencias` - CRUD incidencias

### Sistema
- `GET /api/system/info` - Información del sistema
- `GET /api/health` - Estado del sistema

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests de funcionalidad completa
python test_complete_functionality.py

# Tests de APIs
python test_apis.py
```

### Tests Incluidos
- Validación de rutas
- Funcionalidad de base de datos
- APIs RESTful
- Autenticación
- Captura de formularios

## 📁 Estructura del Proyecto

```
sistema-electoral-caqueta/
├── app.py                          # Aplicación principal
├── api_endpoints.py                # Endpoints de API
├── create_complete_database.py     # Creación de BD
├── recreate_database.py           # Recreación de BD
├── requirements.txt               # Dependencias
├── README.md                     # Documentación
├── static/                       # Archivos estáticos
│   ├── css/
│   │   ├── base.css             # Estilos base
│   │   ├── mobile-responsive.css # Estilos móviles
│   │   └── roles/               # Estilos por rol
│   └── js/
│       └── base.js              # JavaScript base
├── templates/                    # Templates HTML
│   ├── base.html               # Template base
│   ├── dashboard.html          # Dashboard general
│   ├── roles/                  # Templates por rol
│   │   └── testigo_electoral/  # Testigo electoral
│   │       ├── dashboard.html
│   │       ├── e14.html        # Captura E14
│   │       ├── e24.html        # Captura E24
│   │       ├── observaciones.html
│   │       ├── incidencias.html
│   │       ├── reportes.html
│   │       └── resultados.html
│   └── components/             # Componentes reutilizables
└── .kiro/                      # Especificaciones del proyecto
    └── specs/
        └── funcionalidad-completa-sistema/
```

## 🤝 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- Seguir PEP 8 para Python
- Comentarios en español
- Tests para nuevas funcionalidades
- Documentación actualizada

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo de Desarrollo

- **Desarrollador Principal**: Sistema desarrollado con Kiro AI
- **Cliente**: Departamento del Caquetá
- **Propósito**: Modernización de procesos electorales

## 📞 Soporte

Para soporte técnico o consultas:
- **Email**: soporte@sistema-electoral-caqueta.gov.co
- **Documentación**: Ver carpeta `/docs`
- **Issues**: Usar el sistema de issues de GitHub

## 🔄 Changelog

### v1.0.0 (2024-11-06)
- ✅ Sistema completo multi-rol
- ✅ Captura E14 y E24 con zoom
- ✅ Sistema de reportes avanzado
- ✅ Geolocalización visual
- ✅ Optimización móvil completa
- ✅ Observaciones e incidencias
- ✅ APIs RESTful completas
- ✅ Base de datos completa
- ✅ Sistema de autenticación
- ✅ Validaciones y seguridad

## 🎯 Roadmap

### Próximas Versiones
- [ ] Integración con sistemas externos
- [ ] Notificaciones push
- [ ] Modo offline completo
- [ ] Análisis de datos con IA
- [ ] Integración blockchain para auditoría
- [ ] App móvil nativa

---

**Sistema Electoral ERP - Caquetá** | Desarrollado con ❤️ para la democracia colombiana