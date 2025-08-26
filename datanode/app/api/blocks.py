from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io
import hashlib
from ..storage.block_storage import BlockStorage
import os

router = APIRouter(prefix="/blocks", tags=["blocks"])

# Inicializar el almacenamiento de bloques
storage_path = os.getenv("STORAGE_PATH", "/app/storage/blocks")
block_storage = BlockStorage(storage_path)

# Modelos Pydantic
class BlockInfo(BaseModel):
    block_id: str
    size: int
    checksum: str
    created_at: str

class StorageInfo(BaseModel):
    total_size: int
    block_count: int
    storage_path: str

# Endpoints
@router.post("/upload")
async def upload_block(
    block_id: str = Form(...),
    checksum: str = Form(...),
    file: UploadFile = File(...)
):
    """Sube un bloque al DataNode"""
    try:
        # Leer el contenido del archivo
        data = await file.read()
        
        # Almacenar el bloque
        success = await block_storage.store_block(block_id, data, checksum)
        
        if success:
            return {
                "message": "Block uploaded successfully",
                "block_id": block_id,
                "size": len(data)
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to store block")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading block: {str(e)}")

@router.get("/download/{block_id}")
async def download_block(block_id: str):
    """Descarga un bloque del DataNode"""
    try:
        # Recuperar el bloque
        data = await block_storage.retrieve_block(block_id)
        
        if data is None:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Crear respuesta de streaming
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={block_id}.block"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading block: {str(e)}")

@router.delete("/{block_id}")
async def delete_block(block_id: str):
    """Elimina un bloque del DataNode"""
    try:
        success = await block_storage.delete_block(block_id)
        
        if success:
            return {"message": "Block deleted successfully", "block_id": block_id}
        else:
            raise HTTPException(status_code=404, detail="Block not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting block: {str(e)}")

@router.get("/{block_id}/info", response_model=BlockInfo)
async def get_block_info(block_id: str):
    """Obtiene información de un bloque"""
    try:
        info = await block_storage.get_block_info(block_id)
        
        if info is None:
            raise HTTPException(status_code=404, detail="Block not found")
        
        return BlockInfo(**info)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting block info: {str(e)}")

@router.get("/list", response_model=List[BlockInfo])
async def list_blocks():
    """Lista todos los bloques almacenados"""
    try:
        blocks = await block_storage.list_blocks()
        return [BlockInfo(**block) for block in blocks]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing blocks: {str(e)}")

@router.get("/storage/info", response_model=StorageInfo)
async def get_storage_info():
    """Obtiene información del almacenamiento"""
    try:
        info = block_storage.get_storage_usage()
        return StorageInfo(**info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting storage info: {str(e)}")

@router.post("/verify/{block_id}")
async def verify_block(block_id: str, expected_checksum: str):
    """Verifica la integridad de un bloque"""
    try:
        # Recuperar el bloque
        data = await block_storage.retrieve_block(block_id)
        
        if data is None:
            raise HTTPException(status_code=404, detail="Block not found")
        
        # Calcular checksum
        calculated_checksum = hashlib.sha256(data).hexdigest()
        
        # Verificar
        is_valid = calculated_checksum == expected_checksum
        
        return {
            "block_id": block_id,
            "is_valid": is_valid,
            "expected_checksum": expected_checksum,
            "calculated_checksum": calculated_checksum
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying block: {str(e)}")
