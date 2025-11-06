// JavaScript específico para Coordinador Electoral

document.addEventListener('DOMContentLoaded', function() {
    initializeCoordinatorDashboard();
    initializeCharts();
    initializeRealTimeUpdates();
});

// Inicializar dashboard del coordinador
function initializeCoordinatorDashboard() {
    console.log('Inicializando dashboard de Coordinador Electoral');
    
    // Configurar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar animaciones de entrada
    animateCards();
    
    // Configurar actualizaciones automáticas
    setInterval(updateMetrics, 30000); // Actualizar cada 30 segundos
}

// Inicializar gráficos
function initializeCharts() {
    // Gráfico de progreso de procesos electorales
    const ctx = document.getElementById('processProgressChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
                datasets: [{
                    label: 'Procesos Completados',
                    data: [12, 19, 15, 25, 22, 30],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Procesos en Curso',
                    data: [8, 12, 18, 15, 20, 25],
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Progreso Mensual de Procesos Electorales'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }
}

// Animar cards al cargar
function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Actualizar métricas en tiempo real
function updateMetrics() {
    fetch('/api/coordinator/metrics')
        .then(response => response.json())
        .then(data => {
            updateMetricCard('procesos_activos', data.procesos_activos);
            updateMetricCard('mesas_configuradas', data.mesas_configuradas);
            updateMetricCard('candidatos_registrados', data.candidatos_registrados);
            updateMetricCard('reportes_pendientes', data.reportes_pendientes);
        })
        .catch(error => {
            console.error('Error actualizando métricas:', error);
        });
}

// Actualizar card de métrica individual
function updateMetricCard(metric, value) {
    const element = document.querySelector(`[data-metric="${metric}"]`);
    if (element) {
        const currentValue = parseInt(element.textContent);
        if (currentValue !== value) {
            element.style.transform = 'scale(1.1)';
            element.textContent = value;
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

// Configurar actualizaciones en tiempo real
function initializeRealTimeUpdates() {
    // Simular actualizaciones en tiempo real
    setInterval(() => {
        updateTaskList();
        updateNotifications();
    }, 60000); // Actualizar cada minuto
}

// Actualizar lista de tareas
function updateTaskList() {
    fetch('/api/coordinator/tasks')
        .then(response => response.json())
        .then(data => {
            const taskList = document.querySelector('.list-group');
            if (taskList && data.tasks) {
                // Actualizar tareas pendientes
                updateTaskItems(data.tasks);
            }
        })
        .catch(error => {
            console.error('Error actualizando tareas:', error);
        });
}

// Actualizar elementos de tarea
function updateTaskItems(tasks) {
    const taskContainer = document.querySelector('.list-group');
    if (!taskContainer) return;
    
    taskContainer.innerHTML = '';
    
    tasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = 'list-group-item d-flex justify-content-between align-items-center';
        taskElement.innerHTML = `
            ${task.description}
            <span class="badge bg-${task.priority === 'urgent' ? 'danger' : task.priority === 'pending' ? 'warning' : 'info'} rounded-pill">
                ${task.priority === 'urgent' ? 'Urgente' : task.priority === 'pending' ? 'Pendiente' : 'En Proceso'}
            </span>
        `;
        taskContainer.appendChild(taskElement);
    });
}

// Actualizar notificaciones
function updateNotifications() {
    fetch('/api/coordinator/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                showNotification(data.notifications[0]);
            }
        })
        .catch(error => {
            console.error('Error actualizando notificaciones:', error);
        });
}

// Mostrar notificación
function showNotification(notification) {
    const toast = document.createElement('div');
    toast.className = 'toast position-fixed top-0 end-0 m-3';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-bell text-primary me-2"></i>
            <strong class="me-auto">Sistema Electoral</strong>
            <small class="text-muted">ahora</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${notification.message}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover el toast después de que se oculte
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toast);
    });
}

// Funciones de acción rápida
function createNewProcess() {
    window.location.href = '/electoral/create';
}

function registerCandidate() {
    window.location.href = '/candidates/create';
}

function generateReport() {
    window.location.href = '/reports/generate';
}

function monitorProcesses() {
    window.location.href = '/electoral/monitor';
}

// Exportar funciones para uso global
window.CoordinatorDashboard = {
    updateMetrics,
    createNewProcess,
    registerCandidate,
    generateReport,
    monitorProcesses
};