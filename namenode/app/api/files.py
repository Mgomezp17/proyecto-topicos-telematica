from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.block import Block
from ..models.file import File
from ..models.user import User
from ..services.file_service import FileService
from .auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])


# Modelos Pydantic
class FileResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    size: int
    block_size: int
    num_blocks: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FileUploadRequest(BaseModel):
    filename: str
    filepath: str
    size: int


class FileUploadResponse(BaseModel):
    file_id: int
    block_distribution: List[dict]


class BlockInfo(BaseModel):
    block_id: str
    block_index: int
    size: int
    datanode_url: str
    checksum: str


class FileInfo(BaseModel):
    file: FileResponse
    blocks: List[BlockInfo]


class BlockRegistrationRequest(BaseModel):
    block_index: int
    block_size: int
    datanode_url: str
    checksum: str


# Endpoints
@router.post("/upload", response_model=FileUploadResponse)
def upload_file(
    file_data: FileUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Inicia el proceso de upload de un archivo"""
    # Verificar si el archivo ya existe
    existing_file = FileService.get_file_by_path(
        db, file_data.filepath, current_user.id
    )
    if existing_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File already exists"
        )

    # Crear metadatos del archivo
    file = FileService.create_file_metadata(
        db=db,
        filename=file_data.filename,
        filepath=file_data.filepath,
        size=file_data.size,
        owner_id=current_user.id,
    )

    # Obtener DataNodes disponibles
    datanodes = FileService.get_available_datanodes()
    if not datanodes:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No DataNodes available",
        )

    # Distribuir bloques
    block_distribution = FileService.distribute_blocks(file_data.size, datanodes)

    return FileUploadResponse(file_id=file.id, block_distribution=block_distribution)


@router.get("/list", response_model=List[FileResponse])
def list_files(
    directory: str = "/",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los archivos de un usuario en un directorio"""
    files = FileService.list_user_files(db, current_user.id, directory)
    return files


@router.get("/{file_id}", response_model=FileInfo)
def get_file_info(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene información detallada de un archivo y sus bloques"""
    file = FileService.get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    blocks = FileService.get_file_blocks(db, file_id)

    return FileInfo(
        file=file,
        blocks=[
            BlockInfo(
                block_id=block.block_id,
                block_index=block.block_index,
                size=block.size,
                datanode_url=block.datanode_url,
                checksum=block.checksum,
            )
            for block in blocks
        ],
    )


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un archivo"""
    success = FileService.delete_file(db, file_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return {"message": "File deleted successfully"}


@router.post("/mkdir")
def create_directory(
    dirpath: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un directorio"""
    success = FileService.create_directory(db, dirpath, current_user.id)
    return {"message": "Directory created successfully"}


@router.delete("/rmdir")
def remove_directory(
    dirpath: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un directorio y todos sus archivos"""
    success = FileService.remove_directory(db, dirpath, current_user.id)
    return {"message": "Directory removed successfully"}


@router.post("/register-block/{file_id}")
def register_block(
    file_id: int,
    request: BlockRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra un bloque en el NameNode"""
    try:
        file = FileService.get_file_by_id(db, file_id, current_user.id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        block = FileService.assign_block_to_datanode(
            db=db,
            file_id=file_id,
            block_index=request.block_index,
            block_size=request.block_size,
            datanode_url=request.datanode_url,
            checksum=request.checksum,
        )

        return {"block_id": block.block_id, "message": "Block registered successfully"}
    except Exception as e:
        print(f"Error en register_block: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/test-endpoint", include_in_schema=False)
def test_endpoint():
    """Endpoint de prueba"""
    return {"message": "Test endpoint working"}
