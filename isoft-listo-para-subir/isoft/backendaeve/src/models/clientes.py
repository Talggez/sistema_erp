from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import date


# Modelos SQLAlchemy
class TipoClienteDB(Base):
    __tablename__ = "tipo_cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)

    clientes = relationship("ClienteDB", back_populates="tipo_cliente")


class ClienteDB(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    rut = Column(String(12), unique=True, nullable=False, index=True)
    razon_social = Column(String(200))
    apellidos = Column(String(100))
    email = Column(String(150))
    comuna = Column(String(100))
    direccion = Column(String(255))
    ciudad = Column(String(100))
    activo = Column(Boolean, default=True)
    fecha_registro = Column(Date, default=date.today)
    tipo_cliente_id = Column(Integer, ForeignKey("tipo_cliente.id"))

    tipo_cliente = relationship("TipoClienteDB", back_populates="clientes")


# Modelos Pydantic
class ClienteCreate(BaseModel):
    nombre: str
    rut: str
    razon_social: str | None = None
    apellidos: str | None = None
    email: str | None = None
    comuna: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    tipo_cliente_id: int | None = None


class ClienteUpdate(BaseModel):
    nombre: str | None = None
    rut: str | None = None
    razon_social: str | None = None
    apellidos: str | None = None
    email: str | None = None
    comuna: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    activo: bool | None = None
    tipo_cliente_id: int | None = None


class ClienteResponse(BaseModel):
    id: int
    nombre: str
    rut: str
    razon_social: str | None
    apellidos: str | None
    email: str | None
    comuna: str | None
    direccion: str | None
    ciudad: str | None
    activo: bool
    fecha_registro: date
    tipo_cliente_id: int | None
    tipo_cliente: str | None = None

    class Config:
        from_attributes = True


class TipoClienteResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None

    class Config:
        from_attributes = True
