// JavaScript específico para Jurado de Votación

document.addEventListener('DOMContentLoaded', function() {
    initializeJuradoDashboard();
    initializeVotingModal();
    initializeRealTimeUpdates();
});

// Inicializar dashboard del jurado
function initializeJuradoDashboard() {
    console.log('Inicializando dashboard de Jurado de Votación');
    
    // Configurar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar animaciones de entrada
    animateElements();
    
    // Configurar actualizaciones automáticas
    setInterval(updateVotingStats, 15000); // Actualizar cada 15 segundos
    
    // Verificar estado de la mesa
    checkTableStatus();
}

// Inicializar modal de votación
function initializeVotingModal() {
    const votingModal = document.getElementById('votingModal');
    if (votingModal) {
        votingModal.addEventListener('show.bs.modal', function() {
            resetVotingForm();
        });
    }
}

// Abrir modal de votación
function openVotingModal() {
    const modal = new bootstrap.Modal(document.getElementById('votingModal'));
    modal.show();
}

// Resetear formulario de votación
function resetVotingForm() {
    const form = document.getElementById('votingForm');
    if (form) {
        form.reset();
    }
}

// Enviar voto
function submitVote() {
    const form = document.getElementById('votingForm');
    const formData = new FormData(form);
    
    // Validar formulario
    if (!formData.get('candidato')) {
        showAlert('Por favor seleccione un candidato', 'warning');
        return;
    }
    
    // Confirmar voto
    if (!confirm('¿Está seguro de registrar este voto? Esta acción no se puede deshacer.')) {
        return;
    }
    
    // Enviar voto al servidor
    fetch('/api/voting/submit', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Voto registrado exitosamente', 'success');
            closeVotingModal();
            updateVotingStats();
            addToTimeline('Voto registrado', new Date().toLocaleTimeString());
        } else {
            showAlert(data.message || 'Error al registrar el voto', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error de conexión al registrar el voto', 'danger');
    });
}

// Cerrar modal de votación
function closeVotingModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('votingModal'));
    if (modal) {
        modal.hide();
    }
}

// Ver resultados
function viewResults() {
    fetch('/api/voting/results')
        .then(response => response.json())
        .then(data => {
            showResultsModal(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar los resultados', 'danger');
        });
}

// Mostrar modal de resultados
function showResultsModal(data) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Resultados Actuales</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <canvas id="resultsChart" height="300"></canvas>
                    <div class="table-responsive mt-3">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Candidato</th>
                                    <th>Votos</th>
                                    <th>Porcentaje</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.candidates.map(candidate => `
                                    <tr>
                                        <td>${candidate.name}</td>
                                        <td>${candidate.votes}</td>
                                        <td>${candidate.percentage}%</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Crear gráfico de resultados
    setTimeout(() => {
        createResultsChart(data);
    }, 500);
    
    // Remover modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

// Crear gráfico de resultados
function createResultsChart(data) {
    const ctx = document.getElementById('resultsChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.candidates.map(c => c.name),
                datasets: [{
                    data: data.candidates.map(c => c.votes),
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#17a2b8',
                        '#6f42c1'
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
    }
}

// Generar reporte/acta
function generateReport() {
    if (!confirm('¿Desea generar el acta de votación? Asegúrese de que todos los votos estén registrados.')) {
        return;
    }
    
    fetch('/api/voting/generate-report', {
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
        a.download = `acta_mesa_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('Acta generada y descargada exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al generar el acta', 'danger');
    });
}

// Actualizar estadísticas de votación
function updateVotingStats() {
    fetch('/api/voting/stats')
        .then(response => response.json())
        .then(data => {
            updateStatCard('votos_validos', data.votos_validos);
            updateStatCard('votos_nulos', data.votos_nulos);
            updateStatCard('votos_blanco', data.votos_blanco);
            updateStatCard('participacion', data.participacion + '%');
            
            // Actualizar tabla de candidatos
            updateCandidatesTable(data.candidates);
        })
        .catch(error => {
            console.error('Error actualizando estadísticas:', error);
        });
}

// Actualizar card de estadística
function updateStatCard(stat, value) {
    const element = document.querySelector(`[data-stat="${stat}"]`);
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

// Actualizar tabla de candidatos
function updateCandidatesTable(candidates) {
    const tbody = document.querySelector('.table tbody');
    if (tbody && candidates) {
        tbody.innerHTML = '';
        
        candidates.forEach(candidate => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${candidate.name}</td>
                <td>${candidate.party}</td>
                <td>${candidate.votes}</td>
                <td>${candidate.percentage}%</td>
            `;
            tbody.appendChild(row);
        });
    }
}

// Verificar estado de la mesa
function checkTableStatus() {
    fetch('/api/voting/table-status')
        .then(response => response.json())
        .then(data => {
            updateTableStatus(data.status);
        })
        .catch(error => {
            console.error('Error verificando estado de mesa:', error);
        });
}

// Actualizar estado de la mesa
function updateTableStatus(status) {
    const statusElement = document.querySelector('.voting-status');
    if (statusElement) {
        statusElement.className = `voting-status ${status}`;
        statusElement.textContent = status === 'active' ? 'Mesa Activa' : 'Mesa Cerrada';
    }
}

// Agregar elemento al timeline
function addToTimeline(action, time) {
    const timeline = document.querySelector('.timeline');
    if (timeline) {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        timelineItem.innerHTML = `
            <div class="timeline-marker bg-success"></div>
            <div class="timeline-content">
                <h6>${action}</h6>
                <small class="text-muted">${time}</small>
            </div>
        `;
        
        timeline.insertBefore(timelineItem, timeline.firstChild);
        
        // Limitar a 5 elementos en el timeline
        const items = timeline.querySelectorAll('.timeline-item');
        if (items.length > 5) {
            timeline.removeChild(items[items.length - 1]);
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
}

// Configurar actualizaciones en tiempo real
function initializeRealTimeUpdates() {
    // Actualizar cada 15 segundos
    setInterval(() => {
        updateVotingStats();
        checkTableStatus();
    }, 15000);
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
window.JuradoVotacion = {
    openVotingModal,
    submitVote,
    viewResults,
    generateReport,
    updateVotingStats
};