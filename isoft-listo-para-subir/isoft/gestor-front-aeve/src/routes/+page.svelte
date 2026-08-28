<script lang="js">
    import { onMount } from "svelte";
    import { handleLogin } from "$lib/login.js";

    let email = "";
    let password = "";
    let errorMessage = "";
    let rememberUser = false;
    let isLoading = false;
    let showPassword = false;

    onMount(() => {
        const savedEmail = localStorage.getItem("rememberedEmail");
        if (savedEmail) {
            email = savedEmail;
            rememberUser = true;
        }
    });

    /** @param {SubmitEvent} event */
    async function onSubmit(event) {
        event.preventDefault();
        errorMessage = "";
        isLoading = true;

        try {
            await handleLogin(email, password, rememberUser);
        } catch (error) {
            errorMessage = error.message;
        } finally {
            isLoading = false;
        }
    }

    function togglePassword() {
        showPassword = !showPassword;
    }
</script>

<svelte:head>
    <title>Iniciar Sesión - ERP AEVE</title>
</svelte:head>

<div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black p-4"
>
    <div class="w-full max-w-lg relative">
        <!-- Card principal -->
        <div
            class="relative bg-gradient-to-br from-gray-900 via-black to-gray-800 border-4 border-gray-700/50 rounded-3xl shadow-2xl overflow-hidden"
        >
            <!-- Header con logo -->
            <div
                class="bg-gradient-to-r from-gray-800/30 to-gray-700/30 px-10 pt-10 pb-6"
            >
                <div class="flex justify-center mb-6">
                    <div
                        class="w-24 h-24 bg-black rounded-full flex items-center justify-center border-3 border-gray-600/50 shadow-lg"
                    >
                        <img
                            src="/src/assets/Logo.png"
                            alt="Logo ERP AEVE"
                            class="w-14 h-14 object-contain"
                        />
                    </div>
                </div>
                <h1
                    class="text-white text-3xl font-light text-center tracking-wide"
                >
                    Bienvenido de vuelta
                </h1>
                <p class="text-gray-400 text-base text-center mt-3">
                    Accede a tu cuenta ERP AEVE
                </p>
            </div>

            <!-- Contenido del formulario -->
            <div class="px-10 pb-10 pt-8">
                <!-- Mensaje de error -->
                {#if errorMessage}
                    <div
                        class="mb-8 p-5 bg-red-500/15 border-2 border-red-500/40 rounded-2xl"
                    >
                        <div class="flex items-center">
                            <svg
                                class="w-5 h-5 text-red-400 mr-3"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                            <p class="text-red-400 text-sm font-medium">
                                Credenciales inválidas
                            </p>
                        </div>
                    </div>
                {/if}

                <form class="space-y-8" on:submit|preventDefault={onSubmit}>
                    <!-- Campo de email -->
                    <div class="space-y-3">
                        <label
                            for="email"
                            class="block text-white text-base font-medium"
                        >
                            Correo electrónico
                        </label>
                        <div class="relative group">
                            <input
                                type="email"
                                id="email"
                                bind:value={email}
                                class="w-full px-5 py-4 bg-gray-800/50 border-2 border-gray-600/50 rounded-xl text-white placeholder-gray-400 focus:border-blue-500 focus:bg-gray-700/50 transition-all duration-300 outline-none text-base"
                                placeholder="tu@ejemplo.com"
                                required
                            />
                            <div
                                class="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-600/0 to-orange-500/0 group-focus-within:from-blue-600/10 group-focus-within:to-orange-500/10 pointer-events-none transition-all duration-300"
                            ></div>
                        </div>
                    </div>

                    <!-- Campo de contraseña -->
                    <div class="space-y-3">
                        <label
                            for="password"
                            class="block text-white text-base font-medium"
                        >
                            Contraseña
                        </label>
                        <div class="relative group">
                            <input
                                type={showPassword ? "text" : "password"}
                                id="password"
                                bind:value={password}
                                class="w-full px-5 py-4 pr-14 bg-gray-800/50 border-2 border-gray-600/50 rounded-xl text-white placeholder-gray-400 focus:border-blue-500 focus:bg-gray-700/50 transition-all duration-300 outline-none text-base"
                                placeholder="••••••••"
                                required
                            />
                            <button
                                type="button"
                                on:click={togglePassword}
                                class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors duration-200 p-1"
                                aria-label={showPassword
                                    ? "Ocultar contraseña"
                                    : "Mostrar contraseña"}
                            >
                                {#if showPassword}
                                    <!-- Ojo cerrado -->
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
                                            d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                                        ></path>
                                    </svg>
                                {:else}
                                    <!-- Ojo abierto -->
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
                                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                        ></path>
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                        ></path>
                                    </svg>
                                {/if}
                            </button>
                            <div
                                class="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-600/0 to-orange-500/0 group-focus-within:from-blue-600/10 group-focus-within:to-orange-500/10 pointer-events-none transition-all duration-300"
                            ></div>
                        </div>
                    </div>

                    <!-- Recordar usuario -->
                    <div class="flex items-center pt-2">
                        <input
                            bind:checked={rememberUser}
                            id="remember-checkbox"
                            type="checkbox"
                            class="w-5 h-5 text-blue-600 bg-gray-800/50 border-2 border-gray-600/50 rounded focus:ring-blue-500 focus:ring-2"
                        />
                        <label
                            for="remember-checkbox"
                            class="ml-3 text-base text-gray-300 select-none cursor-pointer"
                        >
                            Recordar mi usuario
                        </label>
                    </div>

                    <!-- Botón de envío -->
                    <button
                        type="submit"
                        disabled={isLoading}
                        class="w-full relative overflow-hidden bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-blue-800 disabled:to-blue-900 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] disabled:scale-100 shadow-lg hover:shadow-blue-500/25 group text-base"
                    >
                        <span
                            class="relative z-10 flex items-center justify-center"
                        >
                            {#if isLoading}
                                <svg
                                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        class="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        stroke-width="4"
                                    ></circle>
                                    <path
                                        class="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    ></path>
                                </svg>
                                Iniciando sesión...
                            {:else}
                                Iniciar Sesión
                            {/if}
                        </span>
                        <div
                            class="absolute inset-0 bg-gradient-to-r from-orange-500/0 via-orange-500/20 to-orange-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"
                        ></div>
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
