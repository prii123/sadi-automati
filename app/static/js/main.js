/**
 * Archivo principal de JavaScript
 * Gestiona la navegación y la inicialización de la aplicación
 */

// Variables globales
let currentView = 'dashboard';

/**
 * Inicializa la aplicación cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFormulario();
    initEmpresasView();
    
    // Cargar la vista inicial
    loadDashboard();
});

/**
 * Inicializa la navegación entre vistas
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = link.getAttribute('data-view');
            switchView(view);
        });
    });
}

/**
 * Cambia entre vistas
 * @param {string} viewName - Nombre de la vista a mostrar
 */
function switchView(viewName) {
    // Ocultar todas las vistas
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    // Mostrar la vista seleccionada
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.add('active');
    }

    // Actualizar navegación activa
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[data-view="${viewName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Actualizar título
    updatePageTitle(viewName);

    // Cargar datos de la vista
    loadViewData(viewName);

    currentView = viewName;
}

/**
 * Actualiza el título de la página según la vista
 * @param {string} viewName - Nombre de la vista
 */
function updatePageTitle(viewName) {
    const titles = {
        'dashboard': 'Dashboard',
        'empresas': 'Gestión de Empresas',
        'notificaciones': 'Notificaciones',
        'triggers': 'Configuración de Triggers',
        'formulario': isEditMode ? 'Editar Empresa' : 'Nueva Empresa',
        'database': 'Database Viewer'
    };

    const pageTitle = document.getElementById('page-title');
    if (pageTitle) {
        pageTitle.textContent = titles[viewName] || 'Sistema de Gestión';
    }
}

/**
 * Carga los datos de una vista
 * @param {string} viewName - Nombre de la vista
 */
function loadViewData(viewName) {
    switch (viewName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'empresas':
            loadEmpresas();
            break;
        case 'notificaciones':
            loadNotificaciones();
            break;
        case 'triggers':
            loadTriggers();
            break;
        case 'database':
            if (typeof loadDatabaseViewer === 'function') {
                loadDatabaseViewer();
            }
            break;
        case 'formulario':
            if (!isEditMode) {
                resetForm();
            }
            break;
    }
}

/**
 * Refresca los datos de la vista actual
 */
function refreshData() {
    loadViewData(currentView);
}

/**
 * Maneja errores globales
 */
window.addEventListener('error', (event) => {
    console.error('Error global:', event.error);
});

/**
 * Maneja errores de promesas no capturados
 */
window.addEventListener('unhandledrejection', (event) => {
    console.error('Promise rechazada:', event.reason);
});
