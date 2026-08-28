from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db
from models.user_model import (
    UsuarioDB, UserUpdate, UserResponse, PasswordChange,
    CargoDB, RolDB, ContrasenaDB
)

perfil_router = APIRouter(tags=["Perfil"])


@perfil_router.get("/perfil/{usuario_id}", response_model=UserResponse)
async def obtener_perfil(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener información del perfil del usuario"""
    try:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Obtener cargo y rol
        cargo = db.query(CargoDB).filter(CargoDB.id == usuario.cargo_id).first()
        rol = db.query(RolDB).filter(RolDB.id == usuario.rol_id).first()

        user_dict = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellidos": usuario.apellidos,
            "email": usuario.email,
            "rut": usuario.rut,
            "telefono": usuario.telefono,
            "direccion": usuario.direccion,
            "cargo": cargo.nombre if cargo else None,
            "rol": rol.nombre if rol else None
        }

        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al obtener perfil: {str(error)}")


@perfil_router.put("/perfil/{usuario_id}", response_model=UserResponse)
async def actualizar_perfil(usuario_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Actualizar información del perfil del usuario"""
    try:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Actualizar solo los campos proporcionados
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(usuario, key, value)

        db.commit()
        db.refresh(usuario)

        # Obtener cargo y rol actualizados
        cargo = db.query(CargoDB).filter(CargoDB.id == usuario.cargo_id).first()
        rol = db.query(RolDB).filter(RolDB.id == usuario.rol_id).first()

        user_dict = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellidos": usuario.apellidos,
            "email": usuario.email,
            "rut": usuario.rut,
            "telefono": usuario.telefono,
            "direccion": usuario.direccion,
            "cargo": cargo.nombre if cargo else None,
            "rol": rol.nombre if rol else None
        }

        return UserResponse(**user_dict)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar perfil: {str(error)}")


@perfil_router.post("/perfil/{usuario_id}/cambiar-contrasena")
async def cambiar_contrasena(usuario_id: int, password_data: PasswordChange, db: Session = Depends(get_db)):
    """Cambiar la contraseña del usuario"""
    try:
        # Verificar que el usuario existe
        usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Validar la contraseña actual usando la función de PostgreSQL
        query = text("""
            SELECT validar_contrasena(:usuario_id, :password) AS login_exitoso
        """)
        result = db.execute(query, {
            "usuario_id": usuario_id,
            "password": password_data.current_password
        })
        password_valida = result.scalar()

        if not password_valida:
            raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")

        # Guardar la contraseña antigua como temporal (opcional)
        contrasena_actual = db.query(ContrasenaDB).filter(
            ContrasenaDB.usuario_id == usuario_id
        ).order_by(ContrasenaDB.fecha_ultima_contrasena.desc()).first()

        # Crear nueva contraseña (el trigger la encriptará automáticamente)
        nueva_contrasena = ContrasenaDB(
            contrasena=password_data.new_password,
            contrasena_temporal=contrasena_actual.contrasena if contrasena_actual else None,
            usuario_id=usuario_id
        )

        db.add(nueva_contrasena)
        db.commit()

        return {
            "status": "success",
            "message": "Contraseña actualizada correctamente"
        }
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cambiar contraseña: {str(error)}")
