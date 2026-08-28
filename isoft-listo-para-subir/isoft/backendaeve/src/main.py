from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from utils.database import get_db, init_db, engine, SessionLocal

# Importar routers
from routers.login import login_router
from routers.clientes import clientes_router
from routers.ventas import sales_router
from routers.productos import productos_router
from routers.perfil import perfil_router
from routers.proveedores import proveedores_router
#descripcion fast api
app = FastAPI(
    title="AEVE ERP",
    description="API para AEVE ERP con PostgreSQL",
    version="1.0.0",
    tags=["Inicio"]
)

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(login_router)
app.include_router(clientes_router)
app.include_router(sales_router)
app.include_router(productos_router)
app.include_router(perfil_router)
app.include_router(proveedores_router)

@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la aplicación"""
    try:
        init_db()
        print("✅ Base de datos inicializada correctamente")

        # Inicializar datos por defecto
        from models.product import TipoProductoDB
        db = SessionLocal()
        try:
            # Verificar si ya existen tipos de producto
            tipos_count = db.query(TipoProductoDB).count()
            if tipos_count == 0:
                print("📦 Inicializando tipos de producto...")
                tipos_default = [
                    TipoProductoDB(id=1, nombre="Electrónico", descripcion="Productos electrónicos y tecnología"),
                    TipoProductoDB(id=2, nombre="Accesorio", descripcion="Accesorios y complementos"),
                    TipoProductoDB(id=3, nombre="Otro", descripcion="Otros productos")
                ]
                db.add_all(tipos_default)
                db.commit()
                print("✅ Tipos de producto creados correctamente")
        except Exception as e:
            print(f"⚠️ Error al inicializar tipos de producto: {e}")
            db.rollback()
        finally:
            db.close()

        print("✅ Routers registrados: login, clientes, ventas, productos, perfil, proveedores")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")

@app.get("/")
async def welcome_api():
    return "The API is working now, good luck with everything!!"

@app.get("/health/db")
async def check_database_connection(db: Session = Depends(get_db)):
    """
    Endpoint para verificar la conexión a la base de datos PostgreSQL
    """
    try:
        # Intentar ejecutar una consulta simple
        result = db.execute(text("SELECT 1")).scalar()

        # Obtener información de la base de datos
        db_version = db.execute(text("SELECT version()")).scalar()

        return {
            "status": "connected",
            "message": "Conexión a PostgreSQL exitosa",
            "test_query_result": result,
            "database_version": db_version
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Error al conectar con la base de datos",
            "error": str(e)
        }


