<script>
    import { onMount } from "svelte";
    import { fly, fade, scale } from "svelte/transition";

    // Estados principales
    let tabActiva = "ventas"; // 'ventas' o 'proyectos'
    let cargando = true;
    let error = null;

    // Datos de ventas
    let ventas = [];
    let proyectos = [];

    // Filtros
    let busqueda = "";
    let fechaInicio = "";
    let fechaFin = "";
    let filtroTipoDoc = "todos"; // 'todos', 'boleta', 'factura'

    // Estados para modales
    let mostrarModalNuevoProyecto = false;
    let mostrarModalCotizacion = false;
    let mostrarModalAvances = false;
    let mostrarModalGastos = false;
    let proyectoSeleccionado = null;

    // Formulario de nuevo proyecto
    let nuevoProyecto = {
        nombre: "",
        cliente: "",
        descripcion: "",
        fechaInicio: new Date().toISOString().split('T')[0],
        fechaFin: "",
    };

    // Cotización
    let cotizacion = {
        items: [],
        observaciones: ""
    };

    // Avances
    let nuevoAvance = {
        descripcion: "",
        porcentaje: 0
    };

    // Gastos
    let nuevoGasto = {
        descripcion: "",
        monto: 0,
        categoria: "materiales",
        fecha: new Date().toISOString().split('T')[0]
    };

    // Obtener datos desde API
    const obtenerVentas = async () => {
        try {
            cargando = true;
            error = null;
            const response = await fetch("http://localhost:5000/mostrar-ventas");

            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);

            const data = await response.json();
            ventas = data.data || [];
        } catch (err) {
            error = err.message;
            console.error("Error al obtener ventas:", err);
            ventas = [];
        } finally {
            cargando = false;
        }
    };

    const obtenerProyectos = async () => {
        try {
            // Cargar proyectos desde localStorage
            const proyectosGuardados = localStorage.getItem('proyectos_aeve');
            if (proyectosGuardados) {
                proyectos = JSON.parse(proyectosGuardados);
            } else {
                // Datos de ejemplo iniciales
                proyectos = [
                    {
                        id: 1,
                        nombre: "Desarrollo Web AEVE",
                        cliente: "Cliente A",
                        estado: "Activo",
                        fechaInicio: "2025-01-15",
                        fechaFin: "2025-06-30",
                        presupuesto: 2500000,
                        gastado: 1200000,
                        progreso: 45,
                        descripcion: "Desarrollo de plataforma web completa para gestión empresarial",
                        tareas: 15,
                        tareasCompletadas: 7
                    },
                    {
                        id: 2,
                        nombre: "App Mobile Inventario",
                        cliente: "Cliente B",
                        estado: "Completado",
                        fechaInicio: "2024-12-01",
                        fechaFin: "2025-03-15",
                        presupuesto: 1800000,
                        gastado: 1750000,
                        progreso: 100,
                        descripcion: "Aplicación móvil para control de inventario en tiempo real",
                        tareas: 12,
                        tareasCompletadas: 12
                    },
                    {
                        id: 3,
                        nombre: "Sistema CRM",
                        cliente: "Cliente C",
                        estado: "En Pausa",
                        fechaInicio: "2025-02-10",
                        fechaFin: "2025-08-20",
                        presupuesto: 3200000,
                        gastado: 800000,
                        progreso: 25,
                        descripcion: "Sistema de gestión de relaciones con clientes",
                        tareas: 20,
                        tareasCompletadas: 5
                    },
                    {
                        id: 4,
                        nombre: "Migración a la Nube",
                        cliente: "Cliente D",
                        estado: "Activo",
                        fechaInicio: "2025-03-01",
                        fechaFin: "2025-05-30",
                        presupuesto: 2200000,
                        gastado: 600000,
                        progreso: 30,
                        descripcion: "Migración de infraestructura local a servicios cloud",
                        tareas: 10,
                        tareasCompletadas: 3
                    },
                ];
                guardarProyectos();
            }
        } catch (err) {
            console.error("Error al obtener proyectos:", err);
        }
    };

    const guardarProyectos = () => {
        try {
            localStorage.setItem('proyectos_aeve', JSON.stringify(proyectos));
        } catch (err) {
            console.error("Error al guardar proyectos:", err);
        }
    };

    onMount(() => {
        obtenerVentas();
        obtenerProyectos();
    });

    // Métricas calculadas para ventas
    $: totalVentas = ventas.reduce((sum, v) => sum + (v.total || 0), 0);
    $: promedioVentas = ventas.length > 0 ? totalVentas / ventas.length : 0;
    $: cantidadBoletas = ventas.filter(v => v.tipo_documento === 'boleta').length;
    $: cantidadFacturas = ventas.filter(v => v.tipo_documento === 'factura').length;

    // Métricas calculadas para proyectos
    $: proyectosActivos = proyectos.filter(p => p.estado === 'Activo').length;
    $: proyectosCompletados = proyectos.filter(p => p.estado === 'Completado').length;
    $: proyectosEnPausa = proyectos.filter(p => p.estado === 'En Pausa').length;
    $: totalPresupuestos = proyectos.reduce((sum, p) => sum + (p.presupuesto || 0), 0);
    $: totalGastado = proyectos.reduce((sum, p) => sum + (p.gastado || 0), 0);
    $: progresoPromedio = proyectos.length > 0 ? proyectos.reduce((sum, p) => sum + (p.progreso || 0), 0) / proyectos.length : 0;
    $: totalTareas = proyectos.reduce((sum, p) => sum + (p.tareas || 0), 0);
    $: totalTareasCompletadas = proyectos.reduce((sum, p) => sum + (p.tareasCompletadas || 0), 0);

    // Filtrado de ventas
    $: ventasFiltradas = ventas.filter(v => {
        const cumpleBusqueda = !busqueda ||
            v.n_venta.toString().includes(busqueda) ||
            v.cliente_nombre?.toLowerCase().includes(busqueda.toLowerCase());

        const cumpleFecha = (!fechaInicio || v.fecha_venta >= fechaInicio) &&
                           (!fechaFin || v.fecha_venta <= fechaFin);

        const cumpleTipo = filtroTipoDoc === 'todos' || v.tipo_documento === filtroTipoDoc;

        return cumpleBusqueda && cumpleFecha && cumpleTipo;
    });

    // Filtrado de proyectos
    $: proyectosFiltrados = proyectos.filter(p => {
        const cumpleBusqueda = !busqueda ||
            p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
            p.cliente.toLowerCase().includes(busqueda.toLowerCase());

        return cumpleBusqueda;
    });

    const formatearPrecio = (precio) => {
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: "CLP",
            minimumFractionDigits: 0,
        }).format(precio || 0).replace('CLP', '').trim();
    };

    const formatearFecha = (fecha) => {
        const date = new Date(fecha);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    };

    const limpiarFiltros = () => {
        busqueda = "";
        fechaInicio = "";
        fechaFin = "";
        filtroTipoDoc = "todos";
    };

    // Función para generar y descargar PDF de documento tributario (SII)
    const descargarDocumentoPDF = async (venta) => {
        const tipoDoc = venta.tipo_documento === 'factura' ? 'FACTURA ELECTRÓNICA' : 'BOLETA ELECTRÓNICA';
        const codigoSII = venta.tipo_documento === 'factura' ? '33' : '39';

        // Crear contenido HTML del documento según estándar SII
        const contenidoHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>${tipoDoc} N° ${venta.n_venta}</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: Arial, sans-serif; padding: 20px; font-size: 12px; }
                    .documento { max-width: 800px; margin: 0 auto; border: 2px solid #000; padding: 20px; }
                    .header { display: flex; justify-content: space-between; margin-bottom: 20px; }
                    .empresa { flex: 1; }
                    .empresa h1 { font-size: 18px; margin-bottom: 5px; }
                    .timbre { width: 200px; border: 2px solid red; padding: 10px; text-align: center; }
                    .timbre .tipo { font-size: 14px; font-weight: bold; color: red; }
                    .timbre .numero { font-size: 16px; font-weight: bold; }
                    .timbre .sii { font-size: 10px; color: red; margin-top: 5px; }
                    .datos-cliente { border: 1px solid #000; padding: 10px; margin-bottom: 20px; }
                    .datos-cliente h3 { margin-bottom: 10px; font-size: 12px; }
                    .datos-cliente p { margin: 3px 0; }
                    .tabla { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                    .tabla th, .tabla td { border: 1px solid #000; padding: 8px; text-align: left; }
                    .tabla th { background: #f0f0f0; }
                    .tabla .cantidad, .tabla .precio, .tabla .total { text-align: right; }
                    .totales { margin-left: auto; width: 250px; }
                    .totales table { width: 100%; }
                    .totales td { padding: 5px; border: 1px solid #000; }
                    .totales .label { text-align: left; }
                    .totales .valor { text-align: right; font-weight: bold; }
                    .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #666; }
                    .timbre-electronico { margin-top: 20px; border: 1px dashed #000; padding: 10px; text-align: center; }
                    .timbre-electronico img { max-width: 150px; }
                    @media print {
                        body { padding: 0; }
                        .documento { border: none; }
                    }
                </style>
            </head>
            <body>
                <div class="documento">
                    <div class="header">
                        <div class="empresa">
                            <h1>AEVE GESTIÓN</h1>
                            <p>RUT: 76.XXX.XXX-X</p>
                            <p>Giro: Servicios de Software</p>
                            <p>Dirección: Santiago, Chile</p>
                            <p>Teléfono: +56 9 XXXX XXXX</p>
                        </div>
                        <div class="timbre">
                            <div class="tipo">${tipoDoc}</div>
                            <div class="numero">N° ${venta.n_venta}</div>
                            <div class="sii">S.I.I. - SANTIAGO</div>
                            <div style="font-size: 10px; margin-top: 5px;">Código: ${codigoSII}</div>
                        </div>
                    </div>

                    <div class="datos-cliente">
                        <h3>DATOS DEL RECEPTOR</h3>
                        <p><strong>Nombre/Razón Social:</strong> ${venta.cliente_nombre || 'Consumidor Final'}</p>
                        <p><strong>Fecha Emisión:</strong> ${formatearFecha(venta.fecha_venta)}</p>
                    </div>

                    <table class="tabla">
                        <thead>
                            <tr>
                                <th>Cantidad</th>
                                <th>Descripción</th>
                                <th class="precio">Precio Unit.</th>
                                <th class="total">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="cantidad">${venta.quantity || 1}</td>
                                <td>Productos/Servicios según detalle</td>
                                <td class="precio">${formatearPrecio(venta.total / (venta.quantity || 1))}</td>
                                <td class="total">${formatearPrecio(venta.total)}</td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="totales">
                        <table>
                            <tr>
                                <td class="label">Neto</td>
                                <td class="valor">${formatearPrecio(venta.total / 1.19)}</td>
                            </tr>
                            <tr>
                                <td class="label">IVA (19%)</td>
                                <td class="valor">${formatearPrecio(venta.total - (venta.total / 1.19))}</td>
                            </tr>
                            <tr>
                                <td class="label"><strong>TOTAL</strong></td>
                                <td class="valor"><strong>${formatearPrecio(venta.total)}</strong></td>
                            </tr>
                        </table>
                    </div>

                    <div class="timbre-electronico">
                        <p><strong>Timbre Electrónico SII</strong></p>
                        <p style="font-size: 8px; color: #666;">Resolución Ex. SII N° XX del XXXX</p>
                        <p style="font-size: 8px;">Verifique documento en www.sii.cl</p>
                    </div>

                    <div class="footer">
                        <p>Documento Tributario Electrónico generado por AEVE Gestión</p>
                        <p>Este documento es una representación impresa de un DTE</p>
                    </div>
                </div>
            </body>
            </html>
        `;

        // Crear ventana de impresión/descarga
        const ventanaImpresion = window.open('', '_blank');
        if (ventanaImpresion) {
            ventanaImpresion.document.write(contenidoHTML);
            ventanaImpresion.document.close();
            ventanaImpresion.focus();

            // Esperar a que cargue y luego imprimir
            setTimeout(() => {
                ventanaImpresion.print();
            }, 500);
        } else {
            alert('Por favor, permita las ventanas emergentes para descargar el documento');
        }
    };

    // Funciones para gestión de proyectos
    const crearProyecto = () => {
        if (!nuevoProyecto.nombre || !nuevoProyecto.cliente) {
            alert("El nombre y el cliente son obligatorios");
            return;
        }

        const proyecto = {
            id: Date.now(),
            ...nuevoProyecto,
            estado: "Activo",
            presupuesto: 0,
            gastado: 0,
            progreso: 0,
            tareas: 0,
            tareasCompletadas: 0,
            cotizacion: null,
            avances: [],
            gastos: []
        };

        proyectos = [...proyectos, proyecto];
        guardarProyectos();
        mostrarModalNuevoProyecto = false;

        // Resetear formulario
        nuevoProyecto = {
            nombre: "",
            cliente: "",
            descripcion: "",
            fechaInicio: new Date().toISOString().split('T')[0],
            fechaFin: "",
        };

        // Abrir modal de cotización automáticamente
        proyectoSeleccionado = proyecto;
        mostrarModalCotizacion = true;
    };

    const abrirCotizacion = (proyecto) => {
        proyectoSeleccionado = proyecto;

        // Cargar cotización si existe
        if (proyecto.cotizacion) {
            cotizacion = {...proyecto.cotizacion};
        } else {
            cotizacion = {
                items: [],
                observaciones: ""
            };
        }

        mostrarModalCotizacion = true;
    };

    const agregarItemCotizacion = () => {
        cotizacion.items = [...cotizacion.items, {
            id: Date.now(),
            descripcion: "",
            cantidad: 1,
            precioUnitario: 0
        }];
    };

    const eliminarItemCotizacion = (id) => {
        cotizacion.items = cotizacion.items.filter(item => item.id !== id);
    };

    const calcularTotalCotizacion = () => {
        return cotizacion.items.reduce((total, item) => {
            return total + (item.cantidad * item.precioUnitario);
        }, 0);
    };

    const guardarCotizacion = () => {
        if (!proyectoSeleccionado) return;

        const totalCotizacion = calcularTotalCotizacion();

        proyectos = proyectos.map(p => {
            if (p.id === proyectoSeleccionado.id) {
                return {
                    ...p,
                    cotizacion: {...cotizacion, total: totalCotizacion},
                    presupuesto: totalCotizacion
                };
            }
            return p;
        });

        guardarProyectos();
        mostrarModalCotizacion = false;
        alert("Cotización guardada exitosamente");
    };

    const abrirAvances = (proyecto) => {
        proyectoSeleccionado = proyecto;
        mostrarModalAvances = true;
    };

    const agregarAvance = () => {
        if (!nuevoAvance.descripcion || nuevoAvance.porcentaje < 0) {
            alert("Complete los campos del avance");
            return;
        }

        proyectos = proyectos.map(p => {
            if (p.id === proyectoSeleccionado.id) {
                const avances = [...(p.avances || []), {
                    id: Date.now(),
                    ...nuevoAvance,
                    fecha: new Date().toISOString()
                }];

                return {
                    ...p,
                    avances,
                    progreso: Math.min(100, nuevoAvance.porcentaje)
                };
            }
            return p;
        });

        guardarProyectos();

        // Actualizar proyecto seleccionado
        proyectoSeleccionado = proyectos.find(p => p.id === proyectoSeleccionado.id);

        // Resetear formulario
        nuevoAvance = {
            descripcion: "",
            porcentaje: 0
        };
    };

    const abrirGastos = (proyecto) => {
        proyectoSeleccionado = proyecto;
        mostrarModalGastos = true;
    };

    const agregarGasto = () => {
        if (!nuevoGasto.descripcion || nuevoGasto.monto <= 0) {
            alert("Complete los campos del gasto");
            return;
        }

        proyectos = proyectos.map(p => {
            if (p.id === proyectoSeleccionado.id) {
                const gastos = [...(p.gastos || []), {
                    id: Date.now(),
                    ...nuevoGasto
                }];

                const totalGastado = gastos.reduce((sum, g) => sum + g.monto, 0);

                return {
                    ...p,
                    gastos,
                    gastado: totalGastado
                };
            }
            return p;
        });

        guardarProyectos();

        // Actualizar proyecto seleccionado
        proyectoSeleccionado = proyectos.find(p => p.id === proyectoSeleccionado.id);

        // Resetear formulario
        nuevoGasto = {
            descripcion: "",
            monto: 0,
            categoria: "materiales",
            fecha: new Date().toISOString().split('T')[0]
        };
    };

    const eliminarGasto = (gastoId) => {
        if (!confirm("¿Eliminar este gasto?")) return;

        proyectos = proyectos.map(p => {
            if (p.id === proyectoSeleccionado.id) {
                const gastos = p.gastos.filter(g => g.id !== gastoId);
                const totalGastado = gastos.reduce((sum, g) => sum + g.monto, 0);

                return {
                    ...p,
                    gastos,
                    gastado: totalGastado
                };
            }
            return p;
        });

        guardarProyectos();
        proyectoSeleccionado = proyectos.find(p => p.id === proyectoSeleccionado.id);
    };
</script>

<svelte:head>
    <title>Reportes - AEVE</title>
</svelte:head>

<div class="flex flex-col gap-6 w-full text-gray-200">
    <!-- Header -->
    <div class="flex justify-between items-center">
        <div>
            <h1 class="text-2xl font-semibold text-white mb-1">Reportes y Análisis</h1>
            <p class="text-gray-400 text-sm">Consulta métricas y analiza el rendimiento de tu negocio</p>
        </div>

        <div class="flex items-center gap-3">
            <button
                on:click={() => { obtenerVentas(); obtenerProyectos(); }}
                disabled={cargando}
                class="px-4 py-2 bg-purple-600/90 hover:bg-purple-600 disabled:bg-gray-600 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
            >
                <svg class="w-4 h-4 {cargando ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Actualizar
            </button>
        </div>
    </div>

    <!-- Tabs -->
    <div class="bg-[#0f0f0f]/80 backdrop-blur-sm border border-[#1f1f1f]/50 rounded-xl overflow-hidden shadow-xl">
        <div class="flex border-b border-[#1f1f1f]/50">
            <button
                on:click={() => { tabActiva = 'ventas'; limpiarFiltros(); }}
                class="flex-1 px-6 py-4 text-sm font-medium transition-all duration-200 {tabActiva === 'ventas'
                    ? 'bg-purple-600/20 text-purple-400 border-b-2 border-purple-500'
                    : 'text-gray-400 hover:text-white hover:bg-[#1a1a1a]/50'}"
            >
                <div class="flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                    </svg>
                    Reportes de Ventas
                </div>
            </button>
            <button
                on:click={() => { tabActiva = 'proyectos'; limpiarFiltros(); }}
                class="flex-1 px-6 py-4 text-sm font-medium transition-all duration-200 {tabActiva === 'proyectos'
                    ? 'bg-purple-600/20 text-purple-400 border-b-2 border-purple-500'
                    : 'text-gray-400 hover:text-white hover:bg-[#1a1a1a]/50'}"
            >
                <div class="flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Reportes de Proyectos
                </div>
            </button>
        </div>

        <!-- Contenido de Ventas -->
        {#if tabActiva === 'ventas'}
            <div class="p-6" in:fly={{ x: -20, duration: 300 }}>
                <!-- Métricas de Ventas -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-purple-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 0 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Total</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{formatearPrecio(totalVentas)}</div>
                        <div class="text-xs text-gray-400">{ventas.length} ventas registradas</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-blue-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 50 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Promedio</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{formatearPrecio(promedioVentas)}</div>
                        <div class="text-xs text-gray-400">Por venta</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-green-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 100 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Boletas</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{cantidadBoletas}</div>
                        <div class="text-xs text-gray-400">Emitidas</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-orange-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 150 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Facturas</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{cantidadFacturas}</div>
                        <div class="text-xs text-gray-400">Emitidas</div>
                    </div>
                </div>

                <!-- Filtros de Ventas -->
                <div class="flex items-center gap-3 mb-6 flex-wrap">
                    <div class="relative flex-1 min-w-[200px]">
                        <input
                            type="text"
                            placeholder="Buscar por N° venta o cliente..."
                            bind:value={busqueda}
                            class="w-full pl-10 pr-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                        />
                        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>

                    <select
                        bind:value={filtroTipoDoc}
                        class="px-3 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    >
                        <option value="todos">Todos los documentos</option>
                        <option value="boleta">Solo Boletas</option>
                        <option value="factura">Solo Facturas</option>
                    </select>

                    <input
                        type="date"
                        bind:value={fechaInicio}
                        class="px-3 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    />

                    <input
                        type="date"
                        bind:value={fechaFin}
                        class="px-3 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    />

                    <button
                        on:click={limpiarFiltros}
                        class="px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-400 hover:text-white border border-[#2f2f2f] rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        Limpiar
                    </button>
                </div>

                <!-- Tabla de Ventas -->
                {#if cargando}
                    <div class="flex justify-center py-12">
                        <div class="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                {:else if ventasFiltradas.length === 0}
                    <div class="text-center py-12">
                        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <p class="text-gray-400">No se encontraron ventas</p>
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
                                    <th class="text-left p-4">
                                        <span class="text-xs font-medium text-gray-400 uppercase tracking-wide">Items</span>
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
                                            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium {venta.tipo_documento === 'factura' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'bg-green-500/20 text-green-300 border border-green-500/30'}">
                                                {venta.tipo_documento === 'factura' ? 'Factura' : 'Boleta'}
                                            </span>
                                        </td>
                                        <td class="p-4">
                                            <span class="font-mono text-sm text-purple-400">#{venta.n_venta}</span>
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
                                        <td class="p-4 text-sm text-gray-400">
                                            {venta.quantity || 0}
                                        </td>
                                        <td class="p-4 text-right">
                                            <span class="font-semibold text-white">{formatearPrecio(venta.total)}</span>
                                        </td>
                                        <td class="p-4 text-right">
                                            <button
                                                on:click={() => descargarDocumentoPDF(venta)}
                                                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-purple-600/90 hover:bg-purple-600 text-white text-xs rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                                                title="Descargar {venta.tipo_documento === 'factura' ? 'Factura' : 'Boleta'} PDF"
                                            >
                                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                                </svg>
                                                PDF
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

        <!-- Contenido de Proyectos -->
        {#if tabActiva === 'proyectos'}
            <div class="p-6" in:fly={{ x: 20, duration: 300 }}>
                <!-- Métricas de Proyectos - Fila 1 -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-purple-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 0 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Presupuesto Total</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{formatearPrecio(totalPresupuestos)}</div>
                        <div class="text-xs text-gray-400">{proyectos.length} proyectos</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-red-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 50 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Gastado</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{formatearPrecio(totalGastado)}</div>
                        <div class="text-xs text-gray-400">{((totalGastado/totalPresupuestos)*100).toFixed(1)}% del total</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-blue-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 100 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Progreso</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{progresoPromedio.toFixed(1)}%</div>
                        <div class="text-xs text-gray-400">Promedio general</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-cyan-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 150 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Tareas</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{totalTareasCompletadas}/{totalTareas}</div>
                        <div class="text-xs text-gray-400">{((totalTareasCompletadas/totalTareas)*100).toFixed(0)}% completadas</div>
                    </div>
                </div>

                <!-- Métricas de Proyectos - Fila 2 (Estados) -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-green-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 200 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Activos</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{proyectosActivos}</div>
                        <div class="text-xs text-gray-400">En progreso</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-orange-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 250 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">En Pausa</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{proyectosEnPausa}</div>
                        <div class="text-xs text-gray-400">Pausados</div>
                    </div>

                    <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-5 rounded-xl border border-[#2f2f2f] hover:border-blue-500/30 transition-all duration-200" in:scale={{ duration: 200, delay: 300 }}>
                        <div class="flex items-center justify-between mb-3">
                            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <span class="text-xs text-gray-500">Completados</span>
                        </div>
                        <div class="text-2xl font-bold text-white mb-1">{proyectosCompletados}</div>
                        <div class="text-xs text-gray-400">Finalizados</div>
                    </div>
                </div>

                <!-- Filtro de búsqueda para proyectos -->
                <div class="flex items-center gap-3 mb-6">
                    <div class="relative flex-1">
                        <input
                            type="text"
                            placeholder="Buscar por nombre o cliente..."
                            bind:value={busqueda}
                            class="w-full pl-10 pr-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                        />
                        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>

                    <button
                        on:click={() => mostrarModalNuevoProyecto = true}
                        class="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm font-medium"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Nuevo Proyecto
                    </button>

                    <button
                        on:click={limpiarFiltros}
                        class="px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-400 hover:text-white border border-[#2f2f2f] rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        Limpiar
                    </button>
                </div>

                <!-- Tarjetas de Proyectos -->
                {#if proyectosFiltrados.length === 0}
                    <div class="text-center py-12">
                        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <p class="text-gray-400">No se encontraron proyectos</p>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {#each proyectosFiltrados as proyecto (proyecto.id)}
                            <div class="bg-gradient-to-br from-[#1f1f1f] to-[#2a2a2a] p-6 rounded-xl border border-[#2f2f2f] hover:border-purple-500/30 transition-all duration-200" in:fly={{ y: 20, duration: 300 }}>
                                <!-- Header del Proyecto -->
                                <div class="flex items-start justify-between mb-4">
                                    <div class="flex-1">
                                        <h3 class="text-lg font-bold text-white mb-1">{proyecto.nombre}</h3>
                                        <div class="flex items-center gap-2 text-sm text-gray-400">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                            </svg>
                                            {proyecto.cliente}
                                        </div>
                                    </div>
                                    <span class="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium {
                                        proyecto.estado === 'Activo' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                                        proyecto.estado === 'Completado' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                                        'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                                    }">
                                        {proyecto.estado}
                                    </span>
                                </div>

                                <!-- Descripción -->
                                <p class="text-sm text-gray-400 mb-4">{proyecto.descripcion}</p>

                                <!-- Barra de Progreso -->
                                <div class="mb-4">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs text-gray-400">Progreso del Proyecto</span>
                                        <span class="text-xs font-bold text-purple-400">{proyecto.progreso}%</span>
                                    </div>
                                    <div class="w-full bg-[#0f0f0f] rounded-full h-2 overflow-hidden">
                                        <div
                                            class="h-full rounded-full transition-all duration-500 {
                                                proyecto.progreso === 100 ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                                                proyecto.progreso >= 50 ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
                                                'bg-gradient-to-r from-orange-500 to-orange-600'
                                            }"
                                            style="width: {proyecto.progreso}%"
                                        ></div>
                                    </div>
                                </div>

                                <!-- Tareas -->
                                <div class="flex items-center gap-2 mb-4">
                                    <div class="flex items-center gap-1 text-sm">
                                        <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                                        </svg>
                                        <span class="text-white font-medium">{proyecto.tareasCompletadas}/{proyecto.tareas}</span>
                                        <span class="text-gray-400">tareas</span>
                                    </div>
                                </div>

                                <!-- Presupuesto vs Gastado -->
                                <div class="grid grid-cols-2 gap-4 mb-4">
                                    <div class="bg-[#0f0f0f] p-3 rounded-lg">
                                        <div class="text-xs text-gray-500 mb-1">Presupuesto</div>
                                        <div class="text-base font-bold text-white">{formatearPrecio(proyecto.presupuesto)}</div>
                                    </div>
                                    <div class="bg-[#0f0f0f] p-3 rounded-lg">
                                        <div class="text-xs text-gray-500 mb-1">Gastado</div>
                                        <div class="text-base font-bold {proyecto.gastado > proyecto.presupuesto ? 'text-red-400' : 'text-white'}">
                                            {formatearPrecio(proyecto.gastado)}
                                        </div>
                                    </div>
                                </div>

                                <!-- Fechas -->
                                <div class="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-[#2f2f2f] mb-4">
                                    <div class="flex items-center gap-1">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                        </svg>
                                        Inicio: {formatearFecha(proyecto.fechaInicio)}
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                        </svg>
                                        Fin: {formatearFecha(proyecto.fechaFin)}
                                    </div>
                                </div>

                                <!-- Botones de acción -->
                                <div class="grid grid-cols-3 gap-2">
                                    <button
                                        on:click={() => abrirCotizacion(proyecto)}
                                        class="px-3 py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5 text-xs font-medium"
                                    >
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                        </svg>
                                        Cotizar
                                    </button>

                                    <button
                                        on:click={() => abrirAvances(proyecto)}
                                        class="px-3 py-2 bg-green-600/20 hover:bg-green-600/30 text-green-300 border border-green-500/30 rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5 text-xs font-medium"
                                    >
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Avances
                                    </button>

                                    <button
                                        on:click={() => abrirGastos(proyecto)}
                                        class="px-3 py-2 bg-orange-600/20 hover:bg-orange-600/30 text-orange-300 border border-orange-500/30 rounded-lg transition-all duration-200 flex items-center justify-center gap-1.5 text-xs font-medium"
                                    >
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
                                        </svg>
                                        Gastos
                                    </button>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

<!-- Modal: Nuevo Proyecto -->
{#if mostrarModalNuevoProyecto}
    <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" on:click={() => mostrarModalNuevoProyecto = false} transition:fade>
        <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-6 max-w-2xl w-full shadow-2xl" on:click|stopPropagation transition:scale>
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-white">Nuevo Proyecto</h2>
                <button on:click={() => mostrarModalNuevoProyecto = false} class="text-gray-400 hover:text-white transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <form on:submit|preventDefault={crearProyecto} class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Nombre del Proyecto *</label>
                    <input
                        type="text"
                        bind:value={nuevoProyecto.nombre}
                        required
                        class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Ej: Desarrollo Web AEVE"
                    />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Cliente *</label>
                    <input
                        type="text"
                        bind:value={nuevoProyecto.cliente}
                        required
                        class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Nombre del cliente"
                    />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Descripción</label>
                    <textarea
                        bind:value={nuevoProyecto.descripcion}
                        rows="3"
                        class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                        placeholder="Breve descripción del proyecto"
                    ></textarea>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">Fecha de Inicio</label>
                        <input
                            type="date"
                            bind:value={nuevoProyecto.fechaInicio}
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">Fecha de Fin Estimada</label>
                        <input
                            type="date"
                            bind:value={nuevoProyecto.fechaFin}
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>
                </div>

                <div class="flex gap-3 pt-4">
                    <button
                        type="button"
                        on:click={() => mostrarModalNuevoProyecto = false}
                        class="flex-1 px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-300 border border-[#2f2f2f] rounded-lg transition-all duration-200 font-medium"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        class="flex-1 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all duration-200 font-medium"
                    >
                        Crear y Cotizar
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}

<!-- Modal: Cotización -->
{#if mostrarModalCotizacion && proyectoSeleccionado}
    <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" on:click={() => mostrarModalCotizacion = false} transition:fade>
        <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" on:click|stopPropagation transition:scale>
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Cotización</h2>
                    <p class="text-sm text-gray-400 mt-1">{proyectoSeleccionado.nombre}</p>
                </div>
                <button on:click={() => mostrarModalCotizacion = false} class="text-gray-400 hover:text-white transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-semibold text-white">Items de Cotización</h3>
                    <button
                        on:click={agregarItemCotizacion}
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 text-sm"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        Agregar Item
                    </button>
                </div>

                {#if cotizacion.items.length === 0}
                    <div class="text-center py-8 text-gray-400">
                        No hay items en la cotización. Agrega items para comenzar.
                    </div>
                {:else}
                    <div class="space-y-3">
                        {#each cotizacion.items as item (item.id)}
                            <div class="bg-[#1f1f1f] p-4 rounded-lg border border-[#2f2f2f]" in:fly={{ y: -10, duration: 200 }}>
                                <div class="grid grid-cols-12 gap-3 items-start">
                                    <div class="col-span-5">
                                        <input
                                            type="text"
                                            bind:value={item.descripcion}
                                            placeholder="Descripción del item"
                                            class="w-full px-3 py-2 bg-[#0f0f0f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div class="col-span-2">
                                        <input
                                            type="number"
                                            bind:value={item.cantidad}
                                            min="1"
                                            placeholder="Cant."
                                            class="w-full px-3 py-2 bg-[#0f0f0f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div class="col-span-3">
                                        <input
                                            type="number"
                                            bind:value={item.precioUnitario}
                                            min="0"
                                            placeholder="Precio Unit."
                                            class="w-full px-3 py-2 bg-[#0f0f0f] border border-[#2f2f2f] rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div class="col-span-2 flex items-center justify-between">
                                        <span class="text-sm font-bold text-white">{formatearPrecio(item.cantidad * item.precioUnitario)}</span>
                                        <button
                                            on:click={() => eliminarItemCotizacion(item.id)}
                                            class="text-red-400 hover:text-red-300 transition-colors"
                                        >
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>

                    <div class="bg-purple-600/20 border border-purple-500/30 rounded-lg p-4 mt-4">
                        <div class="flex items-center justify-between">
                            <span class="text-lg font-semibold text-purple-300">Total Cotización:</span>
                            <span class="text-2xl font-bold text-white">{formatearPrecio(calcularTotalCotizacion())}</span>
                        </div>
                    </div>
                {/if}

                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Observaciones</label>
                    <textarea
                        bind:value={cotizacion.observaciones}
                        rows="3"
                        class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                        placeholder="Observaciones adicionales de la cotización..."
                    ></textarea>
                </div>

                <div class="flex gap-3 pt-4">
                    <button
                        type="button"
                        on:click={() => mostrarModalCotizacion = false}
                        class="flex-1 px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-300 border border-[#2f2f2f] rounded-lg transition-all duration-200 font-medium"
                    >
                        Cancelar
                    </button>
                    <button
                        on:click={guardarCotizacion}
                        class="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 font-medium"
                    >
                        Guardar Cotización
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Modal: Avances -->
{#if mostrarModalAvances && proyectoSeleccionado}
    <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" on:click={() => mostrarModalAvances = false} transition:fade>
        <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" on:click|stopPropagation transition:scale>
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Avances del Proyecto</h2>
                    <p class="text-sm text-gray-400 mt-1">{proyectoSeleccionado.nombre}</p>
                </div>
                <button on:click={() => mostrarModalAvances = false} class="text-gray-400 hover:text-white transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <!-- Formulario de nuevo avance -->
            <div class="bg-green-600/10 border border-green-500/30 rounded-lg p-4 mb-6">
                <h3 class="text-sm font-semibold text-green-300 mb-3">Registrar Nuevo Avance</h3>
                <div class="grid grid-cols-12 gap-3">
                    <div class="col-span-8">
                        <input
                            type="text"
                            bind:value={nuevoAvance.descripcion}
                            placeholder="Descripción del avance"
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>
                    <div class="col-span-2">
                        <input
                            type="number"
                            bind:value={nuevoAvance.porcentaje}
                            min="0"
                            max="100"
                            placeholder="%"
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>
                    <div class="col-span-2">
                        <button
                            on:click={agregarAvance}
                            class="w-full px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-200 font-medium"
                        >
                            Agregar
                        </button>
                    </div>
                </div>
            </div>

            <!-- Lista de avances -->
            {#if proyectoSeleccionado.avances && proyectoSeleccionado.avances.length > 0}
                <div class="space-y-3">
                    <h3 class="text-sm font-semibold text-gray-300 mb-2">Historial de Avances</h3>
                    {#each proyectoSeleccionado.avances.slice().reverse() as avance (avance.id)}
                        <div class="bg-[#1f1f1f] p-4 rounded-lg border border-[#2f2f2f]" in:fly={{ y: -10, duration: 200 }}>
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <p class="text-white font-medium mb-1">{avance.descripcion}</p>
                                    <p class="text-xs text-gray-400">{formatearFecha(avance.fecha)}</p>
                                </div>
                                <span class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold bg-green-500/20 text-green-300 border border-green-500/30">
                                    {avance.porcentaje}%
                                </span>
                            </div>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="text-center py-8 text-gray-400">
                    No hay avances registrados aún.
                </div>
            {/if}

            <div class="flex gap-3 pt-6">
                <button
                    on:click={() => mostrarModalAvances = false}
                    class="flex-1 px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-300 border border-[#2f2f2f] rounded-lg transition-all duration-200 font-medium"
                >
                    Cerrar
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Modal: Gastos -->
{#if mostrarModalGastos && proyectoSeleccionado}
    <div class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" on:click={() => mostrarModalGastos = false} transition:fade>
        <div class="bg-gradient-to-br from-[#1a1a1a] to-[#0f0f0f] border border-[#2f2f2f] rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl" on:click|stopPropagation transition:scale>
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-2xl font-bold text-white">Gestión de Gastos</h2>
                    <p class="text-sm text-gray-400 mt-1">{proyectoSeleccionado.nombre}</p>
                </div>
                <button on:click={() => mostrarModalGastos = false} class="text-gray-400 hover:text-white transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <!-- Resumen de gastos -->
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="bg-purple-600/10 border border-purple-500/30 rounded-lg p-4">
                    <div class="text-xs text-purple-300 mb-1">Presupuesto</div>
                    <div class="text-xl font-bold text-white">{formatearPrecio(proyectoSeleccionado.presupuesto || 0)}</div>
                </div>
                <div class="bg-red-600/10 border border-red-500/30 rounded-lg p-4">
                    <div class="text-xs text-red-300 mb-1">Gastado</div>
                    <div class="text-xl font-bold text-white">{formatearPrecio(proyectoSeleccionado.gastado || 0)}</div>
                </div>
                <div class="bg-green-600/10 border border-green-500/30 rounded-lg p-4">
                    <div class="text-xs text-green-300 mb-1">Disponible</div>
                    <div class="text-xl font-bold text-white">{formatearPrecio((proyectoSeleccionado.presupuesto || 0) - (proyectoSeleccionado.gastado || 0))}</div>
                </div>
            </div>

            <!-- Formulario de nuevo gasto -->
            <div class="bg-orange-600/10 border border-orange-500/30 rounded-lg p-4 mb-6">
                <h3 class="text-sm font-semibold text-orange-300 mb-3">Registrar Nuevo Gasto</h3>
                <div class="grid grid-cols-12 gap-3">
                    <div class="col-span-5">
                        <input
                            type="text"
                            bind:value={nuevoGasto.descripcion}
                            placeholder="Descripción del gasto"
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                    </div>
                    <div class="col-span-3">
                        <input
                            type="number"
                            bind:value={nuevoGasto.monto}
                            min="0"
                            placeholder="Monto"
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500"
                        />
                    </div>
                    <div class="col-span-2">
                        <select
                            bind:value={nuevoGasto.categoria}
                            class="w-full px-4 py-2.5 bg-[#1f1f1f] border border-[#2f2f2f] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                        >
                            <option value="materiales">Materiales</option>
                            <option value="mano_obra">Mano de Obra</option>
                            <option value="servicios">Servicios</option>
                            <option value="otros">Otros</option>
                        </select>
                    </div>
                    <div class="col-span-2">
                        <button
                            on:click={agregarGasto}
                            class="w-full px-4 py-2.5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-all duration-200 font-medium"
                        >
                            Agregar
                        </button>
                    </div>
                </div>
            </div>

            <!-- Lista de gastos -->
            {#if proyectoSeleccionado.gastos && proyectoSeleccionado.gastos.length > 0}
                <div class="space-y-3">
                    <h3 class="text-sm font-semibold text-gray-300 mb-2">Registro de Gastos</h3>
                    {#each proyectoSeleccionado.gastos.slice().reverse() as gasto (gasto.id)}
                        <div class="bg-[#1f1f1f] p-4 rounded-lg border border-[#2f2f2f] group hover:border-orange-500/30 transition-all" in:fly={{ y: -10, duration: 200 }}>
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center gap-2 mb-1">
                                        <p class="text-white font-medium">{gasto.descripcion}</p>
                                        <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-600/30 text-gray-300 border border-gray-500/30">
                                            {gasto.categoria.replace('_', ' ')}
                                        </span>
                                    </div>
                                    <p class="text-xs text-gray-400">{formatearFecha(gasto.fecha)}</p>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="text-lg font-bold text-white">{formatearPrecio(gasto.monto)}</span>
                                    <button
                                        on:click={() => eliminarGasto(gasto.id)}
                                        class="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-all"
                                    >
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="text-center py-8 text-gray-400">
                    No hay gastos registrados aún.
                </div>
            {/if}

            <div class="flex gap-3 pt-6">
                <button
                    on:click={() => mostrarModalGastos = false}
                    class="flex-1 px-4 py-2.5 bg-[#1f1f1f] hover:bg-[#2a2a2a] text-gray-300 border border-[#2f2f2f] rounded-lg transition-all duration-200 font-medium"
                >
                    Cerrar
                </button>
            </div>
        </div>
    </div>
{/if}
