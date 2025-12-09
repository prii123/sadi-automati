/**
 * Módulo para la vista del Dashboard
 * Muestra estadísticas generales y gráficos del sistema
 */

/**
 * Carga y renderiza todas las estadísticas del dashboard
 */
async function loadDashboard() {
    try {
        // Cargar estadísticas en paralelo
        const [resumen, porEstado, certificados, resoluciones, documentos] = await Promise.all([
            EstadisticasAPI.getResumen(),
            EstadisticasAPI.getPorEstado(),
            EstadisticasAPI.getCertificados(),
            EstadisticasAPI.getResoluciones(),
            EstadisticasAPI.getDocumentos()
        ]);

        // Renderizar tarjetas de estadísticas
        renderStatsCards(resumen);

        // Renderizar gráficos
        renderEstadosChart(porEstado);
        renderVencimientosChart(certificados, resoluciones, documentos);

        Utils.showToast('Dashboard cargado correctamente', 'success');
    } catch (error) {
        console.error('Error al cargar dashboard:', error);
        Utils.showToast('Error al cargar las estadísticas', 'error');
    }
}

/**
 * Renderiza las tarjetas de estadísticas principales
 * @param {object} resumen - Datos del resumen general
 */
function renderStatsCards(resumen) {
    const container = document.getElementById('stats-container');
    
    const stats = [
        {
            title: 'Total Empresas',
            value: resumen.total_empresas || 0,
            icon: '🏢',
            color: 'blue'
        },
        {
            title: 'Empresas Activas',
            value: resumen.empresas_activas || 0,
            icon: '✅',
            color: 'green'
        },
        {
            title: 'Certificados',
            value: resumen.total_certificados || 0,
            icon: '📜',
            color: 'purple'
        },
        {
            title: 'Resoluciones',
            value: resumen.total_resoluciones || 0,
            icon: '📋',
            color: 'orange'
        },
        {
            title: 'Documentos',
            value: resumen.total_documentos || 0,
            icon: '📄',
            color: 'teal'
        },
        {
            title: 'Alertas Críticas',
            value: resumen.alertas_criticas || 0,
            icon: '⚠️',
            color: 'red'
        }
    ];

    container.innerHTML = stats.map(stat => `
        <div class="stat-card stat-card-${stat.color}">
            <div class="stat-icon">${stat.icon}</div>
            <div class="stat-content">
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.title}</div>
            </div>
        </div>
    `).join('');
}

/**
 * Renderiza el gráfico de distribución por estado
 * @param {object} porEstado - Datos de empresas por estado
 */
function renderEstadosChart(porEstado) {
    const container = document.getElementById('chart-estados');
    
    const estados = [
        { label: 'Activo', value: porEstado.activo || porEstado.ACTIVO || 0, color: '#10b981' },
        { label: 'Inactivo', value: porEstado.inactivo || porEstado.INACTIVO || 0, color: '#6b7280' },
        { label: 'Suspendido', value: porEstado.suspendido || porEstado.SUSPENDIDO || 0, color: '#f59e0b' }
    ];

    const total = estados.reduce((sum, e) => sum + e.value, 0);

    if (total === 0) {
        container.innerHTML = '<p class="no-data">No hay datos disponibles</p>';
        return;
    }

    container.innerHTML = `
        <div class="chart-bars">
            ${estados.map(estado => {
                const percentage = (estado.value / total * 100).toFixed(1);
                return `
                    <div class="chart-bar-item">
                        <div class="chart-bar-label">
                            <span>${estado.label}</span>
                            <span class="chart-bar-value">${estado.value} (${percentage}%)</span>
                        </div>
                        <div class="chart-bar-track">
                            <div class="chart-bar-fill" style="width: ${percentage}%; background-color: ${estado.color};"></div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Renderiza el gráfico de vencimientos próximos
 * @param {object} certificados - Estadísticas de certificados
 * @param {object} resoluciones - Estadísticas de resoluciones
 * @param {object} documentos - Estadísticas de documentos
 */
function renderVencimientosChart(certificados, resoluciones, documentos) {
    const container = document.getElementById('chart-vencimientos');

    const vencimientos = [
        {
            tipo: 'Certificados',
            modulo: 'certificado',
            vencidos: certificados.vencidos || 0,
            por_vencer: certificados.por_vencer || 0,
            vigentes: certificados.vigentes || 0,
            icon: '📜'
        },
        {
            tipo: 'Resoluciones',
            modulo: 'resolucion',
            vencidos: resoluciones.vencidos || 0,
            por_vencer: resoluciones.por_vencer || 0,
            vigentes: resoluciones.vigentes || 0,
            icon: '📋'
        },
        {
            tipo: 'Documentos',
            modulo: 'documento',
            vencidos: documentos.vencidos || 0,
            por_vencer: documentos.por_vencer || 0,
            vigentes: documentos.vigentes || 0,
            icon: '📄'
        }
    ];

    container.innerHTML = `
        <div class="vencimientos-list">
            ${vencimientos.map(v => `
                <div class="vencimiento-item">
                    <div class="vencimiento-header">
                        <span class="vencimiento-icon">${v.icon}</span>
                        <span class="vencimiento-tipo">${v.tipo}</span>
                    </div>
                    <div class="vencimiento-stats">
                        <div class="vencimiento-stat vencimiento-danger clickable" 
                             onclick="filterEmpresasByVencimiento('${v.modulo}', 'vencidos')"
                             title="Click para ver empresas con ${v.tipo.toLowerCase()} vencidos">
                            <span class="vencimiento-stat-value">${v.vencidos}</span>
                            <span class="vencimiento-stat-label">Vencidos</span>
                        </div>
                        <div class="vencimiento-stat vencimiento-warning clickable"
                             onclick="filterEmpresasByVencimiento('${v.modulo}', 'por_vencer')"
                             title="Click para ver empresas con ${v.tipo.toLowerCase()} por vencer">
                            <span class="vencimiento-stat-value">${v.por_vencer}</span>
                            <span class="vencimiento-stat-label">Por vencer</span>
                        </div>
                        <div class="vencimiento-stat vencimiento-success clickable"
                             onclick="filterEmpresasByVencimiento('${v.modulo}', 'vigentes')"
                             title="Click para ver empresas con ${v.tipo.toLowerCase()} vigentes">
                            <span class="vencimiento-stat-value">${v.vigentes}</span>
                            <span class="vencimiento-stat-label">Vigentes</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Filtra empresas por estado de vencimiento y cambia a la vista de empresas
 * @param {string} modulo - Tipo de módulo (certificado, resolucion, documento)
 * @param {string} estado - Estado (vencidos, por_vencer, vigentes)
 */
function filterEmpresasByVencimiento(modulo, estado) {
    // Establecer el filtro pendiente ANTES de cambiar de vista
    if (typeof pendingFilter !== 'undefined') {
        pendingFilter = { modulo, estado };
    }
    
    // Cambiar a la vista de empresas (esto llamará a loadEmpresas que aplicará el filtro)
    switchView('empresas');
}

/**
 * Refresca los datos del dashboard
 */
function refreshDashboard() {
    loadDashboard();
}
