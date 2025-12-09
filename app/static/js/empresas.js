/**
 * Módulo para la vista de Empresas
 * Gestiona la tabla de empresas, búsqueda y filtros
 */

let empresasData = [];
let empresasFiltradas = [];
let pendingFilter = null; // Almacena filtro pendiente desde dashboard

/**
 * Carga y renderiza la lista de empresas
 */
async function loadEmpresas() {
    try {
        empresasData = await EmpresasAPI.getAll();
        empresasFiltradas = [...empresasData];
        
        // Si hay un filtro pendiente desde el dashboard, aplicarlo
        if (pendingFilter) {
            const { modulo, estado } = pendingFilter;
            pendingFilter = null; // Limpiar filtro pendiente
            applyVencimientoFilter(modulo, estado);
        } else {
            renderEmpresasTable();
            Utils.showToast(`${empresasData.length} empresas cargadas`, 'success');
        }
    } catch (error) {
        console.error('Error al cargar empresas:', error);
        Utils.showToast('Error al cargar las empresas', 'error');
    }
}

/**
 * Renderiza la tabla de empresas
 */
function renderEmpresasTable() {
    const tbody = document.getElementById('empresas-tbody');

    if (empresasFiltradas.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="no-data">No se encontraron empresas</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = empresasFiltradas.map(empresa => {
        const certificado = getDocumentoStatus(empresa.certificado);
        const resolucion = getDocumentoStatus(empresa.resolucion);
        const documento = getDocumentoStatus(empresa.documento);

        return `
            <tr data-nit="${empresa.nit}">
                <td>${empresa.nit}</td>
                <td><strong>${empresa.nombre}</strong></td>
                <td>
                    <span class="badge ${Utils.getEstadoClass(empresa.estado)}">
                        ${empresa.estado}
                    </span>
                </td>
                <td>${certificado}</td>
                <td>${resolucion}</td>
                <td>${documento}</td>
                <td class="table-actions">
                    <button class="btn-icon" onclick="viewEmpresa('${empresa.nit}')" title="Ver detalles">
                        👁️
                    </button>
                    <button class="btn-icon" onclick="editEmpresa('${empresa.nit}')" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon btn-icon-danger" onclick="deleteEmpresa('${empresa.nit}', '${empresa.nombre}')" title="Eliminar">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Obtiene el HTML del estado de un documento (certificado, resolución, documento)
 * @param {object} doc - Datos del documento
 * @returns {string} HTML del estado
 */
function getDocumentoStatus(doc) {
    if (!doc || !doc.fecha_final) {
        return '<span class="badge badge-secondary">N/A</span>';
    }

    const dias = Utils.diasRestantes(doc.fecha_final);
    const prioridadClass = Utils.getPrioridadClass(dias);
    const fechaFormateada = Utils.formatDate(doc.fecha_final);
    
    let statusText = '';
    if (dias === null) {
        statusText = 'Sin fecha';
    } else if (dias < 0) {
        statusText = `Vencido (${Math.abs(dias)}d)`;
    } else {
        statusText = `${dias} días`;
    }

    const renovado = doc.renovado ? '🔄' : '';
    const facturado = doc.facturado ? '💰' : '';

    return `
        <div>
            <span class="badge ${prioridadClass}">${statusText}</span>
            <div style="font-size: 0.75rem; color: #6b7280; margin-top: 2px;">${fechaFormateada}</div>
            <div>${renovado} ${facturado}</div>
        </div>
    `;
}

/**
 * Filtra las empresas según la búsqueda y filtros aplicados
 */
function filterEmpresas() {
    const searchTerm = document.getElementById('search-empresas').value.toLowerCase();
    const estadoFilter = document.getElementById('filter-estado').value;

    empresasFiltradas = empresasData.filter(empresa => {
        // Filtro de búsqueda
        const matchSearch = !searchTerm || 
            empresa.nombre.toLowerCase().includes(searchTerm) ||
            empresa.nit.includes(searchTerm);

        // Filtro de estado
        const matchEstado = !estadoFilter || empresa.estado === estadoFilter;

        return matchSearch && matchEstado;
    });

    renderEmpresasTable();
}

/**
 * Ver detalles de una empresa
 * @param {string} nit - NIT de la empresa
 */
async function viewEmpresa(nit) {
    try {
        const empresa = await EmpresasAPI.getByNit(nit);
        showEmpresaModal(empresa);
    } catch (error) {
        console.error('Error al cargar empresa:', error);
        Utils.showToast('Error al cargar los detalles', 'error');
    }
}

/**
 * Editar una empresa
 * @param {string} nit - NIT de la empresa
 */
async function editEmpresa(nit) {
    try {
        const empresa = await EmpresasAPI.getByNit(nit);
        
        // Cambiar a la vista de formulario
        switchView('formulario');
        
        // Cargar los datos en el formulario
        loadEmpresaToForm(empresa);
        
        Utils.showToast('Editando empresa', 'info');
    } catch (error) {
        console.error('Error al cargar empresa:', error);
        Utils.showToast('Error al cargar la empresa', 'error');
    }
}

/**
 * Eliminar una empresa
 * @param {string} nit - NIT de la empresa
 * @param {string} nombre - Nombre de la empresa
 */
async function deleteEmpresa(nit, nombre) {
    if (!confirm(`¿Está seguro de eliminar la empresa "${nombre}"?`)) {
        return;
    }

    try {
        await EmpresasAPI.delete(nit);
        Utils.showToast('Empresa eliminada correctamente', 'success');
        await loadEmpresas();
    } catch (error) {
        console.error('Error al eliminar empresa:', error);
        Utils.showToast('Error al eliminar la empresa', 'error');
    }
}

/**
 * Muestra un modal con los detalles de la empresa
 * @param {object} empresa - Datos de la empresa
 */
function showEmpresaModal(empresa) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Detalles de Empresa</h2>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div class="modal-body">
                <div class="detail-section">
                    <h3>Información General</h3>
                    <p><strong>NIT:</strong> ${empresa.nit}</p>
                    <p><strong>Nombre:</strong> ${empresa.nombre}</p>
                    <p><strong>Estado:</strong> 
                        <span class="badge ${Utils.getEstadoClass(empresa.estado)}">${empresa.estado}</span>
                    </p>
                </div>

                ${renderDocumentoDetails('Certificado', empresa.certificado, '📜')}
                ${renderDocumentoDetails('Resolución', empresa.resolucion, '📋')}
                ${renderDocumentoDetails('Documento', empresa.documento, '📄')}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cerrar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
}

/**
 * Renderiza los detalles de un documento en el modal
 * @param {string} titulo - Título del documento
 * @param {object} doc - Datos del documento
 * @param {string} icon - Icono del documento
 * @returns {string} HTML de los detalles
 */
function renderDocumentoDetails(titulo, doc, icon) {
    if (!doc) {
        return `
            <div class="detail-section">
                <h3>${icon} ${titulo}</h3>
                <p class="text-muted">No registrado</p>
            </div>
        `;
    }

    const dias = Utils.diasRestantes(doc.fecha_vencimiento);
    const prioridadClass = Utils.getPrioridadClass(dias);

    return `
        <div class="detail-section">
            <h3>${icon} ${titulo}</h3>
            <p><strong>Fecha de vencimiento:</strong> ${Utils.formatDate(doc.fecha_vencimiento)}</p>
            <p><strong>Días restantes:</strong> 
                <span class="badge ${prioridadClass}">
                    ${dias !== null ? (dias < 0 ? `Vencido (${Math.abs(dias)} días)` : `${dias} días`) : 'Sin fecha'}
                </span>
            </p>
            <p><strong>Renovado:</strong> ${doc.renovado ? '✅ Sí' : '❌ No'}</p>
            <p><strong>Facturado:</strong> ${doc.facturado ? '✅ Sí' : '❌ No'}</p>
        </div>
    `;
}

/**
 * Inicializar eventos de la vista de empresas
 */
function initEmpresasView() {
    const searchInput = document.getElementById('search-empresas');
    const filterSelect = document.getElementById('filter-estado');

    if (searchInput) {
        searchInput.addEventListener('input', filterEmpresas);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterEmpresas);
    }
}

/**
 * Refresca la lista de empresas
 */
function refreshEmpresas() {
    loadEmpresas();
}

/**
 * Aplica un filtro de vencimiento desde el dashboard
 * @param {string} modulo - Tipo de módulo (certificado, resolucion, documento)
 * @param {string} estado - Estado (vencidos, por_vencer, vigentes)
 */
function applyVencimientoFilter(modulo, estado) {
    // Limpiar filtros anteriores
    document.getElementById('search-empresas').value = '';
    document.getElementById('filter-estado').value = '';
    
    // Filtrar empresas según el módulo y estado
    empresasFiltradas = empresasData.filter(empresa => {
        const doc = empresa[modulo];
        if (!doc || !doc.fecha_final) return false;
        
        const dias = Utils.diasRestantes(doc.fecha_final);
        
        if (estado === 'vencidos') {
            return dias !== null && dias < 0;
        } else if (estado === 'por_vencer') {
            return dias !== null && dias >= 0 && dias <= 30;
        } else if (estado === 'vigentes') {
            return dias !== null && dias > 30;
        }
        
        return false;
    });
    
    renderEmpresasTable();
    
    // Mostrar mensaje informativo
    const moduloNombres = {
        'certificado': 'Certificados',
        'resolucion': 'Resoluciones',
        'documento': 'Documentos'
    };
    const estadoNombres = {
        'vencidos': 'vencidos',
        'por_vencer': 'por vencer (30 días)',
        'vigentes': 'vigentes'
    };
    
    Utils.showToast(
        `Mostrando empresas con ${moduloNombres[modulo]} ${estadoNombres[estado]}: ${empresasFiltradas.length} encontradas`,
        'info'
    );
}
