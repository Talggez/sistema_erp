from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils.database import Base
from typing import Optional


# Modelo SQLAlchemy
class ProveedorDB(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rut = Column(String(20), unique=True, nullable=False, index=True)
    direccion = Column(String(300))
    telefono = Column(String(20))
    email = Column(String(100))
    web = Column(String(200))
    descripcion = Column(String)


# Modelos Pydantic
class ProveedorCreate(BaseModel):
    nombre: str
    rut: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None
    descripcion: Optional[str] = None


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    rut: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None
    descripcion: Optional[str] = None


class ProveedorResponse(BaseModel):
    id: int
    nombre: str
    rut: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True
