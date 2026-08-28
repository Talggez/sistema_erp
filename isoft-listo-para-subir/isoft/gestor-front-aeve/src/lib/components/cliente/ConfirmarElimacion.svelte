<script>
    export let open = false;
    export let handleClose;
    export let onConfirm;
    export let cantidad = 1;

    let isDeleting = false;

    function handleBackdropClick(e) {
        if (e.target === e.currentTarget && !isDeleting) {
            handleClose();
        }
    }

    function handleKeydown(e) {
        if (e.key === "Escape" && !isDeleting) {
            handleClose();
        }
    }

    async function handleConfirm() {
        if (isDeleting) return;

        isDeleting = true;
        try {
            await onConfirm();
            handleClose();
        } catch (error) {
            console.error("Error al eliminar:", error);
        } finally {
            isDeleting = false;
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
                class="fixed inset-0 bg-black/70 backdrop-blur-sm"
                on:click={handleBackdropClick}
                role="button"
                tabindex="-1"
        ></div>

        <div class="relative w-full max-w-md z-10">
            <div
                    class="relative bg-gradient-to-br from-[#0a0a0a] via-[#111111] to-[#0a0a0a] border border-[#1f1f1f]/50 rounded-2xl shadow-2xl overflow-hidden"
            >
                <div class="absolute inset-0 overflow-hidden pointer-events-none">
                    <div class="absolute top-1/4 right-1/4 w-48 h-48 bg-red-500/5 rounded-full blur-3xl"></div>
                    <div class="absolute bottom-1/4 left-1/4 w-32 h-32 bg-orange-500/5 rounded-full blur-3xl"></div>
                </div>

                <div class="relative z-10 p-8">
                    <div class="flex items-start gap-4 mb-6">
                        <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                            <svg
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="white"
                                    stroke-width="2"
                            >
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                                <line x1="12" y1="9" x2="12" y2="13" />
                                <line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                        </div>

                        <div class="flex-1">
                            <h2 class="text-xl font-semibold text-white mb-2">
                                Confirmar eliminación
                            </h2>
                            <p class="text-gray-400 text-sm leading-relaxed">
                                {#if cantidad > 1}
                                    Estás a punto de eliminar {cantidad} productos. Esta acción no se puede deshacer.
                                {:else}
                                    Estás a punto de eliminar este producto. Esta acción no se puede deshacer.
                                {/if}
                            </p>
                        </div>

                        <button
                                on:click={handleClose}
                                disabled={isDeleting}
                                class="flex-shrink-0 p-2 text-gray-400 hover:text-white hover:bg-[#1f1f1f]/50 rounded-lg transition-all duration-200 disabled:opacity-50"
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

                    <div class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6">
                        <div class="flex items-center gap-3 text-red-300">
                            <svg
                                    width="18"
                                    height="18"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    class="flex-shrink-0"
                            >
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                            </svg>
                            <span class="text-sm">
                                Los datos eliminados no podrán ser recuperados
                            </span>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <button
                                type="button"
                                on:click={handleClose}
                                disabled={isDeleting}
                                class="flex-1 px-6 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white hover:bg-[#1f1f1f]/50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancelar
                        </button>

                        <button
                                type="button"
                                on:click={handleConfirm}
                                disabled={isDeleting}
                                class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-red-500/25"
                        >
                            {#if isDeleting}
                                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                Eliminando...
                            {:else}
                                <svg
                                        width="16"
                                        height="16"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        stroke-width="2"
                                >
                                    <polyline points="3,6 5,6 21,6" />
                                    <path d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2" />
                                </svg>
                                Eliminar
                            {/if}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
