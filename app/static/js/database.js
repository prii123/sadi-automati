/**
 * Módulo para el visor de base de datos
 * Permite visualizar tablas y ejecutar consultas SQL
 */

let currentTable = null;

/**
 * Carga la vista del visor de base de datos
 */
async function loadDatabaseViewer() {
    try {
        const tables = await DatabaseAPI.getTables();
        renderTablesList(tables);
        Utils.showToast('Visor de base de datos cargado', 'success');
    } catch (error) {
        console.error('Error al cargar tablas:', error);
        Utils.showToast('Error al cargar las tablas', 'error');
    }
}

/**
 * Renderiza la lista de tablas disponibles
 * @param {Array} tables - Lista de tablas con información
 */
function renderTablesList(tables) {
    const container = document.getElementById('db-tables-list');
    
    if (!tables || tables.length === 0) {
        container.innerHTML = '<p class="no-data">No hay tablas disponibles</p>';
        return;
    }

    container.innerHTML = `
        <div class="db-tables-grid">
            ${tables.map(table => `
                <div class="db-table-card" onclick="loadTableData('${table.name}')">
                    <div class="db-table-icon">📊</div>
                    <div class="db-table-info">
                        <h4>${table.name}</h4>
                        <p>${table.count || 0} registros | ${table.columns || 0} columnas</p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Carga y muestra los datos de una tabla
 * @param {string} tableName - Nombre de la tabla
 */
async function loadTableData(tableName, limit = 100) {
    try {
        currentTable = tableName;
        const data = await DatabaseAPI.getTableData(tableName, limit);
        renderTableData(data);
        Utils.showToast(`Tabla ${tableName} cargada`, 'success');
    } catch (error) {
        console.error('Error al cargar datos de tabla:', error);
        Utils.showToast('Error al cargar la tabla', 'error');
    }
}

/**
 * Renderiza los datos de una tabla
 * @param {object} data - Datos de la tabla
 */
function renderTableData(data) {
    const container = document.getElementById('db-table-data');
    
    if (!data || !data.data || data.data.length === 0) {
        container.innerHTML = '<p class="no-data">No hay datos en esta tabla</p>';
        return;
    }

    // Obtener columnas del primer registro
    const columns = Object.keys(data.data[0]);

    container.innerHTML = `
        <div class="db-table-header">
            <h3>📊 ${data.table}</h3>
            <p>Mostrando ${data.showing} de ${data.total_rows} registros</p>
        </div>
        
        <div class="db-table-actions">
            <button class="btn btn-secondary" onclick="exportTableToCSV('${data.table}')">
                📥 Exportar CSV
            </button>
            <button class="btn btn-secondary" onclick="refreshTableData()">
                🔄 Actualizar
            </button>
        </div>

        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.data.map(row => `
                        <tr>
                            ${columns.map(col => {
                                let value = row[col];
                                if (value === null) value = '<span class="text-muted">NULL</span>';
                                else if (typeof value === 'boolean') value = value ? '✅' : '❌';
                                return `<td>${value}</td>`;
                            }).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Actualiza los datos de la tabla actual
 */
function refreshTableData() {
    if (currentTable) {
        loadTableData(currentTable);
    }
}

/**
 * Ejecuta una consulta SQL personalizada
 */
async function executeCustomQuery() {
    const query = document.getElementById('db-query-input').value.trim();
    
    if (!query) {
        Utils.showToast('Ingrese una consulta SQL', 'warning');
        return;
    }

    try {
        const result = await DatabaseAPI.executeQuery(query);
        renderQueryResults(result);
        Utils.showToast('Consulta ejecutada correctamente', 'success');
    } catch (error) {
        console.error('Error al ejecutar consulta:', error);
        Utils.showToast(error.message || 'Error al ejecutar la consulta', 'error');
    }
}

/**
 * Renderiza los resultados de una consulta
 * @param {object} result - Resultados de la consulta
 */
function renderQueryResults(result) {
    const container = document.getElementById('db-query-results');
    
    if (!result || !result.results || result.results.length === 0) {
        container.innerHTML = '<p class="no-data">La consulta no devolvió resultados</p>';
        return;
    }

    const columns = Object.keys(result.results[0]);

    container.innerHTML = `
        <div class="db-query-header">
            <h4>Resultados (${result.rows} filas)</h4>
        </div>
        
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${result.results.map(row => `
                        <tr>
                            ${columns.map(col => `<td>${row[col] ?? '<span class="text-muted">NULL</span>'}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Exporta una tabla a CSV
 * @param {string} tableName - Nombre de la tabla
 */
async function exportTableToCSV(tableName) {
    if (!tableName) {
        Utils.showToast('Nombre de tabla no válido', 'error');
        return;
    }

    try {
        Utils.showToast('Exportando datos...', 'info');
        
        // Obtener datos con límite alto
        const response = await DatabaseAPI.getTableData(tableName, 10000);
        
        // console.log('📊 Datos recibidos para exportar:', response);
        
        // Verificar que hay datos
        if (!response || !response.data || response.data.length === 0) {
            Utils.showToast('No hay datos para exportar', 'warning');
            return;
        }

        // Convertir a CSV
        const data = response.data;
        const columns = Object.keys(data[0]);
        
        // Función para escapar valores CSV
        const escapeCSV = (value) => {
            if (value === null || value === undefined) return '';
            
            // Convertir a string
            let strValue = String(value);
            
            // Si contiene comas, saltos de línea o comillas, encerrar en comillas
            if (strValue.includes(',') || strValue.includes('\n') || strValue.includes('"')) {
                // Escapar comillas dobles duplicándolas
                strValue = strValue.replace(/"/g, '""');
                return `"${strValue}"`;
            }
            
            return strValue;
        };
        
        // Crear header
        let csv = columns.map(col => escapeCSV(col)).join(',') + '\n';
        
        // Agregar filas
        data.forEach(row => {
            const values = columns.map(col => escapeCSV(row[col]));
            csv += values.join(',') + '\n';
        });

        // Crear y descargar archivo con BOM para Excel
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csv], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Nombre del archivo con timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        a.download = `${tableName}_${timestamp}.csv`;
        
        document.body.appendChild(a);
        a.click();
        
        // Limpiar
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);

        Utils.showToast(`✅ ${response.showing} registros exportados correctamente`, 'success');
    } catch (error) {
        console.error('❌ Error al exportar tabla:', error);
        Utils.showToast('Error al exportar la tabla: ' + (error.message || 'Error desconocido'), 'error');
    }
}

/**
 * API para operaciones de base de datos
 */
const DatabaseAPI = {
    async getTables() {
        const response = await fetchAPI('/database/tables');
        return response.datos;
    },

    async getTableData(tableName, limit = 100) {
        const response = await fetchAPI(`/database/tables/${tableName}?limit=${limit}`);
        return response.datos;
    },

    async executeQuery(query) {
        const response = await fetchAPI('/database/query', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
        return response.datos;
    },

    async getTableSchema(tableName) {
        const response = await fetchAPI(`/database/schema/${tableName}`);
        return response.datos;
    }
};
