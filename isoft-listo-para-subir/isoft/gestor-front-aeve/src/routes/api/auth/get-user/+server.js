import { json } from '@sveltejs/kit';

export async function GET({ cookies }) {
    try {
        const userSession = cookies.get('user-session');

        if (!userSession) {
            return json({ error: 'No hay sesión activa' }, { status: 401 });
        }

        const userData = JSON.parse(userSession);
        return json(userData);
    } catch (error) {
        return json({ error: 'Error al obtener datos del usuario' }, { status: 500 });
    }
}