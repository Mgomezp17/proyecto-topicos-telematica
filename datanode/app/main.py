from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import blocks
import os

# Crear la aplicación FastAPI
app = FastAPI(
    title="GridDFS DataNode",
    description="Sistema de archivos distribuido por bloques - DataNode",
    version="1.0.0"
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
app.include_router(blocks.router)

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    node_id = os.getenv("NODE_ID", "unknown")
    storage_path = os.getenv("STORAGE_PATH", "/app/storage/blocks")
    print(f"DataNode {node_id} iniciado correctamente")
    print(f"Storage path: {storage_path}")

@app.get("/")
async def root():
    """Endpoint raíz"""
    node_id = os.getenv("NODE_ID", "unknown")
    return {
        "message": "GridDFS DataNode",
        "node_id": node_id,
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    node_id = os.getenv("NODE_ID", "unknown")
    return {
        "status": "healthy",
        "service": "datanode",
        "node_id": node_id
    }

@app.get("/info")
async def node_info():
    """Información del nodo"""
    node_id = os.getenv("NODE_ID", "unknown")
    namenode_url = os.getenv("NAMENODE_URL", "http://namenode:8000")
    storage_path = os.getenv("STORAGE_PATH", "/app/storage/blocks")
    
    return {
        "node_id": node_id,
        "namenode_url": namenode_url,
        "storage_path": storage_path,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
