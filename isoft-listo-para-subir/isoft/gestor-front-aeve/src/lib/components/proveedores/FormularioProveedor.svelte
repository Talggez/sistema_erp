<script>
    export let open = false;
    export let handleClose;
    export let proveedor = null;
    export let modo = "agregar";
    export let onProveedorGuardado = null;

    let guardando = false;
    let error = null;

    // Datos del formulario proveedor
    let formData = {
        nombre: "",
        rut: "",
        direccion: "",
        email: "",
        telefono: "",
        web: "",
        descripcion: "",
    };

    $: modalTitle = modo === "editar" ? "Editar Proveedor" : "Nuevo Proveedor";
    $: submitButtonText = modo === "editar" ? "Actualizar Proveedor" : "Crear Proveedor";

    // Cargar datos del proveedor cuando se abre para editar
    $: if (open) {
        if (proveedor && modo === "editar") {
            formData = {
                nombre: proveedor.nombre || "",
                rut: proveedor.rut || "",
                direccion: proveedor.direccion || "",
                email: proveedor.email || "",
                telefono: proveedor.telefono || "",
                web: proveedor.web || "",
                descripcion: proveedor.descripcion || "",
            };
        } else {
            resetForm();
        }
        error = null; // Limpiar errores al abrir
    }

    function resetForm() {
        formData = {
            nombre: "",
            rut: "",
            direccion: "",
            email: "",
            telefono: "",
            web: "",
            descripcion: "",
        };
        error = null;
    }

    function closeModal() {
        resetForm();
        handleClose();
    }

    function handleBackdropClick(e) {
        if (e.target === e.currentTarget && !guardando) {
            closeModal();
        }
    }

    function handleKeyDown(e) {
        if (e.key === "Escape" && !guardando) {
            closeModal();
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (guardando) return;

        // Validar solo campos requeridos
        if (!formData.nombre?.trim()) {
            error = "El nombre del proveedor es obligatorio.";
            return;
        }

        // Validar formato de campos opcionales si están presentes
        if (formData.email && !validarEmail(formData.email)) {
            error = "El formato del email no es válido.";
            return;
        }

        if (formData.rut && !validarRUT(formData.rut)) {
            error = "El formato del RUT no es válido. Ejemplo: 12345678-9";
            return;
        }

        guardando = true;
        error = null;

        try {
            let response;
            let url;
            let method;

            if (modo === "editar") {
                url = `http://localhost:5000/actualizar_proveedores/${proveedor.id}`;
                method = "PUT";
            } else {
                url = "http://localhost:5000/nuevo_proveedor";
                method = "POST";
            }

            // Mapear campos del frontend a backend
            const datosAEnviar = {
                nombre: formData.nombre,
                rut: formData.rut || "",
                direccion: formData.direccion || "",
                telefono: formData.telefono || "",
                email: formData.email || "",
                web: formData.web || "",
                descripcion: formData.descripcion || "",
            };

            response = await fetch(url, {
                method,
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(datosAEnviar),
            });

            if (!response.ok) {
                let errorMessage = `Error ${response.status}: ${response.statusText}`;

                try {
                    const errorData = await response.json();

                    if (errorData.detail) {
                        if (typeof errorData.detail === "string") {
                            errorMessage = errorData.detail;
                        } else if (Array.isArray(errorData.detail)) {
                            // Manejar errores de validación de FastAPI
                            errorMessage = errorData.detail
                                .map((e) => {
                                    const field = e.loc && e.loc.length > 1 ? e.loc[1] : "campo";
                                    return `${field}: ${e.msg}`;
                                })
                                .join(", ");
                        }
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                } catch (parseError) {
                    // Si no se puede parsear la respuesta, usar el mensaje de estado HTTP
                    console.error("Error parsing response:", parseError);
                }

                throw new Error(errorMessage);
            }

            // Éxito
            if (onProveedorGuardado) {
                await onProveedorGuardado();
            }

            closeModal();

        } catch (err) {
            console.error("Error en handleSubmit:", err);
            error = err.message || "Error inesperado al guardar el proveedor";
        } finally {
            guardando = false;
        }
    }

    // Validar RUT chileno (formato básico)
    function validarRUT(rut) {
        if (!rut) return true; // Opcional
        const rutLimpio = rut.replace(/\./g, '').trim();
        const rutPattern = /^[0-9]+-[0-9kK]{1}$/;
        return rutPattern.test(rutLimpio);
    }

    // Validar email
    function validarEmail(email) {
        if (!email) return true; // Opcional
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email.trim());
    }

    // Validar teléfono chileno
    function validarTelefono(telefono) {
        if (!telefono) return true; // Opcional
        const telefonoPattern = /^(\+56|56)?[\s-]?[9]?[\s-]?[0-9]{4}[\s-]?[0-9]{4}$/;
        return telefonoPattern.test(telefono.replace(/\s/g, ""));
    }
</script>

<svelte:window on:keydown={handleKeyDown} />

{#if open}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div
                class="fixed inset-0 bg-black/70 backdrop-blur-sm"
                on:click={handleBackdropClick}
                role="button"
                tabindex="-1"
        ></div>

        <!-- Modal Content -->
        <div class="relative w-full max-w-4xl max-h-[90vh] overflow-hidden z-10">
            <!-- Contenido del modal -->
            <div
                    class="relative bg-gradient-to-br from-[#0a0a0a] via-[#111111] to-[#0a0a0a] border border-[#1f1f1f]/50 rounded-2xl shadow-2xl overflow-hidden"
            >
                <!-- Efectos de fondo -->
                <div class="absolute inset-0 overflow-hidden pointer-events-none">
                    <div class="absolute top-1/4 right-1/4 w-64 h-64 bg-orange-500/5 rounded-full blur-3xl"></div>
                    <div class="absolute bottom-1/4 left-1/4 w-48 h-48 bg-blue-500/5 rounded-full blur-3xl"></div>
                </div>

                <!-- Header -->
                <div class="relative z-10 flex items-center justify-between p-8 border-b border-[#1f1f1f]/50">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
                            <svg
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="white"
                                    stroke-width="2"
                            >
                                <path d="M3 21h18" />
                                <path d="M5 21V7l8-4v18" />
                                <path d="M19 21V11l-6-4" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="text-2xl font-semibold text-white">
                                {modalTitle}
                            </h2>
                            <p class="text-sm text-gray-400 mt-1">
                                {modo === "editar"
                                    ? "Modifica la información del proveedor"
                                    : "Completa los datos del nuevo proveedor"}
                            </p>
                        </div>
                    </div>

                    <button
                            on:click={closeModal}
                            disabled={guardando}
                            class="p-2 text-gray-400 hover:text-white hover:bg-[#1f1f1f]/50 rounded-lg transition-all duration-200 disabled:opacity-50"
                            type="button"
                    >
                        <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                        >
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                <!-- Mensaje de error -->
                {#if error}
                    <div class="mx-8 mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3">
                        <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                class="text-red-400 mt-0.5 flex-shrink-0"
                        >
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                        <div>
                            <div class="font-medium text-red-300">Error al guardar</div>
                            <div class="text-sm text-red-400 mt-1">{error}</div>
                        </div>
                    </div>
                {/if}

                <!-- Formulario -->
                <form
                        on:submit={handleSubmit}
                        class="p-8 space-y-8 max-h-[60vh] overflow-y-auto custom-scrollbar"
                >
                    <!-- Información básica -->
                    <div class="space-y-6">
                        <h3 class="text-lg font-medium text-white flex items-center gap-2">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="text-orange-400"
                            >
                                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                                <circle cx="9" cy="7" r="4" />
                                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                            </svg>
                            Información Básica
                        </h3>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label
                                        for="nombre"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Nombre del Proveedor *
                                </label>
                                <input
                                        type="text"
                                        id="nombre"
                                        bind:value={formData.nombre}
                                        required
                                        disabled={guardando}
                                        placeholder="Ej: Distribuidora XYZ Ltda."
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div class="space-y-2">
                                <label
                                        for="rut"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    RUT
                                </label>
                                <input
                                        type="text"
                                        id="rut"
                                        bind:value={formData.rut}
                                        disabled={guardando}
                                        placeholder="12.345.678-9"
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-mono"
                                />
                                {#if formData.rut && !validarRUT(formData.rut)}
                                    <p class="text-xs text-orange-400 mt-1">
                                        Formato: 12345678-9
                                    </p>
                                {/if}
                            </div>

                            <div class="space-y-2 md:col-span-2">
                                <label
                                        for="direccion"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Dirección
                                </label>
                                <input
                                        type="text"
                                        id="direccion"
                                        bind:value={formData.direccion}
                                        disabled={guardando}
                                        placeholder="Av. Providencia 1234, Providencia, Santiago"
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                />
                            </div>
                        </div>
                    </div>

                    <!-- Información de contacto -->
                    <div class="space-y-6">
                        <h3 class="text-lg font-medium text-white flex items-center gap-2">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="text-blue-400"
                            >
                                <path
                                        d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
                                />
                            </svg>
                            Información de Contacto
                        </h3>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label
                                        for="email"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Email
                                </label>
                                <div class="relative">
                                    <span
                                            class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
                                    >@</span
                                    >
                                    <input
                                            type="email"
                                            id="email"
                                            bind:value={formData.email}
                                            disabled={guardando}
                                            placeholder="contacto@proveedor.com"
                                            class="w-full pl-8 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                </div>
                                {#if formData.email && !validarEmail(formData.email)}
                                    <p class="text-xs text-blue-400 mt-1">
                                        Ingresa un email válido
                                    </p>
                                {/if}
                            </div>

                            <div class="space-y-2">
                                <label
                                        for="telefono"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Teléfono
                                </label>
                                <div class="relative">
                                    <span
                                            class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
                                    >📞</span
                                    >
                                    <input
                                            type="tel"
                                            id="telefono"
                                            bind:value={formData.telefono}
                                            disabled={guardando}
                                            placeholder="+56 9 1234 5678"
                                            class="w-full pl-10 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                </div>
                                {#if formData.telefono && !validarTelefono(formData.telefono)}
                                    <p class="text-xs text-blue-400 mt-1">
                                        Formato: +56 9 1234 5678
                                    </p>
                                {/if}
                            </div>

                            <div class="space-y-2 md:col-span-2">
                                <label
                                        for="web"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Sitio Web
                                </label>
                                <div class="relative">
                                    <span
                                            class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
                                    >🌐</span
                                    >
                                    <input
                                            type="url"
                                            id="web"
                                            bind:value={formData.web}
                                            disabled={guardando}
                                            placeholder="https://www.proveedor.com"
                                            class="w-full pl-10 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Descripción -->
                    <div class="space-y-6">
                        <h3 class="text-lg font-medium text-white flex items-center gap-2">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="text-purple-400"
                            >
                                <path
                                        d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                                />
                                <polyline points="14,2 14,8 20,8" />
                                <line x1="16" y1="13" x2="8" y2="13" />
                                <line x1="16" y1="17" x2="8" y2="17" />
                                <polyline points="10,9 9,9 8,9" />
                            </svg>
                            Información Adicional
                        </h3>

                        <div class="space-y-2">
                            <label
                                    for="descripcion"
                                    class="block text-sm font-medium text-gray-300"
                            >
                                Descripción del Proveedor
                            </label>
                            <textarea
                                    id="descripcion"
                                    bind:value={formData.descripcion}
                                    rows="4"
                                    disabled={guardando}
                                    placeholder="Describe los productos o servicios que ofrece este proveedor..."
                                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed resize-none"
                            ></textarea>
                            <p class="text-xs text-gray-500">
                                Información adicional sobre los productos o servicios del proveedor
                            </p>
                        </div>
                    </div>
                </form>

                <!-- Footer con botones -->
                <div class="relative z-10 flex items-center justify-between p-8 border-t border-[#1f1f1f]/50 bg-[#0a0a0a]/80 backdrop-blur-sm">
                    <div class="text-sm text-gray-400">
                        * Solo el nombre es obligatorio
                    </div>

                    <div class="flex items-center gap-3">
                        <button
                                type="button"
                                on:click={closeModal}
                                disabled={guardando}
                                class="px-6 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1f1f1f]/50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancelar
                        </button>

                        <button
                                type="button"
                                on:click={handleSubmit}
                                disabled={guardando || !formData.nombre?.trim()}
                                class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-orange-500/25"
                        >
                            {#if guardando}
                                <div
                                        class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                                ></div>
                                Guardando...
                            {:else}
                                <svg
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                >
                                    <path
                                            d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"
                                    />
                                    <polyline points="17,21 17,13 7,13 7,21" />
                                    <polyline points="7,3 7,8 15,8" />
                                </svg>
                                {submitButtonText}
                            {/if}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: rgba(31, 31, 31, 0.3);
        border-radius: 3px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: rgba(249, 115, 22, 0.5);
        border-radius: 3px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: rgba(249, 115, 22, 0.7);
    }
</style>