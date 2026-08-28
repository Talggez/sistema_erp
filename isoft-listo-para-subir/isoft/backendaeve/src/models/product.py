from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Float, TIMESTAMP, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Base


# Modelos SQLAlchemy
class TipoProductoDB(Base):
    __tablename__ = "tipo_producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)

    productos = relationship("ProductoDB", back_populates="tipo_producto")


class ProductoDB(Base):
    __tablename__ = "producto"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    imagen = Column(LargeBinary)  # Para almacenar imagen como BYTEA
    codigo_ska = Column(String(50), index=True)
    unidades = Column(Integer, default=0)
    descripcion = Column(String)
    tipo_producto_id = Column(Integer, ForeignKey("tipo_producto.id"), nullable=True)

    tipo_producto = relationship("TipoProductoDB", back_populates="productos")
    historial_precios = relationship("HistorialPrecioProductoDB", back_populates="producto_rel", order_by="desc(HistorialPrecioProductoDB.fecha_precio)")


class HistorialPrecioProductoDB(Base):
    __tablename__ = "historial_precio_producto"

    id = Column(Integer, primary_key=True, index=True)
    precio_bruto = Column(Numeric(12, 2), nullable=False)
    precio_neto = Column(Numeric(12, 2), nullable=False)
    descuento = Column(Numeric(5, 2), default=0)
    fecha_precio = Column(TIMESTAMP, server_default=func.now())
    producto = Column(Integer, ForeignKey("producto.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True)

    producto_rel = relationship("ProductoDB", back_populates="historial_precios")


# Modelos Pydantic
class ProductCreate(BaseModel):
    nombre: str
    codigo_ska: str | None = None
    unidades: int = 0
    descripcion: str | None = None
    tipo_producto_id: int | None = None
    precio_neto: float = 0
    iva: float = 19
    precio_bruto: float = 0
    descuento: float = 0


class ProductUpdate(BaseModel):
    nombre: str | None = None
    codigo_ska: str | None = None
    unidades: int | None = None
    descripcion: str | None = None
    tipo_producto_id: int | None = None
    precio_neto: float | None = None
    iva: float | None = None
    precio_bruto: float | None = None
    descuento: float | None = None


class HistorialPrecioResponse(BaseModel):
    id: int
    precio_bruto: float
    precio_neto: float
    descuento: float
    fecha_precio: str | None = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    nombre: str
    codigo_ska: str | None
    unidades: int
    descripcion: str | None
    tipo_producto_id: int | None
    tipo_producto: str | None = None
    imagen_url: str | None = None
    precio_neto: float = 0
    iva: float = 19
    precio_bruto: float = 0
    descuento: float = 0

    class Config:
        from_attributes = True


class TipoProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None

    class Config:
        from_attributes = True
