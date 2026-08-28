<script>
    import FormularioProducto from "$lib/components/producto/FormularioProducto.svelte";
    import EliminadoExitosamente from "$lib/components/EliminadoExitosamente.svelte";
    import ConfirmarEliminacion from "$lib/components/producto/ConfirmarEliminacion.svelte";
    import { invalidateAll } from "$app/navigation";

    export let data;

    let showFormDialog = false;
    let productoAEditar = null;
    let productosSeleccionados = new Set();
    let mostrarModalEliminado = false;
    let productosEliminadosCount = 0;
    let busqueda = "";
    let filtroTipo = "todos";
    let filtroStock = "todos";
    let mostrarConfirmarEliminacion = false;
    let accionEliminarCallback = null;
    let showGestionarTiposDialog = false;

    // Gestión de tipos de producto
    let tiposProducto = [];
    let loadingTipos = false;
    let tipoEnEdicion = null;
    let formTipo = { nombre: "", descripcion: "" };
    let errorTipo = null;
    let isSubmittingTipo = false;

    // Cargar tipos al iniciar
    async function cargarTiposInicial() {
        try {
            const response = await fetch("http://localhost:5000/tipos-producto");
            if (response.ok) {
                tiposProducto = await response.json();
            }
        } catch (err) {
            console.error("Error al cargar tipos:", err);
        }
    }

    // Cargar tipos al iniciar la página
    cargarTiposInicial();

    async function cargarTipos() {
        loadingTipos = true;
        try {
            const response = await fetch("http://localhost:5000/tipos-producto");
            if (response.ok) {
                tiposProducto = await response.json();
                // Actualizar también para el selector de filtros
                await cargarTiposInicial();
            }
        } catch (err) {
            console.error("Error al cargar tipos:", err);
        } finally {
            loadingTipos = false;
        }
    }

    async function guardarTipo() {
        if (!formTipo.nombre?.trim()) {
            errorTipo = "El nombre es obligatorio";
            return;
        }

        isSubmittingTipo = true;
        errorTipo = null;

        try {
            const formData = new FormData();
            formData.append("nombre", formTipo.nombre.trim());
            formData.append("descripcion", formTipo.descripcion?.trim() || "");

            const url = tipoEnEdicion
                ? `http://localhost:5000/tipos-producto/${tipoEnEdicion.id}`
                : "http://localhost:5000/tipos-producto";

            const response = await fetch(url, {
                method: tipoEnEdicion ? "PUT" : "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Error al guardar tipo");
            }

            await cargarTipos();
            await invalidateAll();
            cancelarEdicionTipo();
        } catch (error) {
            errorTipo = error.message;
        } finally {
            isSubmittingTipo = false;
        }
    }

    function editarTipo(tipo) {
        tipoEnEdicion = tipo;
        formTipo = { nombre: tipo.nombre, descripcion: tipo.descripcion || "" };
        errorTipo = null;
    }

    function cancelarEdicionTipo() {
        tipoEnEdicion = null;
        formTipo = { nombre: "", descripcion: "" };
        errorTipo = null;
    }

    async function eliminarTipo(tipoId) {
        if (!confirm("¿Estás seguro de eliminar este tipo de producto?")) return;

        try {
            const response = await fetch(`http://localhost:5000/tipos-producto/${tipoId}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Error al eliminar tipo");
            }

            await cargarTipos();
            await invalidateAll();
        } catch (error) {
            alert(error.message);
        }
    }

    // Cargar tipos cuando se abre el modal
    $: if (showGestionarTiposDialog) {
        cargarTipos();
    }

    // Reset form when closing modal
    $: if (!showGestionarTiposDialog) {
        cancelarEdicionTipo();
    }

    // Configuración de ordenamiento
    let sortField = "nombre";
    let sortDirection = "asc";

    // Configuración de paginación
    let currentPage = 1;
    let itemsPerPage = 10;
    const itemsPerPageOptions = [5, 10, 20, 50];

    // Función de ordenamiento
    const sortProducts = (products, field, direction) => {
        return [...products].sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];

            if (
                field === "precio_bruto" ||
                field === "precio_neto" ||
                field === "unidades" ||
                field === "descuento"
            ) {
                aVal = Number(aVal) || 0;
                bVal = Number(bVal) || 0;
            } else if (typeof aVal === "string") {
                aVal = aVal.toLowerCase();
                bVal = (bVal || "").toLowerCase();
            }

            if (aVal < bVal) return direction === "asc" ? -1 : 1;
            if (aVal > bVal) return direction === "asc" ? 1 : -1;
            return 0;
        });
    };

    // Productos filtrados y ordenados
    $: productosFiltrados = (() => {
        let filtered = data?.productos
            ? data.productos.filter((producto) => {
                const coincideBusqueda =
                    !busqueda ||
                    producto.nombre
                        ?.toLowerCase()
                        .includes(busqueda.toLowerCase()) ||
                    producto.codigo
                        ?.toLowerCase()
                        .includes(busqueda.toLowerCase());

                const coincideTipo =
                    filtroTipo === "todos" ||
                    String(producto.tipo_producto_id) === String(filtroTipo);

                const coincideStock =
                    filtroStock === "todos" ||
                    (filtroStock === "disponible" &&
                        (producto.unidades || 0) > 0) ||
                    (filtroStock === "agotado" &&
                        (producto.unidades || 0) === 0) ||
                    (filtroStock === "bajo" &&
                        (producto.unidades || 0) > 0 &&
                        (producto.unidades || 0) < 10);

                return coincideBusqueda && coincideTipo && coincideStock;
            })
            : [];

        return sortProducts(filtered, sortField, sortDirection);
    })();

    // Paginación
    $: totalPages = Math.ceil(productosFiltrados.length / itemsPerPage);
    $: startIndex = (currentPage - 1) * itemsPerPage;
    $: endIndex = startIndex + itemsPerPage;
    $: productosPaginados = productosFiltrados.slice(startIndex, endIndex);

    // Ajustar página actual si es necesario
    $: if (currentPage > totalPages && totalPages > 0) {
        currentPage = totalPages;
    }

    // Estadísticas
    $: totalProductos = data?.productos?.length || 0;
    $: productosDisponibles =
        data?.productos?.filter((p) => (p.unidades || 0) > 0).length || 0;
    $: productosAgotados =
        data?.productos?.filter((p) => (p.unidades || 0) === 0).length || 0;

    const openFormDialog = (producto = null) => {
        productoAEditar = producto;
        showFormDialog = true;
    };

    const closeFormDialog = () => {
        showFormDialog = false;
        productoAEditar = null;
    };

    const cerrarModalEliminado = () => {
        mostrarModalEliminado = false;
    };

    const handleProductoGuardado = async () => {
        await invalidateAll();
    };

    const handleSort = (field) => {
        if (sortField === field) {
            sortDirection = sortDirection === "asc" ? "desc" : "asc";
        } else {
            sortField = field;
            sortDirection = "asc";
        }
        currentPage = 1;
    };

    const goToPage = (page) => {
        currentPage = Math.max(1, Math.min(page, totalPages));
    };

    const goToFirstPage = () => goToPage(1);
    const goToLastPage = () => goToPage(totalPages);
    const goToPreviousPage = () => goToPage(currentPage - 1);
    const goToNextPage = () => goToPage(currentPage + 1);

    const toggleSeleccionProducto = (productoId) => {
        if (productosSeleccionados.has(productoId)) {
            productosSeleccionados.delete(productoId);
        } else {
            productosSeleccionados.add(productoId);
        }
        productosSeleccionados = productosSeleccionados;
    };

    const eliminarProductosSeleccionados = async () => {
        if (productosSeleccionados.size === 0) {
            return;
        }

        mostrarConfirmarEliminacion = true;

        accionEliminarCallback = async () => {
            try {
                const cantidadAEliminar = productosSeleccionados.size;

                const promesasEliminacion = Array.from(productosSeleccionados).map(
                    (id) =>
                        fetch(`http://localhost:5000/eliminar_productos/${id}`, {
                            method: "DELETE",
                        }),
                );

                await Promise.all(promesasEliminacion);

                productosEliminadosCount = cantidadAEliminar;
                productosSeleccionados.clear();
                productosSeleccionados = productosSeleccionados;
                await invalidateAll();

                mostrarModalEliminado = true;
            } catch (error) {
                console.error("Error al eliminar productos:", error);
            }
        };
    };

    const seleccionarTodosEnPagina = () => {
        productosPaginados.forEach((producto) => {
            productosSeleccionados.add(producto.id);
        });
        productosSeleccionados = productosSeleccionados;
    };

    const deseleccionarTodos = () => {
        productosSeleccionados.clear();
        productosSeleccionados = productosSeleccionados;
    };

    const limpiarFiltros = () => {
        busqueda = "";
        filtroTipo = "todos";
        filtroStock = "todos";
        currentPage = 1;
    };

    const getStockStatus = (unidades) => {
        const stock = unidades || 0;
        if (stock === 0) return { label: "Agotado", color: "red", icon: "❌" };
        if (stock < 10)
            return { label: "Bajo stock", color: "orange", icon: "⚠️" };
        return { label: "Disponible", color: "green", icon: "✅" };
    };

    const cerrarConfirmarEliminacion = () => {
        mostrarConfirmarEliminacion = false;
        accionEliminarCallback = null;
    };

    const confirmarEliminacion = async () => {
        if (accionEliminarCallback) {
            await accionEliminarCallback();
            cerrarConfirmarEliminacion();
        }
    };

    $: pageRange = (() => {
        const range = [];
        const maxVisible = 5;
        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);

        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }

        for (let i = start; i <= end; i++) {
            range.push(i);
        }
        return range;
    })();
</script>

<svelte:head>
    <title>Productos - AEVE</title>
</svelte:head>

<!-- Header de la página -->
<div class="mb-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h1 class="text-2xl font-semibold text-white mb-1">Productos</h1>
            <p class="text-gray-400 text-sm">
                Gestiona tu inventario y catálogo de productos
            </p>
        </div>

        <!-- Estadísticas rápidas -->
        <div class="flex items-center gap-6">
            <div class="text-center">
                <div class="text-lg font-semibold text-white">
                    {totalProductos}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    Total
                </div>
            </div>
            <div class="text-center">
                <div class="text-lg font-semibold text-green-400">
                    {productosDisponibles}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    Disponibles
                </div>
            </div>
            <div class="text-center">
                <div class="text-lg font-semibold text-red-400">
                    {productosAgotados}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    Agotados
                </div>
            </div>
            <div class="text-center">
                <div class="text-lg font-semibold text-blue-400">
                    {productosSeleccionados.size}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    Seleccionados
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Error de conexión -->
{#if data?.error}
    <div
        class="bg-red-500/10 border border-red-500/20 text-red-300 p-6 rounded-xl mb-6"
    >
        <div class="flex items-start gap-4">
            <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                class="mt-0.5 flex-shrink-0"
            >
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
            <div>
                <div class="font-semibold mb-2">Error de conexión</div>
                <div class="text-sm opacity-90 mb-3">{data.error}</div>
                <div class="text-xs opacity-75">
                    Verifica que tu servidor backend esté corriendo en
                    http://localhost:5000
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Barra de búsqueda y filtros -->
<div
    class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6"
>
    <div class="flex flex-col lg:flex-row gap-4">
        <!-- Búsqueda -->
        <div class="flex-1">
            <div class="relative">
                <svg
                    class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>
                <input
                    type="text"
                    placeholder="Buscar productos por nombre o SKU..."
                    bind:value={busqueda}
                    class="w-full pl-10 pr-4 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                />
            </div>
        </div>

        <!-- Filtros y configuración de página -->
        <div class="flex gap-3 flex-wrap">
            <select
                bind:value={filtroTipo}
                class="px-3 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            >
                <option value="todos">Todas las categorías</option>
                {#each tiposProducto as tipo}
                    <option value={tipo.id}>{tipo.nombre}</option>
                {/each}
            </select>

            <select
                bind:value={filtroStock}
                class="px-3 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            >
                <option value="todos">Todo el stock</option>
                <option value="disponible">Disponible</option>
                <option value="bajo">Bajo stock</option>
                <option value="agotado">Agotado</option>
            </select>

            <!-- Selector de elementos por página -->
            <select
                bind:value={itemsPerPage}
                on:change={() => (currentPage = 1)}
                class="px-3 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            >
                {#each itemsPerPageOptions as option}
                    <option value={option}>{option} por página</option>
                {/each}
            </select>

            {#if busqueda || filtroTipo !== "todos" || filtroStock !== "todos"}
                <button
                    on:click={limpiarFiltros}
                    class="px-3 py-2.5 text-gray-400 hover:text-white transition-colors text-sm"
                >
                    Limpiar
                </button>
            {/if}
        </div>
    </div>
</div>

<!-- Barra de acciones -->
<div
    class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6"
>
    <div class="flex items-center justify-between gap-4">
        <!-- Selección masiva -->
        <div class="flex items-center gap-4">
            {#if productosPaginados.length > 0}
                <div class="flex items-center gap-3">
                    <button
                        on:click={seleccionarTodosEnPagina}
                        class="text-sm text-gray-400 hover:text-white transition-colors"
                    >
                        Seleccionar página
                    </button>
                    <span class="text-gray-500">•</span>
                    <button
                        on:click={deseleccionarTodos}
                        class="text-sm text-gray-400 hover:text-white transition-colors"
                    >
                        Deseleccionar
                    </button>
                </div>
            {/if}

            {#if productosSeleccionados.size > 0}
                <div
                    class="flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg"
                >
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span class="text-sm text-blue-300">
                        {productosSeleccionados.size} seleccionado{productosSeleccionados.size !==
                        1
                            ? "s"
                            : ""}
                    </span>
                </div>
            {/if}
        </div>

        <!-- Acciones -->
        <div class="flex items-center gap-3">
            <button
                on:click={eliminarProductosSeleccionados}
                disabled={productosSeleccionados.size === 0}
                class="flex items-center gap-2 px-4 py-2 bg-red-600/90 hover:bg-red-600 disabled:bg-red-600/30 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 disabled:opacity-50"
            >
                <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                >
                    <polyline points="3,6 5,6 21,6" />
                    <path
                        d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"
                    />
                    <line x1="10" y1="11" x2="10" y2="17" />
                    <line x1="14" y1="11" x2="14" y2="17" />
                </svg>
                Eliminar ({productosSeleccionados.size})
            </button>

            <button
                on:click={() => showGestionarTiposDialog = true}
                class="flex items-center gap-2 px-4 py-2 bg-purple-600/90 hover:bg-purple-600 text-white rounded-lg transition-all duration-200"
            >
                <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                >
                    <path d="M4 7h16M4 12h16M4 17h16"/>
                </svg>
                Gestionar Categorias
            </button>

            <button
                on:click={() => openFormDialog()}
                class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
            >
                <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                >
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Nuevo Producto
            </button>
        </div>
    </div>
</div>

<!-- Tabla de productos -->
<div
    class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl overflow-hidden"
>
    {#if !data?.productos}
        <div class="p-12 text-center">
            <div class="inline-flex items-center gap-3 text-gray-400">
                <div
                    class="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"
                ></div>
                Cargando productos...
            </div>
        </div>
    {:else if productosFiltrados.length === 0}
        <div class="p-12 text-center">
            <svg
                class="w-12 h-12 text-gray-500 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.5"
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
            </svg>
            <div class="text-gray-400 mb-2">
                {busqueda || filtroTipo !== "todos" || filtroStock !== "todos"
                    ? "No se encontraron productos"
                    : "No hay productos registrados"}
            </div>
            <div class="text-sm text-gray-500">
                {busqueda || filtroTipo !== "todos" || filtroStock !== "todos"
                    ? "Intenta ajustar los filtros de búsqueda"
                    : "Comienza agregando tu primer producto"}
            </div>
        </div>
    {:else}
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead>
                    <tr class="border-b border-[#1f1f1f]/50">
                        <th class="text-left p-4 w-12">
                            <input
                                type="checkbox"
                                checked={productosPaginados.length > 0 &&
                                    productosPaginados.every((p) =>
                                        productosSeleccionados.has(p.id),
                                    )}
                                on:change={(e) =>
                                    e.target.checked
                                        ? seleccionarTodosEnPagina()
                                        : deseleccionarTodos()}
                                class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                            />
                        </th>
                        <th class="text-left p-4">
                            <button
                                class="flex items-center gap-2 group hover:text-white transition-colors"
                                on:click={() => handleSort("nombre")}
                            >
                                <svg
                                    width="16"
                                    height="16"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="1.5"
                                    class="text-gray-400"
                                >
                                    <path
                                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                                    />
                                </svg>
                                <span
                                    class="text-xs font-medium text-gray-400 uppercase tracking-wide group-hover:text-white"
                                    >Producto</span
                                >
                                {#if sortField === "nombre"}
                                    <svg
                                        width="12"
                                        height="12"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        class="text-blue-400"
                                    >
                                        {#if sortDirection === "asc"}
                                            <path d="m7 14 5-5 5 5" />
                                        {:else}
                                            <path d="m17 10-5 5-5-5" />
                                        {/if}
                                    </svg>
                                {/if}
                            </button>
                        </th>
                        <th class="text-left p-4">
                            <button
                                class="flex items-center gap-2 group hover:text-white transition-colors"
                                on:click={() => handleSort("codigo_ska")}
                            >
                                <span
                                    class="text-xs font-medium text-gray-400 uppercase tracking-wide group-hover:text-white"
                                    >SKU</span
                                >
                                {#if sortField === "codigo_ska"}
                                    <svg
                                        width="12"
                                        height="12"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        class="text-blue-400"
                                    >
                                        {#if sortDirection === "asc"}
                                            <path d="m7 14 5-5 5 5" />
                                        {:else}
                                            <path d="m17 10-5 5-5-5" />
                                        {/if}
                                    </svg>
                                {/if}
                            </button>
                        </th>
                        <th class="text-left p-4">
                            <button
                                class="flex items-center gap-2 group hover:text-white transition-colors"
                                on:click={() => handleSort("unidades")}
                            >
                                <span
                                    class="text-xs font-medium text-gray-400 uppercase tracking-wide group-hover:text-white"
                                    >Stock</span
                                >
                                {#if sortField === "unidades"}
                                    <svg
                                        width="12"
                                        height="12"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        class="text-blue-400"
                                    >
                                        {#if sortDirection === "asc"}
                                            <path d="m7 14 5-5 5 5" />
                                        {:else}
                                            <path d="m17 10-5 5-5-5" />
                                        {/if}
                                    </svg>
                                {/if}
                            </button>
                        </th>
                        <th class="text-left p-4">
                            <span
                                class="text-xs font-medium text-gray-400 uppercase tracking-wide"
                                >Descripción</span
                            >
                        </th>
                        <th class="text-left p-4">
                            <span
                                class="text-xs font-medium text-gray-400 uppercase tracking-wide"
                                >Acciones</span
                            >
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {#each productosPaginados as producto (producto.id)}
                        {@const stockStatus = getStockStatus(producto.unidades)}
                        <tr
                            class="border-b border-[#1f1f1f]/30 hover:bg-[#1a1a1a]/50 transition-colors group"
                        >
                            <td class="p-4">
                                <input
                                    type="checkbox"
                                    checked={productosSeleccionados.has(
                                        producto.id,
                                    )}
                                    on:change={() =>
                                        toggleSeleccionProducto(producto.id)}
                                    class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                                />
                            </td>
                            <td class="p-4">
                                <div class="flex items-center gap-3">
                                    {#if producto.imagen_url}
                                        <img
                                            src="http://localhost:5000{producto.imagen_url}"
                                            alt={producto.nombre}
                                            class="w-10 h-10 rounded-lg object-cover border border-blue-500/30"
                                        />
                                    {:else}
                                        <div
                                            class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm"
                                        >
                                            {(producto.nombre || "P")
                                                .charAt(0)
                                                .toUpperCase()}
                                        </div>
                                    {/if}
                                    <div>
                                        <div class="font-medium text-white">
                                            {producto.nombre || "N/A"}
                                        </div>
                                        <div class="text-xs text-gray-400">
                                            {producto.tipo_producto || "Sin categoría"}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="p-4">
                                <span
                                    class="font-mono text-sm text-gray-300 bg-gray-800/50 px-2 py-1 rounded"
                                >
                                    {producto.codigo_ska || "N/A"}
                                </span>
                            </td>
                            <td class="p-4">
                                <div class="flex items-center gap-2">
                                    <span class="font-medium text-{stockStatus.color}-400"
                                        >{producto.unidades || 0}</span
                                    >
                                    <span class="text-xs text-gray-400"
                                        >uds</span
                                    >
                                </div>
                            </td>
                            <td class="p-4">
                                <span class="text-sm text-gray-300">
                                    {producto.descripcion ? (producto.descripcion.length > 50 ? producto.descripcion.substring(0, 50) + '...' : producto.descripcion) : 'Sin descripción'}
                                </span>
                            </td>
                            <td class="p-4">
                                <button
                                    on:click={() => openFormDialog(producto)}
                                    class="flex items-center gap-2 px-3 py-1.5 bg-amber-600/90 hover:bg-amber-600 text-white text-sm rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                                >
                                    <svg
                                        width="14"
                                        height="14"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="1.5"
                                    >
                                        <path
                                            d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"
                                        />
                                    </svg>
                                    Editar
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>

        <!-- Paginación -->
        {#if totalPages > 1}
            <div class="px-6 py-4 border-t border-[#1f1f1f]/50">
                <div class="flex items-center justify-between">
                    <!-- Información de página -->
                    <div class="text-sm text-gray-400">
                        Mostrando {startIndex + 1} - {Math.min(
                            endIndex,
                            productosFiltrados.length,
                        )} de {productosFiltrados.length} productos
                    </div>

                    <!-- Controles de paginación -->
                    <div class="flex items-center gap-2">
                        <!-- Botón Primera página -->
                        <button
                            on:click={goToFirstPage}
                            disabled={currentPage === 1}
                            class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Primera página"
                            aria-label="Ir a pagina anterior"
                        >
                            <svg
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <path d="m11 17-5-5 5-5" />
                                <path d="m18 17-5-5 5-5" />
                            </svg>
                        </button>

                        <!-- Botón Página anterior -->
                        <button
                            on:click={goToPreviousPage}
                            disabled={currentPage === 1}
                            class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Página anterior"
                            aria-label="Pagina anterior"
                        >
                            <svg
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <path d="m15 18-6-6 6-6" />
                            </svg>
                        </button>

                        <!-- Números de página -->
                        <div class="flex items-center gap-1">
                            {#each pageRange as page}
                                <button
                                    on:click={() => goToPage(page)}
                                    class="w-8 h-8 flex items-center justify-center text-sm rounded-lg transition-all duration-200 {page ===
                                    currentPage
                                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                                        : 'text-gray-400 hover:text-white hover:bg-[#1a1a1a]'}"
                                >
                                    {page}
                                </button>
                            {/each}
                        </div>

                        <!-- Botón Página siguiente -->
                        <button
                            on:click={goToNextPage}
                            disabled={currentPage === totalPages}
                            class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Página siguiente"
                            aria-label="Ir a pagina siguiente"
                        >
                            <svg
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <path d="m9 18 6-6-6-6" />
                            </svg>
                        </button>

                        <!-- Botón Última página -->
                        <button
                            on:click={goToLastPage}
                            disabled={currentPage === totalPages}
                            class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            title="Última página"
                            aria-label="Ir a última página"
                        >
                            <svg
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <path d="m13 17 5-5-5-5" />
                                <path d="m6 17 5-5-5-5" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    {/if}
</div>

<!-- Footer con información -->
{#if productosFiltrados.length > 0}
    <div class="mt-6 flex items-center justify-between text-sm text-gray-400">
        <div class="flex items-center gap-4">
            <span>
                {productosFiltrados.length} producto{productosFiltrados.length !==
                1
                    ? "s"
                    : ""}
                {busqueda || filtroTipo !== "todos" || filtroStock !== "todos"
                    ? "encontrado" +
                      (productosFiltrados.length !== 1 ? "s" : "")
                    : "total" + (productosFiltrados.length !== 1 ? "es" : "")}
            </span>
            {#if totalPages > 1}
                <span class="text-gray-500">•</span>
                <span>Página {currentPage} de {totalPages}</span>
            {/if}
        </div>
        <div class="flex items-center gap-4">
            {#if busqueda || filtroTipo !== "todos" || filtroStock !== "todos"}
                <button
                    on:click={limpiarFiltros}
                    class="text-blue-400 hover:text-blue-300 transition-colors"
                >
                    Limpiar filtros
                </button>
            {/if}
        </div>
    </div>
{/if}

<!-- Modales -->
<FormularioProducto
    open={showFormDialog}
    handleClose={closeFormDialog}
    producto={productoAEditar}
    onProductoGuardado={handleProductoGuardado}
/>
<ConfirmarEliminacion
        open={mostrarConfirmarEliminacion}
        handleClose={cerrarConfirmarEliminacion}
        onConfirm={confirmarEliminacion}
        cantidad={productosSeleccionados.size}
/>
<EliminadoExitosamente
    open={mostrarModalEliminado}
    handleClose={cerrarModalEliminado}
/>

<!-- Modal de Gestión de Tipos de Producto -->
{#if showGestionarTiposDialog}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
            class="fixed inset-0 bg-black/70 backdrop-blur-sm"
            on:click={() => showGestionarTiposDialog = false}
            role="button"
            tabindex="-1"
        ></div>

        <div class="relative w-full max-w-3xl max-h-[90vh] overflow-hidden z-10">
            <div class="relative bg-gradient-to-br from-[#0a0a0a] via-[#111111] to-[#0a0a0a] border border-[#1f1f1f]/50 rounded-2xl shadow-2xl">
                <!-- Header -->
                <div class="flex items-center justify-between p-6 border-b border-[#1f1f1f]/50">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                <path d="M4 7h16M4 12h16M4 17h16"/>
                            </svg>
                        </div>
                        <div>
                            <h2 class="text-2xl font-semibold text-white">Categoría de Producto</h2>
                            <p class="text-sm text-gray-400 mt-1">Gestiona las categorías de tus productos</p>
                        </div>
                    </div>
                    <button
                        on:click={() => showGestionarTiposDialog = false}
                        class="p-2 text-gray-400 hover:text-white hover:bg-[#1f1f1f]/50 rounded-lg transition-all duration-200"
                        type="button"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                <!-- Content -->
                <div class="p-6 max-h-[70vh] overflow-y-auto space-y-6">
                    <!-- Formulario -->
                    <div class="bg-[#151515]/60 border border-[#2a2a2a] rounded-xl p-6">
                        <h3 class="text-lg font-semibold text-white mb-4">
                            {tipoEnEdicion ? "Editar Tipo" : "Nuevo Tipo"}
                        </h3>

                        {#if errorTipo}
                            <div class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-sm">
                                {errorTipo}
                            </div>
                        {/if}

                        <form on:submit|preventDefault={guardarTipo} class="space-y-4">
                            <div>
                                <label for="tipo-nombre" class="block text-sm font-medium text-gray-300 mb-2">
                                    Nombre *
                                </label>
                                <input
                                    id="tipo-nombre"
                                    type="text"
                                    bind:value={formTipo.nombre}
                                    disabled={isSubmittingTipo}
                                    class="w-full px-4 py-2.5 bg-[#0a0a0a] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50"
                                    placeholder="Ej: Electrónico, Accesorio..."
                                    required
                                />
                            </div>

                            <div>
                                <label for="tipo-descripcion" class="block text-sm font-medium text-gray-300 mb-2">
                                    Descripción
                                </label>
                                <textarea
                                    id="tipo-descripcion"
                                    bind:value={formTipo.descripcion}
                                    disabled={isSubmittingTipo}
                                    class="w-full px-4 py-2.5 bg-[#0a0a0a] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50 resize-none"
                                    rows="3"
                                    placeholder="Descripción opcional del tipo de producto"
                                ></textarea>
                            </div>

                            <div class="flex gap-3">
                                <button
                                    type="submit"
                                    disabled={isSubmittingTipo}
                                    class="flex-1 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-lg transition-all disabled:cursor-not-allowed"
                                >
                                    {isSubmittingTipo ? "Guardando..." : (tipoEnEdicion ? "Actualizar" : "Crear")}
                                </button>
                                {#if tipoEnEdicion}
                                    <button
                                        type="button"
                                        on:click={cancelarEdicionTipo}
                                        disabled={isSubmittingTipo}
                                        class="px-4 py-2.5 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600/50 text-white rounded-lg transition-all disabled:cursor-not-allowed"
                                    >
                                        Cancelar
                                    </button>
                                {/if}
                            </div>
                        </form>
                    </div>

                    <!-- Lista de tipos -->
                    <div class="bg-[#151515]/60 border border-[#2a2a2a] rounded-xl overflow-hidden">
                        <div class="p-4 border-b border-[#2a2a2a]">
                            <h3 class="text-lg font-semibold text-white">Tipos Existentes</h3>
                        </div>

                        {#if loadingTipos}
                            <div class="p-8 text-center text-gray-400">
                                <div class="inline-flex items-center gap-3">
                                    <div class="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                                    Cargando...
                                </div>
                            </div>
                        {:else if tiposProducto.length === 0}
                            <div class="p-8 text-center text-gray-400">
                                No hay tipos de producto creados
                            </div>
                        {:else}
                            <div class="divide-y divide-[#2a2a2a]">
                                {#each tiposProducto as tipo (tipo.id)}
                                    <div class="p-4 hover:bg-[#1a1a1a]/50 transition-colors group">
                                        <div class="flex items-start justify-between gap-4">
                                            <div class="flex-1">
                                                <div class="font-medium text-white mb-1">{tipo.nombre}</div>
                                                {#if tipo.descripcion}
                                                    <div class="text-sm text-gray-400">{tipo.descripcion}</div>
                                                {/if}
                                            </div>
                                            <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                    on:click={() => editarTipo(tipo)}
                                                    class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-sm rounded-lg transition-all"
                                                >
                                                    Editar
                                                </button>
                                                <button
                                                    on:click={() => eliminarTipo(tipo.id)}
                                                    class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-all"
                                                >
                                                    Eliminar
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
