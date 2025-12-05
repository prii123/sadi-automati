/**
 * Módulo para el formulario de empresas
 * Gestiona la creación y edición de empresas
 */

let isEditMode = false;
let currentNit = null;

/**
 * Inicializa el formulario de empresa
 */
function initFormulario() {
    const form = document.getElementById('empresa-form');
    
    if (!form) return;

    // Evento de submit
    form.addEventListener('submit', handleFormSubmit);

    // Eventos para mostrar/ocultar campos según checkboxes
    setupConditionalFields();

    // Reset del formulario
    form.addEventListener('reset', resetForm);
}

/**
 * Configura los campos condicionales
 */
function setupConditionalFields() {
    // Certificado
    const tieneCertificado = document.getElementById('tiene_certificado');
    const groupCertificado = document.getElementById('group-certificado');
    
    tieneCertificado.addEventListener('change', () => {
        groupCertificado.style.display = tieneCertificado.checked ? 'block' : 'none';
    });

    // Resolución
    const tieneResolucion = document.getElementById('tiene_resolucion');
    const groupResolucion = document.getElementById('group-resolucion');
    
    tieneResolucion.addEventListener('change', () => {
        groupResolucion.style.display = tieneResolucion.checked ? 'block' : 'none';
    });

    // Documento
    const tieneDocumento = document.getElementById('tiene_documento');
    const groupDocumento = document.getElementById('group-documento');
    
    tieneDocumento.addEventListener('change', () => {
        groupDocumento.style.display = tieneDocumento.checked ? 'block' : 'none';
    });
}

/**
 * Maneja el envío del formulario
 * @param {Event} event - Evento de submit
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    try {
        const formData = getFormData();

        if (isEditMode) {
            await EmpresasAPI.update(currentNit, formData);
            Utils.showToast('Empresa actualizada correctamente', 'success');
        } else {
            await EmpresasAPI.create(formData);
            Utils.showToast('Empresa creada correctamente', 'success');
        }

        resetForm();
        switchView('empresas');
        refreshEmpresas();
    } catch (error) {
        console.error('Error al guardar empresa:', error);
        Utils.showToast(error.message || 'Error al guardar la empresa', 'error');
    }
}

/**
 * Obtiene los datos del formulario
 * @returns {object} Datos del formulario
 */
function getFormData() {
    const data = {
        nit: document.getElementById('nit').value.trim(),
        nombre: document.getElementById('nombre').value.trim(),
        estado: document.getElementById('estado').value
    };

    // Certificado
    if (document.getElementById('tiene_certificado').checked) {
        data.certificado = {
            activo: 1,
            fecha_vencimiento: document.getElementById('fecha_vencimiento_certificado').value || null,
            renovado: document.getElementById('certificado_renovado').checked ? 1 : 0,
            facturado: document.getElementById('certificado_facturado').checked ? 1 : 0
        };
    } else {
        data.certificado = null;
    }

    // Resolución
    if (document.getElementById('tiene_resolucion').checked) {
        data.resolucion = {
            activo: 1,
            fecha_vencimiento: document.getElementById('fecha_vencimiento_resolucion').value || null,
            renovado: document.getElementById('resolucion_renovado').checked ? 1 : 0,
            facturado: document.getElementById('resolucion_facturado').checked ? 1 : 0
        };
    } else {
        data.resolucion = null;
    }

    // Documento
    if (document.getElementById('tiene_documento').checked) {
        data.documento = {
            activo: 1,
            fecha_vencimiento: document.getElementById('fecha_vencimiento_documento').value || null,
            renovado: document.getElementById('documento_renovado').checked ? 1 : 0,
            facturado: document.getElementById('documento_facturado').checked ? 1 : 0
        };
    } else {
        data.documento = null;
    }

    return data;
}

/**
 * Carga los datos de una empresa en el formulario para editar
 * @param {object} empresa - Datos de la empresa
 */
function loadEmpresaToForm(empresa) {
    isEditMode = true;
    currentNit = empresa.nit;

    // Información general
    document.getElementById('nit').value = empresa.nit;
    document.getElementById('nit').disabled = true; // No permitir cambiar el NIT
    document.getElementById('nombre').value = empresa.nombre;
    document.getElementById('estado').value = empresa.estado;

    // Certificado
    if (empresa.certificado && (empresa.certificado.fecha_final || empresa.certificado.activo)) {
        document.getElementById('tiene_certificado').checked = true;
        document.getElementById('group-certificado').style.display = 'block';
        
        if (empresa.certificado.fecha_final) {
            document.getElementById('fecha_vencimiento_certificado').value = formatDateForInput(empresa.certificado.fecha_final);
        }
        document.getElementById('certificado_renovado').checked = empresa.certificado.renovado === 1;
        document.getElementById('certificado_facturado').checked = empresa.certificado.facturado === 1;
    }

    // Resolución
    if (empresa.resolucion && (empresa.resolucion.fecha_final || empresa.resolucion.activo)) {
        document.getElementById('tiene_resolucion').checked = true;
        document.getElementById('group-resolucion').style.display = 'block';
        
        if (empresa.resolucion.fecha_final) {
            document.getElementById('fecha_vencimiento_resolucion').value = formatDateForInput(empresa.resolucion.fecha_final);
        }
        document.getElementById('resolucion_renovado').checked = empresa.resolucion.renovado === 1;
        document.getElementById('resolucion_facturado').checked = empresa.resolucion.facturado === 1;
    }

    // Documento
    if (empresa.documento && (empresa.documento.fecha_final || empresa.documento.activo)) {
        document.getElementById('tiene_documento').checked = true;
        document.getElementById('group-documento').style.display = 'block';
        
        if (empresa.documento.fecha_final) {
            document.getElementById('fecha_vencimiento_documento').value = formatDateForInput(empresa.documento.fecha_final);
        }
        document.getElementById('documento_renovado').checked = empresa.documento.renovado === 1;
        document.getElementById('documento_facturado').checked = empresa.documento.facturado === 1;
    }

    // Actualizar título
    document.getElementById('page-title').textContent = 'Editar Empresa';
}

/**
 * Formatea una fecha para el input type="date"
 * @param {string} isoDate - Fecha en formato ISO
 * @returns {string} Fecha en formato YYYY-MM-DD
 */
function formatDateForInput(isoDate) {
    if (!isoDate) return '';
    return isoDate.split('T')[0];
}

/**
 * Resetea el formulario
 */
function resetForm() {
    isEditMode = false;
    currentNit = null;

    const form = document.getElementById('empresa-form');
    if (form) {
        form.reset();
    }

    // Habilitar el campo NIT
    document.getElementById('nit').disabled = false;

    // Ocultar grupos condicionales
    document.getElementById('group-certificado').style.display = 'none';
    document.getElementById('group-resolucion').style.display = 'none';
    document.getElementById('group-documento').style.display = 'none';

    // Restaurar título
    document.getElementById('page-title').textContent = 'Nueva Empresa';
}

/**
 * Valida el formulario antes de enviarlo
 * @returns {boolean} True si es válido
 */
function validateForm() {
    const nit = document.getElementById('nit').value.trim();
    const nombre = document.getElementById('nombre').value.trim();

    if (!nit) {
        Utils.showToast('El NIT es obligatorio', 'error');
        return false;
    }

    if (!nombre) {
        Utils.showToast('El nombre es obligatorio', 'error');
        return false;
    }

    return true;
}
