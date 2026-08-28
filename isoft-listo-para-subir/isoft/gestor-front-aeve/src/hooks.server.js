import { redirect } from '@sveltejs/kit';

const protectedRoutes = ['/app'];

export async function handle({ event, resolve }) {
    const userSession = event.cookies.get('user-session');
    const { pathname } = event.url;

    const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

    // Si trata de acceder a ruta protegida sin sesión, redirigir al login
    if (isProtectedRoute && !userSession) {
        throw redirect(302, '/');
    }

    // Si tiene sesión y trata de acceder al login, redirigir al dashboard
    if (userSession && pathname === '/') {
        throw redirect(302, '/app/producto');
    }

    return resolve(event);
}