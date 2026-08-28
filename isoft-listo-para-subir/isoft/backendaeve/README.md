# Configuraciones de FastAPI

Primero hemos de crear un archivo de configuración para nuestro servidor de FastAPI. Para ello, abrimos un terminal y ejecutamos el siguiente comando:

```bash
cd src/
python -m venv venv
```

Despues de ejecutar el comando anterior, se creará un directorio llamado `venv` dentro del directorio `src/`. Este directorio contiene toda la información necesaria para ejecutar nuestro servidor de FastAPI.
Donde solo hemos de ejecutar los siguientes comandos:

```bash
venv/Scripts/activate # para windows
source venv/bin/activate # para linux
```

Bibliotecas a instalar

```bash
pip install fastapi uvicorn supabase pandas python-dotenv
```

Una vez hemos instalado FastAPI y uvicorn, podemos crear un archivo de configuración para nuestro servidor de FastAPI. Para ello, ejecutamos el siguiente comando:

```bash
uvicorn main:app --reload --port 5000
```
