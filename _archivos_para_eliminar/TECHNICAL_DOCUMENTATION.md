# Documentación Técnica - Dashboards Electorales

## Arquitectura del Sistema

### Estructura de Archivos
```
templates/roles/
├── testigo_electoral/dashboard.html
├── coordinador_puesto/dashboard.html
├── coordinador_municipal/dashboard.html
└── coordinador_departamental/dashboard.html
```

### Herencia de Templates
Todos los dashboards extienden de `base.html` y utilizan la siguiente estructura de bloques:

```html
{% extends "base.html" %}
{% block title %}...{% endblock %}
{% block role_styles %}...{% endblock %}
{% block body_class %}...{% endblock %}
{% block navbar_class %}...{% endblock %}
{% block brand_text %}...{% endblock %}
{% block navigation %}...{% endblock %}
{% block content %}...{% endblock %}
{% block role_scripts %}...{% endblock %}
```

## Sistema de Modales

### Implementación Base
Cada dashboard implementa su propia función de modal con el patrón:

```javascript
function mostrarModal[Role](titulo, contenido) {
    const modalHtml = `
        <div class="modal fade" id="[role]Modal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-[color] text-white">
                        <h5 class="modal-title">${titulo}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${contenido}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Limpiar modal existente
    const existingModal = document.getElementById('[role]Modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Crear y mostrar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('[role]Modal'));
    modal.show();
}
```

### Variaciones por Rol
- **Testigo Electoral**: `mostrarModalTestigo()` - Header azul (`bg-primary`)
- **Coordinador Puesto**: `mostrarModalPuesto()` - Header verde (`bg-success`)
- **Coordinador Municipal**: `mostrarModalMunicipal()` - Header azul claro (`bg-info`)
- **Coordinador Departamental**: `mostrarModalDepartamental()` - Header negro (`bg-dark`)

## Sistema de Notificaciones

### Implementación Estándar
```javascript
function mostrarNotificacion[Role](mensaje, tipo = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-danger',
        'info': 'alert-info'
    }[tipo];
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}
```

### Características
- **Posicionamiento**: Esquina superior derecha (fixed)
- **Z-index**: 1050 (sobre otros elementos)
- **Auto-dismiss**: 5 segundos
- **Tipos**: success, warning, error, info
- **Ancho mínimo**: 300px

## Sistema de Gráficos

### Chart.js Integration
Cada dashboard implementa gráficos específicos usando Chart.js:

```javascript
function inicializarGrafico() {
    const ctx = document.getElementById('[chartId]').getContext('2d');
    window.[chartInstance] = new Chart(ctx, {
        type: '[chartType]',
        data: {
            labels: [...],
            datasets: [{
                data: [...],
                backgroundColor: [...]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // Configuraciones específicas
        }
    });
}
```

### Tipos de Gráficos por Rol
- **Testigo Electoral**: Doughnut chart (`actividadChart`)
- **Coordinador Puesto**: Bar chart (`puestoChart`)
- **Coordinador Municipal**: Radar chart (`municipalChart`)
- **Coordinador Departamental**: Line chart (`departamentalChart`)

## Funciones de Actualización

### Patrón de Implementación
```javascript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard [Role] cargado');
    inicializarGrafico();
    actualizar[Estado]();
    
    // Actualizar cada X segundos
    setInterval(actualizar[Estado], [interval]);
});

function actualizar[Estado]() {
    console.log('Actualizando estado del [role]...');
    // Lógica de actualización
}
```

### Intervalos de Actualización
- **Testigo Electoral**: 120 segundos (2 minutos)
- **Coordinador Puesto**: 120 segundos (2 minutos)
- **Coordinador Municipal**: 90 segundos (1.5 minutos)
- **Coordinador Departamental**: 60 segundos (1 minuto)

## Patrones de Funciones

### Funciones Principales
Implementan modales complejos con formularios y tablas:
```javascript
function [accionPrincipal]() {
    mostrarModal[Role]('Título', `
        <div class="row">
            <div class="col-md-8">
                <!-- Contenido principal -->
            </div>
            <div class="col-md-4">
                <!-- Acciones laterales -->
            </div>
        </div>
    `);
}
```

### Funciones Auxiliares
Implementan notificaciones simples:
```javascript
function [accionAuxiliar]() { 
    mostrarNotificacion[Role]('Mensaje de acción...', 'tipo'); 
}
```

### Funciones Parametrizadas
Reciben parámetros para acciones específicas:
```javascript
function [accion](parametro) { 
    mostrarNotificacion[Role](`Accionando ${parametro}...`, 'tipo'); 
}
```

## Estilos CSS

### Clases de Rol
Cada dashboard tiene una clase específica en el body:
- `role-testigo-electoral`
- `role-coordinador-puesto`
- `role-coordinador-municipal`
- `role-coordinador-departamental`

### Colores por Rol
- **Testigo Electoral**: Azul (`bg-primary`, `navbar-dark bg-primary`)
- **Coordinador Puesto**: Verde (`bg-success`, `navbar-dark bg-success`)
- **Coordinador Municipal**: Azul claro (`bg-info`, `navbar-dark bg-info`)
- **Coordinador Departamental**: Negro (`bg-dark`, `navbar-dark bg-dark`)

## APIs y Endpoints

### Estructura de URLs
```
/dashboard/[role]  # Dashboard principal
/[role]/[seccion]  # Secciones específicas
```

### Ejemplos por Rol
```
# Testigo Electoral
/dashboard/testigo_electoral
/testigo/observacion
/testigo/reportes
/testigo/incidencias

# Coordinador de Puesto
/dashboard/coordinador_puesto
/puesto/mesas
/puesto/personal
/puesto/logistica

# Coordinador Municipal
/dashboard/coordinador_municipal
/municipal/puestos
/municipal/coordinacion
/municipal/reportes

# Coordinador Departamental
/dashboard/coordinador_departamental
/departamental/municipios
/departamental/coordinacion
/departamental/supervision
```

## Mantenimiento y Debugging

### Logging
Cada dashboard incluye logging básico:
```javascript
console.log('Dashboard [Role] cargado');
console.log('Actualizando estado del [role]...');
```

### Debugging de Modales
Para debuggear problemas con modales:
1. Verificar que el ID del modal sea único
2. Comprobar que se elimine el modal existente
3. Validar la sintaxis HTML del contenido

### Debugging de Notificaciones
Para debuggear notificaciones:
1. Verificar el z-index (debe ser 1050+)
2. Comprobar que el elemento se agregue al DOM
3. Validar el timeout de auto-dismiss

### Debugging de Gráficos
Para debuggear Chart.js:
1. Verificar que el canvas exista en el DOM
2. Comprobar que Chart.js esté cargado
3. Validar la estructura de datos
4. Verificar la configuración responsive

## Extensibilidad

### Agregar Nuevas Funciones
1. Definir la función JavaScript
2. Agregar el botón con onclick en HTML
3. Implementar modal o notificación según corresponda
4. Actualizar documentación

### Agregar Nuevos Dashboards
1. Crear archivo HTML siguiendo la estructura base
2. Implementar funciones específicas del rol
3. Definir colores y estilos únicos
4. Agregar rutas en el backend
5. Actualizar navegación

### Modificar Gráficos
1. Cambiar tipo en la configuración de Chart.js
2. Actualizar datos y labels
3. Ajustar opciones de visualización
4. Probar responsive design

---

**Versión**: 1.0
**Última Actualización**: $(Get-Date -Format "yyyy-MM-dd")
**Mantenedor**: Sistema Electoral ERP Team