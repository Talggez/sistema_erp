import { fail } from "@sveltejs/kit";

const API_BASE_URL = "http://localhost:5000";

export async function load({ fetch, url }) {
  try {
    const q = url.searchParams.get("q") || "";
    const tipo = url.searchParams.get("tipo") || "";
    const limit = url.searchParams.get("limit") || "100";
    const offset = url.searchParams.get("offset") || "0";

    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (tipo) params.set("tipo", tipo);
    params.set("limit", limit);
    params.set("offset", offset);

    const res = await fetch(`${API_BASE_URL}/clientes`);

    if (!res.ok) {
      console.error("Error en la respuesta:", res.status, res.statusText);
      return {
        clientes: [],
        count: 0,
        error: `Error del servidor: ${res.status} ${res.statusText}`
      };
    }

    const data = await res.json();
    // El backend devuelve directamente un array de clientes
    const clientes = Array.isArray(data) ? data : [];
    const count = clientes.length;

    return { clientes, count };
  } catch (err) {
    console.error("Error al cargar clientes:", err);
    return {
      clientes: [],
      count: 0,
      error: "No es posible cargar los clientes"
    };
  }
}

export const actions = {
  eliminar: async ({ request, fetch }) => {
    try {
      const form = await request.formData();
      const idsString = form.get("ids")?.toString();

      if (!idsString) {
        return fail(400, { error: "No se especificaron clientes para eliminar" });
      }

      const ids = JSON.parse(idsString);
      if (!Array.isArray(ids) || ids.length === 0) {
        return fail(400, { error: "Lista de IDs inválida" });
      }

      try {
        const bulkRes = await fetch(`${API_BASE_URL}/clientes`, {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ids })
        });

        if (bulkRes.ok) {
          const payload = await bulkRes.json().catch(() => ({}));
          return {
            success: true,
            message: `${payload?.deleted ?? ids.length} cliente(s) eliminado(s) exitosamente`
          };
        }
      } catch (bulkError) {
        console.error("Error en eliminación masiva:", bulkError);
      }

      let exitosos = 0;
      let errores = [];

      for (const id of ids) {
        try {
          const res = await fetch(`${API_BASE_URL}/clientes/${id}`, {
            method: "DELETE"
          });

          if (res.ok) {
            exitosos++;
          } else {
            const err = await res.json().catch(() => ({}));
            errores.push(`ID ${id}: ${err.detail || "Error desconocido"}`);
          }
        } catch {
          errores.push(`ID ${id}: Error de conexión`);
        }
      }

      if (exitosos > 0) {
        return {
          success: true,
          message: `${exitosos} cliente(s) eliminado(s)`,
          warnings: errores.length ? errores : undefined
        };
      }

      return fail(400, {
        error: "No se pudieron eliminar los clientes",
        details: errores
      });
    } catch (err) {
      console.error("Error eliminando clientes:", err);
      return fail(500, { error: "Error interno del servidor" });
    }
  }
};
