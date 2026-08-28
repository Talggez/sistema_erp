<script>
    export let open = false;
    export let handleClose;

    function handleBackdropClick(e) {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    }

    function handleKeydown(e) {
        if (e.key === 'Escape') {
            handleClose();
        }
    }

    function closeModal() {
        handleClose();
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
                    <div class="absolute top-1/4 right-1/4 w-48 h-48 bg-green-500/5 rounded-full blur-3xl"></div>
                    <div class="absolute bottom-1/4 left-1/4 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl"></div>
                </div>

                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 via-green-400 to-teal-400"></div>

                <div class="relative z-10 p-8 text-center">
                    <button
                            class="absolute top-4 right-4 p-2 text-gray-400 hover:text-white hover:bg-[#1f1f1f]/50 rounded-lg transition-all duration-200"
                            on:click={closeModal}
                            aria-label="Cerrar modal"
                    >
                        <svg
                                class="w-5 h-5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                        >
                            <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>

                    <div class="mb-6 flex justify-center">
                        <div class="w-16 h-16 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full flex items-center justify-center shadow-lg animate-pulse">
                            <svg
                                    class="w-8 h-8 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                            >
                                <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="3"
                                        d="M5 13l4 4L19 7"
                                />
                            </svg>
                        </div>
                    </div>

                    <h2 class="text-2xl font-semibold text-white mb-3 tracking-tight">
                        Eliminado exitosamente
                    </h2>

                    <p class="text-gray-400 mb-8 text-sm leading-relaxed">
                        La información ha sido eliminada correctamente del sistema
                    </p>

                    <button
                            class="px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/25 transform hover:scale-105 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                            on:click={closeModal}
                    >
                        Continuar
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}