<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import Cliente from '$lib/components/cliente/Cliente.svelte';

  export let data: any;
  export let form: any;

  let { clientes = [], count = 0, error = null } = data;
  $: ({ clientes, count, error } = data);

  let isModalOpen = false;
  let modalMode = 'crear';
  let selectedCliente: any = null;
  let selectedIds: Set<any> = new Set();
  let searchQuery = '';
  let filterTipo = '';
  let loading = false;
  let showDeleteConfirm = false;

  // Manejar exito del formulario
  async function handleClienteSuccess(event: CustomEvent) {
    await invalidateAll();
  }

  function openCreateModal() {
    modalMode = 'crear';
    selectedCliente = null;
    isModalOpen = true;
  }

  function openEditModal(cliente: any) {
    modalMode = 'actualizar';
    selectedCliente = cliente;
    isModalOpen = true;
  }

  function toggleSelection(id: any) {
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    selectedIds = selectedIds;
  }

  function toggleSelectAll() {
    if (selectedIds.size === clientes.length) {
      selectedIds.clear();
    } else {
      selectedIds = new Set(clientes.map((c: any) => c.id));
    }
    selectedIds = selectedIds;
  }

  async function handleDelete() {
    if (selectedIds.size === 0) return;
    showDeleteConfirm = true;
  }

  async function confirmDelete() {
    loading = true;
    const formData = new FormData();
    formData.append('ids', JSON.stringify([...selectedIds]));

    try {
      const response = await fetch('?/eliminar', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        selectedIds.clear();
        selectedIds = selectedIds;
        await invalidateAll();
      }
    } catch (err) {
      console.error('Error al eliminar:', err);
    } finally {
      loading = false;
      showDeleteConfirm = false;
    }
  }

  function handleSearch() {
    const url = new URL(window.location.href);
    if (searchQuery) url.searchParams.set('q', searchQuery);
    else url.searchParams.delete('q');
    if (filterTipo) url.searchParams.set('tipo', filterTipo);
    else url.searchParams.delete('tipo');
    url.searchParams.set('offset', '0');
    window.location.href = url.toString();
  }

  function clearFilters() {
    searchQuery = '';
    filterTipo = '';
    window.location.href = window.location.pathname;
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget && !loading) {
      showDeleteConfirm = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && !loading) {
      showDeleteConfirm = false;
    }
  }
</script>

<svelte:head>
  <title>Clientes - ERP AEVE</title>
</svelte:head>

<!-- Header de la página -->
<div class="mb-8">
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-semibold text-white mb-1">Clientes</h1>
      <p class="text-gray-400 text-sm">
        Gestiona tu cartera de clientes
      </p>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="flex items-center gap-6">
      <div class="text-center">
        <div class="text-lg font-semibold text-white">
          {count}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Total
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-green-400">
          {clientes.filter((c: any) => c.tipo_cliente_id === 2).length}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Empresas
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-emerald-400">
          {clientes.filter((c: any) => c.tipo_cliente_id === 1).length}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Personas
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg font-semibold text-blue-400">
          {selectedIds.size}
        </div>
        <div class="text-xs text-gray-400 uppercase tracking-wide">
          Seleccionados
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Alertas -->
{#if form?.error}
  <div class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
    <div class="flex items-start gap-4">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mt-0.5 flex-shrink-0 text-red-300">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p class="text-sm font-medium text-red-300">{form.error}</p>
    </div>
  </div>
{/if}

{#if form?.success}
  <div class="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
    <div class="flex items-start gap-4">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mt-0.5 flex-shrink-0 text-green-300">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <p class="text-sm font-medium text-green-300">{form.message}</p>
    </div>
  </div>
{/if}

{#if error}
  <div class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
    <div class="flex items-start gap-4">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mt-0.5 flex-shrink-0 text-red-300">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p class="text-sm font-medium text-red-300">{error}</p>
    </div>
  </div>
{/if}

<!-- Barra de búsqueda y filtros -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
  <div class="flex flex-col lg:flex-row gap-4">
    <!-- Búsqueda -->
    <div class="flex-1">
      <div class="relative">
        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Buscar clientes por nombre, correo o teléfono..."
          bind:value={searchQuery}
          on:keydown={(e) => e.key === 'Enter' && handleSearch()}
          class="w-full pl-10 pr-4 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all"
        />
      </div>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 flex-wrap">
      <select
        bind:value={filterTipo}
        on:change={handleSearch}
        class="px-3 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all"
      >
        <option value="">Todos los tipos</option>
        <option value="2">Empresa</option>
        <option value="1">Persona</option>
      </select>

      {#if searchQuery || filterTipo}
        <button
          on:click={clearFilters}
          class="px-3 py-2.5 text-gray-400 hover:text-white transition-colors text-sm"
        >
          Limpiar
        </button>
      {/if}
    </div>
  </div>
</div>

<!-- Barra de acciones -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
  <div class="flex items-center justify-between gap-4">
    <!-- Información de selección -->
    <div class="flex items-center gap-4">
      {#if selectedIds.size > 0}
        <div class="flex items-center gap-2 px-3 py-2 bg-green-500/10 border border-green-500/20 rounded-lg">
          <div class="w-2 h-2 bg-green-400 rounded-full"></div>
          <span class="text-sm text-green-300">
            {selectedIds.size} seleccionado{selectedIds.size !== 1 ? 's' : ''}
          </span>
        </div>
      {/if}
    </div>

    <!-- Acciones -->
    <div class="flex items-center gap-3">
      <button
        on:click={handleDelete}
        disabled={selectedIds.size === 0}
        class="flex items-center gap-2 px-4 py-2 bg-red-600/90 hover:bg-red-600 disabled:bg-red-600/30 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 disabled:opacity-50"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <polyline points="3,6 5,6 21,6" />
          <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" />
          <line x1="10" y1="11" x2="10" y2="17" />
          <line x1="14" y1="11" x2="14" y2="17" />
        </svg>
        Eliminar ({selectedIds.size})
      </button>

      <button
        on:click={openCreateModal}
        class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white rounded-lg transition-all duration-200 shadow-lg shadow-green-500/25"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Nuevo Cliente
      </button>
    </div>
  </div>
</div>

<!-- Tabla de clientes -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl overflow-hidden">
  {#if clientes.length === 0}
    <div class="p-12 text-center">
      <svg class="w-12 h-12 text-gray-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <div class="text-gray-400 mb-2">
        {searchQuery || filterTipo ? 'No se encontraron clientes' : 'No hay clientes registrados'}
      </div>
      <div class="text-sm text-gray-500">
        {searchQuery || filterTipo ? 'Intenta ajustar los filtros de búsqueda' : 'Comienza agregando tu primer cliente'}
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
                checked={selectedIds.size === clientes.length && clientes.length > 0}
                on:change={toggleSelectAll}
                class="w-4 h-4 text-green-600 bg-transparent border-gray-600 rounded focus:ring-green-500 focus:ring-2"
              />
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Cliente</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">RUT</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Tipo</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Email</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Direccion</span>
            </th>
            <th class="text-left p-4">
              <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Acciones</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {#each clientes as cliente (cliente.id)}
            {@const esEmpresa = cliente.tipo_cliente_id === 2}
            {@const tipoNombre = cliente.tipo_cliente_id === 2 ? 'Empresa' : cliente.tipo_cliente_id === 1 ? 'Persona' : 'Sin tipo'}
            <tr class="border-b border-[#1f1f1f]/30 hover:bg-[#1a1a1a]/50 transition-colors group">
              <td class="p-4">
                <input
                  type="checkbox"
                  checked={selectedIds.has(cliente.id)}
                  on:change={() => toggleSelection(cliente.id)}
                  class="w-4 h-4 text-green-600 bg-transparent border-gray-600 rounded focus:ring-green-500 focus:ring-2"
                />
              </td>
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
                    {(cliente.nombre || 'C').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div class="font-medium text-white">{cliente.nombre || 'N/A'}</div>
                    <div class="text-xs text-gray-400">
                      {#if esEmpresa}
                        {cliente.razon_social || ''}
                      {:else}
                        {cliente.apellidos || ''}
                      {/if}
                    </div>
                  </div>
                </div>
              </td>
              <td class="p-4">
                <span class="font-mono text-sm text-gray-300 bg-gray-800/50 px-2 py-1 rounded">
                  {cliente.rut || 'N/A'}
                </span>
              </td>
              <td class="p-4">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                  {esEmpresa ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                   cliente.tipo_cliente_id === 1 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                   'bg-gray-500/20 text-gray-300 border border-gray-500/30'}">
                  {tipoNombre}
                </span>
              </td>
              <td class="p-4">
                <span class="text-gray-300">{cliente.email || '-'}</span>
              </td>
              <td class="p-4">
                <span class="text-gray-300">{cliente.direccion || '-'}</span>
              </td>
              <td class="p-4">
                <button
                  on:click={() => openEditModal(cliente)}
                  class="flex items-center gap-2 px-3 py-1.5 bg-amber-600/90 hover:bg-amber-600 text-white text-sm rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                  </svg>
                  Editar
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- Modal de confirmación de eliminación -->
{#if showDeleteConfirm}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div class="bg-[#151515] border border-[#2a2a2a] rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 transform animate-scale"
         on:click|stopPropagation>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-red-400">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">Confirmar eliminación</h3>
        </div>
        <button
          on:click={() => showDeleteConfirm = false}
          disabled={loading}
          class="text-gray-400 hover:text-white transition-colors disabled:opacity-50"
          type="button"
          aria-label="Cerrar modal"
        >
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Mensaje -->
      <p class="text-gray-400 mb-6">
        {#if selectedIds.size > 1}
          Estás a punto de eliminar {selectedIds.size} clientes. Esta acción no se puede deshacer.
        {:else}
          Estás a punto de eliminar este cliente. Esta acción no se puede deshacer.
        {/if}
      </p>

      <!-- Advertencia -->
      <div class="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg mb-6">
        <svg class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div class="text-sm text-red-300">
          Los datos eliminados no podrán ser recuperados
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-3">
        <button
          type="button"
          on:click={() => showDeleteConfirm = false}
          disabled={loading}
          class="flex-1 px-5 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white
                 hover:bg-[#1f1f1f]/50 font-medium rounded-xl transition-all duration-200
                 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Cancelar
        </button>
        <button
          type="button"
          on:click={confirmDelete}
          disabled={loading}
          class="flex-1 px-5 py-3 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700
                 hover:to-red-600 text-white font-medium rounded-xl transition-all duration-200
                 shadow-lg shadow-red-500/25 hover:shadow-red-500/40 flex items-center justify-center gap-2
                 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {#if loading}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Eliminando...
          {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6" />
              <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" />
            </svg>
            Eliminar
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<Cliente
  bind:isOpen={isModalOpen}
  mode={modalMode}
  clienteData={selectedCliente}
  on:success={handleClienteSuccess}
/>

<style>
  @keyframes scale {
    from {
      opacity: 0;
      transform: scale(0.9);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .animate-scale {
    animation: scale 0.2s ease-out;
  }
</style>
