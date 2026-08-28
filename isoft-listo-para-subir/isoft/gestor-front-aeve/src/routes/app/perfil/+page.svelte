<script lang="ts">
  import { onMount } from 'svelte';
  // Importa el componente EditarProfile desde la ruta correcta
  import EditarProfile from '$lib/components/userProfile/EditarProfile.svelte';

  // Datos del usuario
  let usuario = {
      id: null,
      nombre: '',
      apellidos: '',
      usuario: '',
      rol: '',
      cargo: '',
      email: '',
      telefono: '',
      rut: '',
      direccion: ''
  };

  let cargando = true;
  let error = null;

  // Estado del modal
  let editarProfileOpen = false;
  let cambiarPasswordOpen = false;
  let mostrarMensajeExito = false;
  let cambioContrasenaEnviando = false;

  // Variables para el formulario de cambio de contraseña
  let passwordActual = '';
  let passwordNueva = '';
  let passwordConfirmar = '';
  let errorPassword = '';

  // Obtener ID del usuario desde la sesión del servidor
  async function obtenerUsuarioId() {
      try {
          const response = await fetch('/api/auth/get-user');
          if (response.ok) {
              const userData = await response.json();
              return userData.userId || 1;
          }
      } catch (err) {
          console.error('Error al obtener sesión:', err);
      }
      return 1;
  }

  // Cargar datos del perfil desde el backend
  async function cargarPerfil() {
      try {
          cargando = true;
          error = null;
          const usuarioId = await obtenerUsuarioId();

          const response = await fetch(`http://localhost:5000/perfil/${usuarioId}`);

          if (!response.ok) {
              throw new Error(`Error ${response.status}: ${response.statusText}`);
          }

          const data = await response.json();
          usuario = {
              id: data.id,
              nombre: data.nombre || '',
              apellidos: data.apellidos || '',
              usuario: data.email?.split('@')[0] || 'usuario',
              rol: data.rol || 'Sin rol',
              cargo: data.cargo || 'Sin cargo',
              email: data.email || '',
              telefono: data.telefono || '',
              rut: data.rut || '',
              direccion: data.direccion || ''
          };
      } catch (err) {
          console.error('Error al cargar perfil:', err);
          error = err instanceof Error ? err.message : 'Error desconocido';
      } finally {
          cargando = false;
      }
  }

  onMount(() => {
      cargarPerfil();
  });

  function openEditProfile() {
      editarProfileOpen = true;
  }

  function closeEditProfile() {
      editarProfileOpen = false;
  }

  function openCambiarPassword() {
      cambiarPasswordOpen = true;
      passwordActual = '';
      passwordNueva = '';
      passwordConfirmar = '';
      errorPassword = '';
  }

  function closeCambiarPassword() {
      cambiarPasswordOpen = false;
      passwordActual = '';
      passwordNueva = '';
      passwordConfirmar = '';
      errorPassword = '';
  }

  async function handleCambiarPassword() {
      errorPassword = '';

      // Validaciones
      if (!passwordActual || !passwordNueva || !passwordConfirmar) {
          errorPassword = 'Todos los campos son obligatorios';
          return;
      }

      if (passwordNueva.length < 6) {
          errorPassword = 'La nueva contraseña debe tener al menos 6 caracteres';
          return;
      }

      if (passwordNueva !== passwordConfirmar) {
          errorPassword = 'Las contraseñas no coinciden';
          return;
      }

      try {
          cambioContrasenaEnviando = true;
          const usuarioId = await obtenerUsuarioId();

          const response = await fetch(`http://localhost:5000/perfil/${usuarioId}/cambiar-contrasena`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  current_password: passwordActual,
                  new_password: passwordNueva
              })
          });

          if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.detail || 'Error al cambiar contraseña');
          }

          // Cerrar modal y mostrar mensaje de éxito
          closeCambiarPassword();
          mostrarMensajeExito = true;

          // Cerrar mensaje automáticamente después de 3 segundos
          setTimeout(() => {
              mostrarMensajeExito = false;
          }, 3000);
      } catch (err) {
          errorPassword = err instanceof Error ? err.message : 'Error desconocido';
      } finally {
          cambioContrasenaEnviando = false;
      }
  }

  async function handleUsuarioGuardado(nuevosDatos: { nombre?: string; email?: string; telefono?: string }) {
      try {
          const usuarioId = await obtenerUsuarioId();

          const response = await fetch(`http://localhost:5000/perfil/${usuarioId}`, {
              method: 'PUT',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  nombre: nuevosDatos.nombre,
                  email: nuevosDatos.email,
                  telefono: nuevosDatos.telefono
              })
          });

          if (!response.ok) {
              throw new Error('Error al actualizar perfil');
          }

          // Recargar datos del perfil
          await cargarPerfil();
      } catch (err) {
          console.error('Error al guardar usuario:', err);
      }
  }
</script>

<svelte:head>
  <title>Perfil - ERP AEVE</title>
</svelte:head>

<!-- Header -->
<div class="mb-8">
  <h1 class="text-3xl font-bold text-white mb-2">Mi Perfil</h1>
  <p class="text-gray-400">Gestiona tu información personal y configuración de cuenta</p>
</div>

<!-- Main Content -->
<div class="max-w-6xl mx-auto">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <!-- Profile Card -->
      <div class="lg:col-span-1">
          <div class="bg-[#151515]/60 border border-[#1f1f1f]/50 rounded-2xl p-6 shadow-2xl">

              <!-- Avatar -->
              <div class="text-center mb-6">
                  <div class="relative inline-block">
                      <div class="w-24 h-24 bg-gradient-to-br from-orange-500 to-orange-600
                                  rounded-full flex items-center justify-center mx-auto mb-4
                                  shadow-lg shadow-orange-500/25">
                          <svg class="w-12 h-12 text-white" viewBox="0 0 24 24" fill="none"
                               stroke="currentColor" stroke-width="2">
                              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                              <circle cx="12" cy="7" r="4"/>
                          </svg>
                      </div>

                      <!-- Status indicator -->
                      <div class="absolute bottom-3 right-3 w-4 h-4 bg-green-500
                                  border-2 border-[#151515] rounded-full"></div>
                  </div>

                  <h2 class="text-2xl font-bold text-white mb-1">{usuario.nombre} {usuario.apellidos}</h2>
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
                               bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      {usuario.rol}
                  </span>
                  {#if usuario.cargo}
                  <p class="text-sm text-gray-400 mt-2">{usuario.cargo}</p>
                  {/if}
              </div>

              <!-- Quick Actions -->
              <div class="space-y-3">
                  <button
                          on:click={openEditProfile}
                          class="w-full flex items-center justify-center gap-2 px-4 py-3
                             bg-gradient-to-r from-orange-600 to-orange-500
                             hover:from-orange-700 hover:to-orange-600
                             text-white font-medium rounded-xl transition-all duration-200
                             shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40
                             transform hover:scale-[1.02] active:scale-[0.98]">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="m18.5 2.5 3 3L10 17l-4 1 1-4L18.5 2.5z"/>
                      </svg>
                      Editar Perfil
                  </button>

                  <button
                          on:click={openCambiarPassword}
                          class="w-full flex items-center justify-center gap-2 px-4 py-3
                                 border border-[#2a2a2a] text-gray-300 hover:text-white
                                 hover:bg-[#1f1f1f]/50 font-medium rounded-xl transition-all duration-200
                                 transform hover:scale-[1.02] active:scale-[0.98]">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                          <circle cx="12" cy="16" r="1"/>
                          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                      Cambiar Contraseña
                  </button>
              </div>
          </div>
      </div>

      <!-- Details Section -->
      <div class="lg:col-span-2 space-y-6">

          <!-- Personal Information -->
          <div class="bg-[#151515]/60 border border-[#1f1f1f]/50 rounded-2xl p-6 shadow-2xl">
              <div class="flex items-center gap-3 mb-6">
                  <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                          <circle cx="12" cy="7" r="4"/>
                      </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-white">Información Personal</h3>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">Nombre Completo</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg">
                          <span class="text-white">{usuario.nombre} {usuario.apellidos}</span>
                      </div>
                  </div>

                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">RUT</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg">
                          <span class="text-white font-mono">{usuario.rut || 'No registrado'}</span>
                      </div>
                  </div>

                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">Rol del Sistema</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg">
                          <span class="text-white">{usuario.rol}</span>
                      </div>
                  </div>

                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">Cargo</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg">
                          <span class="text-white">{usuario.cargo || 'No asignado'}</span>
                      </div>
                  </div>
              </div>
          </div>

          <!-- Contact Information -->
          <div class="bg-[#151515]/60 border border-[#1f1f1f]/50 rounded-2xl p-6 shadow-2xl">
              <div class="flex items-center gap-3 mb-6">
                  <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-green-400" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2">
                          <path d="M22 16.92V19a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.05 4.18 2 2 0 0 1 4 2h2.09a2 2 0 0 1 2 1.72c.12.9.3 1.78.57 2.63a2 2 0 0 1-.45 2.11L7.1 9.9a16 16 0 0 0 6 6l1.44-1.11a2 2 0 0 1 2.11-.45c.85.27 1.73.45 2.63.57A2 2 0 0 1 22 16.92z"/>
                      </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-white">Información de Contacto</h3>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">Correo Electrónico</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg flex items-center gap-2">
                          <svg class="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none"
                               stroke="currentColor" stroke-width="2">
                              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                              <polyline points="22,6 12,13 2,6"/>
                          </svg>
                          <span class="text-white">{usuario.email}</span>
                      </div>
                  </div>

                  <div class="space-y-2">
                      <div class="text-sm font-medium text-gray-400">Teléfono</div>
                      <div class="p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg flex items-center gap-2">
                          <svg class="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none"
                               stroke="currentColor" stroke-width="2">
                              <path d="M22 16.92V19a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.05 4.18 2 2 0 0 1 4 2h2.09a2 2 0 0 1 2 1.72c.12.9.3 1.78.57 2.63a2 2 0 0 1-.45 2.11L7.1 9.9a16 16 0 0 0 6 6l1.44-1.11a2 2 0 0 1 2.11-.45c.85.27 1.73.45 2.63.57A2 2 0 0 1 22 16.92z"/>
                          </svg>
                          <span class="text-white">{usuario.telefono}</span>
                      </div>
                  </div>
              </div>
          </div>

          <!-- Activity Section -->
          <div class="bg-[#151515]/60 border border-[#1f1f1f]/50 rounded-2xl p-6 shadow-2xl">
              <div class="flex items-center gap-3 mb-6">
                  <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                      <svg class="w-5 h-5 text-purple-400" viewBox="0 0 24 24" fill="none"
                           stroke="currentColor" stroke-width="2">
                          <path d="M12 8v4l3 3"/>
                          <circle cx="12" cy="12" r="10"/>
                      </svg>
                  </div>
                  <h3 class="text-xl font-semibold text-white">Actividad Reciente</h3>
              </div>

              <div class="space-y-3">
                  <div class="flex items-center gap-3 p-3 bg-[#0f0f0f]/30 rounded-lg">
                      <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span class="text-gray-300 text-sm">Último acceso: Hoy, 14:30</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-[#0f0f0f]/30 rounded-lg">
                      <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span class="text-gray-300 text-sm">Perfil actualizado: Hace 2 días</span>
                  </div>
                  <div class="flex items-center gap-3 p-3 bg-[#0f0f0f]/30 rounded-lg">
                      <div class="w-2 h-2 bg-orange-500 rounded-full"></div>
                      <span class="text-gray-300 text-sm">Contraseña cambiada: Hace 1 semana</span>
                  </div>
              </div>
          </div>
      </div>
  </div>
</div>

<!-- Modal de Editar Perfil -->
<EditarProfile
      bind:open={editarProfileOpen}
      handleClose={closeEditProfile}
      usuario={usuario}
      onUsuarioGuardado={handleUsuarioGuardado}
/>

<!-- Modal de Cambiar Contraseña -->
{#if cambiarPasswordOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
       on:click={closeCambiarPassword}>
    <div class="bg-[#151515] border border-[#2a2a2a] rounded-2xl p-8 shadow-2xl max-w-md w-full mx-4 transform animate-scale"
         on:click|stopPropagation>

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <circle cx="12" cy="16" r="1"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-white">Cambiar Contraseña</h3>
        </div>
        <button
          on:click={closeCambiarPassword}
          class="text-gray-400 hover:text-white transition-colors">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Formulario -->
      <div class="space-y-4">
        <!-- Contraseña Actual -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-400">Contraseña Actual</label>
          <input
            type="password"
            bind:value={passwordActual}
            placeholder="Ingresa tu contraseña actual"
            class="w-full p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg text-white
                   placeholder-gray-500 focus:border-blue-500 focus:outline-none transition-colors" />
        </div>

        <!-- Nueva Contraseña -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-400">Nueva Contraseña</label>
          <input
            type="password"
            bind:value={passwordNueva}
            placeholder="Ingresa la nueva contraseña"
            class="w-full p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg text-white
                   placeholder-gray-500 focus:border-blue-500 focus:outline-none transition-colors" />
        </div>

        <!-- Confirmar Contraseña -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-400">Confirmar Contraseña</label>
          <input
            type="password"
            bind:value={passwordConfirmar}
            placeholder="Confirma la nueva contraseña"
            class="w-full p-3 bg-[#0f0f0f]/60 border border-[#2a2a2a] rounded-lg text-white
                   placeholder-gray-500 focus:border-blue-500 focus:outline-none transition-colors" />
        </div>

        <!-- Mensaje de Error -->
        {#if errorPassword}
          <div class="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <svg class="w-5 h-5 text-red-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span class="text-sm text-red-300">{errorPassword}</span>
          </div>
        {/if}

        <!-- Información de seguridad -->
        <div class="flex items-start gap-2 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <div class="text-sm text-blue-300">
            La contraseña debe tener al menos 6 caracteres
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-3 mt-6">
        <button
          on:click={closeCambiarPassword}
          class="flex-1 px-5 py-3 border border-[#2a2a2a] text-gray-300 hover:text-white
                 hover:bg-[#1f1f1f]/50 font-medium rounded-xl transition-all duration-200
                 transform hover:scale-[1.02] active:scale-[0.98]">
          Cancelar
        </button>
        <button
          on:click={handleCambiarPassword}
          class="flex-1 px-5 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700
                 hover:to-blue-600 text-white font-medium rounded-xl transition-all duration-200
                 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40
                 transform hover:scale-[1.02] active:scale-[0.98]">
          Cambiar
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Mensaje de Éxito -->
{#if mostrarMensajeExito}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
       on:click={() => mostrarMensajeExito = false}>
    <div class="bg-[#151515] border border-[#2a2a2a] rounded-2xl p-8 shadow-2xl max-w-md mx-4 transform animate-scale"
         on:click|stopPropagation>
      <div class="flex items-center justify-center mb-4">
        <div class="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
        </div>
      </div>

      <h3 class="text-2xl font-bold text-white text-center mb-2">
        Contraseña Cambiada
      </h3>

      <p class="text-gray-400 text-center mb-6">
        Tu contraseña se ha actualizado exitosamente
      </p>

      <button
        on:click={() => mostrarMensajeExito = false}
        class="w-full px-5 py-3 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600
               text-white font-medium rounded-xl transition-all duration-200 shadow-lg shadow-green-500/25
               hover:shadow-green-500/40 transform hover:scale-[1.02] active:scale-[0.98]">
        Aceptar
      </button>
    </div>
  </div>
{/if}

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