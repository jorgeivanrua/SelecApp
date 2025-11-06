/**
 * JavaScript específico para Super Admin
 * Funcionalidades avanzadas de administración
 */

const SuperAdmin = {
    // Configuración específica
    config: {
        refreshInterval: 30000, // 30 segundos
        chartColors: {
            primary: '#1e293b',
            secondary: '#475569',
            accent: '#f59e0b',
            success: '#10b981',
            danger: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        }
    },
    
    // Estado de la aplicación
    state: {
        charts: {},
        intervals: [],
        activeFilters: {}
    }
};

// Inicialización específica para Super Admin
document.addEventListener('DOMContentLoaded', function() {
    if (document.body.classList.contains('super-admin')) {
        initializeSuperAdmin();
    }
});

/**
 * Inicializar funcionalidades de Super Admin
 */
function initializeSuperAdmin() {
    setupDashboardCharts();
    setupRealTimeUpdates();
    setupAdvancedFilters();
    setupSystemMonitoring();
    setupBulkActions();
    setupKeyboardShortcuts();
}

/**
 * Configurar gráficos del dashboard
 */
function setupDashboardCharts() {
    // Gráfico de actividad del sistema
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        SuperAdmin.state.charts.activity = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Usuarios Activos',
                    data: [],
                    borderColor: SuperAdmin.config.chartColors.accent,
                    backgroundColor: SuperAdmin.config.chartColors.accent + '20',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Operaciones',
                    data: [],
                    borderColor: SuperAdmin.config.chartColors.info,
                    backgroundColor: SuperAdmin.config.chartColors.info + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        // Cargar datos iniciales
        loadActivityData();
    }
    
    // Gráfico de distribución de usuarios por rol
    const rolesCtx = document.getElementById('rolesChart');
    if (rolesCtx) {
        SuperAdmin.state.charts.roles = new Chart(rolesCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        SuperAdmin.config.chartColors.primary,
                        SuperAdmin.config.chartColors.accent,
                        SuperAdmin.config.chartColors.success,
                        SuperAdmin.config.chartColors.info,
                        SuperAdmin.config.chartColors.warning,
                        SuperAdmin.config.chartColors.danger
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        loadRolesData();
    }
}

/**
 * Configurar actualizaciones en tiempo real
 */
function setupRealTimeUpdates() {
    // Actualizar métricas cada 30 segundos
    const metricsInterval = setInterval(() => {
        updateDashboardMetrics();
    }, SuperAdmin.config.refreshInterval);
    
    SuperAdmin.state.intervals.push(metricsInterval);
    
    // Actualizar gráficos cada minuto
    const chartsInterval = setInterval(() => {
        updateDashboardCharts();
    }, 60000);
    
    SuperAdmin.state.intervals.push(chartsInterval);
    
    // Verificar alertas cada 2 minutos
    const alertsInterval = setInterval(() => {
        checkSystemAlerts();
    }, 120000);
    
    SuperAdmin.state.intervals.push(alertsInterval);
}

/**
 * Actualizar métricas del dashboard
 */
function updateDashboardMetrics() {
    fetch('/api/super-admin/metrics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateMetricCards(data.data);
            }
        })
        .catch(error => {
            console.error('Error actualizando métricas:', error);
        });
}

/**
 * Actualizar cards de métricas
 */
function updateMetricCards(metrics) {
    Object.keys(metrics).forEach(key => {
        const element = document.querySelector(`[data-metric="${key}"]`);
        if (element) {
            const currentValue = parseInt(element.textContent);
            const newValue = metrics[key];
            
            // Animar cambio de valor
            animateValue(element, currentValue, newValue, 1000);
            
            // Agregar indicador de cambio
            const change = newValue - currentValue;
            if (change !== 0) {
                showMetricChange(element, change);
            }
        }
    });
}

/**
 * Animar cambio de valor
 */
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

/**
 * Mostrar indicador de cambio en métrica
 */
function showMetricChange(element, change) {
    const indicator = document.createElement('span');
    indicator.className = `metric-change ${change > 0 ? 'positive' : 'negative'}`;
    indicator.innerHTML = `<i class="fas fa-arrow-${change > 0 ? 'up' : 'down'}"></i> ${Math.abs(change)}`;
    
    const parent = element.closest('.metric-card');
    if (parent) {
        const existing = parent.querySelector('.metric-change');
        if (existing) existing.remove();
        
        parent.appendChild(indicator);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            indicator.remove();
        }, 5000);
    }
}

/**
 * Cargar datos de actividad
 */
function loadActivityData() {
    fetch('/api/super-admin/activity-data')
        .then(response => response.json())
        .then(data => {
            if (data.success && SuperAdmin.state.charts.activity) {
                SuperAdmin.state.charts.activity.data.labels = data.data.labels;
                SuperAdmin.state.charts.activity.data.datasets[0].data = data.data.users;
                SuperAdmin.state.charts.activity.data.datasets[1].data = data.data.operations;
                SuperAdmin.state.charts.activity.update();
            }
        });
}

/**
 * Cargar datos de roles
 */
function loadRolesData() {
    fetch('/api/super-admin/roles-data')
        .then(response => response.json())
        .then(data => {
            if (data.success && SuperAdmin.state.charts.roles) {
                SuperAdmin.state.charts.roles.data.labels = data.data.labels;
                SuperAdmin.state.charts.roles.data.datasets[0].data = data.data.values;
                SuperAdmin.state.charts.roles.update();
            }
        });
}

/**
 * Actualizar gráficos del dashboard
 */
function updateDashboardCharts() {
    loadActivityData();
    loadRolesData();
}

/**
 * Verificar alertas del sistema
 */
function checkSystemAlerts() {
    fetch('/api/super-admin/system-alerts')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data.length > 0) {
                updateAlertsPanel(data.data);
                
                // Mostrar notificaciones para alertas críticas
                data.data.forEach(alert => {
                    if (alert.severity === 'critical') {
                        showNotification(alert.message, 'danger', 10000);
                    }
                });
            }
        });
}

/**
 * Actualizar panel de alertas
 */
function updateAlertsPanel(alerts) {
    const alertsContainer = document.querySelector('.alerts-container');
    if (alertsContainer) {
        alertsContainer.innerHTML = '';
        
        alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert-admin alert-${alert.type} mb-2`;
            alertElement.innerHTML = `
                <small><strong>${alert.title}</strong></small><br>
                <small>${alert.message}</small>
                <small class="text-muted d-block mt-1">${formatDateTime(alert.timestamp)}</small>
            `;
            alertsContainer.appendChild(alertElement);
        });
    }
}

/**
 * Configurar filtros avanzados
 */
function setupAdvancedFilters() {
    // Filtro de fecha
    const dateFilters = document.querySelectorAll('[data-date-filter]');
    dateFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            const filterType = this.getAttribute('data-date-filter');
            SuperAdmin.state.activeFilters[filterType] = this.value;
            applyFilters();
        });
    });
    
    // Filtro de estado
    const statusFilters = document.querySelectorAll('[data-status-filter]');
    statusFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            SuperAdmin.state.activeFilters.status = this.value;
            applyFilters();
        });
    });
    
    // Búsqueda avanzada
    const searchInput = document.querySelector('#advancedSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            SuperAdmin.state.activeFilters.search = this.value;
            applyFilters();
        }, 500));
    }
}

/**
 * Aplicar filtros
 */
function applyFilters() {
    const params = new URLSearchParams(SuperAdmin.state.activeFilters);
    
    // Actualizar URL sin recargar página
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Recargar datos filtrados
    loadFilteredData();
}

/**
 * Cargar datos filtrados
 */
function loadFilteredData() {
    const params = new URLSearchParams(SuperAdmin.state.activeFilters);
    
    fetch(`/api/super-admin/filtered-data?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDataTables(data.data);
            }
        });
}

/**
 * Actualizar tablas de datos
 */
function updateDataTables(data) {
    // Actualizar tabla de procesos
    const processesTable = document.querySelector('#processesTable tbody');
    if (processesTable && data.processes) {
        processesTable.innerHTML = '';
        data.processes.forEach(process => {
            const row = createProcessRow(process);
            processesTable.appendChild(row);
        });
    }
    
    // Actualizar tabla de usuarios
    const usersTable = document.querySelector('#usersTable tbody');
    if (usersTable && data.users) {
        usersTable.innerHTML = '';
        data.users.forEach(user => {
            const row = createUserRow(user);
            usersTable.appendChild(row);
        });
    }
}

/**
 * Crear fila de proceso
 */
function createProcessRow(process) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <strong>${process.nombre}</strong><br>
            <small class="text-muted">${formatDate(process.fecha_inicio)}</small>
        </td>
        <td>${process.tipo_eleccion}</td>
        <td>
            <span class="badge bg-${process.estado === 'activo' ? 'success' : 'warning'}">
                ${process.estado.charAt(0).toUpperCase() + process.estado.slice(1)}
            </span>
        </td>
        <td>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar" style="width: ${process.progreso}%"></div>
            </div>
            <small class="text-muted">${process.progreso}%</small>
        </td>
        <td>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary" onclick="viewProcess(${process.id})" title="Ver">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-outline-secondary" onclick="editProcess(${process.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-outline-danger" onclick="deleteProcess(${process.id})" title="Eliminar" data-confirm="¿Estás seguro de eliminar este proceso?">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    return row;
}

/**
 * Configurar monitoreo del sistema
 */
function setupSystemMonitoring() {
    // Monitor de rendimiento
    const performanceMonitor = document.querySelector('#performanceMonitor');
    if (performanceMonitor) {
        updatePerformanceMetrics();
        setInterval(updatePerformanceMetrics, 10000); // Cada 10 segundos
    }
    
    // Monitor de base de datos
    const dbMonitor = document.querySelector('#databaseMonitor');
    if (dbMonitor) {
        updateDatabaseMetrics();
        setInterval(updateDatabaseMetrics, 30000); // Cada 30 segundos
    }
}

/**
 * Actualizar métricas de rendimiento
 */
function updatePerformanceMetrics() {
    fetch('/api/super-admin/performance-metrics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updatePerformanceDisplay(data.data);
            }
        });
}

/**
 * Actualizar métricas de base de datos
 */
function updateDatabaseMetrics() {
    fetch('/api/super-admin/database-metrics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDatabaseDisplay(data.data);
            }
        });
}

/**
 * Configurar acciones en lote
 */
function setupBulkActions() {
    // Selección múltiple
    const selectAllCheckbox = document.querySelector('#selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.item-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActionsVisibility();
        });
    }
    
    // Checkboxes individuales
    document.addEventListener('change', function(e) {
        if (e.target.matches('.item-checkbox')) {
            updateBulkActionsVisibility();
        }
    });
    
    // Botones de acciones en lote
    const bulkActionButtons = document.querySelectorAll('[data-bulk-action]');
    bulkActionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-bulk-action');
            const selectedItems = getSelectedItems();
            
            if (selectedItems.length === 0) {
                showNotification('Selecciona al menos un elemento', 'warning');
                return;
            }
            
            executeBulkAction(action, selectedItems);
        });
    });
}

/**
 * Actualizar visibilidad de acciones en lote
 */
function updateBulkActionsVisibility() {
    const selectedCount = document.querySelectorAll('.item-checkbox:checked').length;
    const bulkActionsPanel = document.querySelector('#bulkActionsPanel');
    
    if (bulkActionsPanel) {
        if (selectedCount > 0) {
            bulkActionsPanel.style.display = 'block';
            bulkActionsPanel.querySelector('.selected-count').textContent = selectedCount;
        } else {
            bulkActionsPanel.style.display = 'none';
        }
    }
}

/**
 * Obtener elementos seleccionados
 */
function getSelectedItems() {
    const checkboxes = document.querySelectorAll('.item-checkbox:checked');
    return Array.from(checkboxes).map(checkbox => checkbox.value);
}

/**
 * Ejecutar acción en lote
 */
function executeBulkAction(action, items) {
    const confirmMessage = `¿Estás seguro de ${action} ${items.length} elemento(s)?`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    fetch('/api/super-admin/bulk-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action,
            items: items
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${action} ejecutado exitosamente`, 'success');
            location.reload(); // Recargar para mostrar cambios
        } else {
            showNotification(`Error ejecutando ${action}: ${data.error}`, 'danger');
        }
    });
}

/**
 * Configurar atajos de teclado
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Búsqueda rápida
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#quickSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + N: Nuevo elemento
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newButton = document.querySelector('[data-action="new"]');
            if (newButton) {
                newButton.click();
            }
        }
        
        // Ctrl/Cmd + R: Actualizar
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            location.reload();
        }
    });
}

/**
 * Funciones específicas de acciones
 */
function viewProcess(id) {
    window.location.href = `/super-admin/processes/${id}`;
}

function editProcess(id) {
    window.location.href = `/super-admin/processes/${id}/edit`;
}

function deleteProcess(id) {
    fetch(`/api/super-admin/processes/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Proceso eliminado exitosamente', 'success');
            location.reload();
        } else {
            showNotification('Error eliminando proceso: ' + data.error, 'danger');
        }
    });
}

/**
 * Limpiar recursos al salir
 */
window.addEventListener('beforeunload', function() {
    SuperAdmin.state.intervals.forEach(interval => {
        clearInterval(interval);
    });
});

// Exportar funciones globales específicas de Super Admin
window.SuperAdmin = SuperAdmin;
window.viewProcess = viewProcess;
window.editProcess = editProcess;
window.deleteProcess = deleteProcess;