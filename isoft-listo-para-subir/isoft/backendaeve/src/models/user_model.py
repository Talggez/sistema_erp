from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime


# Modelos SQLAlchemy para la base de datos
class UsuarioDB(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellidos = Column(String(100))
    email = Column(String(150), unique=True, nullable=False, index=True)
    rut = Column(String(12), unique=True)
    telefono = Column(String(20))
    direccion = Column(String(255))
    cargo_id = Column(Integer, ForeignKey("cargo.id"))
    rol_id = Column(Integer, ForeignKey("rol.id"))

    # Relaciones
    cargo = relationship("CargoDB", back_populates="usuarios")
    rol = relationship("RolDB", back_populates="usuarios")
    contrasenas = relationship("ContrasenaDB", back_populates="usuario")


class CargoDB(Base):
    __tablename__ = "cargo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)

    usuarios = relationship("UsuarioDB", back_populates="cargo")


class RolDB(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)

    usuarios = relationship("UsuarioDB", back_populates="rol")


class ContrasenaDB(Base):
    __tablename__ = "contrasena"

    id = Column(Integer, primary_key=True, index=True)
    contrasena_temporal = Column(String(255))
    contrasena = Column(String(255), nullable=False)
    fecha_ultima_contrasena = Column(TIMESTAMP, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)

    usuario = relationship("UsuarioDB", back_populates="contrasenas")


# Modelos Pydantic para validación
class LoginData(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    apellidos: str
    email: str
    rut: str | None
    telefono: str | None
    direccion: str | None
    cargo: str | None
    rol: str | None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nombre: str | None = None
    apellidos: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    rut: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
