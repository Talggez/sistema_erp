from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime


# Modelos SQLAlchemy
class VentaDB(Base):
    __tablename__ = "venta"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(TIMESTAMP, default=datetime.utcnow)
    n_documento = Column(String(50), unique=True, nullable=False, index=True)
    cliente = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    estado_venta = Column(String(50))
    tipo_pago = Column(String(50))
    observacion = Column(String)
    canal_venta = Column(String(50))
    estado_dte = Column(String(50))
    tipo_dte = Column(String(50))
    usuario_vendedor = Column(Integer, ForeignKey("usuario.id"))

    # Relaciones (nota: necesitar�s importar ClienteDB y UsuarioDB)
    detalles = relationship("DetalleVentaDB", back_populates="venta")
    pagos = relationship("PagoVentaDB", back_populates="venta")


class DetalleVentaDB(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True, index=True)
    cantidad_producto = Column(Integer, nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("venta.id"))

    venta = relationship("VentaDB", back_populates="detalles")


class PagoVentaDB(Base):
    __tablename__ = "pago_venta"

    id = Column(Integer, primary_key=True, index=True)
    fecha_pago = Column(TIMESTAMP, nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    tipo_pago = Column(String(50), nullable=False)
    referencia = Column(String(100))
    observacion = Column(String)
    venta_id = Column(Integer, ForeignKey("venta.id"), nullable=False)

    venta = relationship("VentaDB", back_populates="pagos")


# Modelos Pydantic
class DetalleVentaCreate(BaseModel):
    cantidad_producto: int
    id_producto: int


class DetalleVentaResponse(BaseModel):
    id: int
    cantidad_producto: int
    id_producto: int
    nombre_producto: str | None = None
    precio_unitario: float | None = None

    class Config:
        from_attributes = True


class PagoVentaCreate(BaseModel):
    fecha_pago: datetime
    monto: float
    tipo_pago: str
    referencia: str | None = None
    observacion: str | None = None


class PagoVentaResponse(BaseModel):
    id: int
    fecha_pago: datetime
    monto: float
    tipo_pago: str
    referencia: str | None
    observacion: str | None

    class Config:
        from_attributes = True


class VentaCreate(BaseModel):
    n_documento: str
    cliente: int
    estado_venta: str | None = "Pendiente"
    tipo_pago: str | None = None
    observacion: str | None = None
    canal_venta: str | None = None
    estado_dte: str | None = None
    tipo_dte: str | None = None
    detalles: list[DetalleVentaCreate] = []


class VentaUpdate(BaseModel):
    estado_venta: str | None = None
    tipo_pago: str | None = None
    observacion: str | None = None
    estado_dte: str | None = None
    tipo_dte: str | None = None


class VentaResponse(BaseModel):
    id: int
    fecha: datetime
    n_documento: str
    cliente: int
    estado_venta: str | None
    tipo_pago: str | None
    observacion: str | None
    canal_venta: str | None
    estado_dte: str | None
    tipo_dte: str | None
    usuario_vendedor: int | None
    nombre_cliente: str | None = None
    detalles: list[DetalleVentaResponse] = []
    pagos: list[PagoVentaResponse] = []

    class Config:
        from_attributes = True
