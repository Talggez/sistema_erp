# src/models/__init__.py
from .product import ProductoDB, ProductCreate, ProductUpdate, ProductResponse
from .user_model import UsuarioDB, LoginData, UserResponse
from .clientes import ClienteDB, ClienteCreate, ClienteUpdate, ClienteResponse
from .ventas import VentaDB, VentaCreate, VentaUpdate, VentaResponse

__all__ = [
    "ProductoDB", "ProductCreate", "ProductUpdate", "ProductResponse",
    "UsuarioDB", "LoginData", "UserResponse",
    "ClienteDB", "ClienteCreate", "ClienteUpdate", "ClienteResponse",
    "VentaDB", "VentaCreate", "VentaUpdate", "VentaResponse"
]
