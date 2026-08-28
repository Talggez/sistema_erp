<script>
    import { onMount } from "svelte";
    import { fade, fly, scale } from "svelte/transition";

    // Estados de la aplicación
    let productos = [];
    let carrito = new Map();
    let busqueda = "";
    let cargando = true;
    let error = null;
    let tipoVenta = "neto";
    let procesandoVenta = false;

    // Estados para tipo de documento
    let tipoDocumento = "boleta"; // 'boleta' o 'factura'
    let clienteRUT = "";
    let clienteNombre = "";
    let mostrarDatosCliente = false;

    // Estados para el historial de ventas
    let mostrarHistorial = false;
    let ventas = [];
    let cargandoVentas = false;
    let busquedaVentas = "";
    let fechaFiltro = "";
    let filtroTipoDoc = "todos";

    // Estados para modal de error
    let mostrarModalError = false;
    let mensajeError = "";
    let detalleError = "";

    // Función para obtener productos de la API
    const obtenerProductos = async () => {
        try {
            cargando = true;
            error = null;
            const response = await fetch("http://localhost:5000/productos");

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            // La API devuelve un array directamente
            productos = Array.isArray(data) ? data : (data.data || []);
        } catch (err) {
            error = err.message;
            console.error("Error al obtener productos:", err);
        } finally {
            cargando = false;
        }
    };

    // Función para obtener historial de ventas
    const obtenerVentas = async () => {
        try {
            cargandoVentas = true;
            const response = await fetch("http://localhost:5000/mostrar-ventas");

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            ventas = data.data || [];
        } catch (err) {
            console.error("Error al obtener ventas:", err);
            alert("Error al cargar el historial de ventas");
        } finally {
            cargandoVentas = false;
        }
    };

    // Función para eliminar venta
    const eliminarVenta = async (venta) => {
        const tipoDoc = venta.tipo_documento === 'factura' ? 'Factura' : 'Boleta';
        const confirmar = confirm(
            `¿Estás seguro de eliminar la ${tipoDoc} #${venta.n_venta}?\n\n` +
            `Fecha: ${formatearFecha(venta.fecha_venta)}\n` +
            `Items: ${venta.quantity}\n` +
            `Total: ${formatearPrecio(venta.total)}\n\n` +
            `Esta acción restaurará el stock de los productos.`
        );

        if (!confirmar) return;

        try {
            const response = await fetch(`http://localhost:5000/ventas/${venta.id}`, {
                method: "DELETE"
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Error al eliminar venta");
            }

            const result = await response.json();
            alert(result.message);
            await obtenerVentas();
            await obtenerProductos();
        } catch (err) {
            console.error("Error:", err);
            mostrarError("Error al eliminar la venta", err.message);
        }
    };

    // Función para mostrar modal de error
    const mostrarError = (mensaje, detalle = "") => {
        mensajeError = mensaje;
        detalleError = detalle;
        mostrarModalError = true;
    };

    const cerrarModalError = () => {
        mostrarModalError = false;
        mensajeError = "";
        detalleError = "";
    };

    // Validar formato RUT chileno
    const validarRUT = (rut) => {
        const rutLimpio = rut.replace(/\./g, '').replace(/-/g, '').toUpperCase();
        const regex = /^\d{7,8}[0-9K]$/;
        return regex.test(rutLimpio);
    };

    // Formatear RUT mientras se escribe
    const formatearRUTInput = (e) => {
        let value = e.target.value.replace(/\./g, '').replace(/-/g, '').toUpperCase();

        if (value.length > 1) {
            const cuerpo = value.slice(0, -1);
            const dv = value.slice(-1);

            // Formatear con puntos
            let rutFormateado = '';
            for (let i = cuerpo.length - 1, j = 0; i >= 0; i--, j++) {
                if (j > 0 && j % 3 === 0) rutFormateado = '.' + rutFormateado;
                rutFormateado = cuerpo[i] + rutFormateado;
            }

            value = rutFormateado + '-' + dv;
        }

        e.target.value = value;
        clienteRUT = value;
    };

    // Cargar productos al montar el componente
    onMount(() => {
        obtenerProductos();
    });

    // Lógica reactiva
    $: productosFiltrados = productos.filter(
        (producto) =>
            producto.nombre?.toLowerCase().includes(busqueda.toLowerCase()) ||
            producto.codigo_ska?.toLowerCase().includes(busqueda.toLowerCase()),
    );

    $: ventasFiltradas = ventas.filter(venta => {
        const cumpleBusqueda = !busquedaVentas ||
            venta.n_venta.toString().includes(busquedaVentas) ||
            venta.user_name?.toLowerCase().includes(busquedaVentas.toLowerCase()) ||
            venta.cliente_nombre?.toLowerCase().includes(busquedaVentas.toLowerCase());

        let cumpleFecha = true;
        if (fechaFiltro && fechaFiltro.length === 10) {
            const [day, month, year] = fechaFiltro.split('/');
            if (day && month && year) {
                const fechaBusqueda = `${year}-${month}-${day}`;
                cumpleFecha = venta.fecha_venta.startsWith(fechaBusqueda);
            }
        }

        const cumpleTipo = filtroTipoDoc === 'todos' || venta.tipo_documento === filtroTipoDoc;

        return cumpleBusqueda && cumpleFecha && cumpleTipo;
    });

    $: itemsDelCarrito = Array.from(carrito.values());

    $: totalPedido = itemsDelCarrito.reduce((total, item) => {
        const precio = tipoVenta === "bruto" ? item.precio_bruto : item.precio_neto;
        return total + (precio || 0) * item.cantidad;
    }, 0);

    $: cantidadTotal = itemsDelCarrito.reduce(
        (total, item) => total + item.cantidad, 0
    );

    // Mostrar automáticamente campos de cliente para facturas
    $: {
        if (tipoDocumento === 'factura') {
            mostrarDatosCliente = true;
        } else {
            mostrarDatosCliente = false;
            clienteRUT = "";
            clienteNombre = "";
        }
    }

    // Funciones del carrito
    const agregarAlCarrito = (producto) => {
        if (producto.unidades <= 0) return;

        if (carrito.has(producto.id)) {
            const item = carrito.get(producto.id);
            if (item.cantidad < producto.unidades) {
                item.cantidad++;
            }
        } else {
            carrito.set(producto.id, { ...producto, cantidad: 1 });
        }
        carrito = carrito;
    };

    const actualizarCantidad = (productoId, nuevaCantidad) => {
        if (carrito.has(productoId)) {
            const item = carrito.get(productoId);
            const producto = productos.find((p) => p.id === productoId);

            nuevaCantidad = parseInt(nuevaCantidad) || 0;

            if (nuevaCantidad <= 0) {
                carrito.delete(productoId);
            } else if (nuevaCantidad <= producto.unidades) {
                item.cantidad = nuevaCantidad;
            } else {
                item.cantidad = producto.unidades;
            }
            carrito = carrito;
        }
    };

    const incrementarCantidad = (productoId) => {
        if (carrito.has(productoId)) {
            const item = carrito.get(productoId);
            const producto = productos.find((p) => p.id === productoId);
            if (item.cantidad < producto.unidades) {
                item.cantidad++;
                carrito = carrito;
            }
        }
    };

    const decrementarCantidad = (productoId) => {
        if (carrito.has(productoId)) {
            const item = carrito.get(productoId);
            item.cantidad > 1 ? item.cantidad-- : carrito.delete(productoId);
            carrito = carrito;
        }
    };

    const eliminarDelCarrito = (productoId) => {
        carrito.delete(productoId);
        carrito = carrito;
    };

    const limpiarCarrito = () => {
        carrito.clear();
        carrito = carrito;
        clienteRUT = "";
        clienteNombre = "";
    };

    const procesarPedido = async () => {
        if (itemsDelCarrito.length === 0) {
            alert("El carrito está vacío");
            return;
        }

        // Validar datos de factura según normativa SII
        if (tipoDocumento === 'factura') {
            if (!clienteRUT || !clienteNombre) {
                alert("Las facturas requieren RUT y nombre del cliente según normativa SII");
                return;
            }

            if (!validarRUT(clienteRUT)) {
                alert("El formato del RUT es inválido. Use formato XX.XXX.XXX-X");
                return;
            }

            if (clienteNombre.trim().length < 3) {
                alert("El nombre del cliente debe tener al menos 3 caracteres");
                return;
            }
        }

        procesandoVenta = true;
        const numeroVenta = Date.now().toString();

        try {
            // Primero, buscar o crear el cliente
            let clienteId = 1; // Cliente por defecto para boletas

            if (tipoDocumento === 'factura') {
                // Buscar cliente por RUT
                const rutLimpio = clienteRUT.replace(/\./g, '').replace(/-/g, '').toUpperCase();
                const clientesResponse = await fetch("http://localhost:5000/clientes");

                if (clientesResponse.ok) {
                    const clientes = await clientesResponse.json();
                    const clienteExistente = clientes.find(c =>
                        c.rut.replace(/\./g, '').replace(/-/g, '').toUpperCase() === rutLimpio
                    );

                    if (clienteExistente) {
                        clienteId = clienteExistente.id;
                    } else {
                        // Crear nuevo cliente
                        const nuevoClienteResponse = await fetch("http://localhost:5000/clientes", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                nombre: clienteNombre.split(' ')[0] || clienteNombre,
                                apellidos: clienteNombre.split(' ').slice(1).join(' ') || '',
                                rut: clienteRUT,
                                razon_social: clienteNombre,
                                tipo_cliente_id: 1
                            })
                        });

                        if (nuevoClienteResponse.ok) {
                            const nuevoCliente = await nuevoClienteResponse.json();
                            clienteId = nuevoCliente.id;
                        } else {
                            const errorData = await nuevoClienteResponse.json().catch(() => ({}));
                            throw new Error(errorData.detail || "Error al crear cliente");
                        }
                    }
                }
            }

            // Preparar lista de detalles
            const detalles = itemsDelCarrito.map(item => ({
                id_producto: item.id,
                cantidad_producto: item.cantidad
            }));

            // Preparar datos de la venta según el modelo VentaCreate
            const ventaData = {
                n_documento: numeroVenta,
                cliente: clienteId,
                estado_venta: "Completada",
                tipo_pago: "Efectivo",
                canal_venta: "POS",
                tipo_dte: tipoDocumento,
                detalles: detalles
            };

            const response = await fetch("http://localhost:5000/ventas", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(ventaData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Error al crear la venta");
            }

            const result = await response.json();

            // Calcular total de la venta
            const total = itemsDelCarrito.reduce((sum, item) => {
                const precio = tipoVenta === "bruto" ? item.precio_bruto : item.precio_neto;
                return sum + (precio * item.cantidad);
            }, 0) * 1.19;

            mostrarModalExito(
                numeroVenta,
                total,
                tipoDocumento,
                tipoDocumento === 'factura' ? clienteNombre : null
            );
            limpiarCarrito();
            await obtenerProductos();

        } catch (err) {
            console.error("Error al procesar pedido:", err);
            mostrarError("Error al procesar el pedido", err.message);
        } finally {
            procesandoVenta = false;
        }
    };

    const mostrarModalExito = (numeroVenta, total, tipo, clienteNombre = null) => {
        const modal = document.getElementById('modal-exito');
        document.getElementById('modal-tipo-doc').textContent = tipo === 'factura' ? 'Factura' : 'Boleta';
        document.getElementById('modal-numero-venta').textContent = numeroVenta;
        document.getElementById('modal-total-venta').textContent = formatearPrecio(total);

        const clienteInfo = document.getElementById('modal-cliente-info');
        if (tipo === 'factura' && clienteNombre) {
            clienteInfo.textContent = `Cliente: ${clienteNombre}`;
            clienteInfo.classList.remove('hidden');
        } else {
            clienteInfo.classList.add('hidden');
        }

        modal.classList.remove('hidden');
    };

    const cerrarModalExito = () => {
        const modal = document.getElementById('modal-exito');
        modal.classList.add('hidden');
    };

    const toggleHistorial = async () => {
        mostrarHistorial = !mostrarHistorial;
        if (mostrarHistorial && ventas.length === 0) {
            await obtenerVentas();
        }
    };

    const formatearPrecio = (precio) => {
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: "CLP",
            minimumFractionDigits: 0,
            currencyDisplay: "symbol"
        }).format(precio || 0).replace('CLP', '').trim();
    };

    const formatearFecha = (fecha) => {
        const date = new Date(fecha);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        return `${day}/${month}/${year} ${hours}:${minutes}`;
    };

    const obtenerPrecioVenta = (producto) => {
        return tipoVenta === "bruto" ? producto.precio_bruto : producto.precio_neto;
    };
</script>

<svelte:head>
    <title>Ventas - AEVE</title>
</svelte:head>

<div class="flex w-full gap-6 text-gray-200">
    <!-- Columna Central -->
    <main class="flex-1 flex flex-col gap-6">
        <!-- Header -->
        <div class="mb-6">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h1 class="text-2xl font-semibold text-white mb-1">Punto de Venta</h1>
                    <p class="text-gray-400 text-sm">Gestión de ventas según normativa SII</p>
                </div>

                <div class="flex items-center gap-3">
                    <button
                        on:click={toggleHistorial}
                        class="px-4 py-2 rounded-lg text-sm font-medium transition-all {mostrarHistorial ? 'bg-orange-600 text-white' : 'bg-[#1f1f1f]/50 text-gray-400 hover:text-white'} flex items-center gap-2"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        {mostrarHistorial ? 'Ocultar' : 'Ver'} Historial
                    </button>

                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-400">Precio:</span>
                        <select
                            bind:value={tipoVenta}
                            class="px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
                        >
                            <option value="neto">Neto</option>
                            <option value="bruto">Bruto</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Historial de Ventas -->
        {#if mostrarHistorial}
            <div
                class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 shadow-xl"
                transition:fly={{ y: -20, duration: 300 }}
            >
                <div class="flex justify-between items-center mb-6">
                    <div class="flex items-center gap-3">
                        <h3 class="text-lg font-semibold text-white">Historial de Ventas</h3>
                        {#if !cargandoVentas}
                            <span class="text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded-full border border-orange-500/30">
                                {ventasFiltradas.length} ventas
                            </span>
                        {/if}
                    </div>

                    <div class="flex items-center gap-3">
                        <select
                            bind:value={filtroTipoDoc}
                            class="px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
                        >
                            <option value="todos">Todos</option>
                            <option value="boleta">Boletas</option>
                            <option value="factura">Facturas</option>
                        </select>
                        <input
                            type="text"
                            placeholder="DD/MM/YYYY"
                            bind:value={fechaFiltro}
                            on:input={(e) => {
                                let value = e.target?.value.replace(/\D/g, '') || '';
                                if (value.length >= 2) value = value.slice(0,2) + '/' + value.slice(2);
                                if (value.length >= 5) value = value.slice(0,5) + '/' + value.slice(5,9);
                                if (e.target) e.target.value = value;
                                fechaFiltro = value;
                            }}
                            maxlength="10"
                            class="px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all w-32"
                        />
                        <input
                            type="text"
                            placeholder="Buscar..."
                            bind:value={busquedaVentas}
                            class="w-64 px-3 py-2 bg-[#151515]/60 border border-[#2a2a2a] rounded-lg text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 transition-all"
                        />
                        <button
                            on:click={obtenerVentas}
                            disabled={cargandoVentas}
                            class="px-4 py-2 bg-orange-600/90 hover:bg-orange-600 disabled:bg-gray-600 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
                        >
                            <svg class="w-4 h-4 {cargandoVentas ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            Actualizar
                        </button>
                    </div>
                </div>

                {#if cargandoVentas}
                    <div class="flex justify-center py-12">
                        <div class="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                {:else if ventasFiltradas.length === 0}
                    <div class="text-center py-12">
                        <p class="text-gray-400">No hay ventas registradas</p>
                    </div>
                {:else}
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="border-b border-[#1f1f1f]/50">
                                    <th class="text-left p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Tipo</span>
                                    </th>
                                    <th class="text-left p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">N° Venta</span>
                                    </th>
                                    <th class="text-left p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Fecha</span>
                                    </th>
                                    <th class="text-left p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Cliente</span>
                                    </th>
                                    <th class="text-right p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Total</span>
                                    </th>
                                    <th class="text-right p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Acciones</span>
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each ventasFiltradas as venta (venta.id)}
                                    <tr class="border-b border-[#1f1f1f]/30 hover:bg-[#1a1a1a]/50 transition-colors group">
                                        <td class="p-4">
                                            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {venta.tipo_documento === 'factura' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'bg-green-500/20 text-green-300 border border-green-500/30'}">
                                                {venta.tipo_documento === 'factura' ? 'Factura' : 'Boleta'}
                                            </span>
                                        </td>
                                        <td class="p-4">
                                            <span class="font-mono text-sm text-orange-400">#{venta.n_venta}</span>
                                        </td>
                                        <td class="p-4 text-sm text-gray-300">
                                            {formatearFecha(venta.fecha_venta)}
                                        </td>
                                        <td class="p-4 text-sm text-gray-300">
                                            {#if venta.cliente_nombre}
                                                {venta.cliente_nombre}
                                            {:else}
                                                <span class="text-gray-500">-</span>
                                            {/if}
                                        </td>
                                        <td class="p-4 text-right font-semibold text-white">
                                            {formatearPrecio(venta.total)}
                                        </td>
                                        <td class="p-4 text-right">
                                            <button
                                                on:click={() => eliminarVenta(venta)}
                                                class="flex items-center gap-2 px-3 py-1.5 bg-red-600/90 hover:bg-red-600 text-white text-sm rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 ml-auto"
                                                title="Eliminar venta"
                                                aria-label="Eliminar venta"
                                            >
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                                                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                                </svg>
                                                Eliminar
                                            </button>
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}
            </div>
        {/if}

        <!-- Panel de Selección de Productos -->
        <div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl p-6 flex-1 shadow-xl">
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center gap-3">
                    <h3 class="text-lg font-semibold text-white">Catálogo de Productos</h3>
                    {#if error}
                        <span class="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded-full border border-red-500/30">
                            API Offline
                        </span>
                    {:else if !cargando}
                        <span class="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full border border-green-500/30">
                            {productos.length} productos
                        </span>
                    {/if}
                </div>

                <div class="flex items-center gap-3">
                    <div class="relative">
                        <input
                            type="text"
                            placeholder="Buscar por nombre o código..."
                            bind:value={busqueda}
                            class="w-80 pl-10 pr-4 py-3 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200"
                        />
                        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>

                    <button
                        on:click={obtenerProductos}
                        disabled={cargando}
                        class="px-4 py-3 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white rounded-lg transition-all duration-200 flex items-center gap-2"
                    >
                        <svg class="w-4 h-4 {cargando ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        {cargando ? "Cargando..." : "Actualizar"}
                    </button>
                </div>
            </div>

            {#if cargando}
                <div class="flex items-center justify-center py-20">
                    <div class="flex flex-col items-center gap-4">
                        <div class="w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                        <p class="text-gray-400">Cargando productos...</p>
                    </div>
                </div>
            {:else if error && productos.length === 0}
                <div class="flex items-center justify-center py-20">
                    <div class="text-center">
                        <div class="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold text-white mb-2">Error de conexión</h3>
                        <p class="text-gray-400 mb-4">No se pudieron cargar los productos desde la API</p>
                        <button
                            on:click={obtenerProductos}
                            class="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
                        >
                            Reintentar
                        </button>
                    </div>
                </div>
            {:else}
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
                    {#each productosFiltrados as producto (producto.id)}
                        {@const enCarrito = carrito.get(producto.id)}
                        {@const sinStock = producto.unidades <= 0}
                        {@const stockBajo = producto.unidades <= 5 && producto.unidades > 0}

                        <button
                            on:click={() => agregarAlCarrito(producto)}
                            disabled={sinStock}
                            class="relative group text-center bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-4 rounded-xl hover:from-[#2a2a2a] hover:to-[#1f1f1f] transition-all duration-300 border-2 {enCarrito
                                ? 'border-orange-500 shadow-lg shadow-orange-500/20'
                                : sinStock
                                  ? 'border-red-500/30'
                                  : 'border-transparent hover:border-orange-500/50'} aspect-[3/4] flex flex-col justify-between overflow-hidden {sinStock
                                ? 'opacity-50 cursor-not-allowed'
                                : ''}"
                            in:fly={{ y: 20, duration: 300, delay: producto.id * 50 }}
                        >
                            {#if enCarrito}
                                <div
                                    transition:scale={{ duration: 200 }}
                                    class="absolute top-2 right-2 bg-orange-500 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center z-10 shadow-lg"
                                >
                                    {enCarrito.cantidad}
                                </div>
                            {/if}

                            <div class="absolute top-2 left-2 z-10">
                                {#if sinStock}
                                    <span class="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium">Sin Stock</span>
                                {:else if stockBajo}
                                    <span class="bg-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">Stock Bajo</span>
                                {/if}
                            </div>

                            <div class="flex-1 flex flex-col justify-center transition-opacity duration-200">
                                {#if producto.imagen_url}
                                    <img
                                        src="http://localhost:5000{producto.imagen_url}"
                                        alt={producto.nombre}
                                        class="w-12 h-12 rounded-lg mx-auto mb-3 object-cover"
                                    />
                                {:else}
                                    <div class="w-12 h-12 bg-gradient-to-br from-orange-500/20 to-orange-600/20 rounded-lg mx-auto mb-3 flex items-center justify-center">
                                        <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                                        </svg>
                                    </div>
                                {/if}

                                <h4 class="font-semibold text-white text-sm mb-1 line-clamp-2">
                                    {producto.nombre}
                                </h4>
                                <p class="text-xs text-gray-500 mb-2 font-mono">
                                    {producto.codigo_ska || producto.codigo || ''}
                                </p>

                                <div class="space-y-1">
                                    <div class="text-lg font-bold text-orange-400">
                                        {formatearPrecio(obtenerPrecioVenta(producto))}
                                    </div>
                                    <div class="text-xs text-gray-400">
                                        Stock: <span class="font-mono {stockBajo ? 'text-orange-400' : 'text-green-400'}">{producto.unidades}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="absolute inset-0 bg-gradient-to-t from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none"></div>
                        </button>
                    {/each}
                </div>

                {#if productosFiltrados.length === 0 && !cargando}
                    <div class="text-center py-20">
                        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-lg font-semibold text-white mb-2">No se encontraron productos</h3>
                        <p class="text-gray-400">Intenta modificar tu búsqueda</p>
                    </div>
                {/if}
            {/if}
        </div>
    </main>

    <!-- Panel del Carrito -->
    <aside class="w-96 flex flex-col gap-4">
        <!-- Selector de tipo de documento -->
        <div class="bg-gradient-to-br from-[#0f0f0f] to-[#1a1a1a] p-4 rounded-xl border border-[#1f1f1f] shadow-2xl">
            <div class="flex items-center gap-3 mb-3">
                <div class="w-1 h-6 bg-gradient-to-b from-blue-500 to-blue-600 rounded-full"></div>
                <h3 class="text-sm font-semibold text-white">Tipo de Documento</h3>
            </div>

            <div class="grid grid-cols-2 gap-2 mb-3">
                <button
                    on:click={() => tipoDocumento = 'boleta'}
                    class="px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 {tipoDocumento === 'boleta'
                        ? 'bg-green-600 text-white shadow-lg'
                        : 'bg-[#1f1f1f] text-gray-400 hover:bg-[#2a2a2a]'}"
                >
                    Boleta
                </button>
                <button
                    on:click={() => tipoDocumento = 'factura'}
                    class="px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 {tipoDocumento === 'factura'
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-[#1f1f1f] text-gray-400 hover:bg-[#2a2a2a]'}"
                >
                    Factura
                </button>
            </div>

            {#if tipoDocumento === 'factura'}
                <div class="space-y-3 pt-3 border-t border-[#2f2f2f]" transition:fly={{ y: -10, duration: 200 }}>
                    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                        <div class="flex items-start gap-2">
                            <svg class="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <p class="text-xs text-blue-300">
                                Las facturas requieren RUT y nombre del cliente según normativa SII
                            </p>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs text-gray-400 mb-1.5">RUT del Cliente *</label>
                        <input
                            type="text"
                            placeholder="12.345.678-9"
                            bind:value={clienteRUT}
                            on:input={formatearRUTInput}
                            maxlength="12"
                            class="w-full px-3 py-2 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label class="block text-xs text-gray-400 mb-1.5">Nombre del Cliente *</label>
                        <input
                            type="text"
                            placeholder="Nombre completo o razón social"
                            bind:value={clienteNombre}
                            class="w-full px-3 py-2 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
            {/if}
        </div>

        <!-- Botón de procesar pedido -->
        <button
            on:click={procesarPedido}
            disabled={itemsDelCarrito.length === 0 || procesandoVenta}
            class="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 disabled:from-gray-600 disabled:to-gray-500 text-white font-bold py-4 rounded-xl transition-all duration-200 shadow-lg disabled:shadow-none disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
            {#if procesandoVenta}
                <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Procesando...
            {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Emitir {tipoDocumento === 'factura' ? 'Factura' : 'Boleta'} {cantidadTotal > 0 ? `(${cantidadTotal})` : ""}
            {/if}
        </button>

        <!-- Panel del carrito -->
        <div class="bg-gradient-to-br from-[#0f0f0f] to-[#1a1a1a] rounded-xl flex-1 border border-[#1f1f1f] shadow-2xl flex flex-col">
            <!-- Header del carrito -->
            <div class="p-6 border-b border-[#1f1f1f]">
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-3">
                        <div class="w-1 h-8 bg-gradient-to-b from-orange-500 to-orange-600 rounded-full"></div>
                        <h3 class="text-xl font-bold text-white">Carrito</h3>
                        {#if cantidadTotal > 0}
                            <span class="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded-full border border-orange-500/30">
                                {cantidadTotal} items
                            </span>
                        {/if}
                    </div>
                    {#if itemsDelCarrito.length > 0}
                        <button
                            on:click={limpiarCarrito}
                            class="text-red-400 hover:text-red-300 text-sm transition-colors"
                        >
                            Limpiar
                        </button>
                    {/if}
                </div>
            </div>

            <!-- Lista de productos en carrito -->
            <div class="flex-1 overflow-y-auto p-6">
                {#if itemsDelCarrito.length > 0}
                    <div class="space-y-3">
                        {#each itemsDelCarrito as item (item.id)}
                            {@const precio = obtenerPrecioVenta(item)}
                            <div
                                class="bg-[#1f1f1f] p-4 rounded-lg border border-[#2f2f2f] hover:border-[#3f3f3f] transition-all duration-200"
                                in:fly={{ x: -20, duration: 200 }}
                                out:fly={{ x: 20, duration: 200 }}
                            >
                                <div class="flex items-start gap-3">
                                    <div class="flex-1 min-w-0">
                                        <h4 class="font-semibold text-white text-sm truncate">
                                            {item.nombre}
                                        </h4>
                                        <p class="text-xs text-gray-500 font-mono mb-2">
                                            {item.codigo}
                                        </p>
                                        <div class="text-xs text-gray-400">
                                            {formatearPrecio(precio)} × {item.cantidad}
                                            = <span class="font-bold text-orange-400">{formatearPrecio(precio * item.cantidad)}</span>
                                        </div>
                                    </div>

                                    <div class="flex flex-col gap-2">
                                        <!-- Controles de cantidad -->
                                        <div class="flex items-center bg-[#0f0f0f] rounded-md overflow-hidden">
                                            <button
                                                on:click={() => decrementarCantidad(item.id)}
                                                class="w-8 h-8 flex items-center justify-center hover:bg-[#2f2f2f] transition-colors text-gray-400 hover:text-white"
                                            >
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                                                </svg>
                                            </button>
                                            <input
                                                type="number"
                                                min="1"
                                                max={item.unidades}
                                                value={item.cantidad}
                                                on:input={(e) => actualizarCantidad(item.id, e.target.value)}
                                                class="w-12 text-center text-sm font-mono text-white bg-[#1a1a1a] leading-8 border-none focus:outline-none focus:ring-2 focus:ring-orange-500"
                                            />
                                            <button
                                                on:click={() => incrementarCantidad(item.id)}
                                                disabled={item.cantidad >= item.unidades}
                                                class="w-8 h-8 flex items-center justify-center hover:bg-[#2f2f2f] transition-colors text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                                                </svg>
                                            </button>
                                        </div>

                                        <!-- Botón eliminar -->
                                        <button
                                            on:click={() => eliminarDelCarrito(item.id)}
                                            class="w-full h-8 flex items-center justify-center text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-all duration-200"
                                            title="Eliminar del carrito"
                                        >
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="text-center py-16">
                        <div class="w-16 h-16 bg-gray-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5M17 13v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6"></path>
                            </svg>
                        </div>
                        <h4 class="text-lg font-semibold text-gray-400 mb-2">Carrito vacío</h4>
                        <p class="text-gray-500 text-sm">Selecciona productos para agregar al carrito</p>
                    </div>
                {/if}
            </div>

            <!-- Total del pedido -->
            {#if totalPedido > 0}
                <div class="p-6 border-t border-[#1f1f1f] bg-gradient-to-r from-[#0a0a0a] to-[#1a1a1a]">
                    <div class="space-y-2 mb-3">
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-400">Subtotal ({tipoVenta}):</span>
                            <span class="text-white font-semibold">{formatearPrecio(totalPedido)}</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-400">IVA (19%):</span>
                            <span class="text-white font-semibold">{formatearPrecio(totalPedido * 0.19)}</span>
                        </div>
                    </div>
                    <div class="pt-3 border-t border-[#2f2f2f]">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-400 text-sm">Total:</span>
                            <span class="font-bold text-white text-2xl">{formatearPrecio(totalPedido * 1.19)}</span>
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    </aside>
</div>

<!-- Modal de Éxito -->
<div id="modal-exito" class="hidden fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50" transition:fade>
    <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl" transition:scale>
        <!-- Icono de éxito -->
        <div class="flex justify-center mb-6">
            <div class="w-20 h-20 bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-full flex items-center justify-center">
                <svg class="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
        </div>

        <!-- Contenido -->
        <div class="text-center mb-6">
            <h3 class="text-2xl font-bold text-white mb-1"><span id="modal-tipo-doc">Venta</span> Procesada</h3>
            <p class="text-gray-400 mb-4">El documento se ha registrado exitosamente</p>

            <div class="bg-[#1f1f1f] rounded-lg p-4 mb-2">
                <p class="text-sm text-gray-400 mb-1">Número de Documento</p>
                <p class="text-2xl font-bold text-orange-400 font-mono">#<span id="modal-numero-venta"></span></p>
            </div>

            <div id="modal-cliente-info" class="bg-[#1f1f1f] rounded-lg p-3 mb-2 text-sm text-gray-300 hidden"></div>

            <div class="bg-[#1f1f1f] rounded-lg p-4">
                <p class="text-sm text-gray-400 mb-1">Total</p>
                <p class="text-2xl font-bold text-white" id="modal-total-venta"></p>
            </div>
        </div>

        <!-- Botón cerrar -->
        <button
            on:click={cerrarModalExito}
            class="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-bold py-3 rounded-lg transition-all duration-200"
        >
            Aceptar
        </button>
    </div>
</div>

<!-- Modal de Error -->
{#if mostrarModalError}
    <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50" transition:fade>
        <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl" transition:scale>
            <!-- Icono de error -->
            <div class="flex justify-center mb-6">
                <div class="w-20 h-20 bg-gradient-to-br from-red-500/20 to-red-600/20 rounded-full flex items-center justify-center">
                    <svg class="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                </div>
            </div>

            <!-- Contenido -->
            <div class="text-center mb-6">
                <h3 class="text-2xl font-bold text-white mb-2">Error</h3>
                <p class="text-gray-300 mb-4">{mensajeError}</p>

                {#if detalleError}
                    <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                        <p class="text-sm text-red-300 font-mono">{detalleError}</p>
                    </div>
                {/if}
            </div>

            <!-- Botón cerrar -->
            <button
                on:click={cerrarModalError}
                class="w-full bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600 text-white font-bold py-3 rounded-lg transition-all duration-200"
            >
                Cerrar
            </button>
        </div>
    </div>
{/if}

<style>
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    input[type="number"] {
        -moz-appearance: textfield;
    }
</style>
