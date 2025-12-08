/**
 * Funciones para cambio de contraseña
 */

/**
 * Mostrar modal de cambio de contraseña
 */
function showCambiarPasswordModal() {
    console.log('📝 Abriendo modal de cambio de contraseña');
    const modal = document.getElementById('password-modal');
    const form = document.getElementById('password-form');
    
    // Limpiar formulario
    form.reset();
    
    // Mostrar modal
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('show'), 10);
    
    // Focus en primer campo
    document.getElementById('password-actual').focus();
}

/**
 * Cerrar modal de cambio de contraseña
 */
function closeCambiarPasswordModal() {
    console.log('❌ Cerrando modal de cambio de contraseña');
    const modal = document.getElementById('password-modal');
    modal.classList.remove('show');
    setTimeout(() => modal.style.display = 'none', 200);
}

/**
 * Validar formulario de cambio de contraseña
 */
function validarFormularioPassword() {
    const actual = document.getElementById('password-actual').value;
    const nueva = document.getElementById('password-nueva').value;
    const confirmar = document.getElementById('password-confirmar').value;

    // Validar campos obligatorios
    if (!actual || !nueva || !confirmar) {
        showNotification('Por favor, complete todos los campos', 'error');
        return false;
    }

    // Validar longitud mínima
    if (nueva.length < 6) {
        showNotification('La nueva contraseña debe tener al menos 6 caracteres', 'error');
        return false;
    }

    // Validar que las contraseñas coincidan
    if (nueva !== confirmar) {
        showNotification('Las contraseñas nuevas no coinciden', 'error');
        return false;
    }

    // Validar que la nueva contraseña sea diferente de la actual
    if (actual === nueva) {
        showNotification('La nueva contraseña debe ser diferente de la actual', 'error');
        return false;
    }

    return true;
}

/**
 * Manejar envío del formulario de cambio de contraseña
 */
async function handleCambiarPassword(event) {
    event.preventDefault();
    console.log('🔑 Procesando cambio de contraseña...');

    // Validar formulario
    if (!validarFormularioPassword()) {
        return;
    }

    const actual = document.getElementById('password-actual').value;
    const nueva = document.getElementById('password-nueva').value;

    try {
        // Mostrar loading
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Cambiando...';

        // Hacer request al API
        const response = await fetchAPI('/auth/cambiar-password', {
            method: 'POST',
            body: JSON.stringify({
                password_actual: actual,
                password_nueva: nueva
            })
        });

        if (response.success) {
            showNotification('✅ Contraseña cambiada exitosamente', 'success');
            closeCambiarPasswordModal();
            
            // Limpiar formulario
            document.getElementById('password-form').reset();
            
            console.log('✅ Contraseña cambiada correctamente');
        } else {
            throw new Error(response.error || 'Error al cambiar la contraseña');
        }

    } catch (error) {
        console.error('❌ Error al cambiar contraseña:', error);
        
        // Mostrar mensaje específico según el error
        let mensaje = 'Error al cambiar la contraseña';
        if (error.message.includes('incorrecta')) {
            mensaje = 'La contraseña actual es incorrecta';
        } else if (error.message.includes('token')) {
            mensaje = 'Sesión expirada. Por favor, inicie sesión nuevamente';
            setTimeout(() => {
                Auth.logout();
            }, 2000);
        }
        
        showNotification(mensaje, 'error');
    } finally {
        // Restaurar botón
        const submitBtn = event.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '🔐 Cambiar Contraseña';
        }
    }
}

/**
 * Cerrar modal al hacer clic fuera
 */
document.addEventListener('DOMContentLoaded', () => {
    const passwordModal = document.getElementById('password-modal');
    
    if (passwordModal) {
        passwordModal.addEventListener('click', (e) => {
            if (e.target === passwordModal) {
                closeCambiarPasswordModal();
            }
        });
    }
    
    // Cerrar con tecla ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('password-modal');
            if (modal && modal.classList.contains('show')) {
                closeCambiarPasswordModal();
            }
        }
    });
});
