<script lang="ts">
    import SideBar from "$lib/components/layout/SideBar.svelte";
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';

    // Cargar tema al iniciar
    onMount(() => {
        if (browser) {
            const savedTheme = localStorage.getItem('aeve_theme');
            const root = document.documentElement;

            if (savedTheme === 'light') {
                root.classList.remove('dark-theme');
                root.classList.add('light-theme');
            } else {
                root.classList.remove('light-theme');
                root.classList.add('dark-theme');
            }
        }
    });
</script>

<div
    class="flex min-h-screen font-sans antialiased relative overflow-hidden transition-colors duration-300"
    style="background: var(--bg-primary); color: var(--text-primary);"
>
    <div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div
            class="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"
        ></div>
        <div
            class="absolute top-3/4 right-1/4 w-80 h-80 bg-orange-500/5 rounded-full blur-3xl"
        ></div>
        <div
            class="absolute bottom-1/4 left-1/3 w-72 h-72 bg-purple-500/3 rounded-full blur-3xl"
        ></div>
    </div>

    <SideBar />

    <!-- Main Content Area - Scrollable -->
    <main class="flex-1 ml-64 h-screen overflow-y-auto relative">
        <!-- Contenedor con margenes -->
        <div class="p-6">
            <slot />
        </div>
    </main>
</div>

<style>
    /* Tipografia moderna similar a Resend */
    :global(body) {
        font-family:
            "Inter",
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            Roboto,
            "Helvetica Neue",
            Arial,
            sans-serif;
        font-feature-settings: "cv02", "cv03", "cv04", "cv11";
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        background: var(--bg-primary);
        overflow: hidden;
        transition: background 0.3s ease;
    }

    :global(html) {
        overflow: hidden;
    }

    :global(*) {
        border-color: var(--border-light);
    }

    /* Personalizar scrollbar para el main content */
    main::-webkit-scrollbar {
        width: 6px;
    }

    main::-webkit-scrollbar-track {
        background: transparent;
    }

    main::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
        transition: background 0.2s ease;
    }

    main::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
