from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from models.ventas import (
    VentaDB, VentaCreate, VentaUpdate, VentaResponse,
    DetalleVentaDB, DetalleVentaResponse,
    PagoVentaDB, PagoVentaCreate, PagoVentaResponse
)
from models.clientes import ClienteDB
from models.product import ProductoDB, HistorialPrecioProductoDB

sales_router = APIRouter(tags=["Ventas"])


def obtener_precio_producto(producto_id: int, db: Session):
    """Obtener el precio más reciente de un producto"""
    historial = db.query(HistorialPrecioProductoDB).filter(
        HistorialPrecioProductoDB.producto == producto_id
    ).order_by(HistorialPrecioProductoDB.fecha_precio.desc()).first()

    if historial:
        return float(historial.precio_bruto)
    return 0


@sales_router.get("/mostrar-ventas")
async def mostrar_ventas_reporte(db: Session = Depends(get_db)):
    """Endpoint para el módulo de reportes - formato simplificado"""
    try:
        ventas = db.query(VentaDB).all()

        resultado = []
        for venta in ventas:
            # Obtener nombre del cliente
            cliente = db.query(ClienteDB).filter(ClienteDB.id == venta.cliente).first()

            # Calcular total y cantidad de items
            total = 0
            quantity = 0
            for detalle in venta.detalles:
                cantidad = detalle.cantidad_producto
                precio = obtener_precio_producto(detalle.id_producto, db)
                total += cantidad * precio
                quantity += cantidad

            # Determinar tipo de documento
            tipo_documento = "boleta"
            if venta.tipo_dte and "factura" in venta.tipo_dte.lower():
                tipo_documento = "factura"

            venta_data = {
                "id": venta.id,
                "n_venta": venta.n_documento,
                "fecha_venta": venta.fecha.strftime("%Y-%m-%d") if venta.fecha else None,
                "cliente_nombre": f"{cliente.nombre} {cliente.apellidos}" if cliente else None,
                "tipo_documento": tipo_documento,
                "quantity": quantity,
                "total": total
            }
            resultado.append(venta_data)

        return {"data": resultado}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(error)}")


@sales_router.get("/ventas", response_model=list[VentaResponse])
async def mostrar_ventas(db: Session = Depends(get_db)):
    """Obtener todas las ventas"""
    try:
        ventas = db.query(VentaDB).all()

        resultado = []
        for venta in ventas:
            # Obtener nombre del cliente
            cliente = db.query(ClienteDB).filter(ClienteDB.id == venta.cliente).first()

            # Obtener detalles con información de productos
            detalles = []
            for detalle in venta.detalles:
                producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
                detalle_dict = {
                    "id": detalle.id,
                    "cantidad_producto": detalle.cantidad_producto,
                    "id_producto": detalle.id_producto,
                    "nombre_producto": producto.nombre if producto else None,
                    "precio_unitario": None  # Puedes agregar lógica de precios aquí
                }
                detalles.append(DetalleVentaResponse(**detalle_dict))

            # Obtener pagos
            pagos = [PagoVentaResponse.model_validate(pago) for pago in venta.pagos]

            venta_dict = {
                "id": venta.id,
                "fecha": venta.fecha,
                "n_documento": venta.n_documento,
                "cliente": venta.cliente,
                "estado_venta": venta.estado_venta,
                "tipo_pago": venta.tipo_pago,
                "observacion": venta.observacion,
                "canal_venta": venta.canal_venta,
                "estado_dte": venta.estado_dte,
                "tipo_dte": venta.tipo_dte,
                "usuario_vendedor": venta.usuario_vendedor,
                "nombre_cliente": f"{cliente.nombre} {cliente.apellidos}" if cliente else None,
                "detalles": detalles,
                "pagos": pagos
            }

            resultado.append(VentaResponse(**venta_dict))

        return resultado
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(error)}")


@sales_router.get("/ventas/{venta_id}", response_model=VentaResponse)
async def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    """Obtener una venta por ID"""
    try:
        venta = db.query(VentaDB).filter(VentaDB.id == venta_id).first()

        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        cliente = db.query(ClienteDB).filter(ClienteDB.id == venta.cliente).first()

        # Obtener detalles con información de productos
        detalles = []
        for detalle in venta.detalles:
            producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
            detalle_dict = {
                "id": detalle.id,
                "cantidad_producto": detalle.cantidad_producto,
                "id_producto": detalle.id_producto,
                "nombre_producto": producto.nombre if producto else None,
                "precio_unitario": None
            }
            detalles.append(DetalleVentaResponse(**detalle_dict))

        pagos = [PagoVentaResponse.model_validate(pago) for pago in venta.pagos]

        venta_dict = {
            "id": venta.id,
            "fecha": venta.fecha,
            "n_documento": venta.n_documento,
            "cliente": venta.cliente,
            "estado_venta": venta.estado_venta,
            "tipo_pago": venta.tipo_pago,
            "observacion": venta.observacion,
            "canal_venta": venta.canal_venta,
            "estado_dte": venta.estado_dte,
            "tipo_dte": venta.tipo_dte,
            "usuario_vendedor": venta.usuario_vendedor,
            "nombre_cliente": f"{cliente.nombre} {cliente.apellidos}" if cliente else None,
            "detalles": detalles,
            "pagos": pagos
        }

        return VentaResponse(**venta_dict)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener venta: {str(error)}")


@sales_router.post("/ventas", response_model=VentaResponse, status_code=201)
async def crear_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """Crear una nueva venta"""
    try:
        # Verificar que el cliente existe
        cliente = db.query(ClienteDB).filter(ClienteDB.id == venta.cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Verificar que el número de documento no existe
        venta_existente = db.query(VentaDB).filter(VentaDB.n_documento == venta.n_documento).first()
        if venta_existente:
            raise HTTPException(status_code=400, detail="El número de documento ya existe")

        # Crear la venta
        venta_data = venta.model_dump(exclude={"detalles"})
        nueva_venta = VentaDB(**venta_data)
        db.add(nueva_venta)
        db.flush()  # Para obtener el ID de la venta

        # Crear los detalles de la venta
        for detalle in venta.detalles:
            # Verificar que el producto existe
            producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {detalle.id_producto} no encontrado")

            nuevo_detalle = DetalleVentaDB(
                cantidad_producto=detalle.cantidad_producto,
                id_producto=detalle.id_producto,
                venta_id=nueva_venta.id
            )
            db.add(nuevo_detalle)

            # Actualizar el stock del producto
            producto.unidades -= detalle.cantidad_producto
            if producto.unidades < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el producto {producto.nombre}"
                )

        db.commit()
        db.refresh(nueva_venta)

        # Obtener detalles formateados
        detalles = []
        for detalle in nueva_venta.detalles:
            producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
            detalle_dict = {
                "id": detalle.id,
                "cantidad_producto": detalle.cantidad_producto,
                "id_producto": detalle.id_producto,
                "nombre_producto": producto.nombre if producto else None,
                "precio_unitario": None
            }
            detalles.append(DetalleVentaResponse(**detalle_dict))

        venta_dict = {
            "id": nueva_venta.id,
            "fecha": nueva_venta.fecha,
            "n_documento": nueva_venta.n_documento,
            "cliente": nueva_venta.cliente,
            "estado_venta": nueva_venta.estado_venta,
            "tipo_pago": nueva_venta.tipo_pago,
            "observacion": nueva_venta.observacion,
            "canal_venta": nueva_venta.canal_venta,
            "estado_dte": nueva_venta.estado_dte,
            "tipo_dte": nueva_venta.tipo_dte,
            "usuario_vendedor": nueva_venta.usuario_vendedor,
            "nombre_cliente": f"{cliente.nombre} {cliente.apellidos}" if cliente else None,
            "detalles": detalles,
            "pagos": []
        }

        return VentaResponse(**venta_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear venta: {str(error)}")


@sales_router.put("/ventas/{venta_id}", response_model=VentaResponse)
async def actualizar_venta(venta_id: int, venta_data: VentaUpdate, db: Session = Depends(get_db)):
    """Actualizar una venta existente"""
    try:
        venta = db.query(VentaDB).filter(VentaDB.id == venta_id).first()

        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        # Actualizar solo los campos proporcionados
        update_data = venta_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venta, key, value)

        db.commit()
        db.refresh(venta)

        # Obtener información completa para la respuesta
        cliente = db.query(ClienteDB).filter(ClienteDB.id == venta.cliente).first()

        detalles = []
        for detalle in venta.detalles:
            producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
            detalle_dict = {
                "id": detalle.id,
                "cantidad_producto": detalle.cantidad_producto,
                "id_producto": detalle.id_producto,
                "nombre_producto": producto.nombre if producto else None,
                "precio_unitario": None
            }
            detalles.append(DetalleVentaResponse(**detalle_dict))

        pagos = [PagoVentaResponse.model_validate(pago) for pago in venta.pagos]

        venta_dict = {
            "id": venta.id,
            "fecha": venta.fecha,
            "n_documento": venta.n_documento,
            "cliente": venta.cliente,
            "estado_venta": venta.estado_venta,
            "tipo_pago": venta.tipo_pago,
            "observacion": venta.observacion,
            "canal_venta": venta.canal_venta,
            "estado_dte": venta.estado_dte,
            "tipo_dte": venta.tipo_dte,
            "usuario_vendedor": venta.usuario_vendedor,
            "nombre_cliente": f"{cliente.nombre} {cliente.apellidos}" if cliente else None,
            "detalles": detalles,
            "pagos": pagos
        }

        return VentaResponse(**venta_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar venta: {str(error)}")


@sales_router.delete("/ventas/{venta_id}")
async def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    """Eliminar una venta"""
    try:
        venta = db.query(VentaDB).filter(VentaDB.id == venta_id).first()

        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        # Restaurar el stock de los productos antes de eliminar
        for detalle in venta.detalles:
            producto = db.query(ProductoDB).filter(ProductoDB.id == detalle.id_producto).first()
            if producto:
                producto.unidades += detalle.cantidad_producto

        # Eliminar la venta (esto eliminará en cascada los detalles)
        db.delete(venta)
        db.commit()

        return {"status": "success", "message": "Venta eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar venta: {str(error)}")


@sales_router.post("/ventas/{venta_id}/pagos", response_model=PagoVentaResponse, status_code=201)
async def agregar_pago(venta_id: int, pago: PagoVentaCreate, db: Session = Depends(get_db)):
    """Agregar un pago a una venta"""
    try:
        venta = db.query(VentaDB).filter(VentaDB.id == venta_id).first()

        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        nuevo_pago = PagoVentaDB(
            **pago.model_dump(),
            venta_id=venta_id
        )
        db.add(nuevo_pago)
        db.commit()
        db.refresh(nuevo_pago)

        return PagoVentaResponse.model_validate(nuevo_pago)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al agregar pago: {str(error)}")
