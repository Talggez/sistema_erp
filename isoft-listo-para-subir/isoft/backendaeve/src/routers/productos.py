from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from utils.database import get_db
from models.product import (
    ProductoDB, ProductCreate, ProductUpdate, ProductResponse,
    TipoProductoDB, TipoProductoResponse, HistorialPrecioProductoDB
)
from PIL import Image
import io

productos_router = APIRouter(tags=["Productos"])


def obtener_precio_actual(producto):
    """Obtener el precio más reciente del historial de precios"""
    if producto.historial_precios and len(producto.historial_precios) > 0:
        ultimo_precio = producto.historial_precios[0]
        return {
            "precio_neto": float(ultimo_precio.precio_neto),
            "precio_bruto": float(ultimo_precio.precio_bruto),
            "descuento": float(ultimo_precio.descuento) if ultimo_precio.descuento else 0
        }
    return {
        "precio_neto": 0,
        "precio_bruto": 0,
        "descuento": 0
    }


@productos_router.get("/productos", response_model=list[ProductResponse])
async def obtener_productos(db: Session = Depends(get_db)):
    """Obtener todos los productos"""
    try:
        productos = db.query(ProductoDB).all()

        resultado = []
        for producto in productos:
            precios = obtener_precio_actual(producto)
            producto_dict = {
                "id": producto.id,
                "nombre": producto.nombre,
                "codigo_ska": producto.codigo_ska,
                "unidades": producto.unidades,
                "descripcion": producto.descripcion,
                "tipo_producto_id": producto.tipo_producto_id,
                "tipo_producto": producto.tipo_producto.nombre if producto.tipo_producto else None,
                "imagen_url": f"/productos/{producto.id}/imagen" if producto.imagen else None,
                "precio_neto": precios["precio_neto"],
                "iva": 19,  # IVA fijo
                "precio_bruto": precios["precio_bruto"],
                "descuento": precios["descuento"]
            }
            resultado.append(ProductResponse(**producto_dict))

        return resultado
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(error)}")


@productos_router.get("/productos/{producto_id}", response_model=ProductResponse)
async def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID"""
    try:
        producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        precios = obtener_precio_actual(producto)
        producto_dict = {
            "id": producto.id,
            "nombre": producto.nombre,
            "codigo_ska": producto.codigo_ska,
            "unidades": producto.unidades,
            "descripcion": producto.descripcion,
            "tipo_producto_id": producto.tipo_producto_id,
            "tipo_producto": producto.tipo_producto.nombre if producto.tipo_producto else None,
            "imagen_url": f"/productos/{producto.id}/imagen" if producto.imagen else None,
            "precio_neto": precios["precio_neto"],
            "iva": 19,
            "precio_bruto": precios["precio_bruto"],
            "descuento": precios["descuento"]
        }

        return ProductResponse(**producto_dict)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(error)}")


@productos_router.get("/productos/{producto_id}/imagen")
async def obtener_imagen_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener la imagen de un producto"""
    try:
        producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

        if not producto or not producto.imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada")

        return Response(content=producto.imagen, media_type="image/png")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener imagen: {str(error)}")


@productos_router.post("/productos", response_model=ProductResponse, status_code=201)
async def crear_producto(
    nombre: str = Form(...),
    codigo_ska: str = Form(None),
    unidades: int = Form(0),
    descripcion: str = Form(None),
    tipo_producto_id: int = Form(None),
    precio_neto: float = Form(0),
    iva: float = Form(19),
    precio_bruto: float = Form(0),
    descuento: float = Form(0),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto con imagen opcional de 100x100"""
    try:
        # Validar que el tipo de producto existe si se proporciona
        if tipo_producto_id is not None:
            tipo_existe = db.query(TipoProductoDB).filter(TipoProductoDB.id == tipo_producto_id).first()
            if not tipo_existe:
                raise HTTPException(
                    status_code=400,
                    detail=f"El tipo de producto con ID {tipo_producto_id} no existe"
                )

        imagen_bytes = None

        if imagen:
            # Leer la imagen
            imagen_contenido = await imagen.read()

            # Validar y redimensionar la imagen a 100x100
            img = Image.open(io.BytesIO(imagen_contenido))

            # Verificar que sea una imagen válida
            if img.format not in ['PNG', 'JPEG', 'JPG']:
                raise HTTPException(
                    status_code=400,
                    detail="Solo se aceptan imágenes PNG o JPEG"
                )

            # Redimensionar a 100x100
            img_resized = img.resize((100, 100), Image.Resampling.LANCZOS)

            # Convertir a bytes
            img_buffer = io.BytesIO()
            img_resized.save(img_buffer, format='PNG')
            imagen_bytes = img_buffer.getvalue()

        # Crear el producto (sin campos de precio)
        nuevo_producto = ProductoDB(
            nombre=nombre,
            codigo_ska=codigo_ska,
            unidades=unidades,
            descripcion=descripcion,
            tipo_producto_id=tipo_producto_id,
            imagen=imagen_bytes
        )

        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)

        # Crear el registro de precio en historial_precio_producto
        if precio_neto > 0 or precio_bruto > 0:
            historial_precio = HistorialPrecioProductoDB(
                precio_neto=precio_neto,
                precio_bruto=precio_bruto,
                descuento=descuento,
                producto=nuevo_producto.id,
                usuario_id=None  # Podría obtenerlo del token de autenticación
            )
            db.add(historial_precio)
            db.commit()
            db.refresh(nuevo_producto)

        precios = obtener_precio_actual(nuevo_producto)
        producto_dict = {
            "id": nuevo_producto.id,
            "nombre": nuevo_producto.nombre,
            "codigo_ska": nuevo_producto.codigo_ska,
            "unidades": nuevo_producto.unidades,
            "descripcion": nuevo_producto.descripcion,
            "tipo_producto_id": nuevo_producto.tipo_producto_id,
            "tipo_producto": nuevo_producto.tipo_producto.nombre if nuevo_producto.tipo_producto else None,
            "imagen_url": f"/productos/{nuevo_producto.id}/imagen" if nuevo_producto.imagen else None,
            "precio_neto": precios["precio_neto"],
            "iva": 19,
            "precio_bruto": precios["precio_bruto"],
            "descuento": precios["descuento"]
        }

        return ProductResponse(**producto_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(error)}")


@productos_router.put("/productos/{producto_id}", response_model=ProductResponse)
async def actualizar_producto(
    producto_id: int,
    nombre: str = Form(None),
    codigo_ska: str = Form(None),
    unidades: int = Form(None),
    descripcion: str = Form(None),
    tipo_producto_id: int = Form(None),
    precio_neto: float = Form(None),
    iva: float = Form(None),
    precio_bruto: float = Form(None),
    descuento: float = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Actualizar un producto existente"""
    try:
        producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Validar que el tipo de producto existe si se proporciona
        if tipo_producto_id is not None:
            tipo_existe = db.query(TipoProductoDB).filter(TipoProductoDB.id == tipo_producto_id).first()
            if not tipo_existe:
                raise HTTPException(
                    status_code=400,
                    detail=f"El tipo de producto con ID {tipo_producto_id} no existe"
                )

        # Actualizar campos del producto si se proporcionan
        if nombre is not None:
            producto.nombre = nombre
        if codigo_ska is not None:
            producto.codigo_ska = codigo_ska
        if unidades is not None:
            producto.unidades = unidades
        if descripcion is not None:
            producto.descripcion = descripcion
        if tipo_producto_id is not None:
            producto.tipo_producto_id = tipo_producto_id

        # Actualizar imagen si se proporciona
        if imagen:
            imagen_contenido = await imagen.read()
            img = Image.open(io.BytesIO(imagen_contenido))

            if img.format not in ['PNG', 'JPEG', 'JPG']:
                raise HTTPException(
                    status_code=400,
                    detail="Solo se aceptan imágenes PNG o JPEG"
                )

            # Redimensionar a 100x100
            img_resized = img.resize((100, 100), Image.Resampling.LANCZOS)
            img_buffer = io.BytesIO()
            img_resized.save(img_buffer, format='PNG')
            producto.imagen = img_buffer.getvalue()

        db.commit()

        # Si se proporcionan nuevos precios, crear un nuevo registro en el historial
        if precio_neto is not None or precio_bruto is not None or descuento is not None:
            # Obtener precios actuales para valores por defecto
            precios_actuales = obtener_precio_actual(producto)

            nuevo_precio_neto = precio_neto if precio_neto is not None else precios_actuales["precio_neto"]
            nuevo_precio_bruto = precio_bruto if precio_bruto is not None else precios_actuales["precio_bruto"]
            nuevo_descuento = descuento if descuento is not None else precios_actuales["descuento"]

            # Solo crear nuevo registro si hay cambios en los precios
            if (nuevo_precio_neto != precios_actuales["precio_neto"] or
                nuevo_precio_bruto != precios_actuales["precio_bruto"] or
                nuevo_descuento != precios_actuales["descuento"]):
                historial_precio = HistorialPrecioProductoDB(
                    precio_neto=nuevo_precio_neto,
                    precio_bruto=nuevo_precio_bruto,
                    descuento=nuevo_descuento,
                    producto=producto.id,
                    usuario_id=None
                )
                db.add(historial_precio)
                db.commit()

        db.refresh(producto)
        precios = obtener_precio_actual(producto)

        producto_dict = {
            "id": producto.id,
            "nombre": producto.nombre,
            "codigo_ska": producto.codigo_ska,
            "unidades": producto.unidades,
            "descripcion": producto.descripcion,
            "tipo_producto_id": producto.tipo_producto_id,
            "tipo_producto": producto.tipo_producto.nombre if producto.tipo_producto else None,
            "imagen_url": f"/productos/{producto.id}/imagen" if producto.imagen else None,
            "precio_neto": precios["precio_neto"],
            "iva": 19,
            "precio_bruto": precios["precio_bruto"],
            "descuento": precios["descuento"]
        }

        return ProductResponse(**producto_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(error)}")


@productos_router.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """Eliminar un producto"""
    try:
        producto = db.query(ProductoDB).filter(ProductoDB.id == producto_id).first()

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        db.delete(producto)
        db.commit()

        return {"status": "success", "message": "Producto eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(error)}")


@productos_router.get("/tipos-producto", response_model=list[TipoProductoResponse])
async def obtener_tipos_producto(db: Session = Depends(get_db)):
    """Obtener todos los tipos de producto"""
    try:
        tipos = db.query(TipoProductoDB).all()
        return tipos
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos de producto: {str(error)}")


@productos_router.get("/tipos-producto/{tipo_id}", response_model=TipoProductoResponse)
async def obtener_tipo_producto(tipo_id: int, db: Session = Depends(get_db)):
    """Obtener un tipo de producto por ID"""
    try:
        tipo = db.query(TipoProductoDB).filter(TipoProductoDB.id == tipo_id).first()

        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")

        return tipo
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipo de producto: {str(error)}")


@productos_router.post("/tipos-producto", response_model=TipoProductoResponse, status_code=201)
async def crear_tipo_producto(
    nombre: str = Form(...),
    descripcion: str = Form(None),
    db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de producto"""
    try:
        # Verificar si el nombre ya existe
        tipo_existente = db.query(TipoProductoDB).filter(TipoProductoDB.nombre == nombre).first()
        if tipo_existente:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de producto con ese nombre")

        nuevo_tipo = TipoProductoDB(
            nombre=nombre,
            descripcion=descripcion
        )

        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)

        return nuevo_tipo
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear tipo de producto: {str(error)}")


@productos_router.put("/tipos-producto/{tipo_id}", response_model=TipoProductoResponse)
async def actualizar_tipo_producto(
    tipo_id: int,
    nombre: str = Form(None),
    descripcion: str = Form(None),
    db: Session = Depends(get_db)
):
    """Actualizar un tipo de producto existente"""
    try:
        tipo = db.query(TipoProductoDB).filter(TipoProductoDB.id == tipo_id).first()

        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")

        # Verificar si el nuevo nombre ya existe en otro tipo
        if nombre is not None and nombre != tipo.nombre:
            nombre_existente = db.query(TipoProductoDB).filter(
                TipoProductoDB.nombre == nombre,
                TipoProductoDB.id != tipo_id
            ).first()
            if nombre_existente:
                raise HTTPException(status_code=400, detail="Ya existe un tipo de producto con ese nombre")

        # Actualizar campos si se proporcionan
        if nombre is not None:
            tipo.nombre = nombre
        if descripcion is not None:
            tipo.descripcion = descripcion

        db.commit()
        db.refresh(tipo)

        return tipo
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar tipo de producto: {str(error)}")


@productos_router.delete("/tipos-producto/{tipo_id}")
async def eliminar_tipo_producto(tipo_id: int, db: Session = Depends(get_db)):
    """Eliminar un tipo de producto"""
    try:
        tipo = db.query(TipoProductoDB).filter(TipoProductoDB.id == tipo_id).first()

        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")

        # Verificar si hay productos usando este tipo
        productos_con_tipo = db.query(ProductoDB).filter(ProductoDB.tipo_producto_id == tipo_id).count()
        if productos_con_tipo > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar: hay {productos_con_tipo} producto(s) usando este tipo"
            )

        db.delete(tipo)
        db.commit()

        return {"status": "success", "message": "Tipo de producto eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar tipo de producto: {str(error)}")