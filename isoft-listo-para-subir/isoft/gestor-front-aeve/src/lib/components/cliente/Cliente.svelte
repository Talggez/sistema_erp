<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';

  export let isOpen = false;
  export let mode = 'crear';
  export let clienteData: any = null;

  const dispatch = createEventDispatcher();

  let loading = false;
  let mensajeError: string | null = null;

  // Tipos de cliente (solo Persona y Empresa)
  const tiposDisponibles = [
    { id: 1, nombre: 'Persona', descripcion: 'Cliente persona natural' },
    { id: 2, nombre: 'Empresa', descripcion: 'Cliente empresa o razon social' }
  ];

  // Formulario base
  const formularioBase = {
    nombre: '',
    apellidos: '',
    rut: '',
    razon_social: '',
    email: '',
    comuna: '',
    direccion: '',
    ciudad: '',
    tipo_cliente_id: ''
  };

  let formulario = { ...formularioBase };

  // Determinar si es empresa basado en tipo_cliente_id
  $: tipoSeleccionado = tiposDisponibles.find(t => t.id === Number(formulario.tipo_cliente_id));
  $: esEmpresa = tipoSeleccionado?.nombre?.toLowerCase().includes('empresa') || false;

  // Limpiar campos irrelevantes al cambiar de tipo (solo en modo crear)
  let previousTipoId: string | null = null;
  $: if (mode === 'crear' && formulario.tipo_cliente_id && formulario.tipo_cliente_id !== previousTipoId) {
    previousTipoId = formulario.tipo_cliente_id;
    // Limpiar campos al cambiar tipo
    formulario.nombre = '';
    formulario.apellidos = '';
    formulario.razon_social = '';
  }

  // Inicializar formulario cuando cambia clienteData o isOpen
  $: if (isOpen) {
    if (mode === 'actualizar' && clienteData) {
      formulario = {
        nombre: clienteData.nombre || '',
        apellidos: clienteData.apellidos || '',
        rut: clienteData.rut || '',
        razon_social: clienteData.razon_social || '',
        email: clienteData.email || '',
        comuna: clienteData.comuna || '',
        direccion: clienteData.direccion || '',
        ciudad: clienteData.ciudad || '',
        tipo_cliente_id: clienteData.tipo_cliente_id || ''
      };
    } else {
      formulario = { ...formularioBase };
    }
    mensajeError = null;
  }

  function closeModal() {
    isOpen = false;
    clienteData = null;
    mensajeError = null;
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget && !loading) {
      closeModal();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && !loading) {
      closeModal();
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();

    // Validaciones
    if (!formulario.tipo_cliente_id) {
      mensajeError = 'Debes seleccionar un tipo de cliente';
      setTimeout(() => mensajeError = null, 3000);
      return;
    }

    if (!formulario.rut) {
      mensajeError = 'El RUT es obligatorio';
      setTimeout(() => mensajeError = null, 3000);
      return;
    }

    if (esEmpresa) {
      if (!formulario.nombre) {
        mensajeError = 'El nombre de la empresa es obligatorio';
        setTimeout(() => mensajeError = null, 3000);
        return;
      }
      if (!formulario.razon_social) {
        mensajeError = 'La razon social es obligatoria para empresas';
        setTimeout(() => mensajeError = null, 3000);
        return;
      }
    } else {
      if (!formulario.nombre) {
        mensajeError = 'El nombre es obligatorio';
        setTimeout(() => mensajeError = null, 3000);
        return;
      }
    }

    loading = true;

    try {
      const API_BASE_URL = 'http://localhost:5000';

      // Preparar datos segun el tipo
      const body: {
        rut: string;
        email: string | null;
        comuna: string | null;
        direccion: string | null;
        ciudad: string | null;
        tipo_cliente_id: number;
        nombre: string;
        apellidos: string;
        razon_social: string;
      } = {
        rut: formulario.rut,
        email: formulario.email || null,
        comuna: formulario.comuna || null,
        direccion: formulario.direccion || null,
        ciudad: formulario.ciudad || null,
        tipo_cliente_id: parseInt(formulario.tipo_cliente_id),
        nombre: formulario.nombre,
        apellidos: '',
        razon_social: ''
      };

      if (esEmpresa) {
        body.razon_social = formulario.razon_social;
      } else {
        body.apellidos = formulario.apellidos || '';
      }

      let url = `${API_BASE_URL}/clientes`;
      let method = 'POST';

      if (mode === 'actualizar' && clienteData?.id) {
        url = `${API_BASE_URL}/clientes/${clienteData.id}`;
        method = 'PUT';
      }

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}`);
      }

      dispatch('success', {
        message: mode === 'crear' ? 'Cliente creado exitosamente' : 'Cliente actualizado exitosamente'
      });
      closeModal();
    } catch (err) {
      mensajeError = err instanceof Error ? err.message : 'Error al guardar el cliente';
      setTimeout(() => mensajeError = null, 5000);
    } finally {
      loading = false;
    }
  }

  // Formatear RUT mientras se escribe
  function formatearRUT(e: Event) {
    const target = e.target as HTMLInputElement;
    let value = target.value.replace(/[^0-9kK]/g, '').toUpperCase();
    if (value.length > 1) {
      const cuerpo = value.slice(0, -1);
      const dv = value.slice(-1);
      value = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '-' + dv;
    }
    formulario.rut = value;
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn"
    on:click={handleBackdropClick}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    transition:fade={{ duration: 200 }}
  >
    <div
      class="relative w-full max-w-2xl mx-4 max-h-[90vh] overflow-hidden rounded-2xl bg-[#0a0a0a] border border-[#1f1f1f] shadow-2xl animate-slideUp"
      transition:scale={{ duration: 200, start: 0.95 }}
    >
      <!-- Header con gradiente -->
      <div class="relative overflow-hidden border-b border-[#1f1f1f]/50 bg-gradient-to-br from-[#0a0a0a] via-[#0d0d0d] to-[#0a0a0a]">
        <div class="absolute inset-0 bg-gradient-to-r from-green-500/5 via-emerald-500/5 to-green-500/5"></div>
        <div class="relative z-10 flex items-center justify-between p-8">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl border border-green-500/30">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                class="text-green-400"
              >
                {#if esEmpresa}
                  <path d="M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4z"/>
                  <path d="M8 14v3M12 14v3M16 14v3"/>
                {:else}
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                {/if}
              </svg>
            </div>
            <div>
              <h2 class="text-2xl font-bold text-white">
                {mode === 'crear' ? 'Nuevo Cliente' : 'Editar Cliente'}
              </h2>
              <p class="text-sm text-gray-400 mt-1">
                {mode === 'crear' ? 'Completa la informacion del cliente' : 'Actualiza los datos del cliente'}
              </p>
            </div>
          </div>

          <button
            on:click={closeModal}
            type="button"
            disabled={loading}
            aria-label="Cerrar modal"
            class="p-2 text-gray-400 hover:text-white hover:bg-[#1f1f1f]/50 rounded-xl transition-all duration-200 disabled:opacity-50"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mensaje de error -->
      {#if mensajeError}
        <div class="mx-6 mt-4 bg-red-500/10 border border-red-500/20 text-red-300 p-3 rounded-lg text-sm" transition:fade>
          {mensajeError}
        </div>
      {/if}

      <!-- Contenido del formulario con scroll -->
      <div class="overflow-y-auto max-h-[calc(90vh-200px)] custom-scrollbar">
        <form on:submit|preventDefault={handleSubmit} class="p-8 space-y-8">

          <!-- Tipo de Cliente (primero para determinar campos) -->
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
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              Tipo de Cliente
            </h3>

            <div>
              <label for="tipo_cliente" class="block text-sm font-medium text-gray-300 mb-2">
                Seleccionar Tipo <span class="text-orange-400">*</span>
              </label>
              <select
                id="tipo_cliente"
                bind:value={formulario.tipo_cliente_id}
                required
                disabled={loading}
                class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed appearance-none cursor-pointer"
              >
                <option value="">Seleccione un tipo</option>
                {#each tiposDisponibles as tipo}
                  <option value={tipo.id}>{tipo.nombre}</option>
                {/each}
              </select>
              {#if tipoSeleccionado?.descripcion}
                <p class="mt-2 text-xs text-gray-400">{tipoSeleccionado.descripcion}</p>
              {/if}
            </div>
          </div>

          <!-- Informacion segun tipo de cliente -->
          {#if formulario.tipo_cliente_id}
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
                  {#if esEmpresa}
                    <path d="M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4z"/>
                  {:else}
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  {/if}
                </svg>
                {esEmpresa ? 'Datos de la Empresa' : 'Datos Personales'}
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {#if esEmpresa}
                  <!-- Campos para Empresa: Nombre y Razon Social -->
                  <div class="space-y-2">
                    <label for="nombre_empresa" class="block text-sm font-medium text-gray-300">
                      Nombre de la Empresa <span class="text-orange-400">*</span>
                    </label>
                    <input
                      type="text"
                      id="nombre_empresa"
                      bind:value={formulario.nombre}
                      required
                      maxlength="180"
                      disabled={loading}
                      placeholder="Ej: Empresa ABC"
                      class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>

                  <div class="space-y-2">
                    <label for="razon_social" class="block text-sm font-medium text-gray-300">
                      Razon Social <span class="text-orange-400">*</span>
                    </label>
                    <input
                      type="text"
                      id="razon_social"
                      bind:value={formulario.razon_social}
                      required
                      maxlength="180"
                      disabled={loading}
                      placeholder="Ej: Empresa ABC Ltda."
                      class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>
                {:else}
                  <!-- Campos para Persona: Nombre y Apellidos -->
                  <div class="space-y-2">
                    <label for="nombre_persona" class="block text-sm font-medium text-gray-300">
                      Nombre <span class="text-orange-400">*</span>
                    </label>
                    <input
                      type="text"
                      id="nombre_persona"
                      bind:value={formulario.nombre}
                      required
                      maxlength="180"
                      disabled={loading}
                      placeholder="Ej: Juan"
                      class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>

                  <div class="space-y-2">
                    <label for="apellidos" class="block text-sm font-medium text-gray-300">
                      Apellidos
                    </label>
                    <input
                      type="text"
                      id="apellidos"
                      bind:value={formulario.apellidos}
                      maxlength="180"
                      disabled={loading}
                      placeholder="Ej: Perez Gonzalez"
                      class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>
                {/if}

                <!-- RUT (comun para ambos) -->
                <div class="space-y-2">
                  <label for="rut" class="block text-sm font-medium text-gray-300">
                    RUT <span class="text-orange-400">*</span>
                  </label>
                  <input
                    type="text"
                    id="rut"
                    value={formulario.rut}
                    on:input={formatearRUT}
                    required
                    maxlength="12"
                    disabled={loading}
                    placeholder="12.345.678-9"
                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <!-- Email -->
                <div class="space-y-2">
                  <label for="email" class="block text-sm font-medium text-gray-300">
                    Correo Electronico
                  </label>
                  <div class="relative">
                    <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                        <polyline points="22,6 12,13 2,6" />
                      </svg>
                    </div>
                    <input
                      type="email"
                      id="email"
                      bind:value={formulario.email}
                      disabled={loading}
                      placeholder="ejemplo@correo.com"
                      class="w-full pl-11 pr-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Ubicacion -->
            <div class="space-y-6">
              <h3 class="text-lg font-medium text-white flex items-center gap-2">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  class="text-emerald-400"
                >
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                Ubicacion
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2 md:col-span-2">
                  <label for="direccion" class="block text-sm font-medium text-gray-300">
                    Direccion
                  </label>
                  <input
                    type="text"
                    id="direccion"
                    bind:value={formulario.direccion}
                    maxlength="255"
                    disabled={loading}
                    placeholder="Calle Principal #123"
                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div class="space-y-2">
                  <label for="comuna" class="block text-sm font-medium text-gray-300">
                    Comuna
                  </label>
                  <input
                    type="text"
                    id="comuna"
                    bind:value={formulario.comuna}
                    maxlength="100"
                    disabled={loading}
                    placeholder="Ej: Providencia"
                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div class="space-y-2">
                  <label for="ciudad" class="block text-sm font-medium text-gray-300">
                    Ciudad
                  </label>
                  <input
                    type="text"
                    id="ciudad"
                    bind:value={formulario.ciudad}
                    maxlength="100"
                    disabled={loading}
                    placeholder="Ej: Santiago"
                    class="w-full px-4 py-3 bg-[#151515]/60 border border-[#2a2a2a] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          {:else}
            <!-- Mensaje cuando no hay tipo seleccionado -->
            <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <div class="flex items-start gap-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-blue-400 mt-0.5 flex-shrink-0">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <div class="text-sm text-blue-300">
                  <p class="font-medium mb-1">Selecciona un tipo de cliente</p>
                  <p class="text-blue-300/80">
                    El formulario se adaptara segun el tipo seleccionado (Persona o Empresa).
                  </p>
                </div>
              </div>
            </div>
          {/if}

          <!-- Footer con botones -->
          <div class="flex items-center justify-between pt-4 border-t border-[#1f1f1f]">
            <div class="text-sm text-gray-400">
              <span class="text-orange-400">*</span> Campos obligatorios
            </div>

            <div class="flex items-center gap-3">
              <button
                type="button"
                on:click={closeModal}
                disabled={loading}
                class="px-6 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1f1f1f]/50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancelar
              </button>

              <button
                type="submit"
                disabled={loading || !formulario.tipo_cliente_id}
                class="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-green-500/25"
              >
                {#if loading}
                  <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Guardando...
                {:else}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17,21 17,13 7,13 7,21" />
                    <polyline points="7,3 7,8 15,8" />
                  </svg>
                  {mode === 'crear' ? 'Crear Cliente' : 'Actualizar Cliente'}
                {/if}
              </button>
            </div>
          </div>
        </form>
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
    background: rgba(34, 197, 94, 0.5);
    border-radius: 3px;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(34, 197, 94, 0.7);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.2s ease-out;
  }

  .animate-slideUp {
    animation: slideUp 0.3s ease-out;
  }
</style>
