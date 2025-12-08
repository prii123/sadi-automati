/**
 * Gestión de Importación Masiva de Empresas
 */

class ImportacionManager {
    constructor() {
        this.apiUrl = '/api/empresas';
        this.fileInput = null;
        this.init();
    }

    init() {
        console.log('ImportacionManager inicializado');
    }

    /**
     * Descarga la plantilla Excel
     */
    async descargarPlantilla() {
        try {
            const response = await fetch(`${this.apiUrl}/plantilla-excel`);
            
            if (!response.ok) {
                throw new Error('Error al descargar la plantilla');
            }

            // Crear blob y descargar
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'plantilla_empresas.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.mostrarMensaje('Plantilla descargada exitosamente', 'success');
        } catch (error) {
            console.error('Error descargando plantilla:', error);
            this.mostrarMensaje('Error al descargar la plantilla', 'error');
        }
    }

    /**
     * Abre el selector de archivos
     */
    seleccionarArchivo() {
        if (!this.fileInput) {
            this.fileInput = document.createElement('input');
            this.fileInput.type = 'file';
            this.fileInput.accept = '.xlsx,.xls';
            this.fileInput.onchange = (e) => this.handleFileSelected(e);
        }
        this.fileInput.click();
    }

    /**
     * Maneja el archivo seleccionado
     */
    async handleFileSelected(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validar extensión
        if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            this.mostrarMensaje('Por favor selecciona un archivo Excel (.xlsx o .xls)', 'error');
            return;
        }

        // Mostrar confirmación
        const confirmar = confirm(
            `¿Deseas importar el archivo "${file.name}"?\n\n` +
            `Esto creará o actualizará empresas en el sistema.`
        );

        if (!confirmar) {
            this.fileInput.value = '';
            return;
        }

        await this.importarArchivo(file);
    }

    /**
     * Importa el archivo Excel
     */
    async importarArchivo(file) {
        try {
            // Mostrar loading
            this.mostrarLoading('Procesando archivo...');

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiUrl}/importar`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Error al importar archivo');
            }

            // Mostrar resultados
            this.mostrarResultadosImportacion(data.datos);

            // Limpiar input
            if (this.fileInput) {
                this.fileInput.value = '';
            }

            // Recargar empresas
            if (window.empresasManager) {
                await window.empresasManager.cargarEmpresas();
            }

        } catch (error) {
            console.error('Error importando archivo:', error);
            this.mostrarMensaje(`Error: ${error.message}`, 'error');
        } finally {
            this.ocultarLoading();
        }
    }

    /**
     * Muestra los resultados de la importación
     */
    mostrarResultadosImportacion(datos) {
        const { total, exitosas, actualizadas, fallidas, errores } = datos;

        let mensaje = `
            <div class="importacion-resultado">
                <h3>📊 Resultados de la Importación</h3>
                <div class="resultado-stats">
                    <div class="stat">
                        <span class="label">Total procesadas:</span>
                        <span class="value">${total}</span>
                    </div>
                    <div class="stat success">
                        <span class="label">✅ Creadas:</span>
                        <span class="value">${exitosas}</span>
                    </div>
                    <div class="stat info">
                        <span class="label">🔄 Actualizadas:</span>
                        <span class="value">${actualizadas}</span>
                    </div>
                    ${fallidas > 0 ? `
                    <div class="stat error">
                        <span class="label">❌ Fallidas:</span>
                        <span class="value">${fallidas}</span>
                    </div>
                    ` : ''}
                </div>
        `;

        // Mostrar errores si los hay
        if (errores && errores.length > 0) {
            mensaje += `
                <div class="errores-importacion">
                    <h4>⚠️ Errores encontrados:</h4>
                    <ul>
                        ${errores.slice(0, 10).map(error => `<li>${error}</li>`).join('')}
                        ${errores.length > 10 ? `<li><em>... y ${errores.length - 10} errores más</em></li>` : ''}
                    </ul>
                </div>
            `;
        }

        mensaje += '</div>';

        // Mostrar en modal
        this.mostrarModal('Importación Completada', mensaje);
    }

    /**
     * Muestra un modal con contenido HTML
     */
    mostrarModal(titulo, contenidoHTML) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>${titulo}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${contenidoHTML}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Cerrar al hacer clic fuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    /**
     * Muestra mensaje de loading
     */
    mostrarLoading(mensaje) {
        const loading = document.createElement('div');
        loading.id = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <p>${mensaje}</p>
            </div>
        `;
        document.body.appendChild(loading);
    }

    /**
     * Oculta el loading
     */
    ocultarLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Muestra un mensaje toast
     */
    mostrarMensaje(mensaje, tipo = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${tipo}`;
        toast.textContent = mensaje;
        document.body.appendChild(toast);

        // Auto remover después de 3 segundos
        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    window.importacionManager = new ImportacionManager();
});
