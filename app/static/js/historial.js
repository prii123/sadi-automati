/**
 * historial.js
 * Manejo del historial de ejecuciones de triggers
 */

/**
 * Cambia entre tabs de triggers
 */
function showTriggersTab(tab) {
    // Actualizar tabs
    document.querySelectorAll('.btn-tab').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.triggerTab === tab) {
            btn.classList.add('active');
        }
    });
    
    // Mostrar contenido correspondiente
    document.querySelectorAll('.triggers-tab').forEach(content => {
        content.style.display = 'none';
    });
    
    const tabContent = document.getElementById(`triggers-tab-${tab}`);
    if (tabContent) {
        tabContent.style.display = 'block';
    }
    
    // Cargar datos si es necesario
    if (tab === 'historial') {
        loadHistorial();
        loadTriggerOptionsForHistorial();
    }
}

/**
 * Carga las opciones de triggers en el filtro de historial
 */
async function loadTriggerOptionsForHistorial() {
    try {
        const response = await fetch('/api/triggers');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('historial-trigger-filter');
            const currentValue = select.value;
            
            // Limpiar opciones excepto la primera
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Agregar opciones de triggers
            data.datos.forEach(trigger => {
                const option = document.createElement('option');
                option.value = trigger.id;
                option.textContent = trigger.nombre;
                select.appendChild(option);
            });
            
            // Restaurar valor seleccionado
            if (currentValue) {
                select.value = currentValue;
            }
        }
    } catch (error) {
        console.error('Error cargando triggers para historial:', error);
    }
}

/**
 * Carga el historial de ejecuciones
 */
async function loadHistorial() {
    const container = document.getElementById('historial-container');
    if (!container) {
        console.error('Container historial-container no encontrado');
        return;
    }
    
    const triggerFilterEl = document.getElementById('historial-trigger-filter');
    const limitEl = document.getElementById('historial-limit');
    
    if (!triggerFilterEl || !limitEl) {
        console.error('Elementos de filtro no encontrados');
        return;
    }
    
    const triggerFilter = triggerFilterEl.value;
    const limit = limitEl.value;
    
    try {
        container.innerHTML = '<div class="loading">Cargando historial...</div>';
        
        let url = '/api/triggers/ejecuciones';
        let params = new URLSearchParams({ limit: limit });
        
        // Si hay un trigger específico seleccionado
        if (triggerFilter) {
            url = `/api/triggers/${triggerFilter}/ejecuciones`;
            params = new URLSearchParams({ limit: Math.min(limit, 200) });
        }
        
        console.log('Cargando historial desde:', `${url}?${params}`);
        
        const response = await fetch(`${url}?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (data.success && data.datos && data.datos.length > 0) {
            console.log(`Renderizando ${data.datos.length} ejecuciones`);
            renderHistorial(data.datos, triggerFilter);
        } else {
            console.log('No hay ejecuciones o respuesta no exitosa');
            container.innerHTML = '<div class="empty-state">📋 No hay ejecuciones registradas</div>';
        }
    } catch (error) {
        console.error('Error cargando historial:', error);
        container.innerHTML = `<div class="error-state">❌ Error cargando historial: ${error.message}</div>`;
    }
}

/**
 * Renderiza el historial de ejecuciones
 */
function renderHistorial(ejecuciones, triggerId = null) {
    const container = document.getElementById('historial-container');
    
    if (!ejecuciones || ejecuciones.length === 0) {
        container.innerHTML = '<div class="empty-state">📋 No hay ejecuciones registradas</div>';
        return;
    }
    
    console.log('Renderizando historial con', ejecuciones.length, 'ejecuciones');
    
    // Si hay un trigger seleccionado, mostrar sus estadísticas
    let html = '';
    if (triggerId) {
        html += '<div id="trigger-stats-container" class="card" style="margin-bottom: 20px;"></div>';
        loadTriggerStats(triggerId);
    }
    
    // Tabla de ejecuciones
    html += `
        <div class="card">
            <h3>Registro de Ejecuciones (${ejecuciones.length})</h3>
            <div class="table-container">
                <table class="data-table historial-table">
                    <thead>
                        <tr>
                            <th>Fecha/Hora</th>
                            <th>Trigger</th>
                            <th>Estado</th>
                            <th>Notificaciones</th>
                            <th>Empresas</th>
                            <th>Detalles</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    ejecuciones.forEach(ejecucion => {
        const fecha = formatDateTime(ejecucion.fecha_ejecucion);
        const estadoClass = ejecucion.estado === 'exitoso' ? 'success' : 'error';
        const estadoIcon = ejecucion.estado === 'exitoso' ? '✓' : '✗';
        
        html += `
            <tr>
                <td>${fecha}</td>
                <td>${escapeHtml(ejecucion.trigger_nombre || 'N/A')}</td>
                <td><span class="badge badge-${estadoClass}">${estadoIcon} ${ejecucion.estado}</span></td>
                <td class="text-center">${ejecucion.notificaciones_enviadas || 0}</td>
                <td class="text-center">${ejecucion.empresas_procesadas || 0}</td>
                <td>
                    ${ejecucion.error_mensaje ? 
                        `<span class="error-message" title="${escapeHtml(ejecucion.error_mensaje)}">⚠️ Ver error</span>` : 
                        '-'}
                </td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    console.log('Historial renderizado exitosamente');
}

/**
 * Carga las estadísticas de un trigger específico
 */
async function loadTriggerStats(triggerId) {
    try {
        const response = await fetch(`/api/triggers/${triggerId}/estadisticas`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.datos;
            const container = document.getElementById('trigger-stats-container');
            
            container.innerHTML = `
                <h3>Estadísticas del Trigger</h3>
                <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_ejecuciones}</div>
                        <div class="stat-label">Total Ejecuciones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value success">${stats.exitosas}</div>
                        <div class="stat-label">Exitosas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value error">${stats.fallidas}</div>
                        <div class="stat-label">Fallidas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.tasa_exito}%</div>
                        <div class="stat-label">Tasa de Éxito</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_notificaciones}</div>
                        <div class="stat-label">Notificaciones Enviadas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_empresas}</div>
                        <div class="stat-label">Empresas Procesadas</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

/**
 * Formatea fecha y hora para mostrar
 */
function formatDateTime(isoString) {
    if (!isoString) return '-';
    
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    // Si fue hace menos de 1 minuto
    if (diffMins < 1) return 'Hace un momento';
    
    // Si fue hace menos de 1 hora
    if (diffMins < 60) return `Hace ${diffMins} min`;
    
    // Si fue hace menos de 24 horas
    if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
    
    // Si fue hace menos de 7 días
    if (diffDays < 7) return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
    
    // Formato completo
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
