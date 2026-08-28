import { goto } from '$app/navigation';

/**
 * Maneja la lógica de inicio de sesión
 * @param {string} email
 * @param {string} password
 * @param {boolean} rememberUser
 * @returns {Promise<void>}
 */
export async function handleLogin(email, password, rememberUser) {
    try {
        const response = await fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Login exitoso', result);

            // Guardar la sesión del usuario usando el endpoint interno
            const sessionResponse = await fetch('/api/auth/set-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId: result.userId,
                    userRut: result.userRut,
                    userName: result.userName,
                    userEmail: result.userEmail,
                    userRole: result.userRole
                })
            });

            if (!sessionResponse.ok) {
                throw new Error('Error al establecer la sesión');
            }

            if (rememberUser) {
                localStorage.setItem('rememberedEmail', email);
            } else {
                localStorage.removeItem('rememberedEmail');
            }

            await goto('/app/producto');
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Usuario o contraseña inválidos');
        }
    } catch (err) {
        console.error('Error de login:', err);
        throw new Error(err.message || 'Error de conexión. Intenta nuevamente.');
    }
}

/**
 * Maneja el logout
 */
export async function handleLogout() {
    try {
        // Limpiar sesión del servidor
        await fetch('/api/auth/logout', {
            method: 'POST'
        });

        // Limpiar localStorage
        localStorage.removeItem('rememberedEmail');

        // Redirigir al login
        await goto('/');
    } catch (error) {
        // Aunque falle la petición, limpiamos localmente
        localStorage.removeItem('rememberedEmail');
        await goto('/');
    }
}

/**
 * Obtiene la información del usuario actual
 * @returns {Promise<Object|null>}
 */
export async function getCurrentUser() {
    try {
        const response = await fetch('/api/auth/get-user');
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('Error al obtener usuario:', error);
        return null;
    }
}