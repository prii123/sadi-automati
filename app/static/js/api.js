/**
 * Módulo para consumir el API REST
 * Configuración base y funciones para interactuar con el backend
 */

// Configuración del API
const API_CONFIG = {
    baseURL: window.API_BASE_URL || 'http://localhost:5000/api',
    timeout: 10000
};

/**
 * Obtiene el token de autenticación desde cookies o localStorage
 */
function getAuthToken() {
    // console.log('🔐 getAuthToken() - Verificando Auth disponible:', typeof Auth !== 'undefined');
    
    // Usar Auth si está disponible, sino fallback a localStorage
    if (typeof Auth !== 'undefined' && Auth.getToken) {
        const token = Auth.getToken();
        // console.log('🔐 getAuthToken() - Usando Auth.getToken():', token ? token.substring(0, 20) + '...' : 'null');
        return token;
    }
    
    const tokenLocal = localStorage.getItem('token');
    // console.log('🔐 getAuthToken() - Fallback a localStorage:', tokenLocal ? tokenLocal.substring(0, 20) + '...' : 'null');
    return tokenLocal;
}

/**
 * Realiza una petición HTTP al API con autenticación
 * @param {string} endpoint - Ruta del endpoint
 * @param {object} options - Opciones de la petición (method, body, etc.)
 * @returns {Promise<object>} Respuesta del API
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    
    // console.log('📡 fetchAPI() - Endpoint:', endpoint);
    // console.log('📡 fetchAPI() - URL completa:', url);
    // console.log('📡 fetchAPI() - Auth disponible?', typeof Auth !== 'undefined');
    
    // Obtener token directamente de Auth
    let token = null;
    if (typeof Auth !== 'undefined' && Auth.getToken) {
        token = Auth.getToken();
        // console.log('✅ Token obtenido de Auth.getToken():', token ? token.substring(0, 20) + '...' : 'NULL');
    } else {
        token = localStorage.getItem('token');
        // console.log('⚠️ Fallback a localStorage:', token ? token.substring(0, 20) + '...' : 'NULL');
    }
    
    // Log para debugging
    if (token) {
        // console.log('✅ Token encontrado, enviando en Authorization header');
        // console.log('📤 Authorization: Bearer', token.substring(0, 30) + '...');
    } else {
        console.error('❌ NO HAY TOKEN - Request será rechazado');
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        ...options
    };
    
    // console.log('📋 Headers completos:', JSON.stringify(defaultOptions.headers, null, 2));

    try {
        const response = await fetch(url, defaultOptions);
        
        // Manejar errores de autenticación
        if (response.status === 401) {
            // console.error('❌ Error 401: Token inválido o expirado');
            
            // Limpiar sesión usando Auth si está disponible
            if (typeof Auth !== 'undefined' && Auth.clearSession) {
                Auth.clearSession();
            } else {
                localStorage.removeItem('token');
                localStorage.removeItem('usuario');
            }
            
            window.location.href = '/login';
            throw new Error('Sesión expirada');
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.mensaje || error.error || `Error ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error en petición API:', error);
        throw error;
    }
}

/**
 * API de Empresas
 */
const EmpresasAPI = {
    /**
     * Obtiene todas las empresas
     * @returns {Promise<Array>} Lista de empresas
     */
    async getAll() {
        const response = await fetchAPI('/empresas');
        return response.datos;
    },

    /**
     * Obtiene una empresa por NIT
     * @param {string} nit - NIT de la empresa
     * @returns {Promise<object>} Datos de la empresa
     */
    async getByNit(nit) {
        const response = await fetchAPI(`/empresas/${nit}`);
        return response.datos;
    },

    /**
     * Crea una nueva empresa
     * @param {object} empresaData - Datos de la empresa
     * @returns {Promise<object>} Empresa creada
     */
    async create(empresaData) {
        return await fetchAPI('/empresas', {
            method: 'POST',
            body: JSON.stringify(empresaData)
        });
    },

    /**
     * Actualiza una empresa existente
     * @param {string} nit - NIT de la empresa
     * @param {object} empresaData - Datos a actualizar
     * @returns {Promise<object>} Empresa actualizada
     */
    async update(nit, empresaData) {
        return await fetchAPI(`/empresas/${nit}`, {
            method: 'PUT',
            body: JSON.stringify(empresaData)
        });
    },

    /**
     * Elimina una empresa
     * @param {string} nit - NIT de la empresa
     * @returns {Promise<object>} Respuesta de eliminación
     */
    async delete(nit) {
        return await fetchAPI(`/empresas/${nit}`, {
            method: 'DELETE'
        });
    },

    /**
     * Busca empresas por nombre
     * @param {string} nombre - Nombre a buscar
     * @returns {Promise<Array>} Empresas encontradas
     */
    async searchByName(nombre) {
        const response = await fetchAPI(`/empresas/buscar/nombre?nombre=${encodeURIComponent(nombre)}`);
        return response.datos;
    },

    /**
     * Filtra empresas por estado
     * @param {string} estado - Estado (ACTIVO, INACTIVO, SUSPENDIDO)
     * @returns {Promise<Array>} Empresas filtradas
     */
    async filterByStatus(estado) {
        const response = await fetchAPI(`/empresas/filtrar/estado?estado=${estado}`);
        return response.datos;
    }
};

/**
 * API de Estadísticas
 */
const EstadisticasAPI = {
    /**
     * Obtiene el resumen general del sistema
     * @returns {Promise<object>} Estadísticas generales
     */
    async getResumen() {
        const response = await fetchAPI('/estadisticas/resumen');
        return response.datos;
    },

    /**
     * Obtiene estadísticas por estado de empresa
     * @returns {Promise<object>} Distribución por estado
     */
    async getPorEstado() {
        const response = await fetchAPI('/estadisticas/por-estado');
        return response.datos;
    },

    /**
     * Obtiene estadísticas de certificados
     * @returns {Promise<object>} Estadísticas de certificados
     */
    async getCertificados() {
        const response = await fetchAPI('/estadisticas/certificados');
        return response.datos;
    },

    /**
     * Obtiene estadísticas de resoluciones
     * @returns {Promise<object>} Estadísticas de resoluciones
     */
    async getResoluciones() {
        const response = await fetchAPI('/estadisticas/resoluciones');
        return response.datos;
    },

    /**
     * Obtiene estadísticas de documentos
     * @returns {Promise<object>} Estadísticas de documentos
     */
    async getDocumentos() {
        const response = await fetchAPI('/estadisticas/documentos');
        return response.datos;
    }
};

/**
 * API de Notificaciones
 */
const NotificacionesAPI = {
    /**
     * Obtiene todas las notificaciones de vencimientos
     * @param {number} dias - Días de anticipación (default: 30)
     * @returns {Promise<Array>} Lista de notificaciones
     */
    async getVencimientos(dias = 30) {
        const response = await fetchAPI(`/notificaciones/vencimientos?dias=${dias}`);
        return response.datos;
    },

    /**
     * Obtiene notificaciones críticas (próximas a vencer)
     * @returns {Promise<Array>} Notificaciones críticas
     */
    async getCriticas() {
        const response = await fetchAPI('/notificaciones/criticas');
        return response.datos;
    },

    /**
     * Obtiene el conteo de notificaciones por prioridad
     * @returns {Promise<object>} Conteo de notificaciones
     */
    async getConteo() {
        const response = await fetchAPI('/notificaciones/conteo');
        return response.datos;
    }
};

/**
 * Utilidades
 */
const Utils = {
    /**
     * Formatea una fecha en formato ISO a formato legible
     * @param {string} isoDate - Fecha en formato ISO
     * @returns {string} Fecha formateada
     */
    formatDate(isoDate) {
        if (!isoDate) return 'N/A';
        const date = new Date(isoDate);
        return date.toLocaleDateString('es-CO', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    },

    /**
     * Calcula los días restantes hasta una fecha
     * @param {string} fechaVencimiento - Fecha de vencimiento
     * @returns {number} Días restantes (negativo si ya venció)
     */
    diasRestantes(fechaVencimiento) {
        if (!fechaVencimiento) return null;
        const hoy = new Date();
        const vencimiento = new Date(fechaVencimiento);
        const diff = vencimiento - hoy;
        return Math.ceil(diff / (1000 * 60 * 60 * 24));
    },

    /**
     * Obtiene una clase CSS según el estado
     * @param {string} estado - Estado (ACTIVO, INACTIVO, SUSPENDIDO)
     * @returns {string} Clase CSS
     */
    getEstadoClass(estado) {
        const estadoUpper = estado ? estado.toUpperCase() : '';
        const classes = {
            'ACTIVO': 'badge-success',
            'INACTIVO': 'badge-secondary',
            'SUSPENDIDO': 'badge-warning'
        };
        return classes[estadoUpper] || 'badge-secondary';
    },

    /**
     * Obtiene una clase CSS según la prioridad de vencimiento
     * @param {number} dias - Días restantes
     * @returns {string} Clase CSS
     */
    getPrioridadClass(dias) {
        if (dias === null) return 'badge-secondary';
        if (dias < 0) return 'badge-danger';
        if (dias <= 7) return 'badge-danger';
        if (dias <= 30) return 'badge-warning';
        return 'badge-success';
    },

    /**
     * Muestra un toast de notificación
     * @param {string} mensaje - Mensaje a mostrar
     * @param {string} tipo - Tipo de toast (success, error, warning, info)
     */
    showToast(mensaje, tipo = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = mensaje;
        toast.className = `toast show toast-${tipo}`;
        
        setTimeout(() => {
            toast.className = 'toast';
        }, 3000);
    },

    /**
     * Formatea un número como moneda
     * @param {number} valor - Valor a formatear
     * @returns {string} Valor formateado
     */
    formatCurrency(valor) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(valor);
    }
};

/**
 * API General - Wrapper para hacer peticiones genéricas
 */
const API = {
    async get(endpoint) {
        return fetchAPI(endpoint, { method: 'GET' });
    },
    
    async post(endpoint, data) {
        return fetchAPI(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(endpoint, data) {
        return fetchAPI(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async patch(endpoint, data) {
        return fetchAPI(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },
    
    async delete(endpoint) {
        return fetchAPI(endpoint, { method: 'DELETE' });
    }
};

