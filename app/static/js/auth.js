/**
 * Módulo de autenticación
 * Maneja login, logout y validación de tokens usando cookies
 */

const Auth = {
    /**
     * Obtiene una cookie por nombre
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    },

    /**
     * Establece una cookie
     */
    setCookie(name, value, days = 1) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    },

    /**
     * Elimina una cookie
     */
    deleteCookie(name) {
        document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
    },

    /**
     * Obtiene el token de autenticación
     */
    getToken() {
        // Primero intenta obtener de cookie, luego de localStorage (para compatibilidad)
        const tokenCookie = this.getCookie('token');
        const tokenLocal = localStorage.getItem('token');
        const token = tokenCookie || tokenLocal;
        
        // console.log('🔍 Auth.getToken() - Cookie:', tokenCookie ? tokenCookie.substring(0, 20) + '...' : 'null');
        // console.log('🔍 Auth.getToken() - LocalStorage:', tokenLocal ? tokenLocal.substring(0, 20) + '...' : 'null');
        // console.log('🔍 Auth.getToken() - Retornando:', token ? token.substring(0, 20) + '...' : 'null');
        
        return token;
    },

    /**
     * Obtiene el usuario autenticado
     */
    getUsuario() {
        const usuarioStr = this.getCookie('usuario') || localStorage.getItem('usuario');
        try {
            return usuarioStr ? JSON.parse(decodeURIComponent(usuarioStr)) : null;
        } catch (e) {
            return null;
        }
    },

    /**
     * Verifica si el usuario está autenticado
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Verifica si el usuario es admin
     */
    isAdmin() {
        const usuario = this.getUsuario();
        return usuario && usuario.rol === 'admin';
    },

    /**
     * Guarda el token y usuario en cookies y localStorage (respaldo)
     */
    setSession(token, usuario) {
        // console.log('💾 Auth.setSession() - Guardando token:', token.substring(0, 20) + '...');
        // console.log('💾 Auth.setSession() - Usuario:', usuario.nombre || usuario.username);
        
        // Guardar en cookies (preferido)
        this.setCookie('token', token, 1); // 1 día
        this.setCookie('usuario', encodeURIComponent(JSON.stringify(usuario)), 1);
        
        // Guardar en localStorage como respaldo
        localStorage.setItem('token', token);
        localStorage.setItem('usuario', JSON.stringify(usuario));
        
        // Verificar que se guardó correctamente
        // console.log('✅ Token guardado en cookie:', this.getCookie('token') ? 'SI' : 'NO');
        // console.log('✅ Token guardado en localStorage:', localStorage.getItem('token') ? 'SI' : 'NO');
    },

    /**
     * Limpia la sesión
     */
    clearSession() {
        // Limpiar cookies
        this.deleteCookie('token');
        this.deleteCookie('usuario');
        
        // Limpiar localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('usuario');
    },

    /**
     * Realiza logout
     */
    async logout() {
        const token = this.getToken();
        
        if (token) {
            try {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            } catch (error) {
                console.error('Error al hacer logout:', error);
            }
        }

        this.clearSession();
        window.location.href = '/login';
    },

    /**
     * Verifica la sesión y redirige si no está autenticado
     */
    checkAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    },

    /**
     * Maneja errores de autenticación en las respuestas de API
     */
    handleAuthError(response) {
        if (response.status === 401) {
            this.clearSession();
            window.location.href = '/login';
            return true;
        }
        return false;
    },

    /**
     * Wrapper para fetch que incluye el token automáticamente
     */
    async fetchWithAuth(url, options = {}) {
        const token = this.getToken();
        
        if (!token) {
            throw new Error('No hay token de autenticación');
        }

        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Si es 401, redirigir a login
        if (response.status === 401) {
            this.clearSession();
            window.location.href = '/login';
            throw new Error('Sesión expirada');
        }

        return response;
    }
};

// Verificar autenticación al cargar la página (excepto en login)
if (window.location.pathname !== '/login') {
    if (!Auth.isAuthenticated()) {
        window.location.href = '/login';
    }
}
