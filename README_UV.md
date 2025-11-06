# Sistema Electoral ERP - Caquetá (UV Edition)

Sistema integral de gestión electoral para el departamento de Caquetá, Colombia. Desarrollado con Flask y arquitectura modular tipo ERP, utilizando **UV** como gestor de paquetes moderno para Python.

## 🚀 Características Principales

- **Gestión Electoral Completa**: Administración de procesos electorales, mesas de votación y resultados
- **Gestión de Candidatos**: Registro y seguimiento de candidatos y partidos políticos
- **Sistema de Usuarios**: Control de acceso basado en roles con 8 tipos de usuario diferentes
- **Reportes y Analytics**: Generación de reportes detallados y visualización de datos
- **Dashboard Personalizado**: Interfaces específicas para cada tipo de usuario con estilos únicos
- **API REST**: Endpoints completos para integración con otros sistemas
- **UI Adaptativa**: Estilos y funcionalidades específicas por rol de usuario
- **Gestión Moderna**: Utiliza UV para gestión rápida y eficiente de dependencias

## 🏗️ Arquitectura

El sistema está construido con una arquitectura modular inspirada en Frappe Framework:

```
sistema-electoral-erp/
├── pyproject.toml        # Configuración UV y dependencias
├── uv.lock              # Lock file de dependencias
├── core/                # Núcleo del sistema
│   ├── auth.py          # Autenticación y autorización
│   ├── permissions.py   # Sistema de permisos granular
│   ├── database.py      # Gestión de base de datos
│   └── api.py           # Utilidades para API REST
├── modules/             # Módulos funcionales
│   ├── electoral/       # Gestión electoral
│   ├── candidates/      # Gestión de candidatos
│   ├── users/          # Gestión de usuarios
│   ├── reports/        # Sistema de reportes
│   └── dashboard/      # Dashboards personalizados
├── templates/          # Templates HTML con estilos por rol
│   ├── base.html       # Template base
│   ├── roles/          # Templates específicos por rol
│   └── forms/          # Formularios especializados
├── static/            # Archivos estáticos
│   ├── css/roles/     # CSS específico por rol
│   └── js/roles/      # JavaScript específico por rol
└── config.py         # Configuración del sistema
```

## 👥 Roles de Usuario con UI Personalizada

Cada rol tiene su propia interfaz, colores y funcionalidades:

1. **Super Administrador** 🔴: Control total del sistema (Rojo/Azul)
2. **Administrador Departamental** 🟡: Gestión departamental (Azul/Cyan)
3. **Administrador Municipal** 🟠: Gestión municipal (Naranja/Amarillo)
4. **Coordinador Electoral** 🟢: Coordinación electoral (Verde/Teal)
5. **Jurado de Votación** 🔵: Gestión de mesas (Azul/Cyan)
6. **Testigo de Mesa** 🟣: Observación y registro (Púrpura/Rosa)
7. **Auditor Electoral** ⚫: Auditoría y verificación (Gris/Negro)
8. **Observador Internacional** 🟤: Observación internacional (Marrón/Beige)

## 🛠️ Instalación con UV

### Requisitos Previos

- Python 3.8 o superior
- UV package manager (se instala automáticamente)
- Git

### Instalación Automática (Recomendada)

```bash
# Clonar el repositorio
git clone <repository-url>
cd sistema-electoral-erp

# Ejecutar instalador automático con UV
python install_uv.py
```

Este script:
- ✅ Instala UV automáticamente si no está presente
- ✅ Configura el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Inicializa la base de datos
- ✅ Ejecuta tests de verificación

### Instalación Manual con UV

```bash
# Instalar UV (si no está instalado)
# Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Sincronizar dependencias
uv sync

# Instalar dependencias de desarrollo
uv sync --extra dev

# Configurar base de datos
uv run python initialization_service.py

# Ejecutar aplicación
uv run python app.py
```

### Comandos UV Útiles

```bash
# Agregar nueva dependencia
uv add flask-mail

# Agregar dependencia de desarrollo
uv add --dev pytest

# Remover dependencia
uv remove package-name

# Actualizar dependencias
uv sync --upgrade

# Ejecutar comando en el entorno
uv run python script.py

# Ver dependencias instaladas
uv pip list

# Crear lock file
uv lock

# Instalar desde lock file
uv sync --frozen
```

## 🚀 Uso

### Iniciar el Sistema

```bash
uv run python app.py
```

El sistema estará disponible en: http://localhost:5000

### Scripts Disponibles

```bash
# Iniciar servidor
uv run electoral-server

# Inicializar base de datos
uv run electoral-init

# Ejecutar demo
uv run electoral-demo

# Ejecutar tests
uv run electoral-test
```

### Usuarios de Demostración

| Rol | Cédula | Contraseña | Color UI |
|-----|--------|------------|----------|
| Super Administrador | 12345678 | admin123 | Rojo/Azul |
| Admin Departamental | 87654321 | admin123 | Azul/Cyan |
| Admin Municipal | 11111111 | admin123 | Naranja/Amarillo |
| Coordinador Electoral | 33333333 | coord123 | Verde/Teal |
| Jurado de Votación | 44444444 | jurado123 | Azul/Cyan |
| Testigo de Mesa | 22222222 | testigo123 | Púrpura/Rosa |

## 🎨 Características de UI por Rol

### Super Administrador
- **Colores**: Rojo y azul corporativo
- **Funciones**: Acceso completo, gestión de usuarios, configuración global
- **Dashboard**: Métricas generales del sistema, usuarios activos, logs de auditoría

### Administrador Departamental  
- **Colores**: Azul y cyan profesional
- **Funciones**: Gestión departamental, supervisión municipal, reportes regionales
- **Dashboard**: Estadísticas departamentales, municipios activos, procesos en curso

### Administrador Municipal
- **Colores**: Naranja y amarillo energético
- **Funciones**: Gestión municipal, mesas locales, candidatos municipales
- **Dashboard**: Mesas municipales, participación local, resultados por zona

### Coordinador Electoral
- **Colores**: Verde y teal coordinado
- **Funciones**: Coordinación de procesos, supervisión electoral, reportes operativos
- **Dashboard**: Procesos activos, cronogramas, tareas pendientes

### Jurado de Votación
- **Colores**: Azul y cyan confiable
- **Funciones**: Gestión de mesa, registro de votos, generación de actas
- **Dashboard**: Estado de mesa, votos registrados, candidatos, timeline de actividad

### Testigo de Mesa
- **Colores**: Púrpura y rosa distintivo
- **Funciones**: Observación, registro de incidencias, reportes de testigo
- **Dashboard**: Lista de verificación, observaciones, timeline de eventos

## 📊 Funcionalidades

### Gestión Electoral
- Creación y administración de procesos electorales
- Configuración de mesas de votación con formularios especializados
- Registro de resultados en tiempo real
- Monitoreo de participación electoral

### Gestión de Candidatos
- Registro de candidatos con formularios adaptativos
- Gestión de partidos políticos
- Seguimiento de campañas
- Validación de requisitos por cargo

### Sistema de Reportes
- Reportes de participación electoral
- Análisis de resultados por zona
- Reportes de incidencias por rol
- Exportación a PDF y Excel

### Dashboard Personalizado
- Interfaces específicas por rol con colores únicos
- Métricas en tiempo real
- Gráficos interactivos con Chart.js
- Notificaciones automáticas por rol

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///caqueta_electoral.db
JWT_SECRET_KEY=your-jwt-secret

# Configuración de correo
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=

# Redis para caché
REDIS_URL=redis://localhost:6379/0
```

### Configuración UV (pyproject.toml)

El archivo `pyproject.toml` incluye:

```toml
[project]
name = "sistema-electoral-erp"
version = "1.0.0"
description = "Sistema Electoral ERP modular para Caquetá con estilos por rol"
requires-python = ">=3.8"

dependencies = [
    "flask>=2.3.3",
    "flask-cors>=4.0.0",
    "flask-jwt-extended>=4.5.3",
    "sqlalchemy>=2.0.23",
    # ... más dependencias
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.11.0",
    "flake8>=6.1.0",
    # ... dependencias de desarrollo
]

[project.scripts]
electoral-server = "run:main"
electoral-init = "initialization_service:main"
electoral-demo = "demo:main"
electoral-test = "test_system:main"
```

## 📡 API REST

El sistema incluye una API REST completa con endpoints específicos por rol:

### Endpoints Principales

```bash
# Autenticación
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/profile

# Electoral
GET /api/electoral/processes
POST /api/electoral/processes
GET /api/electoral/mesas
POST /api/electoral/mesas

# Candidatos
GET /api/candidates
POST /api/candidates
PUT /api/candidates/{id}

# Reportes por rol
GET /api/reports/admin
GET /api/reports/municipal
GET /api/reports/testigo

# Dashboard por rol
GET /api/dashboard/super-admin
GET /api/dashboard/municipal
GET /api/dashboard/testigo
```

### Autenticación JWT

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"cedula": "12345678", "password": "admin123"}'

# Usar token
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/electoral/processes
```

## 🐳 Docker con UV

### Dockerfile Optimizado

```dockerfile
FROM python:3.11-slim

# Instalar UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configurar proyecto
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copiar código
COPY . .
EXPOSE 5000

# Ejecutar aplicación
CMD ["uv", "run", "python", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 🧪 Testing con UV

### Ejecutar Tests

```bash
# Tests completos
uv run python test_system.py

# Tests con pytest
uv run pytest

# Coverage
uv run pytest --cov=core --cov=modules

# Tests específicos por módulo
uv run pytest tests/test_electoral.py
uv run pytest tests/test_roles.py

# Tests con watch mode
uv run pytest-watch
```

### Configuración de Testing

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]

[tool.coverage.run]
source = ["core", "modules"]
omit = ["*/tests/*", "*/test_*.py"]
```

## 📈 Monitoreo y Métricas

El sistema incluye:
- Métricas de Prometheus en `/metrics`
- Logs estructurados por rol
- Monitoreo de performance por dashboard
- Alertas automáticas por tipo de usuario

```bash
# Ver métricas
curl http://localhost:5000/metrics
```

## 🔒 Seguridad

- Autenticación JWT con refresh tokens
- Control de acceso granular por rol
- Validación de entrada por formulario
- Protección CSRF
- Logs de auditoría por usuario
- Encriptación de datos sensibles

## 🚀 Despliegue en Producción

### Con Gunicorn

```bash
# Instalar gunicorn
uv add gunicorn

# Ejecutar en producción
uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Variables de Producción

```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/electoral_db
REDIS_URL=redis://localhost:6379/0
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Instalar dependencias: `uv sync --extra dev`
4. Ejecutar tests: `uv run pytest`
5. Formatear código: `uv run black .`
6. Lint código: `uv run flake8`
7. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
8. Push a la rama (`git push origin feature/AmazingFeature`)
9. Abrir Pull Request

### Herramientas de Desarrollo

```bash
# Formatear código
uv run black .

# Lint
uv run flake8

# Type checking
uv run mypy .

# Pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico:
- Email: soporte@sistema-electoral.com
- Issues: GitHub Issues
- Documentación: `/docs`

## 🗺️ Roadmap

- [x] Sistema base con UV
- [x] UI específica por rol
- [x] Dashboards personalizados
- [x] Formularios adaptativos
- [x] API REST completa
- [ ] App móvil para testigos
- [ ] Integración blockchain
- [ ] IA para detección de anomalías
- [ ] Integración con sistemas externos
- [ ] Notificaciones push por rol
- [ ] Modo offline para mesas remotas

## 🔄 Changelog

### v1.0.0 (2024-11-05)
- ✅ Migración completa a UV package manager
- ✅ UI específica por rol con colores únicos
- ✅ Dashboards personalizados por tipo de usuario
- ✅ Formularios adaptativos
- ✅ JavaScript específico por rol
- ✅ Sistema de instalación automática
- ✅ Scripts de comando personalizados
- ✅ Configuración optimizada para desarrollo y producción

---

**Sistema Electoral ERP v1.0.0** - Desarrollado con UV para la modernización electoral de Caquetá