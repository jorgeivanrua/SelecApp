/**
 * JavaScript para el Dashboard del Coordinador Municipal
 * Sistema Electoral Caquetá
 */

// Variables globales
let dashboardData = {};
let availableWitnesses = [];
let availableTables = [];
let politicalParties = [];

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadPoliticalParties();
    setupEventListeners();
    
    // Actualizar datos cada 5 minutos
    setInterval(refreshDashboard, 300000);
});

/**
 * Inicializar el dashboard
 */
async function initializeDashboard() {
    showLoading();
    try {
        await loadDashboardData();
        await loadNotifications();
        updateDashboardUI();
    } catch (error) {
        console.error('Error inicializando dashboard:', error);
        showAlert('Error cargando el dashboard', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Cargar datos del dashboard
 */
async function loadDashboardData() {
    try {
        const response = await fetch('/api/coordination/dashboard');
        const result = await response.json();
        
        if (result.success) {
            dashboardData = result.data;
            return dashboardData;
        } else {
            throw new Error(result.error || 'Error cargando datos del dashboard');
        }
    } catch (error) {
        console.error('Error cargando dashboard:', error);
        throw error;
    }
}

/**
 * Actualizar la interfaz del dashboard
 */
function updateDashboardUI() {
    if (!dashboardData.coordinator_info) return;
    
    // Actualizar información del coordinador
    updateCoordinatorInfo();
    
    // Actualizar estadísticas principales
    updateMainStatistics();
    
    // Actualizar tabla de cobertura
    updateCoverageTable();
    
    // Actualizar tareas pendientes
    updatePendingTasks();
    
    // Mostrar alertas si existen
    showAlerts();
}

/**
 * Actualizar información del coordinador
 */
function updateCoordinatorInfo() {
    const info = dashboardData.coordinator_info;
    
    document.getElementById('coordinatorName').textContent = info.nombre_completo || 'Coordinador';
    document.getElementById('coordinatorFullName').textContent = info.nombre_completo || '-';
    document.getElementById('municipioName').textContent = info.municipio_nombre || '-';
    document.getElementById('coordinatorCedula').textContent = info.cedula || '-';
    document.getElementById('coordinatorTelefono').textContent = info.telefono || '-';
    document.getElementById('coordinatorEmail').textContent = info.email || '-';
    
    if (info.fecha_asignacion) {
        const fecha = new Date(info.fecha_asignacion).toLocaleDateString('es-CO');
        document.getElementById('fechaAsignacion').textContent = fecha;
    }
}

/**
 * Actualizar estadísticas principales
 */
function updateMainStatistics() {
    const stats = dashboardData.statistics;
    
    document.getElementById('totalTestigos').textContent = stats.total_testigos || 0;
    document.getElementById('testigosAsignados').textContent = stats.testigos_asignados || 0;
    document.getElementById('mesasCubiertas').textContent = stats.mesas_cubiertas || 0;
    document.getElementById('porcentajeCobertura').textContent = `${stats.porcentaje_cobertura || 0}%`;
    
    // Actualizar colores según porcentaje de cobertura
    const coverageCard = document.querySelector('#porcentajeCobertura').closest('.card');
    const percentage = stats.porcentaje_cobertura || 0;
    
    coverageCard.className = 'card text-white';
    if (percentage >= 80) {
        coverageCard.classList.add('bg-success');
    } else if (percentage >= 60) {
        coverageCard.classList.add('bg-warning');
    } else {
        coverageCard.classList.add('bg-danger');
    }
}

/**
 * Actualizar tabla de cobertura por puesto
 */
function updateCoverageTable() {
    const tbody = document.querySelector('#coverageTable tbody');
    tbody.innerHTML = '';
    
    if (!dashboardData.coverage_summary || dashboardData.coverage_summary.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No hay datos de cobertura</td></tr>';
        return;
    }
    
    dashboardData.coverage_summary.forEach(puesto => {
        const row = document.createElement('tr');
        const percentage = puesto.porcentaje_cobertura || 0;
        
        let statusBadge = '';
        let statusClass = '';
        
        if (percentage >= 80) {
            statusBadge = '<span class="badge bg-success">Completa</span>';
            statusClass = 'table-success';
        } else if (percentage >= 60) {
            statusBadge = '<span class="badge bg-warning">Parcial</span>';
            statusClass = 'table-warning';
        } else if (percentage > 0) {
            statusBadge = '<span class="badge bg-danger">Baja</span>';
            statusClass = 'table-danger';
        } else {
            statusBadge = '<span class="badge bg-secondary">Sin Cobertura</span>';
            statusClass = 'table-light';
        }
        
        row.className = statusClass;
        row.innerHTML = `
            <td>
                <strong>${puesto.puesto_nombre || 'Sin nombre'}</strong>
            </td>
            <td class="text-center">${puesto.total_mesas || 0}</td>
            <td class="text-center">${puesto.mesas_cubiertas || 0}</td>
            <td class="text-center">
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-2" style="height: 8px;">
                        <div class="progress-bar ${percentage >= 80 ? 'bg-success' : percentage >= 60 ? 'bg-warning' : 'bg-danger'}" 
                             style="width: ${percentage}%"></div>
                    </div>
                    <small class="text-muted">${percentage.toFixed(1)}%</small>
                </div>
            </td>
            <td class="text-center">${statusBadge}</td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Actualizar tareas pendientes
 */
function updatePendingTasks() {
    const container = document.getElementById('pendingTasksList');
    container.innerHTML = '';
    
    if (!dashboardData.pending_tasks || dashboardData.pending_tasks.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay tareas pendientes</p>';
        return;
    }
    
    dashboardData.pending_tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = `task-item task-priority-${getPriorityClass(task.prioridad)}`;
        
        const priorityIcon = getPriorityIcon(task.prioridad);
        const dueDate = task.fecha_limite ? new Date(task.fecha_limite).toLocaleDateString('es-CO') : 'Sin fecha';
        
        taskElement.innerHTML = `
            <div class="task-title">
                ${priorityIcon} ${task.titulo}
            </div>
            <div class="task-meta">
                <small>
                    <i class="fas fa-calendar me-1"></i>Vence: ${dueDate}
                    <span class="ms-2">
                        <i class="fas fa-tasks me-1"></i>Progreso: ${task.progreso || 0}%
                    </span>
                </small>
            </div>
        `;
        
        taskElement.addEventListener('click', () => showTaskDetails(task));
        container.appendChild(taskElement);
    });
}

/**
 * Mostrar alertas del sistema
 */
function showAlerts() {
    const stats = dashboardData.statistics;
    const alertsSection = document.getElementById('alertsSection');
    const alertsContent = document.getElementById('alertsContent');
    
    let alerts = [];
    
    // Verificar mesas sin cobertura
    if (stats.mesas_sin_cobertura > 0) {
        alerts.push({
            type: 'warning',
            icon: 'fas fa-exclamation-triangle',
            message: `${stats.mesas_sin_cobertura} mesas sin cobertura de testigos`,
            action: 'showUncoveredTables()'
        });
    }
    
    // Verificar testigos disponibles
    if (stats.testigos_disponibles === 0 && stats.mesas_sin_cobertura > 0) {
        alerts.push({
            type: 'danger',
            icon: 'fas fa-user-times',
            message: 'No hay testigos disponibles para asignar',
            action: 'showCreateWitnessModal()'
        });
    }
    
    // Verificar cobertura baja
    if (stats.porcentaje_cobertura < 50) {
        alerts.push({
            type: 'danger',
            icon: 'fas fa-chart-line',
            message: `Cobertura muy baja: ${stats.porcentaje_cobertura}%`,
            action: 'generateCoverageReport()'
        });
    }
    
    if (alerts.length > 0) {
        alertsContent.innerHTML = alerts.map(alert => `
            <div class="alert alert-${alert.type} alert-dismissible fade show" role="alert">
                <i class="${alert.icon} me-2"></i>
                ${alert.message}
                ${alert.action ? `<button type="button" class="btn btn-sm btn-outline-${alert.type} ms-2" onclick="${alert.action}">Acción</button>` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `).join('');
        
        alertsSection.style.display = 'block';
    } else {
        alertsSection.style.display = 'none';
    }
}

/**
 * Cargar notificaciones
 */
async function loadNotifications() {
    // TODO: Implementar carga de notificaciones
    const notificationCount = document.getElementById('notificationCount');
    notificationCount.textContent = '0';
}

/**
 * Cargar partidos políticos
 */
async function loadPoliticalParties() {
    try {
        const response = await fetch('/api/admin/partidos');
        const result = await response.json();
        
        if (result.success) {
            politicalParties = result.data;
            updatePartySelect();
        }
    } catch (error) {
        console.error('Error cargando partidos políticos:', error);
    }
}

/**
 * Actualizar select de partidos
 */
function updatePartySelect() {
    const select = document.getElementById('witnessParty');
    select.innerHTML = '<option value="">Seleccionar partido...</option>';
    
    politicalParties.forEach(party => {
        const option = document.createElement('option');
        option.value = party.id;
        option.textContent = `${party.nombre} (${party.sigla})`;
        select.appendChild(option);
    });
}

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Event listeners para navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                // TODO: Implementar navegación por pestañas
            }
        });
    });
}

/**
 * Mostrar modal para crear testigo
 */
function showCreateWitnessModal() {
    const modal = new bootstrap.Modal(document.getElementById('createWitnessModal'));
    document.getElementById('createWitnessForm').reset();
    modal.show();
}

/**
 * Crear nuevo testigo
 */
async function createWitness() {
    const form = document.getElementById('createWitnessForm');
    const formData = new FormData(form);
    
    const witnessData = {
        nombre_completo: document.getElementById('witnessName').value,
        cedula: document.getElementById('witnessCedula').value,
        telefono: document.getElementById('witnessPhone').value,
        email: document.getElementById('witnessEmail').value,
        direccion: document.getElementById('witnessAddress').value,
        partido_id: document.getElementById('witnessParty').value || null,
        tipo_testigo: document.getElementById('witnessType').value,
        observaciones: document.getElementById('witnessObservations').value
    };
    
    // Validar campos requeridos
    if (!witnessData.nombre_completo || !witnessData.cedula || !witnessData.telefono) {
        showAlert('Por favor complete todos los campos requeridos', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/coordination/witnesses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(witnessData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Testigo registrado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createWitnessModal')).hide();
            await refreshDashboard();
        } else {
            showAlert(result.error || 'Error registrando testigo', 'danger');
        }
    } catch (error) {
        console.error('Error creando testigo:', error);
        showAlert('Error de conexión', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Mostrar modal para asignar testigo
 */
async function showAssignWitnessModal() {
    try {
        showLoading();
        
        // Cargar testigos disponibles
        const witnessResponse = await fetch('/api/coordination/witnesses/available');
        const witnessResult = await witnessResponse.json();
        
        // Cargar mesas sin cobertura
        const tablesResponse = await fetch('/api/coordination/voting-tables?sin_cobertura=true');
        const tablesResult = await tablesResponse.json();
        
        if (witnessResult.success && tablesResult.success) {
            availableWitnesses = witnessResult.data;
            availableTables = tablesResult.data;
            
            updateWitnessSelect();
            updateTableSelect();
            
            const modal = new bootstrap.Modal(document.getElementById('assignWitnessModal'));
            modal.show();
        } else {
            showAlert('Error cargando datos para asignación', 'danger');
        }
    } catch (error) {
        console.error('Error cargando datos de asignación:', error);
        showAlert('Error de conexión', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Actualizar select de testigos
 */
function updateWitnessSelect() {
    const select = document.getElementById('assignWitnessSelect');
    select.innerHTML = '<option value="">Seleccionar testigo...</option>';
    
    availableWitnesses.forEach(witness => {
        const option = document.createElement('option');
        option.value = witness.id;
        option.textContent = `${witness.nombre_completo} (${witness.cedula})`;
        select.appendChild(option);
    });
}

/**
 * Actualizar select de mesas
 */
function updateTableSelect() {
    const select = document.getElementById('assignTableSelect');
    select.innerHTML = '<option value="">Seleccionar mesa...</option>';
    
    availableTables.forEach(table => {
        const option = document.createElement('option');
        option.value = table.id;
        option.textContent = `Mesa ${table.numero_mesa} - ${table.puesto_nombre}`;
        select.appendChild(option);
    });
}

/**
 * Asignar testigo a mesa
 */
async function assignWitness() {
    const assignmentData = {
        testigo_id: parseInt(document.getElementById('assignWitnessSelect').value),
        mesa_id: parseInt(document.getElementById('assignTableSelect').value),
        proceso_electoral_id: 1, // TODO: Obtener proceso electoral activo
        hora_inicio: document.getElementById('assignStartTime').value,
        hora_fin: document.getElementById('assignEndTime').value,
        observaciones: document.getElementById('assignObservations').value
    };
    
    // Validar campos requeridos
    if (!assignmentData.testigo_id || !assignmentData.mesa_id) {
        showAlert('Por favor seleccione testigo y mesa', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/coordination/assignments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(assignmentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Testigo asignado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignWitnessModal')).hide();
            await refreshDashboard();
        } else {
            showAlert(result.error || 'Error asignando testigo', 'danger');
        }
    } catch (error) {
        console.error('Error asignando testigo:', error);
        showAlert('Error de conexión', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Generar reporte de cobertura
 */
async function generateCoverageReport() {
    try {
        showLoading();
        const response = await fetch('/api/coordination/reports/coverage');
        const result = await response.json();
        
        if (result.success) {
            // TODO: Mostrar reporte en modal o nueva ventana
            console.log('Reporte de cobertura:', result.data);
            showAlert('Reporte generado exitosamente', 'success');
        } else {
            showAlert(result.error || 'Error generando reporte', 'danger');
        }
    } catch (error) {
        console.error('Error generando reporte:', error);
        showAlert('Error de conexión', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Mostrar mesas sin cobertura
 */
async function showUncoveredTables() {
    try {
        showLoading();
        const response = await fetch('/api/coordination/voting-tables?sin_cobertura=true');
        const result = await response.json();
        
        if (result.success) {
            // TODO: Mostrar lista de mesas sin cobertura en modal
            console.log('Mesas sin cobertura:', result.data);
            showAlert(`${result.data.length} mesas sin cobertura encontradas`, 'info');
        } else {
            showAlert(result.error || 'Error obteniendo mesas sin cobertura', 'danger');
        }
    } catch (error) {
        console.error('Error obteniendo mesas sin cobertura:', error);
        showAlert('Error de conexión', 'danger');
    } finally {
        hideLoading();
    }
}

/**
 * Refrescar dashboard
 */
async function refreshDashboard() {
    try {
        await loadDashboardData();
        updateDashboardUI();
    } catch (error) {
        console.error('Error refrescando dashboard:', error);
    }
}

/**
 * Mostrar detalles de tarea
 */
function showTaskDetails(task) {
    // TODO: Implementar modal de detalles de tarea
    console.log('Detalles de tarea:', task);
}

/**
 * Obtener clase CSS para prioridad
 */
function getPriorityClass(priority) {
    switch (priority) {
        case 1: return 'high';
        case 2: return 'medium';
        case 3: return 'low';
        default: return 'medium';
    }
}

/**
 * Obtener icono para prioridad
 */
function getPriorityIcon(priority) {
    switch (priority) {
        case 1: return '<i class="fas fa-exclamation-circle text-danger"></i>';
        case 2: return '<i class="fas fa-exclamation-triangle text-warning"></i>';
        case 3: return '<i class="fas fa-info-circle text-info"></i>';
        default: return '<i class="fas fa-circle text-secondary"></i>';
    }
}

/**
 * Mostrar alerta
 */
function showAlert(message, type = 'info') {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Mostrar indicador de carga
 */
function showLoading() {
    let loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <div class="mt-2">Cargando...</div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
    loadingOverlay.style.display = 'flex';
}

/**
 * Ocultar indicador de carga
 */
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}