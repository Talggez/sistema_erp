import { error, fail } from "@sveltejs/kit";

const API_BASE_URL = "http://localhost:5000";

export async function load({ fetch }) {
  try {
    const resultCall = await fetch(`${API_BASE_URL}/proveedores`);

    if (!resultCall.ok) {
      console.error("❌ Error en la respuesta:", resultCall.status, resultCall.statusText);
      return {
        proveedores: [],
        error: `Error del servidor: ${resultCall.status} ${resultCall.statusText}`,
      };
    }

    const data = await resultCall.json();

    // El backend puede devolver directamente un array o { status: "success", data: [...] }
    let proveedores = [];
    if (Array.isArray(data)) {
      proveedores = data;
    } else if (data.data && Array.isArray(data.data)) {
      proveedores = data.data;
    }

    return {
      proveedores: proveedores,
      error: null
    };

  } catch (error) {
    console.error("Failed to load suppliers", error);
    return {
      proveedores: [],
      error: "No es posible cargar los proveedores"
    }
  }
}

/** @type {import('./$types').Actions} */
export const actions = {
  crear: async ({ request, fetch }) => {
    try {
      const data = await request.formData();

      const proveedor = {
        rut: data.get("rut")?.toString().trim(),
        name: data.get("nombre")?.toString().trim(),
        address: data.get("direccion")?.toString().trim() || "",
        phone_number: data.get("telefono")?.toString().trim() || "",
        email: data.get("email")?.toString().trim() || "",
        web: "",
        description: ""
      };

      // Validaciones básicas
      if (!proveedor.name || !proveedor.rut) {
        return fail(400, {
          error: "Nombre y RUT son campos obligatorios",
        });
      }

      const response = await fetch(`${API_BASE_URL}/nuevo_proveedor`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(proveedor),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return fail(response.status, {
          error: errorData.detail || `Error ${response.status}`,
        });
      }

      return { success: true, message: "Proveedor creado exitosamente" };

    } catch (err) {
      console.error("Error creando proveedor:", err);
      return fail(500, { error: "Error interno del servidor" });
    }
  },

  actualizar: async ({ request, fetch }) => {
    try {
      const data = await request.formData();
      const id = data.get("id")?.toString();

      const proveedor = {
        rut: data.get("rut")?.toString().trim(),
        name: data.get("nombre")?.toString().trim(),
        address: data.get("direccion")?.toString().trim() || "",
        phone_number: data.get("telefono")?.toString().trim() || "",
        email: data.get("email")?.toString().trim() || "",
        web: "",
        description: ""
      };

      if (!id || !proveedor.name || !proveedor.rut) {
        return fail(400, {
          error: "ID, nombre y RUT son campos obligatorios",
        });
      }

      const response = await fetch(`${API_BASE_URL}/actualizar_proveedores/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(proveedor),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return fail(response.status, {
          error: errorData.detail || `Error ${response.status}`,
        });
      }

      return { success: true, message: "Proveedor actualizado exitosamente" };

    } catch (err) {
      console.error("Error actualizando proveedor:", err);
      return fail(500, { error: "Error interno del servidor" });
    }
  },

  eliminar: async ({ request, fetch }) => {
    try {
      const data = await request.formData();
      const idsString = data.get("ids")?.toString();

      if (!idsString) {
        return fail(400, { error: "No se especificaron proveedores para eliminar" });
      }

      const ids = JSON.parse(idsString);

      if (!Array.isArray(ids) || ids.length === 0) {
        return fail(400, { error: "Lista de IDs inválida" });
      }

      let exitosos = 0;
      let errores = [];

      // Eliminar proveedores uno por uno
      for (const id of ids) {
        try {
          const response = await fetch(`${API_BASE_URL}/eliminar_proveedor/${id}`, {
            method: "DELETE",
          });

          if (response.ok) {
            exitosos++;
          } else {
            const errorData = await response.json().catch(() => ({}));
            errores.push(`Proveedor ID ${id}: ${errorData.detail || 'Error desconocido'}`);
          }
        } catch (err) {
          errores.push(`Proveedor ID ${id}: Error de conexión`);
        }
      }

      if (exitosos > 0) {
        return {
          success: true,
          message: `${exitosos} proveedor(es) eliminado(s) exitosamente`,
          warnings: errores.length > 0 ? errores : undefined
        };
      } else {
        return fail(400, {
          error: "No se pudieron eliminar los proveedores",
          details: errores,
        });
      }

    } catch (err) {
      console.error("Error eliminando proveedores:", err);
      return fail(500, { error: "Error interno del servidor" });
    }
  },
};