from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from models.clientes import (
    ClienteDB, ClienteCreate, ClienteUpdate, ClienteResponse,
    TipoClienteDB, TipoClienteResponse
)

clientes_router = APIRouter(tags=["Clientes"])


@clientes_router.get("/clientes", response_model=list[ClienteResponse])
async def obtener_clientes(db: Session = Depends(get_db)):
    """Obtener todos los clientes activos"""
    try:
        clientes = db.query(ClienteDB).filter(ClienteDB.activo == True).all()

        # Formatear respuesta con el tipo de cliente
        resultado = []
        for cliente in clientes:
            cliente_dict = {
                "id": cliente.id,
                "nombre": cliente.nombre,
                "rut": cliente.rut,
                "razon_social": cliente.razon_social,
                "apellidos": cliente.apellidos,
                "email": cliente.email,
                "comuna": cliente.comuna,
                "direccion": cliente.direccion,
                "ciudad": cliente.ciudad,
                "activo": cliente.activo,
                "fecha_registro": cliente.fecha_registro,
                "tipo_cliente_id": cliente.tipo_cliente_id,
                "tipo_cliente": cliente.tipo_cliente.nombre if cliente.tipo_cliente else None
            }
            resultado.append(ClienteResponse(**cliente_dict))

        return resultado
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener clientes: {str(error)}")


@clientes_router.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por ID"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()

        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        cliente_dict = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "rut": cliente.rut,
            "razon_social": cliente.razon_social,
            "apellidos": cliente.apellidos,
            "email": cliente.email,
            "comuna": cliente.comuna,
            "direccion": cliente.direccion,
            "ciudad": cliente.ciudad,
            "activo": cliente.activo,
            "fecha_registro": cliente.fecha_registro,
            "tipo_cliente_id": cliente.tipo_cliente_id,
            "tipo_cliente": cliente.tipo_cliente.nombre if cliente.tipo_cliente else None
        }

        return ClienteResponse(**cliente_dict)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener cliente: {str(error)}")


@clientes_router.post("/clientes", response_model=ClienteResponse, status_code=201)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    try:
        # Verificar si el RUT ya existe
        cliente_existente = db.query(ClienteDB).filter(ClienteDB.rut == cliente.rut).first()
        if cliente_existente:
            raise HTTPException(status_code=400, detail="El RUT ya esta registrado")

        # Crear nuevo cliente
        nuevo_cliente = ClienteDB(**cliente.model_dump())
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)

        cliente_dict = {
            "id": nuevo_cliente.id,
            "nombre": nuevo_cliente.nombre,
            "rut": nuevo_cliente.rut,
            "razon_social": nuevo_cliente.razon_social,
            "apellidos": nuevo_cliente.apellidos,
            "email": nuevo_cliente.email,
            "comuna": nuevo_cliente.comuna,
            "direccion": nuevo_cliente.direccion,
            "ciudad": nuevo_cliente.ciudad,
            "activo": nuevo_cliente.activo,
            "fecha_registro": nuevo_cliente.fecha_registro,
            "tipo_cliente_id": nuevo_cliente.tipo_cliente_id,
            "tipo_cliente": nuevo_cliente.tipo_cliente.nombre if nuevo_cliente.tipo_cliente else None
        }

        return ClienteResponse(**cliente_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(error)}")


@clientes_router.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(cliente_id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db)):
    """Actualizar un cliente existente"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()

        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Actualizar solo los campos proporcionados
        update_data = cliente_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cliente, key, value)

        db.commit()
        db.refresh(cliente)

        cliente_dict = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "rut": cliente.rut,
            "razon_social": cliente.razon_social,
            "apellidos": cliente.apellidos,
            "email": cliente.email,
            "comuna": cliente.comuna,
            "direccion": cliente.direccion,
            "ciudad": cliente.ciudad,
            "activo": cliente.activo,
            "fecha_registro": cliente.fecha_registro,
            "tipo_cliente_id": cliente.tipo_cliente_id,
            "tipo_cliente": cliente.tipo_cliente.nombre if cliente.tipo_cliente else None
        }

        return ClienteResponse(**cliente_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(error)}")


@clientes_router.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Eliminar (desactivar) un cliente"""
    try:
        cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()

        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Desactivar en lugar de eliminar
        cliente.activo = False
        db.commit()

        return {"status": "success", "message": "Cliente desactivado correctamente"}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(error)}")


@clientes_router.get("/tipos-cliente", response_model=list[TipoClienteResponse])
async def obtener_tipos_cliente(db: Session = Depends(get_db)):
    """Obtener todos los tipos de cliente"""
    try:
        tipos = db.query(TipoClienteDB).all()
        return tipos
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos de cliente: {str(error)}")
