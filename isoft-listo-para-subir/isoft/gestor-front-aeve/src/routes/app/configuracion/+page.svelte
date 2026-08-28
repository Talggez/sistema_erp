<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  // Tipos
  type Usuario = {
    id: string;
    nombre: string;
    email: string;
    rol: 'Administrador' | 'Editor' | 'Visualizador';
    permisos: {
      productos: boolean;
      proveedores: boolean;
      clientes: boolean;
      proyectos: boolean;
      ventas: boolean;
      reportes: boolean;
      graficos: boolean;
    };
    activo: boolean;
    fechaCreacion: string;
  };

  // Estado del tema
  let temaOscuro = true;

  // Cargar tema desde localStorage
  onMount(() => {
    if (browser) {
      const savedTheme = localStorage.getItem('aeve_theme');
      temaOscuro = savedTheme !== 'light';
      aplicarTema();
    }
  });

  // Aplicar tema al documento
  function aplicarTema() {
    if (browser) {
      const root = document.documentElement;
      if (temaOscuro) {
        root.classList.remove('light-theme');
        root.classList.add('dark-theme');
      } else {
        root.classList.remove('dark-theme');
        root.classList.add('light-theme');
      }
      localStorage.setItem('aeve_theme', temaOscuro ? 'dark' : 'light');
    }
  }

  // Toggle tema
  function toggleTema() {
    temaOscuro = !temaOscuro;
    aplicarTema();
  }

  // Configuracion de la empresa
  let empresa = {
    nombre: 'AEVE Gestion',
    rut: '76.XXX.XXX-X',
    direccion: 'Santiago, Chile',
    telefono: '+56 9 XXXX XXXX',
    email: 'contacto@aeve.cl'
  };

  // Modulos del sistema
  let modulos = [
    { nombre: 'Productos', activo: true },
    { nombre: 'Proveedores', activo: true },
    { nombre: 'Clientes', activo: true },
    { nombre: 'Proyectos', activo: true },
    { nombre: 'Ventas', activo: true },
    { nombre: 'Reportes', activo: true },
    { nombre: 'Graficos', activo: true }
  ];

  // Usuarios
  let usuarios: Usuario[] = [
    {
      id: '1',
      nombre: 'Admin Principal',
      email: 'admin@aeve.com',
      rol: 'Administrador',
      permisos: {
        productos: true,
        proveedores: true,
        clientes: true,
        proyectos: true,
        ventas: true,
        reportes: true,
        graficos: true
      },
      activo: true,
      fechaCreacion: '2024-01-15'
    }
  ];

  // Estados UI
  let mensajeExito: string | null = null;
  let guardando = false;
  let mostrarModalUsuario = false;
  let modoUsuario: 'new' | 'edit' = 'new';
  let usuarioAEditar: Usuario | null = null;

  const formularioBaseUsuario: Usuario = {
    id: '',
    nombre: '',
    email: '',
    rol: 'Visualizador',
    permisos: {
      productos: false,
      proveedores: false,
      clientes: false,
      proyectos: false,
      ventas: false,
      reportes: false,
      graficos: false
    },
    activo: true,
    fechaCreacion: ''
  };

  let formularioUsuario: Usuario = { ...formularioBaseUsuario };

  // Permisos predefinidos por rol
  const permisosPorRol = {
    Administrador: {
      productos: true,
      proveedores: true,
      clientes: true,
      proyectos: true,
      ventas: true,
      reportes: true,
      graficos: true
    },
    Editor: {
      productos: true,
      proveedores: true,
      clientes: true,
      proyectos: true,
      ventas: true,
      reportes: true,
      graficos: false
    },
    Visualizador: {
      productos: false,
      proveedores: false,
      clientes: false,
      proyectos: false,
      ventas: false,
      reportes: true,
      graficos: true
    }
  };

  function abrirModalUsuario(modo: 'new' | 'edit', usuario: Usuario | null = null) {
    modoUsuario = modo;
    if (modo === 'edit' && usuario) {
      formularioUsuario = { ...usuario, permisos: { ...usuario.permisos } };
      usuarioAEditar = usuario;
    } else {
      formularioUsuario = {
        ...formularioBaseUsuario,
        permisos: { ...formularioBaseUsuario.permisos },
        id: crypto.randomUUID(),
        fechaCreacion: new Date().toISOString().split('T')[0]
      };
      usuarioAEditar = null;
    }
    mostrarModalUsuario = true;
  }

  function cerrarModalUsuario() {
    mostrarModalUsuario = false;
    usuarioAEditar = null;
  }

  function guardarUsuario() {
    if (!formularioUsuario.nombre || !formularioUsuario.email) {
      return;
    }

    if (modoUsuario === 'edit' && usuarioAEditar) {
      const index = usuarios.findIndex(u => u.id === usuarioAEditar!.id);
      if (index !== -1) {
        usuarios[index] = { ...formularioUsuario };
        usuarios = [...usuarios];
      }
      mensajeExito = 'Usuario actualizado correctamente';
    } else {
      usuarios = [...usuarios, { ...formularioUsuario }];
      mensajeExito = 'Usuario creado correctamente';
    }

    cerrarModalUsuario();
    setTimeout(() => mensajeExito = null, 3000);
  }

  function cambiarRol(rol: 'Administrador' | 'Editor' | 'Visualizador') {
    formularioUsuario.rol = rol;
    formularioUsuario.permisos = { ...permisosPorRol[rol] };
  }

  function eliminarUsuario(id: string) {
    if (confirm('¿Estas seguro de que deseas eliminar este usuario?')) {
      usuarios = usuarios.filter(u => u.id !== id);
      mensajeExito = 'Usuario eliminado correctamente';
      setTimeout(() => mensajeExito = null, 3000);
    }
  }

  function toggleUsuarioActivo(id: string) {
    const index = usuarios.findIndex(u => u.id === id);
    if (index !== -1) {
      usuarios[index].activo = !usuarios[index].activo;
      usuarios = [...usuarios];
    }
  }

  // Guardar configuracion
  async function guardarConfiguracion() {
    guardando = true;
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (browser) {
      localStorage.setItem('aeve_config_empresa', JSON.stringify(empresa));
      localStorage.setItem('aeve_config_modulos', JSON.stringify(modulos));
      localStorage.setItem('aeve_config_usuarios', JSON.stringify(usuarios));
    }

    mensajeExito = 'Configuracion guardada correctamente';
    guardando = false;
    setTimeout(() => mensajeExito = null, 3000);
  }

  // Cargar configuracion guardada
  onMount(() => {
    if (browser) {
      const savedEmpresa = localStorage.getItem('aeve_config_empresa');
      const savedModulos = localStorage.getItem('aeve_config_modulos');
      const savedUsuarios = localStorage.getItem('aeve_config_usuarios');

      if (savedEmpresa) empresa = JSON.parse(savedEmpresa);
      if (savedModulos) modulos = JSON.parse(savedModulos);
      if (savedUsuarios) usuarios = JSON.parse(savedUsuarios);
    }
  });

  // Restablecer valores
  function restablecerValores() {
    if (confirm('¿Estas seguro de restablecer todos los valores?')) {
      temaOscuro = true;
      aplicarTema();
      modulos = modulos.map(m => ({ ...m, activo: true }));
      mensajeExito = 'Valores restablecidos correctamente';
      setTimeout(() => mensajeExito = null, 3000);
    }
  }
</script>

<svelte:head>
  <title>Configuracion - ERP AEVE</title>
</svelte:head>

<!-- Fondo con efectos -->
<div class="relative">
  <div class="pointer-events-none absolute inset-0 -z-10">
    <div class="absolute -top-32 -left-24 w-[520px] h-[520px] rounded-full blur-3xl opacity-[.18]"
         style="background: radial-gradient(50% 50% at 50% 50%, #0ea5e9 0%, transparent 65%);"></div>
    <div class="absolute bottom-10 right-0 w-[520px] h-[520px] rounded-full blur-3xl opacity-[.12]"
         style="background: radial-gradient(50% 50% at 50% 50%, #f97316 0%, transparent 60%);"></div>
  </div>
</div>

<!-- Header -->
<div class="mb-8">
  <h1 class="text-3xl font-bold mb-2" style="color: var(--text-primary);">Configuracion</h1>
  <p style="color: var(--text-secondary);">Administra las preferencias del sistema, usuarios y modulos</p>
</div>

{#if mensajeExito}
  <div class="mb-6 bg-green-500/10 border border-green-500/20 text-green-300 p-4 rounded-xl">
    <div class="flex items-center gap-3">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 6L9 17l-5-5"/>
      </svg>
      <span class="text-sm">{mensajeExito}</span>
    </div>
  </div>
{/if}

<div class="max-w-6xl mx-auto">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

    <!-- APARIENCIA -->
    <div class="rounded-2xl p-6 shadow-2xl transition-colors duration-300" style="background: var(--bg-card); border: 1px solid var(--border-color);">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold" style="color: var(--text-primary);">Apariencia</h2>
      </div>

      <div class="flex items-center justify-between p-4 rounded-xl transition-colors duration-300" style="background: var(--bg-input); border: 1px solid var(--border-color);">
        <div class="flex items-center gap-3">
          {#if temaOscuro}
            <svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          {:else}
            <svg class="w-5 h-5 text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
          {/if}
          <div>
            <p class="text-sm font-medium" style="color: var(--text-primary);">{temaOscuro ? 'Modo Oscuro' : 'Modo Claro'}</p>
            <p class="text-xs" style="color: var(--text-secondary);">{temaOscuro ? 'Interfaz con colores oscuros' : 'Interfaz con colores claros'}</p>
          </div>
        </div>
        <button
          on:click={toggleTema}
          aria-label={temaOscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          class="relative w-14 h-7 rounded-full transition-colors duration-300 {temaOscuro ? 'bg-blue-600' : 'bg-yellow-500'}"
        >
          <div class="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-300 {temaOscuro ? 'translate-x-7' : 'translate-x-0'}"></div>
        </button>
      </div>
    </div>

    <!-- DATOS DE LA EMPRESA -->
    <div class="rounded-2xl p-6 shadow-2xl transition-colors duration-300" style="background: var(--bg-card); border: 1px solid var(--border-color);">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold" style="color: var(--text-primary);">Datos de la Empresa</h2>
      </div>

      <div class="space-y-3">
        <div>
          <label for="empresa-nombre" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Nombre</label>
          <input id="empresa-nombre" type="text" bind:value={empresa.nombre}
            class="w-full px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors duration-300"
            style="background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary);" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="empresa-rut" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">RUT</label>
            <input id="empresa-rut" type="text" bind:value={empresa.rut}
              class="w-full px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors duration-300"
              style="background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary);" />
          </div>
          <div>
            <label for="empresa-telefono" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Telefono</label>
            <input id="empresa-telefono" type="text" bind:value={empresa.telefono}
              class="w-full px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors duration-300"
              style="background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary);" />
          </div>
        </div>
        <div>
          <label for="empresa-email" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Email</label>
          <input id="empresa-email" type="email" bind:value={empresa.email}
            class="w-full px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors duration-300"
            style="background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary);" />
        </div>
      </div>
    </div>

    <!-- MODULOS ACTIVOS -->
    <div class="lg:col-span-2 rounded-2xl p-6 shadow-2xl transition-colors duration-300" style="background: var(--bg-card); border: 1px solid var(--border-color);">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4"/>
            <circle cx="12" cy="12" r="10"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold" style="color: var(--text-primary);">Modulos Activos</h2>
      </div>

      <ul class="divide-y" style="border-color: var(--border-light);">
        {#each modulos as m}
          <li class="flex items-center justify-between py-3">
            <div class="flex items-center gap-3">
              <span class="w-2.5 h-2.5 rounded-full {m.activo ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
              <span class="text-sm" style="color: var(--text-primary);">{m.nombre}</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" class="sr-only peer" bind:checked={m.activo} />
              <div class="w-11 h-6 rounded-full peer peer-checked:bg-blue-600 transition-colors duration-200" style="background: var(--border-color);"></div>
              <div class="absolute left-0.5 top-0.5 h-5 w-5 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
            </label>
          </li>
        {/each}
      </ul>
    </div>

    <!-- GESTION DE USUARIOS -->
    <div class="lg:col-span-2 rounded-2xl p-6 shadow-2xl transition-colors duration-300" style="background: var(--bg-card); border: 1px solid var(--border-color);">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2 class="text-xl font-semibold" style="color: var(--text-primary);">Gestion de Usuarios</h2>
        </div>
        <button
          on:click={() => abrirModalUsuario('new')}
          class="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600
                 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-purple-500/25
                 flex items-center gap-2"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nuevo Usuario
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <th class="text-left py-3 px-4 text-xs font-medium uppercase tracking-wide" style="color: var(--text-secondary);">Usuario</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase tracking-wide" style="color: var(--text-secondary);">Rol</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase tracking-wide" style="color: var(--text-secondary);">Estado</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase tracking-wide" style="color: var(--text-secondary);">Permisos</th>
              <th class="text-left py-3 px-4 text-xs font-medium uppercase tracking-wide" style="color: var(--text-secondary);">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each usuarios as usuario}
              <tr class="transition-colors hover:opacity-80" style="border-bottom: 1px solid var(--border-light);">
                <td class="py-4 px-4">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                      {usuario.nombre.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div class="text-sm font-medium" style="color: var(--text-primary);">{usuario.nombre}</div>
                      <div class="text-xs" style="color: var(--text-secondary);">{usuario.email}</div>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium {
                    usuario.rol === 'Administrador' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                    usuario.rol === 'Editor' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                    'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                  }">
                    {usuario.rol}
                  </span>
                </td>
                <td class="py-4 px-4">
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" checked={usuario.activo} on:change={() => toggleUsuarioActivo(usuario.id)} />
                    <div class="w-11 h-6 rounded-full peer peer-checked:bg-green-600 transition-colors duration-200" style="background: var(--border-color);"></div>
                    <div class="absolute left-0.5 top-0.5 h-5 w-5 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
                  </label>
                </td>
                <td class="py-4 px-4">
                  <div class="flex flex-wrap gap-1">
                    {#if usuario.permisos.productos}
                      <span class="px-2 py-0.5 bg-blue-500/10 text-blue-300 text-xs rounded">Productos</span>
                    {/if}
                    {#if usuario.permisos.ventas}
                      <span class="px-2 py-0.5 bg-green-500/10 text-green-300 text-xs rounded">Ventas</span>
                    {/if}
                    {#if usuario.permisos.clientes}
                      <span class="px-2 py-0.5 bg-purple-500/10 text-purple-300 text-xs rounded">Clientes</span>
                    {/if}
                    {#if Object.values(usuario.permisos).filter(Boolean).length > 3}
                      <span class="px-2 py-0.5 bg-gray-500/10 text-gray-300 text-xs rounded">
                        +{Object.values(usuario.permisos).filter(Boolean).length - 3}
                      </span>
                    {/if}
                  </div>
                </td>
                <td class="py-4 px-4">
                  <div class="flex items-center gap-2">
                    <button
                      on:click={() => abrirModalUsuario('edit', usuario)}
                      class="px-3 py-1.5 bg-amber-600/90 hover:bg-amber-600 text-white text-xs rounded-lg transition-colors"
                    >
                      Editar
                    </button>
                    <button
                      on:click={() => eliminarUsuario(usuario.id)}
                      class="px-3 py-1.5 bg-red-600/90 hover:bg-red-600 text-white text-xs rounded-lg transition-colors"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- FOOTER DE ACCIONES -->
  <div class="mt-6 flex flex-wrap gap-3">
    <button
      on:click={guardarConfiguracion}
      disabled={guardando}
      class="px-5 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600
             text-white font-medium rounded-xl transition-all duration-200 shadow-lg shadow-orange-500/25
             disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
      {#if guardando}
        <svg class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg>
        Guardando...
      {:else}
        Guardar cambios
      {/if}
    </button>
    <button
      on:click={restablecerValores}
      class="px-5 py-3 font-medium rounded-xl transition-all duration-200 hover:opacity-80"
      style="border: 1px solid var(--border-color); color: var(--text-secondary);">
      Restablecer valores
    </button>
  </div>
</div>

<!-- MODAL CREAR/EDITAR USUARIO -->
{#if mostrarModalUsuario}
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
    on:click={cerrarModalUsuario}
    on:keydown={(e) => e.key === 'Escape' && cerrarModalUsuario()}
    role="button"
    tabindex="0"
    aria-label="Cerrar modal"
  ></div>

  <div class="fixed top-0 right-0 bottom-0 w-full max-w-xl z-50 flex flex-col shadow-2xl transition-colors duration-300" style="background: var(--bg-primary); border-left: 1px solid var(--border-color);">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4" style="border-bottom: 1px solid var(--border-color);">
      <h2 class="text-xl font-semibold" style="color: var(--text-primary);">
        {modoUsuario === 'new' ? 'Nuevo Usuario' : 'Editar Usuario'}
      </h2>
      <button
        on:click={cerrarModalUsuario}
        aria-label="Cerrar modal"
        class="w-8 h-8 flex items-center justify-center rounded-lg transition-colors hover:opacity-80"
        style="background: var(--bg-tertiary); color: var(--text-secondary);"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <form on:submit|preventDefault={guardarUsuario} class="space-y-5">
        <div>
          <label for="usuario-nombre" class="block text-sm font-medium mb-2" style="color: var(--text-secondary);">Nombre completo *</label>
          <input id="usuario-nombre" type="text" bind:value={formularioUsuario.nombre} required
            class="w-full px-4 py-2.5 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-colors duration-300"
            style="background: var(--bg-secondary); border: 1px solid var(--border-color); color: var(--text-primary);" />
        </div>

        <div>
          <label for="usuario-email" class="block text-sm font-medium mb-2" style="color: var(--text-secondary);">Correo electronico *</label>
          <input id="usuario-email" type="email" bind:value={formularioUsuario.email} required
            class="w-full px-4 py-2.5 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-colors duration-300"
            style="background: var(--bg-secondary); border: 1px solid var(--border-color); color: var(--text-primary);" />
        </div>

        <div>
          <span class="block text-sm font-medium mb-2" style="color: var(--text-secondary);">Rol *</span>
          <div class="grid grid-cols-3 gap-3">
            <button type="button" on:click={() => cambiarRol('Administrador')}
              class="px-3 py-3 rounded-lg border-2 transition-all text-center {
                formularioUsuario.rol === 'Administrador'
                  ? 'border-red-500 bg-red-500/10 text-red-300'
                  : 'text-gray-400 hover:border-red-500/50'
              }"
              style={formularioUsuario.rol !== 'Administrador' ? 'border-color: var(--border-color); background: var(--bg-secondary);' : ''}>
              <div class="text-sm font-medium">Admin</div>
            </button>
            <button type="button" on:click={() => cambiarRol('Editor')}
              class="px-3 py-3 rounded-lg border-2 transition-all text-center {
                formularioUsuario.rol === 'Editor'
                  ? 'border-blue-500 bg-blue-500/10 text-blue-300'
                  : 'text-gray-400 hover:border-blue-500/50'
              }"
              style={formularioUsuario.rol !== 'Editor' ? 'border-color: var(--border-color); background: var(--bg-secondary);' : ''}>
              <div class="text-sm font-medium">Editor</div>
            </button>
            <button type="button" on:click={() => cambiarRol('Visualizador')}
              class="px-3 py-3 rounded-lg border-2 transition-all text-center {
                formularioUsuario.rol === 'Visualizador'
                  ? 'border-gray-500 bg-gray-500/10 text-gray-300'
                  : 'text-gray-400 hover:border-gray-500/50'
              }"
              style={formularioUsuario.rol !== 'Visualizador' ? 'border-color: var(--border-color); background: var(--bg-secondary);' : ''}>
              <div class="text-sm font-medium">Ver</div>
            </button>
          </div>
        </div>

        <div>
          <span class="block text-sm font-medium mb-3" style="color: var(--text-secondary);">Permisos</span>
          <div class="grid grid-cols-2 gap-2">
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.productos} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Productos</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.proveedores} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Proveedores</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.clientes} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Clientes</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.proyectos} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Proyectos</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.ventas} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Ventas</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.reportes} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Reportes</span>
            </label>
            <label class="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:opacity-80 transition-colors duration-300"
              style="background: var(--bg-secondary); border: 1px solid var(--border-color);">
              <input type="checkbox" bind:checked={formularioUsuario.permisos.graficos} class="w-4 h-4 text-purple-600 bg-transparent border-gray-600 rounded" />
              <span class="text-sm capitalize" style="color: var(--text-secondary);">Graficos</span>
            </label>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4" style="border-top: 1px solid var(--border-color);">
          <button type="button" on:click={cerrarModalUsuario}
            class="px-4 py-2 rounded-lg transition-colors hover:opacity-80"
            style="background: var(--bg-tertiary); color: var(--text-secondary);">
            Cancelar
          </button>
          <button type="submit"
            class="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white rounded-lg transition-all duration-200">
            {modoUsuario === 'new' ? 'Crear Usuario' : 'Guardar'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
