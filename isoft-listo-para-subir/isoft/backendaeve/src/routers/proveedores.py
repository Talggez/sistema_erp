from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from models.proveedores import (
    ProveedorDB, ProveedorCreate, ProveedorUpdate, ProveedorResponse
)

proveedores_router = APIRouter(tags=["Proveedores"])


@proveedores_router.get("/proveedores", response_model=list[ProveedorResponse])
async def obtener_proveedores(db: Session = Depends(get_db)):
    """Obtener todos los proveedores"""
    try:
        proveedores = db.query(ProveedorDB).all()
        return proveedores
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedores: {str(error)}")


@proveedores_router.get("/proveedores/{proveedor_id}", response_model=ProveedorResponse)
async def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    """Obtener un proveedor por ID"""
    try:
        proveedor = db.query(ProveedorDB).filter(ProveedorDB.id == proveedor_id).first()

        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        return proveedor
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedor: {str(error)}")


@proveedores_router.post("/nuevo_proveedor", response_model=ProveedorResponse, status_code=201)
async def crear_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo proveedor"""
    try:
        # Verificar si el RUT ya existe
        proveedor_existente = db.query(ProveedorDB).filter(ProveedorDB.rut == proveedor.rut).first()
        if proveedor_existente:
            raise HTTPException(status_code=400, detail="El RUT ya está registrado")

        # Crear nuevo proveedor
        nuevo_proveedor = ProveedorDB(**proveedor.model_dump())
        db.add(nuevo_proveedor)
        db.commit()
        db.refresh(nuevo_proveedor)

        return nuevo_proveedor
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear proveedor: {str(error)}")


@proveedores_router.put("/actualizar_proveedores/{proveedor_id}", response_model=ProveedorResponse)
async def actualizar_proveedor(proveedor_id: int, proveedor_data: ProveedorUpdate, db: Session = Depends(get_db)):
    """Actualizar un proveedor existente"""
    try:
        proveedor = db.query(ProveedorDB).filter(ProveedorDB.id == proveedor_id).first()

        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        # Actualizar solo los campos proporcionados
        update_data = proveedor_data.model_dump(exclude_unset=True)

        # Si se intenta actualizar el RUT, verificar que no exista otro proveedor con ese RUT
        if 'rut' in update_data and update_data['rut'] != proveedor.rut:
            rut_existente = db.query(ProveedorDB).filter(
                ProveedorDB.rut == update_data['rut'],
                ProveedorDB.id != proveedor_id
            ).first()
            if rut_existente:
                raise HTTPException(status_code=400, detail="El RUT ya está registrado en otro proveedor")

        for key, value in update_data.items():
            setattr(proveedor, key, value)

        db.commit()
        db.refresh(proveedor)

        return proveedor
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar proveedor: {str(error)}")


@proveedores_router.delete("/eliminar_proveedor/{proveedor_id}")
async def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    """Eliminar un proveedor"""
    try:
        proveedor = db.query(ProveedorDB).filter(ProveedorDB.id == proveedor_id).first()

        if not proveedor:
            raise HTTPException(status_code=404, detail=f"Proveedor con ID {proveedor_id} no encontrado")

        db.delete(proveedor)
        db.commit()

        return {
            "success": True,
            "message": f"Proveedor con ID {proveedor_id} eliminado exitosamente",
            "id": proveedor_id
        }
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar proveedor: {str(error)}")
