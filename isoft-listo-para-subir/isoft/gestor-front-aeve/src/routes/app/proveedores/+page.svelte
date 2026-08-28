<script>
    import FormularioProveedor from "$lib/components/proveedores/FormularioProveedor.svelte";
    import ConfirmDialog from "$lib/components/proveedores/ConfirmarElimacion.svelte";
    import SuccessModal from "$lib/components/proveedores/ElimanacionExitosaProveedor.svelte";
    import { enhance } from "$app/forms";
    import { invalidateAll } from "$app/navigation";
    import { page } from "$app/stores";

    export let data;
    export let form;

    // Estado del formulario
    let showDialog = false;
    let showConfirmDialog = false;
    let showSuccessModal = false;
    let modoFormulario = "agregar";
    let proveedorSeleccionado = null;

    // Estado de selección
    let proveedoresSeleccionados = [];
    let seleccionarTodos = false;
    let eliminandoProveedores = false;

    // Estado de búsqueda y filtros
    let busqueda = "";
    let paginaActual = 1;
    let itemsPorPagina = 10;
    let campoOrdenamiento = "name";
    let direccionOrdenamiento = "asc";

    const opcionesPaginacion = [5, 10, 20, 30];

    // Computados reactivos
    $: proveedores = data.proveedores || [];

    $: proveedoresFiltrados = proveedores.filter(p =>
        p.nombre?.toLowerCase().includes(busqueda.toLowerCase()) ||
        p.rut?.toLowerCase().includes(busqueda.toLowerCase()) ||
        p.email?.toLowerCase().includes(busqueda.toLowerCase())
    );

    $: proveedoresOrdenados = [...proveedoresFiltrados].sort((a, b) => {
        const valorA = (a[campoOrdenamiento] || "").toString().toLowerCase();
        const valorB = (b[campoOrdenamiento] || "").toString().toLowerCase();
        return direccionOrdenamiento === "asc"
            ? valorA.localeCompare(valorB)
            : valorB.localeCompare(valorA);
    });

    $: totalPaginas = Math.ceil(proveedoresOrdenados.length / itemsPorPagina);
    $: inicioIndice = (paginaActual - 1) * itemsPorPagina;
    $: finIndice = Math.min(inicioIndice + itemsPorPagina, proveedoresOrdenados.length);
    $: proveedoresPaginados = proveedoresOrdenados.slice(inicioIndice, finIndice);

    // Resetear página al buscar
    $: if (busqueda) paginaActual = 1;

    // Manejo de mensajes
    $: if (form?.success) {
        setTimeout(() => {
            showSuccessModal = true;
        }, 100);
        proveedoresSeleccionados = [];
        seleccionarTodos = false;
    }

    $: if (form?.error) {
        setTimeout(() => {
            let mensaje = form.error;
            if (form.details && Array.isArray(form.details)) {
                mensaje += "\n\nDetalles:\n" + form.details.join("\n");
            }
            alert(mensaje);
        }, 100);
    }

    // Funciones de diálogo
    const openDialogAgregar = () => {
        modoFormulario = "agregar";
        proveedorSeleccionado = null;
        showDialog = true;
    };

    const openDialogEditar = (proveedor) => {
        modoFormulario = "editar";
        proveedorSeleccionado = proveedor;
        showDialog = true;
    };

    const closeDialog = () => {
        showDialog = false;
        proveedorSeleccionado = null;
    };

    // Funciones de selección
    const getProveedorId = (p) => p.id || p.rut || p.name;

    const toggleSeleccionProveedor = (proveedorId) => {
        if (proveedoresSeleccionados.includes(proveedorId)) {
            proveedoresSeleccionados = proveedoresSeleccionados.filter(id => id !== proveedorId);
        } else {
            proveedoresSeleccionados = [...proveedoresSeleccionados, proveedorId];
        }
        // El estado de seleccionarTodos se actualiza automáticamente por el bloque reactivo
    };

    const toggleSeleccionarTodos = () => {
        const ids = proveedoresPaginados.map(getProveedorId);
        if (seleccionarTodos) {
            // Si ya están seleccionados todos, deseleccionar
            proveedoresSeleccionados = proveedoresSeleccionados.filter(id => !ids.includes(id));
            seleccionarTodos = false;
        } else {
            // Seleccionar todos los de la página actual
            proveedoresSeleccionados = [...new Set([...proveedoresSeleccionados, ...ids])];
            seleccionarTodos = true;
        }
    };

    // Actualizar el estado de "seleccionar todos" cuando cambia la selección individual
    $: {
        if (proveedoresPaginados.length > 0) {
            const ids = proveedoresPaginados.map(getProveedorId);
            seleccionarTodos = ids.every(id => proveedoresSeleccionados.includes(id));
        } else {
            seleccionarTodos = false;
        }
    }

    // Funciones de ordenamiento
    const ordenarPor = (campo) => {
        if (campoOrdenamiento === campo) {
            direccionOrdenamiento = direccionOrdenamiento === "asc" ? "desc" : "asc";
        } else {
            campoOrdenamiento = campo;
            direccionOrdenamiento = "asc";
        }
        paginaActual = 1;
    };

    // Funciones de paginación
    const cambiarPagina = (nuevaPagina) => {
        if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
            paginaActual = nuevaPagina;
        }
    };

    const cambiarItemsPorPagina = (nuevoTamaño) => {
        itemsPorPagina = parseInt(nuevoTamaño);
        paginaActual = 1;
        seleccionarTodos = false;
    };

    const irPrimeraPagina = () => cambiarPagina(1);
    const irUltimaPagina = () => cambiarPagina(totalPaginas);

    const getPaginasVisibles = () => {
        const rango = 2;
        let inicio = Math.max(1, paginaActual - rango);
        let fin = Math.min(totalPaginas, paginaActual + rango);

        if (fin - inicio < 4) {
            if (inicio === 1) {
                fin = Math.min(totalPaginas, inicio + 4);
            } else if (fin === totalPaginas) {
                inicio = Math.max(1, fin - 4);
            }
        }

        return Array.from({ length: fin - inicio + 1 }, (_, i) => inicio + i);
    };

    // Funciones de eliminación
    const eliminarSeleccionados = () => {
        if (proveedoresSeleccionados.length === 0) {
            alert("No hay proveedores seleccionados para eliminar.");
            return;
        }

        showConfirmDialog = true;
    };

    const confirmarEliminacion = async () => {
        const form = document.getElementById("form-eliminar");
        if (form) {
            form.requestSubmit();
        }
    };

    const onProveedorGuardado = async () => {
        await invalidateAll();
        closeDialog();
    };

    // Definición de columnas para evitar repetición
    const columnas = [
        { campo: 'nombre', label: 'Nombre', icon: true },
        { campo: 'rut', label: 'RUT' },
        { campo: 'direccion', label: 'Dirección' },
        { campo: 'email', label: 'Email' },
        { campo: 'telefono', label: 'Teléfono' }
    ];
</script>

<svelte:head>
    <title>Proveedores - AEVE</title>
</svelte:head>

<!-- Header de la página -->
<div class="mb-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h1 class="text-3xl font-bold text-white mb-2">Proveedores</h1>
            <p class="text-gray-400">Gestiona tus proveedores y contactos comerciales</p>
        </div>

        <!-- Estadísticas rápidas -->
        <div class="flex items-center gap-6">
            <div class="text-center">
                <div class="text-2xl font-bold text-white">{proveedores.length}</div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">Total</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-400">{proveedoresSeleccionados.length}</div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">Seleccionados</div>
            </div>
        </div>
    </div>
</div>

<!-- Barra de acciones -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
    <div class="flex items-center justify-between gap-4">
        <!-- Búsqueda -->
        <div class="flex-1 max-w-md">
            <div class="relative">
                <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input
                        type="text"
                        placeholder="Buscar proveedores..."
                        bind:value={busqueda}
                        class="w-full pl-10 pr-4 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                />
            </div>
        </div>

        <!-- Acciones -->
        <div class="flex items-center gap-3">
            {#if proveedoresSeleccionados.length > 0}
                <div class="flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span class="text-sm text-blue-300">
                        {proveedoresSeleccionados.length} seleccionado{proveedoresSeleccionados.length !== 1 ? "s" : ""}
                    </span>
                </div>
            {/if}

            <!-- Selector de elementos por página -->
            <div class="flex items-center gap-2">
                <label for="items-per-page" class="text-sm text-gray-400">Mostrar:</label>
                <select
                        id="items-per-page"
                        bind:value={itemsPorPagina}
                        on:change={() => cambiarItemsPorPagina(itemsPorPagina)}
                        class="bg-[#151515]/60 border border-[#2a2a2a] rounded-lg px-8 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 cursor-pointer"
                >
                    {#each opcionesPaginacion as opcion}
                        <option value={opcion}>{opcion}</option>
                    {/each}
                </select>
                <span class="text-sm text-gray-400">por página</span>
            </div>

            <!-- Formulario oculto para eliminación -->
            <form
                    id="form-eliminar"
                    method="POST"
                    action="?/eliminar"
                    use:enhance={() => {
                    eliminandoProveedores = true;
                    return async ({ update }) => {
                        eliminandoProveedores = false;
                        await update();
                    };
                }}
                    style="display: none;"
            >
                <input type="hidden" name="ids" value={JSON.stringify(proveedoresSeleccionados)}/>
            </form>

            <button
                    on:click={eliminarSeleccionados}
                    disabled={proveedoresSeleccionados.length === 0 || eliminandoProveedores}
                    class="flex items-center gap-2 px-4 py-2 bg-red-600/90 hover:bg-red-600 disabled:bg-red-600/30 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 disabled:opacity-50"
            >
                {#if eliminandoProveedores}
                    <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {:else}
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <polyline points="3,6 5,6 21,6"/>
                        <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"/>
                        <line x1="10" y1="11" x2="10" y2="17"/>
                        <line x1="14" y1="11" x2="14" y2="17"/>
                    </svg>
                {/if}
                Eliminar
            </button>

            <button
                    on:click={openDialogAgregar}
                    class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
            >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Nuevo Proveedor
            </button>
        </div>
    </div>
</div>

<!-- Componente del formulario -->
<FormularioProveedor
        open={showDialog}
        handleClose={closeDialog}
        proveedor={proveedorSeleccionado}
        modo={modoFormulario}
        {onProveedorGuardado}
/>

<!-- Modal de confirmación de eliminación -->
<ConfirmDialog
        open={showConfirmDialog}
        handleClose={() => showConfirmDialog = false}
        onConfirm={confirmarEliminacion}
        cantidad={proveedoresSeleccionados.length}
/>

<!-- Modal de éxito -->
<SuccessModal
        open={showSuccessModal}
        handleClose={() => showSuccessModal = false}
/>

<!-- Mensajes de estado -->
{#if $page.status >= 400}
    <div class="bg-red-500/10 border border-red-500/20 text-red-300 p-4 rounded-xl mb-6 flex items-center gap-3">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        <div>
            <div class="font-medium">Error al cargar datos</div>
            <div class="text-sm opacity-90">Hubo un problema al cargar los proveedores</div>
        </div>
    </div>
{/if}

<!-- Tabla de proveedores -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl overflow-hidden">
    {#if proveedoresOrdenados.length === 0}
        <div class="p-12 text-center">
            <svg class="w-12 h-12 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <div class="text-gray-400 mb-2">
                {busqueda ? "No se encontraron proveedores" : "No hay proveedores registrados"}
            </div>
            <div class="text-sm text-gray-500">
                {busqueda ? "Intenta con otros términos de búsqueda" : "Comienza agregando tu primer proveedor"}
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
                                checked={seleccionarTodos}
                                on:click={toggleSeleccionarTodos}
                                class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                        />
                    </th>
                    {#each columnas as columna}
                        <th class="text-left p-4">
                            <button
                                    on:click={() => ordenarPor(columna.campo)}
                                    class="flex items-center gap-2 hover:text-white transition-colors group"
                            >
                                {#if columna.icon}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-gray-400">
                                        <path d="M3 21h18"/>
                                        <path d="M5 21V7l8-4v18"/>
                                        <path d="M19 21V11l-6-4"/>
                                    </svg>
                                {/if}
                                <span class="text-xs font-medium text-gray-400 uppercase tracking-wide group-hover:text-white">
                                        {columna.label}
                                    </span>
                                {#if campoOrdenamiento === columna.campo}
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                         class="text-blue-400 transition-transform duration-200 {direccionOrdenamiento === 'desc' ? 'rotate-180' : ''}">
                                        <polyline points="18,15 12,9 6,15"></polyline>
                                    </svg>
                                {/if}
                            </button>
                        </th>
                    {/each}
                    <th class="text-left p-4">
                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Acciones</span>
                    </th>
                </tr>
                </thead>
                <tbody>
                {#each proveedoresPaginados as proveedor, index}
                    <tr class="border-b border-[#1f1f1f]/30 hover:bg-[#1a1a1a]/50 transition-colors group">
                        <td class="p-4">
                            <input
                                    type="checkbox"
                                    checked={proveedoresSeleccionados.includes(getProveedorId(proveedor))}
                                    on:change={() => toggleSeleccionProveedor(getProveedorId(proveedor))}
                                    class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                            />
                        </td>
                        <td class="p-4">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
                                    {proveedor.nombre?.charAt(0).toUpperCase() || "?"}
                                </div>
                                <div>
                                    <div class="font-medium text-white">{proveedor.nombre}</div>
                                    <div class="text-xs text-gray-400">Proveedor #{inicioIndice + index + 1}</div>
                                </div>
                            </div>
                        </td>
                        <td class="p-4"><span class="font-mono text-sm text-gray-300">{proveedor.rut || 'N/A'}</span></td>
                        <td class="p-4"><span class="text-sm text-gray-300">{proveedor.direccion || 'N/A'}</span></td>
                        <td class="p-4">
                            {#if proveedor.email}
                                <a href="mailto:{proveedor.email}" class="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                                    {proveedor.email}
                                </a>
                            {:else}
                                <span class="text-sm text-gray-500">N/A</span>
                            {/if}
                        </td>
                        <td class="p-4">
                            {#if proveedor.telefono}
                                <a href="tel:{proveedor.telefono}" class="text-sm text-gray-300 hover:text-white transition-colors">
                                    {proveedor.telefono}
                                </a>
                            {:else}
                                <span class="text-sm text-gray-500">N/A</span>
                            {/if}
                        </td>
                        <td class="p-4">
                            <button
                                    on:click={() => openDialogEditar(proveedor)}
                                    class="flex items-center gap-2 px-3 py-1.5 bg-amber-600/90 hover:bg-amber-600 text-white text-sm rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                            >
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
                                </svg>
                                Editar
                            </button>
                        </td>
                    </tr>
                {/each}
                </tbody>
            </table>
        </div>

        <!-- Paginación mejorada -->
        {#if totalPaginas > 1}
            <div class="px-6 py-4 border-t border-[#1f1f1f]/50">
                <div class="flex items-center justify-between">
                    <!-- Información de la paginación -->
                    <div class="flex items-center gap-4">
                        <div class="text-sm text-gray-400">
                            Mostrando <span class="text-white font-medium">{inicioIndice + 1}</span> a
                            <span class="text-white font-medium">{finIndice}</span> de
                            <span class="text-white font-medium">{proveedoresOrdenados.length}</span> resultados
                        </div>
                    </div>

                    <!-- Controles de paginación -->
                    <div class="flex items-center gap-1">
                        <!-- Botón primera página -->
                        <button
                                on:click={irPrimeraPagina}
                                disabled={paginaActual === 1}
                                class="flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-white hover:bg-[#1a1a1a] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                title="Primera página"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="11,17 6,12 11,7"></polyline>
                                <polyline points="18,17 13,12 18,7"></polyline>
                            </svg>
                        </button>

                        <!-- Botón página anterior -->
                        <button
                                on:click={() => cambiarPagina(paginaActual - 1)}
                                disabled={paginaActual === 1}
                                class="flex items-center gap-1 px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-gray-300 hover:text-white hover:bg-[#1a1a1a] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <polyline points="15,18 9,12 15,6"></polyline>
                            </svg>
                            <span class="text-sm">Anterior</span>
                        </button>

                        <!-- Números de página -->
                        <div class="flex items-center gap-1">
                            {#if totalPaginas <= 7}
                                {#each Array.from({ length: totalPaginas }, (_, i) => i + 1) as pagina}
                                    <button
                                            on:click={() => cambiarPagina(pagina)}
                                            class="w-10 h-10 flex items-center justify-center rounded-lg text-sm font-medium transition-all
                                        {pagina === paginaActual
                                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                                            : 'bg-[#151515]/60 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1a1a1a]'}"
                                    >
                                        {pagina}
                                    </button>
                                {/each}
                            {:else}
                                {#each getPaginasVisibles() as pagina}
                                    <button
                                            on:click={() => cambiarPagina(pagina)}
                                            class="w-10 h-10 flex items-center justify-center rounded-lg text-sm font-medium transition-all
                                        {pagina === paginaActual
                                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                                            : 'bg-[#151515]/60 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1a1a1a]'}"
                                    >
                                        {pagina}
                                    </button>
                                {/each}

                                {#if getPaginasVisibles()[getPaginasVisibles().length - 1] < totalPaginas - 1}
                                    <span class="px-4 text-gray-500">...</span>
                                    <button
                                            on:click={() => cambiarPagina(totalPaginas)}
                                            class="w-10 h-10 flex items-center justify-center rounded-lg text-sm font-medium bg-[#151515]/60 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1a1a1a] transition-all"
                                    >
                                        {totalPaginas}
                                    </button>
                                {/if}
                            {/if}
                        </div>

                        <!-- Botón página siguiente -->
                        <button
                                on:click={() => cambiarPagina(paginaActual + 1)}
                                disabled={paginaActual === totalPaginas}
                                class="flex items-center gap-1 px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-gray-300 hover:text-white hover:bg-[#1a1a1a] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <span class="text-sm">Siguiente</span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <polyline points="9,18 15,12 9,6"></polyline>
                            </svg>
                        </button>

                        <!-- Botón última página -->
                        <button
                                on:click={irUltimaPagina}
                                disabled={paginaActual === totalPaginas}
                                class="flex items-center justify-center w-8 h-8 rounded-lg text-gray-400 hover:text-white hover:bg-[#1a1a1a] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                title="Última página"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="13,17 18,12 13,7"></polyline>
                                <polyline points="6,17 11,12 6,7"></polyline>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    {/if}
</div>

<!-- Footer con información -->
{#if proveedoresOrdenados.length > 0}
    <div class="mt-6 flex items-center justify-between text-sm text-gray-400">
        <div class="flex items-center gap-4">
            <span>
                Total: <span class="text-white font-medium">{proveedoresOrdenados.length}</span> de
                <span class="text-white font-medium">{proveedores.length}</span> proveedores
            </span>
            {#if busqueda}
                <span class="text-blue-400">• Filtrado por: "{busqueda}"</span>
            {/if}
            {#if campoOrdenamiento}
                <span class="text-orange-400">
                    • Ordenado por: {campoOrdenamiento} ({direccionOrdenamiento === "asc" ? "Ascendente" : "Descendente"})
                </span>
            {/if}
        </div>
        <div class="flex items-center gap-4">
            {#if busqueda}
                <button
                        on:click={() => busqueda = ""}
                        class="text-blue-400 hover:text-blue-300 transition-colors"
                >
                    Limpiar filtros
                </button>
            {/if}
            {#if totalPaginas > 1}
                <span class="text-gray-500">Página {paginaActual} de {totalPaginas}</span>
            {/if}
        </div>
    </div>
{/if}

<style>
    .rotate-180 {
        transform: rotate(180deg);
    }
</style>