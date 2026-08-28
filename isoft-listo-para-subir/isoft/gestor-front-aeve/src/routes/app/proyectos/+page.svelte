<script lang="ts">
  import ProyectoModal from '$lib/components/proyectos/ProyectoModal.svelte';

  // ===== Tipos y estado =====
  type Proyecto = {
    id: string;
    nombre: string;
    clienteAsociado: string;
    fechaInicio: string;
    estado: 'Activo' | 'En Pausa' | 'Completado';
    descripcion?: string;
    presupuesto?: number;
  };

  let busqueda = '';
  let mensajeError: string | null = null;
  let proyectos: Proyecto[] = [];
  let filtroEstado = 'todos';

  // Estados para el modal
  let mostrarModal = false;
  let modalMode: 'new' | 'edit' | 'cotizar' = 'new';
  let proyectoSeleccionado: Proyecto | null = null;

  // Configuración de paginación
  let currentPage = 1;
  let itemsPerPage = 10;
  const itemsPerPageOptions = [5, 10, 20, 50];

  // ===== Lógica de selección =====
  let seleccionados = new Set<string>();

  function alternarUno(id: string) {
    seleccionados.has(id) ? seleccionados.delete(id) : seleccionados.add(id);
    seleccionados = new Set(seleccionados);
  }

  function eliminarSeleccionados() {
    if (!seleccionados.size) return;
    proyectos = proyectos.filter((p) => !seleccionados.has(p.id));
    seleccionados.clear();
    seleccionados = new Set();
  }

  const seleccionarTodosEnPagina = () => {
    proyectosPaginados.forEach((proyecto) => {
      seleccionados.add(proyecto.id);
    });
    seleccionados = seleccionados;
  };

  const deseleccionarTodos = () => {
    seleccionados.clear();
    seleccionados = seleccionados;
  };

  // ===== Lógica de búsqueda y filtros =====
  $: filtrados = proyectos.filter((p) => {
    const t = busqueda.toLowerCase();
    const coincideBusqueda = !t || p.nombre.toLowerCase().includes(t) || p.clienteAsociado.toLowerCase().includes(t);
    const coincideEstado = filtroEstado === 'todos' || p.estado === filtroEstado;
    return coincideBusqueda && coincideEstado;
  });

  // Paginación
  $: totalPages = Math.ceil(filtrados.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = startIndex + itemsPerPage;
  $: proyectosPaginados = filtrados.slice(startIndex, endIndex);

  // Ajustar página actual si es necesario
  $: if (currentPage > totalPages && totalPages > 0) {
    currentPage = totalPages;
  }

  const goToPage = (page: number) => {
    currentPage = Math.max(1, Math.min(page, totalPages));
  };

  const goToFirstPage = () => goToPage(1);
  const goToLastPage = () => goToPage(totalPages);
  const goToPreviousPage = () => goToPage(currentPage - 1);
  const goToNextPage = () => goToPage(currentPage + 1);

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

  const limpiarFiltros = () => {
    busqueda = '';
    filtroEstado = 'todos';
    currentPage = 1;
  };

  // Estadísticas
  $: totalProyectos = proyectos.length;
  $: proyectosActivos = proyectos.filter((p) => p.estado === 'Activo').length;
  $: proyectosCompletados = proyectos.filter((p) => p.estado === 'Completado').length;

  // ===== Lógica del Modal =====
  function abrirModal(mode: 'new' | 'edit' | 'cotizar', proyecto: Proyecto | null = null) {
    modalMode = mode;
    proyectoSeleccionado = proyecto;
    mostrarModal = true;
  }

  function cerrarModal() {
    mostrarModal = false;
    proyectoSeleccionado = null;
  }

  function guardarProyecto(event: CustomEvent<Proyecto>) {
    const proyecto = event.detail;

    if (modalMode === 'edit' && proyectoSeleccionado) {
      const index = proyectos.findIndex(p => p.id === proyectoSeleccionado!.id);
      if (index !== -1) {
        proyectos[index] = { ...proyecto };
        proyectos = [...proyectos];
      }
    } else if (modalMode === 'new') {
      proyectos = [...proyectos, { ...proyecto }];
    }
  }

  function generarCotizacion(event: CustomEvent<Proyecto>) {
    const proyecto = event.detail;
    alert(`Cotización generada para el proyecto "${proyecto.nombre}" por un presupuesto de $${proyecto.presupuesto?.toLocaleString('es-CL')}`);
  }

  const formatearPrecio = (precio: number | undefined) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(precio || 0);
  };
</script>

<svelte:head>
  <title>Proyectos - AEVE</title>
</svelte:head>

<!-- Header de la página -->
<div class="mb-8">
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-semibold text-white mb-1">Proyectos</h1>
      <p class="text-gray-400 text-sm">
        Gestiona tus proyectos y genera cotizaciones
      </p>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="flex items-center gap-6">
      <div class="text-center">
        <div class="text-lg font-semibold text-white">
          {totalProyectos}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Total
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-green-400">
          {proyectosActivos}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Activos
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-blue-400">
          {proyectosCompletados}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Completados
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-purple-400">
          {seleccionados.size}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Seleccionados
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Barra de búsqueda y filtros -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
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
          placeholder="Buscar proyectos por nombre o cliente..."
          bind:value={busqueda}
          class="w-full pl-10 pr-4 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
        />
      </div>
    </div>

    <!-- Filtros y configuración de página -->
    <div class="flex gap-3 flex-wrap">
      <select
        bind:value={filtroEstado}
        class="px-3 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
      >
        <option value="todos">Todos los estados</option>
        <option value="Activo">Activos</option>
        <option value="En Pausa">En Pausa</option>
        <option value="Completado">Completados</option>
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

      {#if busqueda || filtroEstado !== 'todos'}
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

{#if mensajeError}
  <div class="bg-red-500/10 border border-red-500/20 text-red-300 p-6 rounded-xl mb-6">
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
        <div class="font-semibold mb-2">Error</div>
        <div class="text-sm opacity-90">{mensajeError}</div>
      </div>
    </div>
  </div>
{/if}

<!-- Barra de acciones -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
  <div class="flex items-center justify-between gap-4">
    <!-- Selección masiva -->
    <div class="flex items-center gap-4">
      {#if proyectosPaginados.length > 0}
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

      {#if seleccionados.size > 0}
        <div class="flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
          <span class="text-sm text-blue-300">
            {seleccionados.size} seleccionado{seleccionados.size !== 1 ? 's' : ''}
          </span>
        </div>
      {/if}
    </div>

    <!-- Acciones -->
    <div class="flex items-center gap-3">
      <button
        on:click={eliminarSeleccionados}
        disabled={seleccionados.size === 0}
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
          <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" />
          <line x1="10" y1="11" x2="10" y2="17" />
          <line x1="14" y1="11" x2="14" y2="17" />
        </svg>
        Eliminar ({seleccionados.size})
      </button>

      <button
        on:click={() => abrirModal('new')}
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
        Nuevo Proyecto
      </button>
    </div>
  </div>
</div>

<!-- Tabla de proyectos -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl overflow-hidden">
  {#if proyectos.length === 0}
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
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <div class="text-gray-400 mb-2">No hay proyectos registrados</div>
      <div class="text-sm text-gray-500 mb-4">Comienza agregando tu primer proyecto</div>
      <button
        on:click={() => abrirModal('new')}
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Crear Proyecto
      </button>
    </div>
  {:else if filtrados.length === 0}
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
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <div class="text-gray-400 mb-2">No se encontraron proyectos</div>
      <div class="text-sm text-gray-500">Intenta ajustar los filtros de búsqueda</div>
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-[#1f1f1f]/50">
            <th class="text-left p-4 w-12">
              <input
                type="checkbox"
                checked={proyectosPaginados.length > 0 && proyectosPaginados.every((p) => seleccionados.has(p.id))}
                on:change={(e) => e.target.checked ? seleccionarTodosEnPagina() : deseleccionarTodos()}
                class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
              />
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Proyecto</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Cliente</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Estado</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Fecha Inicio</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Presupuesto</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Acciones</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {#each proyectosPaginados as p (p.id)}
            <tr class="border-b border-[#1f1f1f]/30 hover:bg-[#1a1a1a]/50 transition-colors group">
              <td class="p-4">
                <input
                  type="checkbox"
                  checked={seleccionados.has(p.id)}
                  on:change={() => alternarUno(p.id)}
                  class="w-4 h-4 text-blue-600 bg-transparent border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                />
              </td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
                    {(p.nombre || 'P').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div class="font-medium text-white">
                      {p.nombre || 'N/A'}
                    </div>
                    {#if p.descripcion}
                      <div class="text-xs text-gray-400 truncate max-w-xs">
                        {p.descripcion}
                      </div>
                    {/if}
                  </div>
                </div>
              </td>
              <td class="p-4">
                <span class="text-gray-300">{p.clienteAsociado || 'N/A'}</span>
              </td>
              <td class="p-4">
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {
                    p.estado === 'Activo' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                    p.estado === 'En Pausa' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                    'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  }"
                >
                  {p.estado}
                </span>
              </td>
              <td class="p-4">
                <span class="text-gray-300">{new Date(p.fechaInicio).toLocaleDateString('es-CL')}</span>
              </td>
              <td class="p-4">
                <span class="font-semibold text-white">{formatearPrecio(p.presupuesto)}</span>
              </td>
              <td class="p-4">
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    on:click={() => abrirModal('edit', p)}
                    class="flex items-center gap-1 px-3 py-1.5 bg-amber-600/90 hover:bg-amber-600 text-white text-sm rounded-lg transition-all duration-200"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                    </svg>
                    Editar
                  </button>
                  <button
                    on:click={() => abrirModal('cotizar', p)}
                    class="flex items-center gap-1 px-3 py-1.5 bg-green-600/90 hover:bg-green-600 text-white text-sm rounded-lg transition-all duration-200"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="2" y="6" width="20" height="12" rx="2" />
                      <path d="M12 12h.01M6 12h.01M18 12h.01" />
                    </svg>
                    Cotizar
                  </button>
                </div>
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
          <div class="text-sm text-gray-400">
            Mostrando {startIndex + 1} - {Math.min(endIndex, filtrados.length)} de {filtrados.length} proyectos
          </div>

          <div class="flex items-center gap-2">
            <button
              on:click={goToFirstPage}
              disabled={currentPage === 1}
              class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Primera página"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m11 17-5-5 5-5" />
                <path d="m18 17-5-5 5-5" />
              </svg>
            </button>

            <button
              on:click={goToPreviousPage}
              disabled={currentPage === 1}
              class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Página anterior"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6" />
              </svg>
            </button>

            <div class="flex items-center gap-1">
              {#each pageRange as page}
                <button
                  on:click={() => goToPage(page)}
                  class="w-8 h-8 flex items-center justify-center text-sm rounded-lg transition-all duration-200 {page === currentPage
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                    : 'text-gray-400 hover:text-white hover:bg-[#1a1a1a]'}"
                >
                  {page}
                </button>
              {/each}
            </div>

            <button
              on:click={goToNextPage}
              disabled={currentPage === totalPages}
              class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Página siguiente"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 18 6-6-6-6" />
              </svg>
            </button>

            <button
              on:click={goToLastPage}
              disabled={currentPage === totalPages}
              class="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Última página"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
{#if filtrados.length > 0}
  <div class="mt-6 flex items-center justify-between text-sm text-gray-400">
    <div class="flex items-center gap-4">
      <span>
        {filtrados.length} proyecto{filtrados.length !== 1 ? 's' : ''}
        {busqueda || filtroEstado !== 'todos' ? 'encontrado' + (filtrados.length !== 1 ? 's' : '') : 'total' + (filtrados.length !== 1 ? 'es' : '')}
      </span>
      {#if totalPages > 1}
        <span class="text-gray-500">•</span>
        <span>Página {currentPage} de {totalPages}</span>
      {/if}
    </div>
    <div class="flex items-center gap-4">
      {#if busqueda || filtroEstado !== 'todos'}
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

<!-- Modal para crear/editar/cotizar proyecto -->
<ProyectoModal
  visible={mostrarModal}
  mode={modalMode}
  proyecto={proyectoSeleccionado}
  on:close={cerrarModal}
  on:save={guardarProyecto}
  on:cotizar={generarCotizacion}
/>