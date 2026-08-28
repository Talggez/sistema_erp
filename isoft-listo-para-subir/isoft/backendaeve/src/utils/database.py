from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Obtener las credenciales de la base de datos desde variables de entorno
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "aeve_erp")

# Construir la URL de conexion a PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica la conexion antes de usarla
    pool_size=10,  # Numero de conexiones en el pool
    max_overflow=20,  # Conexiones adicionales si el pool esta lleno
    echo=False  # Cambiar a True para ver las consultas SQL en los logs
)

# Crear una sesion local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesion de base de datos
def get_db():
    """
    Genera una sesion de base de datos y la cierra automaticamente despues de su uso.
    Usala como dependencia en tus rutas de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funcion para inicializar la base de datos
def init_db():
    """
    Crea todas las tablas definidas en los modelos.
    Ejecuta esto al iniciar la aplicacion.
    """
    Base.metadata.create_all(bind=engine)
