<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { fade, scale } from 'svelte/transition';

    // Tipos
    type Proyecto = {
        id: string;
        nombre: string;
        clienteAsociado: string;
        fechaInicio: string;
        estado: 'Activo' | 'En Pausa' | 'Completado';
        descripcion?: string;
        presupuesto?: number;
    };

    // Props
    export let visible = false;
    export let mode: 'new' | 'edit' | 'cotizar' = 'new';
    export let proyecto: Proyecto | null = null;

    // Dispatcher
    const dispatch = createEventDispatcher();

    // Estado del formulario
    const formularioBase: Proyecto = {
        id: '',
        nombre: '',
        clienteAsociado: '',
        fechaInicio: '',
        estado: 'Activo',
        descripcion: '',
        presupuesto: 0
    };

    let formulario: Proyecto = { ...formularioBase };
    let mensajeError: string | null = null;

    // Inicializar formulario cuando cambia el proyecto o el modo
    $: if (visible) {
        if (mode === 'edit' && proyecto) {
            formulario = { ...proyecto };
        } else if (mode === 'cotizar' && proyecto) {
            formulario = { ...proyecto };
        } else {
            formulario = {
                ...formularioBase,
                id: crypto.randomUUID(),
                fechaInicio: new Date().toISOString().split('T')[0]
            };
        }
    }

    // Funciones
    const cerrar = () => {
        mensajeError = null;
        dispatch('close');
    };

    const guardar = (e?: SubmitEvent) => {
        e?.preventDefault?.();

        if (!formulario.nombre || !formulario.clienteAsociado) {
            mensajeError = 'El nombre y el cliente son obligatorios.';
            setTimeout(() => mensajeError = null, 3000);
            return;
        }

        if (mode === 'cotizar') {
            if (!formulario.presupuesto || formulario.presupuesto <= 0) {
                mensajeError = 'Debes ingresar un presupuesto válido para generar la cotización.';
                setTimeout(() => mensajeError = null, 3000);
                return;
            }
            dispatch('cotizar', formulario);
        } else {
            dispatch('save', formulario);
        }

        cerrar();
    };

    const formatearPrecio = (precio: number | undefined) => {
        return new Intl.NumberFormat('es-CL', {
            style: 'currency',
            currency: 'CLP',
        }).format(precio || 0);
    };

    // Cerrar con Escape
    const handleKeydown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            cerrar();
        }
    };
</script>

<svelte:window on:keydown={handleKeydown} />

{#if visible}
    <!-- Overlay -->
    <div
        class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
        on:click={cerrar}
        on:keydown={(e) => e.key === 'Enter' && cerrar()}
        role="button"
        tabindex="0"
        transition:fade={{ duration: 200 }}
    ></div>

    <!-- Modal -->
    <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        transition:fade={{ duration: 200 }}
    >
        <div
            class="bg-[#0a0a0a] border border-[#1f1f1f] rounded-2xl w-full max-w-lg shadow-2xl"
            transition:scale={{ duration: 200, start: 0.95 }}
            on:click|stopPropagation
            on:keydown|stopPropagation
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-[#1f1f1f]">
                <h2 id="modal-title" class="text-xl font-semibold text-white">
                    {mode === 'new' ? 'Nuevo Proyecto' : mode === 'edit' ? 'Editar Proyecto' : 'Generar Cotización'}
                </h2>
                <button
                    on:click={cerrar}
                    class="w-8 h-8 flex items-center justify-center rounded-lg bg-[#1a1a1a] hover:bg-[#2a2a2a] text-gray-400 hover:text-white transition-colors"
                    aria-label="Cerrar modal"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>
            </div>

            <!-- Mensaje de error -->
            {#if mensajeError}
                <div class="mx-6 mt-4 bg-red-500/10 border border-red-500/20 text-red-300 p-3 rounded-lg text-sm" transition:fade>
                    {mensajeError}
                </div>
            {/if}

            <!-- Content -->
            <div class="p-6">
                <form on:submit|preventDefault={guardar} class="space-y-4">
                    <!-- Nombre del Proyecto -->
                    <div>
                        <label for="nombre" class="block text-sm font-medium text-gray-300 mb-2">
                            Nombre del Proyecto *
                        </label>
                        <input
                            id="nombre"
                            type="text"
                            placeholder="Ej: Rediseño de plataforma web"
                            bind:value={formulario.nombre}
                            required
                            disabled={mode === 'cotizar'}
                            class="w-full px-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                        />
                    </div>

                    <!-- Cliente Asociado -->
                    <div>
                        <label for="cliente" class="block text-sm font-medium text-gray-300 mb-2">
                            Cliente Asociado *
                        </label>
                        <input
                            id="cliente"
                            type="text"
                            placeholder="Nombre del cliente"
                            bind:value={formulario.clienteAsociado}
                            required
                            disabled={mode === 'cotizar'}
                            class="w-full px-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                        />
                    </div>

                    <!-- Descripción -->
                    <div>
                        <label for="descripcion" class="block text-sm font-medium text-gray-300 mb-2">
                            Descripción
                        </label>
                        <textarea
                            id="descripcion"
                            placeholder="Descripción breve del proyecto..."
                            bind:value={formulario.descripcion}
                            disabled={mode === 'cotizar'}
                            rows="3"
                            class="w-full px-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all resize-none"
                        ></textarea>
                    </div>

                    <!-- Fecha de Inicio y Estado -->
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label for="fechaInicio" class="block text-sm font-medium text-gray-300 mb-2">
                                Fecha de Inicio
                            </label>
                            <input
                                id="fechaInicio"
                                type="date"
                                bind:value={formulario.fechaInicio}
                                disabled={mode === 'cotizar'}
                                class="w-full px-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                            />
                        </div>

                        <div>
                            <label for="estado" class="block text-sm font-medium text-gray-300 mb-2">
                                Estado
                            </label>
                            <select
                                id="estado"
                                bind:value={formulario.estado}
                                disabled={mode === 'cotizar'}
                                class="w-full px-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
                            >
                                <option value="Activo">Activo</option>
                                <option value="En Pausa">En Pausa</option>
                                <option value="Completado">Completado</option>
                            </select>
                        </div>
                    </div>

                    <!-- Presupuesto -->
                    <div>
                        <label for="presupuesto" class="block text-sm font-medium text-gray-300 mb-2">
                            Presupuesto {mode === 'cotizar' ? '*' : '(Opcional)'}
                        </label>
                        <div class="relative">
                            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                            <input
                                id="presupuesto"
                                type="number"
                                placeholder="0"
                                bind:value={formulario.presupuesto}
                                required={mode === 'cotizar'}
                                min="0"
                                step="1000"
                                class="w-full pl-8 pr-4 py-2.5 bg-[#151515] border border-[#2a2a2a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                            />
                        </div>
                        {#if mode === 'cotizar'}
                            <p class="mt-2 text-xs text-gray-400">
                                Este presupuesto se incluirá en la cotización generada
                            </p>
                        {/if}
                    </div>

                    {#if mode === 'cotizar'}
                        <div class="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                            <div class="flex items-start gap-3">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-blue-400 mt-0.5 flex-shrink-0">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="12" y1="16" x2="12" y2="12" />
                                    <line x1="12" y1="8" x2="12.01" y2="8" />
                                </svg>
                                <div class="text-sm text-blue-300">
                                    <p class="font-medium mb-1">Modo Cotización</p>
                                    <p class="text-blue-300/80">
                                        Se generará una cotización para este proyecto con el presupuesto especificado.
                                    </p>
                                </div>
                            </div>
                        </div>
                    {/if}

                    <!-- Footer con botones -->
                    <div class="flex items-center justify-end gap-3 pt-4 border-t border-[#1f1f1f]">
                        <button
                            type="button"
                            on:click={cerrar}
                            class="px-4 py-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] text-gray-300 rounded-lg transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            class="px-4 py-2 bg-gradient-to-r {mode === 'cotizar' ? 'from-green-600 to-green-500 hover:from-green-700 hover:to-green-600' : 'from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600'} text-white rounded-lg transition-all duration-200 shadow-lg {mode === 'cotizar' ? 'shadow-green-500/25' : 'shadow-blue-500/25'}"
                        >
                            {mode === 'new' ? 'Crear Proyecto' : mode === 'edit' ? 'Guardar Cambios' : 'Generar Cotización'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
