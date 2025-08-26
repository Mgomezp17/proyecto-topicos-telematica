import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, files, public
from .database import create_tables

# Crear la aplicación FastAPI
app = FastAPI(
    title="GridDFS NameNode",
    description="Sistema de archivos distribuido por bloques - NameNode",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(public.router)


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    # Crear las tablas de la base de datos
    create_tables()
    print("NameNode iniciado correctamente")
    print(f"Block size configurado: {os.getenv('BLOCK_SIZE', '67108864')} bytes")


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "GridDFS NameNode", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "service": "namenode"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
