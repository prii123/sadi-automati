/**
 * Módulo para la vista de Notificaciones
 * Muestra alertas de vencimientos próximos
 */

let notificacionesData = [];

/**
 * Carga y renderiza las notificaciones
 * @param {number} dias - Días de anticipación
 */
async function loadNotificaciones(dias = 30) {
    try {
        const response = await NotificacionesAPI.getVencimientos(dias);
        notificacionesData = Array.isArray(response) ? response : [];
        renderNotificaciones();
        Utils.showToast(`${notificacionesData.length} notificaciones encontradas`, 'success');
    } catch (error) {
        console.error('Error al cargar notificaciones:', error);
        notificacionesData = [];
        renderNotificaciones();
        Utils.showToast('Error al cargar las notificaciones', 'error');
    }
}

/**
 * Renderiza las notificaciones
 */
function renderNotificaciones() {
    const container = document.getElementById('notificaciones-container');

    if (notificacionesData.length === 0) {
        container.innerHTML = `
            <div class="no-notifications">
                <div class="no-notifications-icon">✅</div>
                <h3>No hay notificaciones pendientes</h3>
                <p>Todos los certificados, resoluciones y documentos están vigentes.</p>
            </div>
        `;
        return;
    }

    // Aplanar las notificaciones por empresa y alerta
    const alertasFlat = [];
    notificacionesData.forEach(notif => {
        notif.alertas.forEach(alerta => {
            alertasFlat.push({
                ...alerta,
                empresa: notif.empresa
            });
        });
    });

    // Agrupar por prioridad
    const criticas = alertasFlat.filter(a => a.prioridad === 'CRITICA');
    const altas = alertasFlat.filter(a => a.prioridad === 'ALTA');
    const medias = alertasFlat.filter(a => a.prioridad === 'MEDIA');

    container.innerHTML = `
        ${renderNotificacionesGroup('Críticas', criticas, 'danger')}
        ${renderNotificacionesGroup('Alta Prioridad', altas, 'warning')}
        ${renderNotificacionesGroup('Prioridad Media', medias, 'info')}
    `;
}

/**
 * Renderiza un grupo de notificaciones por prioridad
 * @param {string} titulo - Título del grupo
 * @param {Array} notificaciones - Lista de notificaciones
 * @param {string} tipo - Tipo de alerta (danger, warning, info)
 * @returns {string} HTML del grupo
 */
function renderNotificacionesGroup(titulo, notificaciones, tipo) {
    if (notificaciones.length === 0) {
        return '';
    }

    return `
        <div class="notification-group">
            <h3 class="notification-group-title notification-${tipo}">
                ${getNotificationIcon(tipo)} ${titulo} (${notificaciones.length})
            </h3>
            <div class="notification-list">
                ${notificaciones.map(n => renderNotificacion(n, tipo)).join('')}
            </div>
        </div>
    `;
}

/**
 * Renderiza una notificación individual
 * @param {object} alerta - Datos de la alerta
 * @param {string} tipo - Tipo de alerta
 * @returns {string} HTML de la notificación
 */
function renderNotificacion(alerta, tipo) {
    const tipoDoc = getTipoDocumentoIcon(alerta.tipo);
    const diasRestantes = alerta.dias_restantes !== null ? alerta.dias_restantes : null;
    const estadoRenovado = alerta.renovado ? '🔄 Renovado' : '';
    const estadoFacturado = alerta.facturado ? '💰 Facturado' : '';
    
    let diasTexto = 'Sin fecha';
    if (diasRestantes !== null) {
        if (diasRestantes < 0) {
            diasTexto = `Vencido hace ${Math.abs(diasRestantes)} días`;
        } else {
            diasTexto = `${diasRestantes} días restantes`;
        }
    }
    
    return `
        <div class="notification-card notification-card-${tipo}">
            <div class="notification-icon">${tipoDoc}</div>
            <div class="notification-content">
                <h4 class="notification-empresa">${alerta.empresa.nombre}</h4>
                <p class="notification-nit">NIT: ${alerta.empresa.nit}</p>
                <p class="notification-message">
                    <strong>${alerta.modulo}</strong><br>
                    ${alerta.motivo}
                </p>
                <div class="notification-meta">
                    ${alerta.fecha_vencimiento ? `
                        <span class="notification-date">
                            📅 Vence: ${Utils.formatDate(alerta.fecha_vencimiento)}
                        </span>
                    ` : ''}
                    <span class="badge badge-${getPrioridadBadgeColor(tipo)}">
                        ${diasTexto}
                    </span>
                </div>
                <div class="notification-status">
                    ${estadoRenovado} ${estadoFacturado}
                </div>
            </div>
            <div class="notification-actions">
                <button class="btn-icon" onclick="viewEmpresaFromNotification('${alerta.empresa.nit}')" title="Ver empresa">
                    👁️
                </button>
                <button class="btn-icon" onclick="markAsResolved('${alerta.empresa.nit}', '${alerta.tipo}', ${alerta.renovado}, ${alerta.facturado})" title="Marcar como resuelto">
                    ✅
                </button>
            </div>
        </div>
    `;
}

/**
 * Obtiene el icono según el tipo de notificación
 * @param {string} tipo - Tipo de notificación
 * @returns {string} Icono
 */
function getNotificationIcon(tipo) {
    const icons = {
        'danger': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[tipo] || 'ℹ️';
}

/**
 * Obtiene el icono según el tipo de documento
 * @param {string} tipoDoc - Tipo de documento
 * @returns {string} Icono
 */
function getTipoDocumentoIcon(tipoDoc) {
    const icons = {
        'certificado': '📜',
        'resolucion': '📋',
        'documento': '📄'
    };
    return icons[tipoDoc] || '📄';
}

/**
 * Obtiene el color del badge según la prioridad
 * @param {string} tipo - Tipo de alerta
 * @returns {string} Color del badge
 */
function getPrioridadBadgeColor(tipo) {
    const colors = {
        'danger': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return colors[tipo] || 'secondary';
}

/**
 * Ver empresa desde notificación
 * @param {string} nit - NIT de la empresa
 */
async function viewEmpresaFromNotification(nit) {
    try {
        const empresa = await EmpresasAPI.getByNit(nit);
        showEmpresaModal(empresa);
    } catch (error) {
        console.error('Error al cargar empresa:', error);
        Utils.showToast('Error al cargar los detalles', 'error');
    }
}

/**
 * Marcar notificación como resuelta
 * @param {string} nit - NIT de la empresa
 * @param {string} tipoDocumento - Tipo de documento
 * @param {boolean} renovado - Si ya está renovado
 * @param {boolean} facturado - Si ya está facturado
 */
async function markAsResolved(nit, tipoDocumento, renovado, facturado) {
    try {
        const empresa = await EmpresasAPI.getByNit(nit);
        
        // Determinar qué actualizar según el estado actual
        // Si está renovado pero no facturado, marcar como facturado
        // Si no está renovado, marcarlo como renovado
        const updateData = { ...empresa };
        
        const modulo = tipoDocumento.toLowerCase();
        
        if (updateData[modulo]) {
            if (renovado && !facturado) {
                // Ya está renovado, marcar como facturado
                updateData[modulo].facturado = 1;
                updateData[modulo].renovado = 1;
            } else {
                // No está renovado, marcarlo como renovado
                updateData[modulo].renovado = 1;
            }
        }

        await EmpresasAPI.update(nit, updateData);
        Utils.showToast('Notificación marcada como resuelta', 'success');
        await loadNotificaciones();
    } catch (error) {
        console.error('Error al marcar como resuelto:', error);
        Utils.showToast('Error al actualizar', 'error');
    }
}

/**
 * Filtrar notificaciones por días
 * @param {number} dias - Días de anticipación
 */
function filterNotificacionesByDays(dias) {
    loadNotificaciones(dias);
}

/**
 * Refresca las notificaciones
 */
function refreshNotificaciones() {
    loadNotificaciones();
}
