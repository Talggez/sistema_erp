<script>
    export let open = false;
    export let handleClose;
    export let usuario = null;
    export let onUsuarioGuardado = () => {};

    let isSubmitting = false;
    let error = null;
    let success = false;

    let formData = {
        nombre: "",
        usuario: "",
        email: "",
        telefono: "",
        rol: ""
    };

    $: isEditing = usuario !== null;

    // Cargar datos del usuario cuando se abre el modal
    $: if (open && usuario) {
        formData = {
            nombre: usuario.nombre || "",
            usuario: usuario.usuario || "admin",
            email: usuario.email || "",
            telefono: usuario.telefono || "",
            rol: usuario.rol || "Administrador"
        };
        error = null;
        success = false;
    }

    function handleBackdropClick(e) {
        if (e.target === e.currentTarget && !isSubmitting) {
            closeModal();
        }
    }

    function handleKeydown(e) {
        if (e.key === "Escape" && !isSubmitting) {
            closeModal();
        }
    }

    function closeModal() {
        resetForm();
        handleClose();
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (isSubmitting) return;

        // Validar campos requeridos
        if (!formData.nombre?.trim()) {
            error = "El nombre es obligatorio.";
            return;
        }

        if (!formData.email?.trim()) {
            error = "El email es obligatorio.";
            return;
        }

        // Validar formato de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            error = "El formato del email no es válido.";
            return;
        }

        isSubmitting = true;
        error = null;

        try {
            const userData = {
                nombre: formData.nombre.trim(),
                usuario: formData.usuario.trim() || "admin",
                email: formData.email.trim(),
                telefono: formData.telefono.trim() || "",
                rol: formData.rol || "Administrador"
            };

            // Simulación de llamada a API
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Mostrar mensaje de éxito
            success = true;

            // Llamar callback
            if (onUsuarioGuardado) {
                await onUsuarioGuardado(userData);
            }

            // Cerrar modal después de un momento
            setTimeout(() => {
                closeModal();
            }, 1000);

        } catch (err) {
            console.error("Error en handleSubmit:", err);
            error = err.message || "Error inesperado al guardar el perfil";
        } finally {
            isSubmitting = false;
        }
    }

    function resetForm() {
        formData = {
            nombre: "",
            usuario: "",
            email: "",
            telefono: "",
            rol: ""
        };
        error = null;
        success = false;
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
    <!-- Backdrop -->
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
                class="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity duration-300"
                on:click={handleBackdropClick}
                role="button"
                tabindex="-1"
        ></div>

        <!-- Modal Container -->
        <div class="relative w-full max-w-4xl max-h-[95vh] z-10 transform transition-all duration-300 scale-100">

            <!-- Modal Content -->
            <div class="relative bg-[#111111] border border-[#1f1f1f] rounded-2xl shadow-2xl overflow-hidden">

                <!-- Header -->
                <div class="relative z-10 flex items-center justify-between p-6 border-b border-[#1f1f1f]">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600
                                    rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/25">
                            <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="text-2xl font-bold text-white">Editar Perfil</h2>
                            <p class="text-sm text-gray-400 mt-1">Actualiza los datos de tu cuenta</p>
                        </div>
                    </div>

                    <button
                            on:click={closeModal}
                            disabled={isSubmitting}
                            class="p-2.5 text-gray-400 hover:text-white hover:bg-[#1f1f1f]
                               rounded-xl transition-all duration-200 disabled:opacity-50
                               transform hover:scale-105 active:scale-95"
                            type="button"
                            aria-label="Cerrar modal"
                    >
                        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                <!-- Messages -->
                {#if error}
                    <div class="mx-6 mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl
                                flex items-start gap-3 animate-pulse">
                        <svg class="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                        <div>
                            <div class="font-semibold text-red-300">Error al guardar</div>
                            <div class="text-sm text-red-400 mt-1">{error}</div>
                        </div>
                    </div>
                {/if}

                {#if success}
                    <div class="mx-6 mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-xl
                                flex items-start gap-3 animate-pulse">
                        <svg class="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                            <polyline points="22,4 12,14.01 9,11.01" />
                        </svg>
                        <div>
                            <div class="font-semibold text-green-300">¡Perfil actualizado!</div>
                            <div class="text-sm text-green-400 mt-1">Los cambios se han guardado correctamente</div>
                        </div>
                    </div>
                {/if}

                <!-- Form Content -->
                <form on:submit={handleSubmit} class="p-6 space-y-8 max-h-[60vh] overflow-y-auto scrollbar-thin
                                                     scrollbar-thumb-[#333] scrollbar-track-transparent">

                    <!-- Información Básica -->
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none"
                                     stroke="currentColor" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                    <circle cx="12" cy="7" r="4" />
                                </svg>
                            </div>
                            <h3 class="text-lg font-semibold text-white">Información Básica</h3>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Nombre -->
                            <div class="space-y-2">
                                <label for="nombre" class="block text-sm font-medium text-gray-300">
                                    Nombre Completo *
                                </label>
                                <input
                                        type="text"
                                        id="nombre"
                                        bind:value={formData.nombre}
                                        required
                                        disabled={isSubmitting}
                                        placeholder="Ej: Juan Pérez"
                                        class="w-full px-4 py-3 bg-[#0a0a0a] border border-[#1f1f1f]
                                           rounded-xl text-white placeholder-gray-500
                                           focus:outline-none focus:ring-2 focus:ring-blue-500/50
                                           focus:border-blue-500/50 transition-all duration-200
                                           disabled:opacity-50 disabled:cursor-not-allowed
                                           hover:bg-[#111111]"
                                />
                            </div>

                            <!-- Usuario -->
                            <div class="space-y-2">
                                <label for="usuario" class="block text-sm font-medium text-gray-300">
                                    Usuario
                                </label>
                                <div class="relative">
                                    <span class="absolute left-4 top-1/2 transform -translate-y-1/2
                                                 text-gray-400 font-mono">@</span>
                                    <input
                                            type="text"
                                            id="usuario"
                                            bind:value={formData.usuario}
                                            disabled={isSubmitting}
                                            placeholder="tu_usuario"
                                            class="w-full pl-8 pr-4 py-3 bg-[#0a0a0a] border border-[#1f1f1f]
                                               rounded-xl text-white placeholder-gray-500 font-mono
                                               focus:outline-none focus:ring-2 focus:ring-blue-500/50
                                               focus:border-blue-500/50 transition-all duration-200
                                               disabled:opacity-50 disabled:cursor-not-allowed
                                               hover:bg-[#111111]"
                                    />
                                </div>
                            </div>

                            <!-- Rol -->
                            <div class="space-y-2 md:col-span-2">
                                <label for="rol" class="block text-sm font-medium text-gray-300">
                                    Rol del Sistema
                                </label>
                                <select
                                        id="rol"
                                        bind:value={formData.rol}
                                        disabled={isSubmitting}
                                        class="w-full px-4 py-3 bg-[#0a0a0a] border border-[#1f1f1f]
                                           rounded-xl text-white focus:outline-none focus:ring-2
                                           focus:ring-blue-500/50 focus:border-blue-500/50
                                           transition-all duration-200 disabled:opacity-50
                                           disabled:cursor-not-allowed hover:bg-[#111111]"
                                >
                                    <option value="">Seleccionar rol</option>
                                    <option value="Administrador">Administrador</option>
                                    <option value="Editor">Editor</option>
                                    <option value="Viewer">Viewer</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Información de Contacto -->
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-4 h-4 text-green-400" viewBox="0 0 24 24" fill="none"
                                     stroke="currentColor" stroke-width="2">
                                    <path d="M22 16.92V19a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.05 4.18 2 2 0 0 1 4 2h2.09a2 2 0 0 1 2 1.72c.12.9.3 1.78.57 2.63a2 2 0 0 1-.45 2.11L7.1 9.9a16 16 0 0 0 6 6l1.44-1.11a2 2 0 0 1 2.11-.45c.85.27 1.73.45 2.63.57A2 2 0 0 1 22 16.92z" />
                                </svg>
                            </div>
                            <h3 class="text-lg font-semibold text-white">Información de Contacto</h3>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Email -->
                            <div class="space-y-2">
                                <label for="email" class="block text-sm font-medium text-gray-300">
                                    Correo Electrónico *
                                </label>
                                <div class="relative">
                                    <svg class="absolute left-4 top-1/2 transform -translate-y-1/2
                                                w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="2">
                                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                        <polyline points="22,6 12,13 2,6"/>
                                    </svg>
                                    <input
                                            type="email"
                                            id="email"
                                            bind:value={formData.email}
                                            required
                                            disabled={isSubmitting}
                                            placeholder="contacto@aeve.cl"
                                            class="w-full pl-12 pr-4 py-3 bg-[#0a0a0a] border border-[#1f1f1f]
                                               rounded-xl text-white placeholder-gray-500
                                               focus:outline-none focus:ring-2 focus:ring-green-500/50
                                               focus:border-green-500/50 transition-all duration-200
                                               disabled:opacity-50 disabled:cursor-not-allowed
                                               hover:bg-[#111111]"
                                    />
                                </div>
                            </div>

                            <!-- Teléfono -->
                            <div class="space-y-2">
                                <label for="telefono" class="block text-sm font-medium text-gray-300">
                                    Teléfono
                                </label>
                                <div class="relative">
                                    <svg class="absolute left-4 top-1/2 transform -translate-y-1/2
                                                w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="2">
                                        <path d="M22 16.92V19a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.05 4.18 2 2 0 0 1 4 2h2.09a2 2 0 0 1 2 1.72c.12.9.3 1.78.57 2.63a2 2 0 0 1-.45 2.11L7.1 9.9a16 16 0 0 0 6 6l1.44-1.11a2 2 0 0 1 2.11-.45c.85.27 1.73.45 2.63.57A2 2 0 0 1 22 16.92z"/>
                                    </svg>
                                    <input
                                            type="tel"
                                            id="telefono"
                                            bind:value={formData.telefono}
                                            disabled={isSubmitting}
                                            placeholder="+56 9 1234 5678"
                                            class="w-full pl-12 pr-4 py-3 bg-[#0a0a0a] border border-[#1f1f1f]
                                               rounded-xl text-white placeholder-gray-500
                                               focus:outline-none focus:ring-2 focus:ring-green-500/50
                                               focus:border-green-500/50 transition-all duration-200
                                               disabled:opacity-50 disabled:cursor-not-allowed
                                               hover:bg-[#111111]"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Preview Section -->
                    <div class="space-y-6">
                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-4 h-4 text-purple-400" viewBox="0 0 24 24" fill="none"
                                     stroke="currentColor" stroke-width="2">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                    <circle cx="12" cy="12" r="3"/>
                                </svg>
                            </div>
                            <h3 class="text-lg font-semibold text-white">Vista Previa</h3>
                        </div>

                        <div class="p-4 bg-[#0a0a0a] border border-[#1f1f1f] rounded-xl">
                            <div class="flex items-center gap-4">
                                <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600
                                            rounded-full flex items-center justify-center">
                                    <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="2">
                                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                        <circle cx="12" cy="7" r="4" />
                                    </svg>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-white">
                                        {formData.nombre || 'Nombre del usuario'}
                                    </h4>
                                    <p class="text-sm text-gray-400">
                                        {formData.rol || 'Rol no especificado'} •
                                        @{formData.usuario || 'usuario'}
                                    </p>
                                    <p class="text-sm text-gray-500 mt-1">
                                        {formData.email || 'email@ejemplo.com'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>

                <!-- Footer -->
                <div class="relative z-10 flex items-center justify-between p-6 border-t border-[#1f1f1f]">
                    <div class="text-sm text-gray-400">
                        * Campos obligatorios
                    </div>

                    <div class="flex items-center gap-3">
                        <button
                                type="button"
                                on:click={closeModal}
                                disabled={isSubmitting}
                                class="px-6 py-3 border border-[#1f1f1f] text-gray-300 hover:text-white
                                   hover:bg-[#1f1f1f] rounded-xl transition-all duration-200
                                   disabled:opacity-50 disabled:cursor-not-allowed font-medium
                                   transform hover:scale-105 active:scale-95"
                        >
                            Cancelar
                        </button>

                        <button
                                type="button"
                                on:click={handleSubmit}
                                disabled={isSubmitting || !formData.nombre?.trim() || !formData.email?.trim()}
                                class="flex items-center gap-2 px-6 py-3
                                   bg-gradient-to-r from-orange-600 to-orange-500
                                   hover:from-orange-700 hover:to-orange-600
                                   text-white font-medium rounded-xl transition-all duration-200
                                   disabled:opacity-50 disabled:cursor-not-allowed
                                   shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40
                                   transform hover:scale-105 active:scale-95"
                        >
                            {#if isSubmitting}
                                <div class="w-4 h-4 border-2 border-white border-t-transparent
                                            rounded-full animate-spin"></div>
                                Guardando...
                            {:else if success}
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none"
                                     stroke="currentColor" stroke-width="2">
                                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                    <polyline points="22,4 12,14.01 9,11.01" />
                                </svg>
                                ¡Guardado!
                            {:else}
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none"
                                     stroke="currentColor" stroke-width="2">
                                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                                    <polyline points="17,21 17,13 7,13 7,21" />
                                    <polyline points="7,3 7,8 15,8" />
                                </svg>
                                Guardar Cambios
                            {/if}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}