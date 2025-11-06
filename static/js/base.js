/**
 * JavaScript base para Sistema Electoral ERP
 * Funcionalidades comunes para todos los roles
 */

// Configuración global
const ElectoralSystem = {
    apiUrl: '/api',
    token: localStorage.getItem('auth_token'),
    currentUser: null,
    
    // Configuración de notificaciones
    notifications: {
        duration: 5000,
        position: 'top-right'
    }
};

// Inicialización del sistema
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
    setupGlobalEventListeners();
    checkAuthStatus();
});

/**
 * Inicializar sistema
 */
function initializeSystem() {
    // Configurar CSRF token si existe
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        ElectoralSystem.csrfToken = csrfToken.getAttribute('content');
    }
    
    // Configurar interceptores de fetch
    setupFetchInterceptors();
    
    // Inicializar tooltips de Bootstrap
    initializeTooltips();
    
    // Configurar auto-logout por inactividad
    setupAutoLogout();
}

/**
 * Configurar event listeners globales
 */
function setupGlobalEventListeners() {
    // Confirmar acciones destructivas
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-confirm]')) {
            const message = e.target.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Auto-submit en cambio de select
    document.addEventListener('change', function(e) {
        if (e.target.matches('[data-auto-submit]')) {
            e.target.closest('form').submit();
        }
    });
    
    // Validación en tiempo real
    document.addEventListener('input', function(e) {
        if (e.target.matches('[data-validate]')) {
            validateField(e.target);
        }
    });
}

/**
 * Verificar estado de autenticación
 */
function checkAuthStatus() {
    if (ElectoralSystem.token) {
        fetch(`${ElectoralSystem.apiUrl}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${ElectoralSystem.token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Token inválido');
            }
            return response.json();
        })
        .then(data => {
            ElectoralSystem.currentUser = data.user;
            updateUserInterface();
        })
        .catch(error => {
            console.warn('Error verificando autenticación:', error);
            // No redirigir automáticamente, dejar que el servidor maneje
        });
    }
}

/**
 * Configurar interceptores de fetch
 */
function setupFetchInterceptors() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        // Agregar token de autorización automáticamente
        if (args[1] && ElectoralSystem.token) {
            args[1].headers = args[1].headers || {};
            if (!args[1].headers['Authorization']) {
                args[1].headers['Authorization'] = `Bearer ${ElectoralSystem.token}`;
            }
        }
        
        // Agregar CSRF token si es necesario
        if (args[1] && args[1].method && ['POST', 'PUT', 'DELETE'].includes(args[1].method.toUpperCase())) {
            if (ElectoralSystem.csrfToken) {
                args[1].headers = args[1].headers || {};
                args[1].headers['X-CSRF-Token'] = ElectoralSystem.csrfToken;
            }
        }
        
        return originalFetch.apply(this, args)
            .then(response => {
                // Manejar errores de autenticación globalmente
                if (response.status === 401) {
                    handleAuthError();
                }
                return response;
            })
            .catch(error => {
                console.error('Error en petición:', error);
                throw error;
            });
    };
}

/**
 * Manejar errores de autenticación
 */
function handleAuthError() {
    localStorage.removeItem('auth_token');
    showNotification('Sesión expirada. Por favor, inicia sesión nuevamente.', 'warning');
    
    // Redirigir al login después de un breve delay
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

/**
 * Actualizar interfaz de usuario
 */
function updateUserInterface() {
    if (ElectoralSystem.currentUser) {
        // Actualizar información del usuario en la interfaz
        const userElements = document.querySelectorAll('[data-user-info]');
        userElements.forEach(element => {
            const info = element.getAttribute('data-user-info');
            if (ElectoralSystem.currentUser[info]) {
                element.textContent = ElectoralSystem.currentUser[info];
            }
        });
    }
}

/**
 * Mostrar notificación
 */
function showNotification(message, type = 'info', duration = null) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show notification-alert`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    `;
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove después del tiempo especificado
    const timeout = duration || ElectoralSystem.notifications.duration;
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, timeout);
}

/**
 * Validar campo de formulario
 */
function validateField(field) {
    const validationType = field.getAttribute('data-validate');
    let isValid = true;
    let message = '';
    
    switch (validationType) {
        case 'required':
            isValid = field.value.trim() !== '';
            message = 'Este campo es requerido';
            break;
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            isValid = emailRegex.test(field.value);
            message = 'Ingresa un email válido';
            break;
        case 'phone':
            const phoneRegex = /^[\d\s\-\+\(\)]+$/;
            isValid = phoneRegex.test(field.value) && field.value.length >= 10;
            message = 'Ingresa un teléfono válido';
            break;
        case 'cedula':
            const cedulaRegex = /^\d{8,10}$/;
            isValid = cedulaRegex.test(field.value);
            message = 'Ingresa una cédula válida (8-10 dígitos)';
            break;
        case 'number':
            isValid = !isNaN(field.value) && field.value !== '';
            message = 'Ingresa un número válido';
            break;
    }
    
    // Actualizar estado visual del campo
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Mostrar/ocultar mensaje de error
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!isValid) {
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    } else if (feedback) {
        feedback.remove();
    }
    
    return isValid;
}

/**
 * Inicializar tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Configurar auto-logout por inactividad
 */
function setupAutoLogout() {
    let inactivityTimer;
    const inactivityTime = 30 * 60 * 1000; // 30 minutos
    
    function resetTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(() => {
            showNotification('Sesión cerrada por inactividad', 'warning');
            localStorage.removeItem('auth_token');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        }, inactivityTime);
    }
    
    // Eventos que resetean el timer
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });
    
    resetTimer();
}

/**
 * Formatear números
 */
function formatNumber(number, decimals = 0) {
    return new Intl.NumberFormat('es-CO', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * Formatear fecha
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    return new Intl.DateTimeFormat('es-CO', { ...defaultOptions, ...options }).format(new Date(date));
}

/**
 * Formatear fecha y hora
 */
function formatDateTime(datetime, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat('es-CO', { ...defaultOptions, ...options }).format(new Date(datetime));
}

/**
 * Debounce function
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Cargar datos con loading state
 */
function loadData(url, options = {}) {
    const loadingElement = options.loadingElement;
    
    if (loadingElement) {
        loadingElement.classList.add('loading');
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .finally(() => {
            if (loadingElement) {
                loadingElement.classList.remove('loading');
            }
        });
}

/**
 * Exportar funciones globales
 */
window.ElectoralSystem = ElectoralSystem;
window.showNotification = showNotification;
window.validateField = validateField;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.debounce = debounce;
window.throttle = throttle;
window.loadData = loadData;