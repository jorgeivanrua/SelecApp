// JavaScript específico para Administrador Municipal

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminMunicipalDashboard();
    initializeMesaManagement();
    initializeCharts();
    initializeRealTimeUpdates();
});

// Inicializar dashboard del administrador municipal
function initializeAdminMunicipalDashboard() {
    console.log('Inicializando dashboard de Administrador Municipal');
    
    // Configurar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar animaciones de entrada
    animateElements();
    
    // Configurar actualizaciones automáticas
    setInterval(updateMunicipalStats, 20000); // Actualizar cada 20 segundos
}

// Inicializar gestión de mesas
function initializeMesaManagement() {
    const mesaItems = document.querySelectorAll('.mesa-item');
    mesaItems.forEach(item => {
        item.addEventListener('click', function() {
            const mesaId = this.dataset.mesaId;
            if (mesaId) {
                showMesaDetails(mesaId);
            }
        });
    });
}

// Mostrar detalles de mesa
function showMesaDetails(mesaId) {
    fetch(`/api/municipal/mesa/${mesaId}`)
        .then(response => response.json())
        .then(data => {
            showMesaModal(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar los detalles de la mesa', 'danger');
        });
}

// Mostrar modal de mesa
function showMesaModal(mesaData) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Mesa ${mesaData.numero} - ${mesaData.puesto_votacion}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Información General</h6>
                            <p><strong>Estado:</strong> 
                                <span class="badge bg-${mesaData.estado === 'activa' ? 'success' : 'warning'}">
                                    ${mesaData.estado}
                                </span>
                            </p>
                            <p><strong>Votantes Habilitados:</strong> ${mesaData.votantes_habilitados}</p>
                            <p><strong>Votos Registrados:</strong> ${mesaData.votos_registrados}</p>
                            <p><strong>Participación:</strong> ${mesaData.participacion}%</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Personal Asignado</h6>
                            <p><strong>Jurado Principal:</strong> ${mesaData.jurado_principal || 'No asignado'}</p>
                            <p><strong>Jurado Suplente:</strong> ${mesaData.jurado_suplente || 'No asignado'}</p>
                            <p><strong>Testigos:</strong> ${mesaData.testigos ? mesaData.testigos.length : 0}</p>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6>Resultados Parciales</h6>
                            <canvas id="mesaResultsChart" height="200"></canvas>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="button" class="btn btn-primary" onclick="generateMesaReport('${mesaData.id}')">
                        Generar Reporte
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Crear gráfico de resultados de mesa
    setTimeout(() => {
        createMesaResultsChart(mesaData.resultados);
    }, 500);
    
    // Remover modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Crear gráfico de resultados de mesa
function createMesaResultsChart(resultados) {
    const ctx = document.getElementById('mesaResultsChart');
    if (ctx && resultados) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: resultados.map(r => r.candidato),
                datasets: [{
                    label: 'Votos',
                    data: resultados.map(r => r.votos),
                    backgroundColor: [
                        '#fd7e14',
                        '#ffc107',
                        '#20c997',
                        '#17a2b8',
                        '#6f42c1',
                        '#e83e8c'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Inicializar gráficos municipales
function initializeCharts() {
    // Gráfico de participación por zona
    const participationCtx = document.getElementById('participationChart');
    if (participationCtx) {
        new Chart(participationCtx, {
            type: 'doughnut',
            data: {
                labels: ['Zona Urbana', 'Zona Rural', 'Zona Periférica'],
                datasets: [{
                    data: [65, 45, 55],
                    backgroundColor: ['#fd7e14', '#ffc107', '#20c997']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Participación por Zona (%)'
                    }
                }
            }
        });
    }
    
    // Gráfico de progreso de mesas
    const progressCtx = document.getElementById('mesasProgressChart');
    if (progressCtx) {
        new Chart(progressCtx, {
            type: 'line',
            data: {
                labels: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'],
                datasets: [{
                    label: 'Mesas Activas',
                    data: [15, 28, 35, 42, 38, 45],
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
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
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Actividad de Mesas Durante el Día'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Crear nueva mesa
function createNewMesa() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Crear Nueva Mesa</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="newMesaForm">
                        <div class="mb-3">
                            <label for="mesaNumero" class="form-label">Número de Mesa</label>
                            <input type="text" class="form-control" id="mesaNumero" name="numero" required>
                        </div>
                        <div class="mb-3">
                            <label for="puestoVotacion" class="form-label">Puesto de Votación</label>
                            <input type="text" class="form-control" id="puestoVotacion" name="puesto_votacion" required>
                        </div>
                        <div class="mb-3">
                            <label for="votantesHabilitados" class="form-label">Votantes Habilitados</label>
                            <input type="number" class="form-control" id="votantesHabilitados" name="votantes_habilitados" required>
                        </div>
                        <div class="mb-3">
                            <label for="zona" class="form-label">Zona</label>
                            <select class="form-select" id="zona" name="zona" required>
                                <option value="">Seleccionar zona...</option>
                                <option value="urbana">Urbana</option>
                                <option value="rural">Rural</option>
                                <option value="periferica">Periférica</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="submitNewMesa()">Crear Mesa</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remover modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Enviar nueva mesa
function submitNewMesa() {
    const form = document.getElementById('newMesaForm');
    const formData = new FormData(form);
    
    fetch('/api/municipal/mesa/create', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Mesa creada exitosamente', 'success');
            const modal = bootstrap.Modal.getInstance(document.querySelector('.modal'));
            modal.hide();
            
            // Actualizar lista de mesas
            updateMesasList();
        } else {
            showAlert(data.message || 'Error al crear la mesa', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de conexión al crear la mesa', 'danger');
    });
}

// Generar reporte municipal
function generateMunicipalReport() {
    if (!confirm('¿Desea generar el reporte municipal completo?')) {
        return;
    }
    
    fetch('/api/municipal/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_municipal_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('Reporte municipal generado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al generar el reporte municipal', 'danger');
    });
}

// Generar reporte de mesa específica
function generateMesaReport(mesaId) {
    fetch(`/api/municipal/mesa/${mesaId}/report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_mesa_${mesaId}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('Reporte de mesa generado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al generar el reporte de mesa', 'danger');
    });
}

// Actualizar estadísticas municipales
function updateMunicipalStats() {
    fetch('/api/municipal/stats')
        .then(response => response.json())
        .then(data => {
            updateMetric('mesas_activas', data.mesas_activas);
            updateMetric('participacion_total', data.participacion_total + '%');
            updateMetric('votos_registrados', data.votos_registrados);
            updateMetric('incidencias', data.incidencias);
            
            // Actualizar estado de mesas
            updateMesasStatus(data.mesas_status);
        })
        .catch(error => {
            console.error('Error actualizando estadísticas municipales:', error);
        });
}

// Actualizar métrica individual
function updateMetric(metric, value) {
    const element = document.querySelector(`[data-metric="${metric}"]`);
    if (element) {
        const currentValue = element.textContent.replace('%', '');
        if (currentValue !== value.toString().replace('%', '')) {
            element.style.transform = 'scale(1.1)';
            element.textContent = value;
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

// Actualizar estado de mesas
function updateMesasStatus(mesasStatus) {
    mesasStatus.forEach(mesa => {
        const mesaElement = document.querySelector(`[data-mesa-id="${mesa.id}"]`);
        if (mesaElement) {
            const statusElement = mesaElement.querySelector('.mesa-status');
            if (statusElement) {
                statusElement.className = `mesa-status ${mesa.status}`;
            }
        }
    });
}

// Actualizar lista de mesas
function updateMesasList() {
    fetch('/api/municipal/mesas')
        .then(response => response.json())
        .then(data => {
            const mesasContainer = document.querySelector('.mesa-map');
            if (mesasContainer && data.mesas) {
                renderMesasList(data.mesas);
            }
        })
        .catch(error => {
            console.error('Error actualizando lista de mesas:', error);
        });
}

// Renderizar lista de mesas
function renderMesasList(mesas) {
    const container = document.querySelector('.mesa-map');
    if (!container) return;
    
    container.innerHTML = '';
    
    mesas.forEach(mesa => {
        const mesaElement = document.createElement('div');
        mesaElement.className = 'mesa-item';
        mesaElement.dataset.mesaId = mesa.id;
        mesaElement.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="mesa-status ${mesa.status}"></div>
                <div>
                    <strong>Mesa ${mesa.numero}</strong><br>
                    <small class="text-muted">${mesa.puesto_votacion}</small>
                </div>
            </div>
            <div class="text-end">
                <small>${mesa.votos_registrados}/${mesa.votantes_habilitados}</small><br>
                <small class="text-muted">${mesa.participacion}%</small>
            </div>
        `;
        
        mesaElement.addEventListener('click', () => showMesaDetails(mesa.id));
        container.appendChild(mesaElement);
    });
}

// Animar elementos al cargar
function animateElements() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Configurar actualizaciones en tiempo real
function initializeRealTimeUpdates() {
    // Actualizar cada 20 segundos
    setInterval(() => {
        updateMunicipalStats();
    }, 20000);
}

// Mostrar alerta
function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

// Obtener token CSRF
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Exportar funciones para uso global
window.AdminMunicipal = {
    createNewMesa,
    generateMunicipalReport,
    generateMesaReport,
    updateMunicipalStats,
    showMesaDetails
};