// JavaScript específico para Testigo de Mesa

document.addEventListener('DOMContentLoaded', function() {
    initializeTestigoDashboard();
    initializeObservationForm();
    initializeChecklist();
    initializeRealTimeUpdates();
});

// Inicializar dashboard del testigo
function initializeTestigoDashboard() {
    console.log('Inicializando dashboard de Testigo de Mesa');
    
    // Configurar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar animaciones de entrada
    animateElements();
    
    // Configurar actualizaciones automáticas
    setInterval(updateObservations, 30000); // Actualizar cada 30 segundos
}

// Inicializar formulario de observaciones
function initializeObservationForm() {
    const observationForm = document.getElementById('observationForm');
    if (observationForm) {
        observationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitObservation();
        });
    }
}

// Inicializar lista de verificación
function initializeChecklist() {
    const checklistItems = document.querySelectorAll('.checklist-item');
    checklistItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                updateChecklistItem(item, this.checked);
            });
        }
    });
}

// Actualizar elemento de lista de verificación
function updateChecklistItem(item, checked) {
    if (checked) {
        item.classList.remove('pending');
        item.classList.add('completed');
        
        // Agregar animación de éxito
        item.style.transform = 'scale(1.05)';
        setTimeout(() => {
            item.style.transform = 'scale(1)';
        }, 200);
        
        // Registrar en el timeline
        const itemText = item.querySelector('label').textContent;
        addToEventTimeline(`Verificado: ${itemText}`, new Date().toLocaleTimeString());
    } else {
        item.classList.remove('completed');
        item.classList.add('pending');
    }
    
    // Actualizar progreso general
    updateOverallProgress();
}

// Actualizar progreso general
function updateOverallProgress() {
    const totalItems = document.querySelectorAll('.checklist-item').length;
    const completedItems = document.querySelectorAll('.checklist-item.completed').length;
    const progress = Math.round((completedItems / totalItems) * 100);
    
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = progress + '%';
        progressBar.textContent = progress + '%';
    }
    
    // Actualizar métrica de progreso
    const progressMetric = document.querySelector('[data-metric="progress"]');
    if (progressMetric) {
        progressMetric.textContent = progress + '%';
    }
}

// Enviar observación
function submitObservation() {
    const form = document.getElementById('observationForm');
    const formData = new FormData(form);
    
    // Validar formulario
    if (!formData.get('observation_type') || !formData.get('description')) {
        showAlert('Por favor complete todos los campos requeridos', 'warning');
        return;
    }
    
    // Enviar observación al servidor
    fetch('/api/witness/observation', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Observación registrada exitosamente', 'success');
            form.reset();
            
            // Agregar al timeline
            addToEventTimeline(
                `Observación: ${formData.get('observation_type')}`, 
                new Date().toLocaleTimeString()
            );
            
            // Actualizar contador de observaciones
            updateObservationCount();
        } else {
            showAlert(data.message || 'Error al registrar la observación', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de conexión al registrar la observación', 'danger');
    });
}

// Actualizar contador de observaciones
function updateObservationCount() {
    const countElement = document.querySelector('[data-metric="observations"]');
    if (countElement) {
        const currentCount = parseInt(countElement.textContent) || 0;
        countElement.textContent = currentCount + 1;
        
        // Animación de actualización
        countElement.style.transform = 'scale(1.2)';
        countElement.style.color = '#28a745';
        setTimeout(() => {
            countElement.style.transform = 'scale(1)';
            countElement.style.color = '';
        }, 300);
    }
}

// Agregar evento al timeline
function addToEventTimeline(event, time) {
    const timeline = document.querySelector('.event-timeline');
    if (timeline) {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        eventItem.innerHTML = `
            <div class="event-marker bg-success"></div>
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">${event}</h6>
                    <small class="text-muted">${time}</small>
                </div>
                <span class="badge bg-primary">Nuevo</span>
            </div>
        `;
        
        timeline.insertBefore(eventItem, timeline.firstChild);
        
        // Animación de entrada
        eventItem.style.opacity = '0';
        eventItem.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            eventItem.style.transition = 'all 0.3s ease';
            eventItem.style.opacity = '1';
            eventItem.style.transform = 'translateX(0)';
        }, 100);
        
        // Limitar a 10 elementos en el timeline
        const items = timeline.querySelectorAll('.event-item');
        if (items.length > 10) {
            timeline.removeChild(items[items.length - 1]);
        }
        
        // Remover badge "Nuevo" después de 5 segundos
        setTimeout(() => {
            const badge = eventItem.querySelector('.badge');
            if (badge) {
                badge.remove();
            }
        }, 5000);
    }
}

// Generar reporte de testigo
function generateWitnessReport() {
    if (!confirm('¿Desea generar el reporte de testigo? Incluirá todas las observaciones registradas.')) {
        return;
    }
    
    fetch('/api/witness/generate-report', {
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
        a.download = `reporte_testigo_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('Reporte generado y descargado exitosamente', 'success');
        addToEventTimeline('Reporte generado', new Date().toLocaleTimeString());
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al generar el reporte', 'danger');
    });
}

// Ver observaciones anteriores
function viewPreviousObservations() {
    fetch('/api/witness/observations')
        .then(response => response.json())
        .then(data => {
            showObservationsModal(data.observations);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar las observaciones', 'danger');
        });
}

// Mostrar modal de observaciones
function showObservationsModal(observations) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Observaciones Registradas</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Hora</th>
                                    <th>Tipo</th>
                                    <th>Descripción</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${observations.map(obs => `
                                    <tr>
                                        <td>${obs.time}</td>
                                        <td><span class="badge bg-info">${obs.type}</span></td>
                                        <td>${obs.description}</td>
                                        <td><span class="badge bg-${obs.status === 'resolved' ? 'success' : 'warning'}">${obs.status}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="button" class="btn btn-primary" onclick="generateWitnessReport()">Generar Reporte</button>
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

// Actualizar observaciones
function updateObservations() {
    fetch('/api/witness/stats')
        .then(response => response.json())
        .then(data => {
            updateMetric('observations', data.total_observations);
            updateMetric('alerts', data.alerts);
            updateMetric('progress', data.progress + '%');
        })
        .catch(error => {
            console.error('Error actualizando observaciones:', error);
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
    
    const checklistItems = document.querySelectorAll('.checklist-item');
    checklistItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.6s ease-out';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, (index + cards.length) * 100);
    });
}

// Configurar actualizaciones en tiempo real
function initializeRealTimeUpdates() {
    // Actualizar cada 30 segundos
    setInterval(() => {
        updateObservations();
    }, 30000);
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
window.TestigoMesa = {
    submitObservation,
    generateWitnessReport,
    viewPreviousObservations,
    updateObservations
};