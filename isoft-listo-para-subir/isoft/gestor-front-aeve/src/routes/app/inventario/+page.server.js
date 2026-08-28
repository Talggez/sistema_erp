export async function load({ fetch }) {
    try {
        const resultCall = await fetch("http://localhost:5000/proveedores");
        if(!resultCall.ok) {
            console.error("❌ Error en la respuesta:", resultCall.status, resultCall.statusText);
            return {
                productos: [],
                error: `Error del servidor: ${resultCall.status} ${resultCall.statusText}`,
            };
        }
        const data = await resultCall.json();

        return {
            supplies: data.data,
            count: data.count
        };

    } catch (error) {
        console.error("Failed to load supplies", error);
        return {
            supplies: [],
            error: "it's not possible load the supplies "
        }
    }
}