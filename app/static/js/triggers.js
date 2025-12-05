/**
 * Gestión de Triggers de Notificaciones
 */

let currentEditingTriggerId = null;

/**
 * Carga y muestra todos los triggers
 */
async function loadTriggers() {
    try {
        const response = await API.get('/triggers');
        const triggers = response.datos || [];
        
        renderTriggers(triggers);
    } catch (error) {
        console.error('Error cargando triggers:', error);
        Utils.showToast('Error al cargar triggers', 'error');
    }
}

/**
 * Renderiza la lista de triggers
 */
function renderTriggers(triggers) {
    const container = document.getElementById('triggers-container');
    
    if (triggers.length === 0) {
        container.innerHTML = `
            <div class="trigger-empty">
                <div class="trigger-empty-icon">⚙️</div>
                <h3>No hay triggers configurados</h3>
                <p>Crea un nuevo trigger para automatizar el envío de notificaciones</p>
                <button class="btn btn-primary" onclick="showTriggerModal()" style="margin-top: 1rem;">
                    ➕ Crear Primer Trigger
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = triggers.map(trigger => renderTrigger(trigger)).join('');
}

/**
 * Renderiza un trigger individual
 */
function renderTrigger(trigger) {
    const activo = trigger.activo === 1;
    const frecuenciaText = getFrecuenciaText(trigger);
    const prioridadesText = trigger.prioridades || 'CRITICA,ALTA,MEDIA';
    const destinatariosCount = trigger.destinatarios.split(',').length;
    
    // Formatear próxima ejecución
    let proximaEjecucion = 'No programada';
    if (trigger.proxima_ejecucion) {
        try {
            const fecha = new Date(trigger.proxima_ejecucion);
            proximaEjecucion = fecha.toLocaleString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            proximaEjecucion = trigger.proxima_ejecucion;
        }
    }
    
    // Formatear última ejecución
    let ultimaEjecucion = 'Nunca';
    if (trigger.ultima_ejecucion) {
        try {
            const fecha = new Date(trigger.ultima_ejecucion);
            ultimaEjecucion = fecha.toLocaleString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            ultimaEjecucion = trigger.ultima_ejecucion;
        }
    }
    
    return `
        <div class="trigger-card">
            <div class="trigger-card-header">
                <div>
                    <div class="trigger-card-title">${trigger.nombre}</div>
                    ${trigger.descripcion ? `<div class="trigger-card-description">${trigger.descripcion}</div>` : ''}
                </div>
                <span class="trigger-status ${activo ? 'activo' : 'inactivo'}">
                    ${activo ? '✓ Activo' : '○ Inactivo'}
                </span>
            </div>
            
            <div class="trigger-badges">
                <span class="trigger-badge frecuencia">📅 ${frecuenciaText}</span>
                <span class="trigger-badge prioridad">👥 ${destinatariosCount} destinatario(s)</span>
            </div>
            
            <div class="trigger-info">
                <div class="trigger-info-row">
                    <span class="trigger-info-label">Próxima ejecución:</span>
                    <span class="trigger-info-value">${proximaEjecucion}</span>
                </div>
                <div class="trigger-info-row">
                    <span class="trigger-info-label">Última ejecución:</span>
                    <span class="trigger-info-value">${ultimaEjecucion}</span>
                </div>
                <div class="trigger-info-row">
                    <span class="trigger-info-label">Prioridades:</span>
                    <span class="trigger-info-value">${prioridadesText}</span>
                </div>
            </div>
            
            <div class="trigger-card-actions">
                <button class="btn ${activo ? 'btn-secondary' : 'btn-success'}" 
                        onclick="toggleTriggerStatus(${trigger.id}, ${!activo})">
                    ${activo ? '⏸ Desactivar' : '▶️ Activar'}
                </button>
                <button class="btn btn-primary" onclick="editTrigger(${trigger.id})">
                    ✏️ Editar
                </button>
                <button class="btn btn-danger" onclick="deleteTrigger(${trigger.id})">
                    🗑️
                </button>
            </div>
        </div>
    `;
}

/**
 * Obtiene el texto descriptivo de la frecuencia
 */
function getFrecuenciaText(trigger) {
    switch (trigger.frecuencia) {
        case 'diaria':
            return `Diaria a las ${trigger.hora}`;
        case 'semanal':
            let dias = 'Todos los días';
            if (trigger.dias_semana) {
                try {
                    const diasArray = JSON.parse(trigger.dias_semana);
                    dias = diasArray.join(', ');
                } catch (e) {
                    dias = trigger.dias_semana;
                }
            }
            return `Semanal (${dias}) a las ${trigger.hora}`;
        case 'mensual':
            return `Mensual (día ${trigger.dia_mes || 1}) a las ${trigger.hora}`;
        case 'personalizada':
            return `Cada ${trigger.intervalo_horas} hora(s)`;
        default:
            return trigger.frecuencia;
    }
}

/**
 * Muestra el modal para crear/editar trigger
 */
function showTriggerModal(triggerId = null) {
    const modal = document.getElementById('trigger-modal');
    const form = document.getElementById('trigger-form');
    const title = document.getElementById('trigger-modal-title');
    
    currentEditingTriggerId = triggerId;
    
    if (triggerId) {
        title.textContent = 'Editar Trigger';
        loadTriggerToForm(triggerId);
    } else {
        title.textContent = 'Nuevo Trigger';
        form.reset();
        document.getElementById('trigger-id').value = '';
        // Marcar todas las prioridades por defecto
        document.querySelectorAll('#trigger-form input[value="CRITICA"], #trigger-form input[value="ALTA"], #trigger-form input[value="MEDIA"]').forEach(cb => cb.checked = true);
    }
    
    modal.classList.add('show');
    updateFrecuenciaFields();
}

/**
 * Cierra el modal
 */
function closeTriggerModal() {
    const modal = document.getElementById('trigger-modal');
    modal.classList.remove('show');
    currentEditingTriggerId = null;
}

/**
 * Actualiza campos según la frecuencia seleccionada
 */
function updateFrecuenciaFields() {
    const frecuencia = document.getElementById('trigger-frecuencia').value;
    
    document.getElementById('group-hora').style.display = 
        frecuencia !== 'personalizada' ? 'block' : 'none';
    
    document.getElementById('group-dias-semana').style.display = 
        frecuencia === 'semanal' ? 'block' : 'none';
    
    document.getElementById('group-dia-mes').style.display = 
        frecuencia === 'mensual' ? 'block' : 'none';
    
    document.getElementById('group-intervalo').style.display = 
        frecuencia === 'personalizada' ? 'block' : 'none';
}

/**
 * Carga datos de un trigger en el formulario
 */
async function loadTriggerToForm(triggerId) {
    try {
        const response = await API.get(`/triggers/${triggerId}`);
        const trigger = response.datos;
        
        document.getElementById('trigger-id').value = trigger.id;
        document.getElementById('trigger-nombre').value = trigger.nombre;
        document.getElementById('trigger-descripcion').value = trigger.descripcion || '';
        document.getElementById('trigger-frecuencia').value = trigger.frecuencia;
        document.getElementById('trigger-hora').value = trigger.hora;
        document.getElementById('trigger-dia-mes').value = trigger.dia_mes || 1;
        document.getElementById('trigger-intervalo').value = trigger.intervalo_horas || 1;
        document.getElementById('trigger-destinatarios').value = trigger.destinatarios;
        
        // Días de semana
        if (trigger.dias_semana) {
            try {
                const dias = JSON.parse(trigger.dias_semana);
                document.querySelectorAll('#group-dias-semana input[type="checkbox"]').forEach(cb => {
                    cb.checked = dias.includes(cb.value);
                });
            } catch (e) {
                console.error('Error parsing dias_semana:', e);
            }
        }
        
        // Prioridades
        const prioridades = trigger.prioridades.split(',');
        document.querySelectorAll('#trigger-form input[type="checkbox"][value^="CRITICA"], #trigger-form input[type="checkbox"][value^="ALTA"], #trigger-form input[type="checkbox"][value^="MEDIA"]').forEach(cb => {
            cb.checked = prioridades.includes(cb.value);
        });
        
        updateFrecuenciaFields();
    } catch (error) {
        console.error('Error cargando trigger:', error);
        Utils.showToast('Error al cargar trigger', 'error');
    }
}

/**
 * Edita un trigger
 */
function editTrigger(triggerId) {
    showTriggerModal(triggerId);
}

/**
 * Guarda trigger (crear o actualizar)
 */
document.getElementById('trigger-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const triggerId = document.getElementById('trigger-id').value;
    const frecuencia = document.getElementById('trigger-frecuencia').value;
    
    // Recopilar días de semana si es semanal
    let dias_semana = null;
    if (frecuencia === 'semanal') {
        const diasSeleccionados = Array.from(
            document.querySelectorAll('#group-dias-semana input:checked')
        ).map(cb => cb.value);
        
        if (diasSeleccionados.length === 0) {
            Utils.showToast('Selecciona al menos un día de la semana', 'error');
            return;
        }
        
        dias_semana = diasSeleccionados;
    }
    
    // Recopilar prioridades
    const prioridades = Array.from(
        document.querySelectorAll('#trigger-form input[type="checkbox"]:checked')
    )
    .filter(cb => ['CRITICA', 'ALTA', 'MEDIA'].includes(cb.value))
    .map(cb => cb.value);
    
    if (prioridades.length === 0) {
        Utils.showToast('Selecciona al menos una prioridad', 'error');
        return;
    }
    
    const datos = {
        nombre: document.getElementById('trigger-nombre').value,
        descripcion: document.getElementById('trigger-descripcion').value,
        frecuencia: frecuencia,
        hora: document.getElementById('trigger-hora').value,
        dias_semana: dias_semana,
        dia_mes: frecuencia === 'mensual' ? parseInt(document.getElementById('trigger-dia-mes').value) : null,
        intervalo_horas: frecuencia === 'personalizada' ? parseInt(document.getElementById('trigger-intervalo').value) : null,
        destinatarios: document.getElementById('trigger-destinatarios').value,
        prioridades: prioridades.join(','),
        activo: 1
    };
    
    try {
        if (triggerId) {
            // Actualizar
            await API.put(`/triggers/${triggerId}`, datos);
            Utils.showToast('Trigger actualizado exitosamente', 'success');
        } else {
            // Crear
            await API.post('/triggers', datos);
            Utils.showToast('Trigger creado exitosamente', 'success');
        }
        
        closeTriggerModal();
        loadTriggers();
    } catch (error) {
        console.error('Error guardando trigger:', error);
        Utils.showToast(error.message || 'Error al guardar trigger', 'error');
    }
});

/**
 * Cambia el estado de un trigger (activo/inactivo)
 */
async function toggleTriggerStatus(triggerId, activo) {
    try {
        await API.patch(`/triggers/${triggerId}/estado`, { activo });
        Utils.showToast(
            `Trigger ${activo ? 'activado' : 'desactivado'} exitosamente`,
            'success'
        );
        loadTriggers();
    } catch (error) {
        console.error('Error cambiando estado:', error);
        Utils.showToast('Error al cambiar estado del trigger', 'error');
    }
}

/**
 * Elimina un trigger
 */
async function deleteTrigger(triggerId) {
    if (!confirm('¿Estás seguro de eliminar este trigger? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        await API.delete(`/triggers/${triggerId}`);
        Utils.showToast('Trigger eliminado exitosamente', 'success');
        loadTriggers();
    } catch (error) {
        console.error('Error eliminando trigger:', error);
        Utils.showToast('Error al eliminar trigger', 'error');
    }
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('trigger-modal');
    if (event.target === modal) {
        closeTriggerModal();
    }
};
