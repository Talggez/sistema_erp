import { json } from '@sveltejs/kit';

export async function POST({ request, cookies }) {
    try {
        const userData = await request.json();

        if (!userData.userId) {
            return json({ error: 'Datos de usuario requeridos' }, { status: 400 });
        }

        // Crear un objeto con la información del usuario
        const userSession = JSON.stringify({
            userId: userData.userId,
            userRut: userData.userRut,
            userName: userData.userName,
            userEmail: userData.userEmail,
            userRole: userData.userRole,
            loginTime: new Date().toISOString()
        });

        // Establecer cookie httpOnly con la sesión
        cookies.set('user-session', userSession, {
            path: '/',
            maxAge: 60 * 60 * 24 * 7, // 7 días
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict'
        });

        return json({ success: true });
    } catch (error) {
        return json({ error: 'Error interno del servidor' }, { status: 500 });
    }
}