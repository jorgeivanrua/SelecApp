// JavaScript específico para Testigo de Mesa

document.addEventListener('DOMContentLoaded', function() {
    initializeTestigoDashboard();
});

function initializeTestigoDashboard() {
    console.log('Inicializando dashboard de Testigo de Mesa');
    
    // Configurar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Exportar funciones para uso global
window.TestigoMesa = {
    initializeTestigoDashboard
};