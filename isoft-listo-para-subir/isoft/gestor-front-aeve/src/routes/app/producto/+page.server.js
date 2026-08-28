export async function load({ fetch }) {
    try {
        const res = await fetch("http://localhost:5000/productos");

        if (!res.ok) {
            console.error("Error en la respuesta:", res.status, res.statusText);
            return {
                productos: [],
                error: `Error del servidor: ${res.status} ${res.statusText}`,
            };
        }

        const productos = await res.json();

        return {
            productos: Array.isArray(productos) ? productos : [],
            error: null,
        };
    } catch (error) {
        console.error("Error capturado en load function:", error);
        console.error("Stack trace:", error.stack);
        return {
            productos: [],
            error: `Error de conexión: ${error.message}`,
        };
    }
}