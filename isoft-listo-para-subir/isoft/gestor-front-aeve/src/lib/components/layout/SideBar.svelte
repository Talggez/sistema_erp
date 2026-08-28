<script>
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { handleLogout, getCurrentUser } from '$lib/login.js';
    import logo from "../../../assets/Logo.png";

    // Usar rune para el estado del usuario
    let currentUser = $state(null);

    onMount(async () => {
        currentUser = await getCurrentUser();
    });

    /**
     * @param {string} route - La ruta a verificar
     * @returns {boolean} - True si la ruta está activa
     */
    function isActive(route) {
        return $page.url.pathname === route;
    }
</script>

<aside
        class="w-64 bg-[#0a0a0a]/80 backdrop-blur-xl border-r border-[#1f1f1f]/50 flex flex-col h-screen fixed left-0 top-0 z-20"
>
    <!-- Efecto de vidrio en el sidebar -->
    <div
            class="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none"
    ></div>

    <!-- Header con logo -->
    <div class="p-6 border-b border-[#1f1f1f]/50 relative z-10 flex-shrink-0">
        <div class="flex items-center gap-2">
            <div class="relative">
                <img src={logo} alt="AEVE" class="w-8 h-8" />
                <div
                        class="absolute inset-0 bg-blue-500/20 rounded-lg blur-sm -z-10"
                ></div>
            </div>
            <span class="text-xl font-semibold">AEVE</span>
            <span
                    class="text-xs bg-gradient-to-r from-blue-600 to-blue-500 text-white px-2 py-0.5 rounded-full ml-auto shadow-lg shadow-blue-500/25"
            >Pro</span>
        </div>
    </div>

    <!-- Navigation - Scrollable area -->
    <nav class="flex-1 px-4 py-6 relative z-10 overflow-y-auto">
        <ul class="space-y-1">
            <li>
                <a
                href="/app/producto"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/producto',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path
                            d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"
                    />
                    <path d="m3.3 7 8.7 5 8.7-5" />
                    <path d="M12 22V12" />
                </svg>
                Productos
                </a>
            </li>

            <li>
                <a
                href="/app/proveedores"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/proveedores',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path d="M3 21h18" />
                    <path d="M5 21V7l8-4v18" />
                    <path d="M19 21V11l-6-4" />
                </svg>
                Proveedores
                </a>
            </li>

            <li>
                <a
                href="/app/clientes"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/clientes',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                Clientes
                </a>
            </li>

            <li>
                <a
                href="/app/proyectos"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/proyectos',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
                Proyectos
                </a>
            </li>

            <li>
                <a
                href="/app/ventas"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/ventas',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <circle cx="8" cy="21" r="1" />
                    <circle cx="19" cy="21" r="1" />
                    <path
                            d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"
                    />
                </svg>
                Ventas
                </a>
            </li>

            <li>
                <a
                href="/app/reportes"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/reportes',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path
                            d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                    />
                    <polyline points="14,2 14,8 20,8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10,9 9,9 8,9" />
                </svg>
                Reportes
                </a>
            </li>

            <li>
                <a
                href="/app/graficos"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/graficos',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <line x1="18" y1="20" x2="18" y2="10" />
                    <line x1="12" y1="20" x2="12" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="14" />
                </svg>
                Gráficos
                </a>
            </li>

            <!-- Separador -->
            <li class="border-t border-[#1f1f1f]/50 my-4"></li>

            <li>
                <a
                href="/app/configuracion"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/configuracion',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <circle cx="12" cy="12" r="3" />
                    <path
                            d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
                    />
                </svg>
                Configuración
                </a>
            </li>

            <li>
                <a
                href="/app/perfil"
                class="flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all duration-200 {isActive(
                '/app/perfil',
            )
                ? 'bg-gradient-to-r from-blue-600/20 to-orange-500/20 text-white shadow-lg backdrop-blur-sm border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-[#151515]/80 hover:backdrop-blur-sm'}"
                >
                <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                </svg>
                Perfil de Usuario
                </a>
            </li>
        </ul>
    </nav>

    <!-- Footer con información del usuario y logout -->
    <div class="p-4 border-t border-[#1f1f1f]/50 relative z-10 flex-shrink-0">
        <div
                class="flex items-center gap-3 bg-[#0f0f0f]/60 backdrop-blur-sm rounded-lg p-3 border border-[#1f1f1f]/30"
        >
            <div
                    class="w-8 h-8 bg-gradient-to-br from-blue-500 to-orange-500 rounded-full flex items-center justify-center text-xs font-bold shadow-lg"
            >
                {#if currentUser}
                    {currentUser.userName.charAt(0).toUpperCase()}
                {:else}
                    A
                {/if}
            </div>
            <div class="flex-1 min-w-0">
                {#if currentUser}
                    <div class="text-sm font-medium text-white truncate">{currentUser.userName}</div>
                    <div class="text-xs text-gray-500 truncate">{currentUser.userEmail}</div>
                {:else}
                    <div class="text-sm font-medium text-white truncate">Cargando...</div>
                {/if}
            </div>
            <button
                    onclick={handleLogout}
                    class="text-red-400 hover:text-red-300 transition-colors p-1 rounded hover:bg-red-900/20"
                    title="Cerrar Sesión"
                    aria-label="Cerrar Sesión"
            >
                <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                >
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16,17 21,12 16,7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
            </button>
        </div>
    </div>
</aside>