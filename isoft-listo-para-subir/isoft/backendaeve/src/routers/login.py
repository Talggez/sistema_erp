from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db
from models.user_model import LoginData, UsuarioDB, CargoDB, RolDB

login_router = APIRouter(tags=["Autenticación"])


@login_router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    """
    Endpoint de login que valida credenciales usando la función
    validar_contrasena de PostgreSQL con bcrypt
    """
    email = data.email
    password = data.password

    try:
        # Buscar el usuario por email
        usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()

        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Validar la contraseña usando la función de PostgreSQL
        query = text("""
            SELECT validar_contrasena(:usuario_id, :password) AS login_exitoso
        """)
        result = db.execute(query, {"usuario_id": usuario.id, "password": password})
        login_exitoso = result.scalar()

        if not login_exitoso:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Obtener información del cargo y rol
        cargo = db.query(CargoDB).filter(CargoDB.id == usuario.cargo_id).first()
        rol = db.query(RolDB).filter(RolDB.id == usuario.rol_id).first()

        return {
            "status": "success",
            "message": "Inicio de sesión exitoso",
            "userId": usuario.id,
            "userRut": usuario.rut,
            "userName": usuario.nombre,
            "userEmail": usuario.email,
            "userRole": rol.nombre if rol else None,
            "userCargo": cargo.nombre if cargo else None
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(error)}")


@login_router.get("/verify-session")
async def verify_session(db: Session = Depends(get_db)):
    """
    Endpoint para verificar si hay una sesión activa
    """
    return {"status": "active"}
