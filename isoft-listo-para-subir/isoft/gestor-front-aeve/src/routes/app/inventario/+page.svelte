<script>
    export let data;
    let color = 4;
    let search = "";
</script>

<svelte:head>
    <title>Proveedores - AEVE</title>
</svelte:head>



<!-- Header of the project -->
<div class="mb-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h1 class="text-3xl font-bold text-white mb-2">Proveedores</h1>
            <p class="text-gray-400">
                Gestiona tus proveedores y contactos comerciales
            </p>
        </div>
        <!-- Estadística -->
        <div class="flex items-center gap-6">
            <div class="text-center">
                <div class="text-2xl font-bold text-white">
                    {data.count}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    Total
                </div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-400">
                    {data.count}
                </div>
                <div class="text-xs text-gray-400 uppercase tracking-wide">
                    {#if data.count <= 1}
                        Seleccionado
                    {:else}
                        Seleccionados
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>


<!-- Barra de acción -->
<div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 mb-6">
    <div class="flex items-center justify-between gap-4">

        <div class="flex-1 max-w-md">
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

            <input type="text" bind:value={search}
                   placeholder="Buscar proveedores..."
                   class="w-full pl-10 pr-4 py-2.5 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
            />
            </div>
        </div>
        <button
                class="flex items-center gap-2 px-4 py-2 bg-red-600/90 hover:bg-red-600 disabled:bg-red-600/30 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 disabled:opacity-50"
        >
            {#if color === 0}
                <div
                        class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                ></div>
            {:else}
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
            {/if}
            Eliminar
        </button>

        <button class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white rounded-lg transition-all duration-200 shadow-lg shadow-blue-500/25">
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
            Nuevo Proveedor
        </button>
    </div>
</div>


<div class="">
    {#if data.error}
        <p>La data no se ha podido cargar: {data.error}</p>
    {:else}
        <table>
            <thead>

                <tr>
                    <th>Nombre</th>
                    <th>Rut</th>
                    <th>Dirección</th>
                    <th>Email</th>
                    <th>Teléfono</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>


            </tbody>
        </table>

        {#each data.supplies as supplies}


            <p>This is the name {supplies.name}</p>
        {/each}

    {/if}
</div>
