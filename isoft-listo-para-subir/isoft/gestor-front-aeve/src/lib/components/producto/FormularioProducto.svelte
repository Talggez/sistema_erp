<script>
    export let open = false;
    export let handleClose;
    export let producto = null;
    export let onProductoGuardado = () => {};

    let isSubmitting = false;
    let error = null;
    let tiposProducto = [];
    let loadingTipos = false;

    let formData = {
        codigo_ska: "",
        nombre: "",
        unidades: "",
        descripcion: "",
        tipo_producto_id: null,
        precio_neto: "",
        precio_bruto: "",
        descuento: "0",
    };

    let imagenFile = null;
    let imagenPreview = null;
    let modoIngreso = "neto"; // 'neto' o 'bruto'

    const IVA_FIJO = 19; // IVA fijo al 19%

    // Función para actualizar precio bruto cuando cambia el neto
    function onNetoChange() {
        const neto = parseFloat(formData.precio_neto) || 0;
        if (neto > 0) {
            formData.precio_bruto = (neto * (1 + IVA_FIJO / 100)).toFixed(0);
        } else {
            formData.precio_bruto = "";
        }
    }

    // Función para actualizar precio neto cuando cambia el bruto
    function onBrutoChange() {
        const bruto = parseFloat(formData.precio_bruto) || 0;
        if (bruto > 0) {
            formData.precio_neto = (bruto / (1 + IVA_FIJO / 100)).toFixed(0);
        } else {
            formData.precio_neto = "";
        }
    }

    function cambiarModoIngreso(modo) {
        modoIngreso = modo;
    }

    $: isEditing = producto !== null;
    $: modalTitle = isEditing ? "Editar Producto" : "Nuevo Producto";
    $: submitButtonText = isEditing ? "Actualizar Producto" : "Crear Producto";

    // Cálculos para el resumen
    $: descuentoNum = parseFloat(formData.descuento) || 0;
    $: precioNetoCalculado = parseFloat(formData.precio_neto) || 0;
    $: precioBrutoCalculado = parseFloat(formData.precio_bruto) || 0;
    $: montoIva = precioNetoCalculado * (IVA_FIJO / 100);
    $: montoDescuento = precioBrutoCalculado * (descuentoNum / 100);
    $: precioFinal = precioBrutoCalculado - montoDescuento;

    // Cargar tipos de producto al abrir el modal
    async function cargarTiposProducto() {
        loadingTipos = true;
        try {
            const response = await fetch("http://localhost:5000/tipos-producto");
            if (response.ok) {
                tiposProducto = await response.json();
            }
        } catch (err) {
            console.error("Error al cargar tipos de producto:", err);
        } finally {
            loadingTipos = false;
        }
    }

    // Cargar datos del producto cuando se abre para editar
    $: if (open) {
        cargarTiposProducto();
        if (producto && isEditing) {
            formData = {
                codigo_ska: producto.codigo_ska || "",
                nombre: producto.nombre || "",
                unidades: producto.unidades?.toString() || "",
                descripcion: producto.descripcion || "",
                tipo_producto_id: producto.tipo_producto_id || null,
                precio_neto: producto.precio_neto?.toString() || "0",
                precio_bruto: producto.precio_bruto?.toString() || "0",
                descuento: producto.descuento?.toString() || "0",
            };
            modoIngreso = "neto";
            imagenPreview = producto.imagen_url ? `http://localhost:5000${producto.imagen_url}` : null;
        } else {
            resetForm();
        }
        error = null; // Limpiar errores al abrir
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

    function handleImageChange(e) {
        const file = e.target.files?.[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                error = "Por favor selecciona un archivo de imagen válido.";
                return;
            }

            if (file.size > 5 * 1024 * 1024) { // 5MB max
                error = "La imagen no debe superar los 5MB.";
                return;
            }

            imagenFile = file;

            // Crear preview
            const reader = new FileReader();
            reader.onload = (event) => {
                imagenPreview = event.target.result;
            };
            reader.readAsDataURL(file);
            error = null;
        }
    }

    function removeImage() {
        imagenFile = null;
        imagenPreview = null;
        const inputElement = document.getElementById("imagen");
        if (inputElement) {
            inputElement.value = "";
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (isSubmitting) return;

        // Validar solo campos requeridos
        if (!formData.nombre?.trim()) {
            error = "El nombre del producto es obligatorio.";
            return;
        }

        if (formData.unidades && isNaN(Number(formData.unidades))) {
            error = "Las unidades deben ser un número válido.";
            return;
        }

        isSubmitting = true;
        error = null;

        try {
            // Crear FormData para enviar archivos
            const formDataToSend = new FormData();
            formDataToSend.append("nombre", formData.nombre.trim());
            formDataToSend.append("codigo_ska", formData.codigo_ska.trim() || "");
            formDataToSend.append("unidades", formData.unidades ? parseInt(formData.unidades).toString() : "0");
            formDataToSend.append("descripcion", formData.descripcion.trim() || "");
            formDataToSend.append("precio_neto", precioNetoCalculado.toString());
            formDataToSend.append("iva", IVA_FIJO.toString());
            formDataToSend.append("precio_bruto", precioBrutoCalculado.toString());
            formDataToSend.append("descuento", descuentoNum.toString());

            if (formData.tipo_producto_id) {
                formDataToSend.append("tipo_producto_id", formData.tipo_producto_id.toString());
            }

            if (imagenFile) {
                formDataToSend.append("imagen", imagenFile);
            }

            let response;
            let url;
            let method;

            if (isEditing) {
                url = `http://localhost:5000/productos/${producto.id}`;
                method = "PUT";
            } else {
                url = "http://localhost:5000/productos";
                method = "POST";
            }

            response = await fetch(url, {
                method,
                body: formDataToSend,
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
                    console.error("Error parsing response:", parseError);
                }

                throw new Error(errorMessage);
            }

            // Éxito
            if (onProductoGuardado) {
                await onProductoGuardado();
            }

            closeModal();

        } catch (err) {
            console.error("Error en handleSubmit:", err);
            error = err.message || "Error inesperado al guardar el producto";
        } finally {
            isSubmitting = false;
        }
    }

    function resetForm() {
        formData = {
            codigo_ska: "",
            nombre: "",
            unidades: "",
            descripcion: "",
            tipo_producto_id: null,
            precio_neto: "",
            precio_bruto: "",
            descuento: "0",
        };
        modoIngreso = "neto";
        imagenFile = null;
        imagenPreview = null;
        error = null;
    }
</script>

<svelte:window on:keydown={handleKeydown} />

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
                    <div class="absolute top-1/4 right-1/4 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl"></div>
                    <div class="absolute bottom-1/4 left-1/4 w-48 h-48 bg-orange-500/5 rounded-full blur-3xl"></div>
                </div>

                <!-- Header -->
                <div class="relative z-10 flex items-center justify-between p-8 border-b border-[#1f1f1f]/50">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                            <svg
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="white"
                                    stroke-width="2"
                            >
                                <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="text-2xl font-semibold text-white">
                                {modalTitle}
                            </h2>
                            <p class="text-sm text-gray-400 mt-1">
                                {isEditing
                                    ? "Modifica la información del producto"
                                    : "Completa los datos del nuevo producto"}
                            </p>
                        </div>
                    </div>

                    <button
                            on:click={closeModal}
                            disabled={isSubmitting}
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
                                    class="text-blue-400"
                            >
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                <polyline points="14,2 14,8 20,8" />
                                <line x1="16" y1="13" x2="8" y2="13" />
                                <line x1="16" y1="17" x2="8" y2="17" />
                                <polyline points="10,9 9,9 8,9" />
                            </svg>
                            Información Básica
                        </h3>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label
                                        for="nombre"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Nombre del Producto *
                                </label>
                                <input
                                        type="text"
                                        id="nombre"
                                        bind:value={formData.nombre}
                                        required
                                        disabled={isSubmitting}
                                        placeholder="Ej: iPhone 14 Pro Max"
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                />
                            </div>

                            <div class="space-y-2">
                                <label
                                        for="codigo_ska"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Código/SKU
                                </label>
                                <input
                                        type="text"
                                        id="codigo_ska"
                                        bind:value={formData.codigo_ska}
                                        disabled={isSubmitting}
                                        placeholder="Ej: IPH14PM-256GB"
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-mono"
                                />
                            </div>

                            <div class="space-y-2">
                                <label
                                        for="tipo_producto_id"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Tipo de Producto
                                </label>
                                <select
                                        id="tipo_producto_id"
                                        bind:value={formData.tipo_producto_id}
                                        disabled={isSubmitting || loadingTipos}
                                        class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <option value={null}>
                                        {loadingTipos ? "Cargando tipos..." : "Seleccionar tipo"}
                                    </option>
                                    {#each tiposProducto as tipo}
                                        <option value={tipo.id}>{tipo.nombre}</option>
                                    {/each}
                                </select>
                            </div>

                            <div class="space-y-2">
                                <label
                                        for="unidades"
                                        class="block text-sm font-medium text-gray-300"
                                >
                                    Stock Inicial
                                </label>
                                <div class="relative">
                                    <input
                                            type="number"
                                            id="unidades"
                                            bind:value={formData.unidades}
                                            min="0"
                                            disabled={isSubmitting}
                                            placeholder="0"
                                            class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                    <span class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm">
                                        unidades
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Precios y Descuentos -->
                    <div class="space-y-6">
                        <h3 class="text-lg font-medium text-white flex items-center gap-2">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="text-yellow-400"
                            >
                                <line x1="12" y1="1" x2="12" y2="23"/>
                                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                            </svg>
                            Precios y Descuentos
                        </h3>

                        <div class="space-y-6">
                            <!-- Selector de modo de ingreso -->
                            <div class="flex gap-2 p-1 bg-[#0a0a0a] rounded-lg border border-[#2a2a2a]">
                                <button
                                    type="button"
                                    on:click={() => cambiarModoIngreso("neto")}
                                    class="flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all {modoIngreso === 'neto' ? 'bg-yellow-600 text-white' : 'text-gray-400 hover:text-white'}"
                                >
                                    Ingresar Precio Neto
                                </button>
                                <button
                                    type="button"
                                    on:click={() => cambiarModoIngreso("bruto")}
                                    class="flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all {modoIngreso === 'bruto' ? 'bg-yellow-600 text-white' : 'text-gray-400 hover:text-white'}"
                                >
                                    Ingresar Precio Bruto
                                </button>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <!-- Campo de precio según modo -->
                                {#if modoIngreso === "neto"}
                                    <div class="space-y-2">
                                        <label
                                                for="precio_neto"
                                                class="block text-sm font-medium text-gray-300"
                                        >
                                            Precio Neto (sin IVA)
                                        </label>
                                        <div class="relative">
                                            <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">$</span>
                                            <input
                                                    type="number"
                                                    id="precio_neto"
                                                    bind:value={formData.precio_neto}
                                                    on:input={onNetoChange}
                                                    min="0"
                                                    step="1"
                                                    disabled={isSubmitting}
                                                    placeholder="0"
                                                    class="w-full pl-8 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                            />
                                        </div>
                                    </div>
                                {:else}
                                    <div class="space-y-2">
                                        <label
                                                for="precio_bruto"
                                                class="block text-sm font-medium text-gray-300"
                                        >
                                            Precio Bruto (con IVA)
                                        </label>
                                        <div class="relative">
                                            <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">$</span>
                                            <input
                                                    type="number"
                                                    id="precio_bruto"
                                                    bind:value={formData.precio_bruto}
                                                    on:input={onBrutoChange}
                                                    min="0"
                                                    step="1"
                                                    disabled={isSubmitting}
                                                    placeholder="0"
                                                    class="w-full pl-8 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                            />
                                        </div>
                                    </div>
                                {/if}

                                <!-- Descuento -->
                                <div class="space-y-2">
                                    <label
                                            for="descuento"
                                            class="block text-sm font-medium text-gray-300"
                                    >
                                        Descuento (%)
                                    </label>
                                    <div class="relative">
                                        <input
                                                type="number"
                                                id="descuento"
                                                bind:value={formData.descuento}
                                                min="0"
                                                max="100"
                                                step="0.1"
                                                disabled={isSubmitting}
                                                placeholder="0"
                                                class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:border-yellow-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                        />
                                        <span class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">%</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Resumen de precios calculados -->
                            <div class="bg-[#0a0a0a] border border-[#2a2a2a] rounded-xl p-4 space-y-2">
                                <div class="text-sm font-medium text-gray-300 mb-3">Resumen de Precios</div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-400">Precio Neto:</span>
                                    <span class="text-white">${precioNetoCalculado.toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-gray-400">IVA ({IVA_FIJO}%):</span>
                                    <span class="text-yellow-400">+${montoIva.toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
                                </div>
                                <div class="flex justify-between text-sm border-t border-[#2a2a2a] pt-2">
                                    <span class="text-gray-400">Precio Bruto:</span>
                                    <span class="text-white font-medium">${precioBrutoCalculado.toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
                                </div>
                                {#if descuentoNum > 0}
                                    <div class="flex justify-between text-sm">
                                        <span class="text-gray-400">Descuento ({descuentoNum}%):</span>
                                        <span class="text-red-400">-${montoDescuento.toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
                                    </div>
                                    <div class="flex justify-between text-sm border-t border-[#2a2a2a] pt-2">
                                        <span class="text-green-400 font-medium">Precio Final:</span>
                                        <span class="text-green-400 font-bold">${precioFinal.toLocaleString('es-CL', {minimumFractionDigits: 0, maximumFractionDigits: 0})}</span>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>

                    <!-- Imagen del producto -->
                    <div class="space-y-6">
                        <h3 class="text-lg font-medium text-white flex items-center gap-2">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="text-green-400"
                            >
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <polyline points="21 15 16 10 5 21"/>
                            </svg>
                            Imagen del Producto
                        </h3>

                        <div class="space-y-4">
                            <div class="flex items-center gap-4">
                                {#if imagenPreview}
                                    <div class="relative">
                                        <img
                                                src={imagenPreview}
                                                alt="Vista previa"
                                                class="w-24 h-24 object-cover rounded-lg border-2 border-blue-500/30"
                                        />
                                        <button
                                                type="button"
                                                on:click={removeImage}
                                                disabled={isSubmitting}
                                                class="absolute -top-2 -right-2 w-6 h-6 bg-red-600 hover:bg-red-700 text-white rounded-full flex items-center justify-center transition-colors disabled:opacity-50"
                                        >
                                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                <line x1="18" y1="6" x2="6" y2="18" />
                                                <line x1="6" y1="6" x2="18" y2="18" />
                                            </svg>
                                        </button>
                                    </div>
                                {/if}
                                <div class="flex-1">
                                    <label
                                            for="imagen"
                                            class="block text-sm font-medium text-gray-300 mb-2"
                                    >
                                        {imagenPreview ? "Cambiar imagen" : "Seleccionar imagen"}
                                    </label>
                                    <input
                                            type="file"
                                            id="imagen"
                                            accept="image/png, image/jpeg, image/jpg"
                                            on:change={handleImageChange}
                                            disabled={isSubmitting}
                                            class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                    <p class="text-xs text-gray-500 mt-1">
                                        PNG o JPEG, máximo 5MB. La imagen se redimensionará a 100x100px.
                                    </p>
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
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                <polyline points="14,2 14,8 20,8" />
                                <line x1="16" y1="13" x2="8" y2="13" />
                                <line x1="16" y1="17" x2="8" y2="17" />
                                <polyline points="10,9 9,9 8,9" />
                            </svg>
                            Descripción Adicional
                        </h3>

                        <div class="space-y-2">
                            <label
                                    for="descripcion"
                                    class="block text-sm font-medium text-gray-300"
                            >
                                Descripción del Producto
                            </label>
                            <textarea
                                    id="descripcion"
                                    bind:value={formData.descripcion}
                                    rows="4"
                                    disabled={isSubmitting}
                                    placeholder="Describe las características principales del producto..."
                                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed resize-none"
                            ></textarea>
                            <p class="text-xs text-gray-500">
                                Información adicional que ayude a identificar el producto
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
                                disabled={isSubmitting}
                                class="px-6 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1f1f1f]/50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancelar
                        </button>

                        <button
                                type="button"
                                on:click={handleSubmit}
                                disabled={isSubmitting || !formData.nombre?.trim()}
                                class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25"
                        >
                            {#if isSubmitting}
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
        background: rgba(59, 130, 246, 0.5);
        border-radius: 3px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }

    /* Quitar las flechas de los inputs number */
    input[type="number"]::-webkit-outer-spin-button,
    input[type="number"]::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    /* Para Firefox */
    input[type="number"] {
        -moz-appearance: textfield;
    }
</style>