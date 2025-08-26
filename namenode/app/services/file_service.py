from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.file import File
from ..models.block import Block
from ..models.user import User
import os
import hashlib
import uuid

class FileService:
    BLOCK_SIZE = int(os.getenv("BLOCK_SIZE", 67108864))  # 64MB por defecto
    
    @staticmethod
    def calculate_file_blocks(file_size: int) -> int:
        """Calcula el número de bloques necesarios para un archivo"""
        return (file_size + FileService.BLOCK_SIZE - 1) // FileService.BLOCK_SIZE

    @staticmethod
    def generate_block_id() -> str:
        """Genera un ID único para un bloque"""
        return str(uuid.uuid4())

    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """Calcula el checksum SHA-256 de los datos"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def create_file_metadata(
        db: Session, 
        filename: str, 
        filepath: str, 
        size: int, 
        owner_id: int
    ) -> File:
        """Crea los metadatos de un archivo"""
        num_blocks = FileService.calculate_file_blocks(size)
        
        file = File(
            filename=filename,
            filepath=filepath,
            size=size,
            block_size=FileService.BLOCK_SIZE,
            num_blocks=num_blocks,
            owner_id=owner_id
        )
        
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def get_file_by_path(db: Session, filepath: str, owner_id: int) -> Optional[File]:
        """Obtiene un archivo por su ruta y propietario"""
        return db.query(File).filter(
            File.filepath == filepath,
            File.owner_id == owner_id
        ).first()

    @staticmethod
    def get_file_by_id(db: Session, file_id: int, owner_id: int) -> Optional[File]:
        """Obtiene un archivo por su ID y propietario"""
        return db.query(File).filter(
            File.id == file_id,
            File.owner_id == owner_id
        ).first()

    @staticmethod
    def list_user_files(db: Session, owner_id: int, directory: str = "/") -> List[File]:
        """Lista los archivos de un usuario en un directorio"""
        return db.query(File).filter(
            File.owner_id == owner_id,
            File.filepath.like(f"{directory}%")
        ).all()

    @staticmethod
    def delete_file(db: Session, file_id: int, owner_id: int) -> bool:
        """Elimina un archivo y sus bloques"""
        file = FileService.get_file_by_id(db, file_id, owner_id)
        if not file:
            return False
        
        # Eliminar bloques asociados
        db.query(Block).filter(Block.file_id == file_id).delete()
        
        # Eliminar archivo
        db.delete(file)
        db.commit()
        return True

    @staticmethod
    def create_directory(db: Session, dirpath: str, owner_id: int) -> bool:
        """Crea un directorio (en GridDFS, los directorios son virtuales)"""
        # En GridDFS, los directorios son implícitos basados en las rutas de archivos
        # No necesitamos crear entradas en la base de datos para directorios
        return True

    @staticmethod
    def remove_directory(db: Session, dirpath: str, owner_id: int) -> bool:
        """Elimina un directorio y todos sus archivos"""
        # Eliminar todos los archivos en el directorio
        files = db.query(File).filter(
            File.owner_id == owner_id,
            File.filepath.like(f"{dirpath}%")
        ).all()
        
        for file in files:
            FileService.delete_file(db, file.id, owner_id)
        
        return True

    @staticmethod
    def get_file_blocks(db: Session, file_id: int) -> List[Block]:
        """Obtiene todos los bloques de un archivo ordenados por índice"""
        return db.query(Block).filter(
            Block.file_id == file_id
        ).order_by(Block.block_index).all()

    @staticmethod
    def assign_block_to_datanode(
        db: Session,
        file_id: int,
        block_index: int,
        block_size: int,
        datanode_url: str,
        checksum: str
    ) -> Block:
        """Asigna un bloque a un DataNode específico"""
        block_id = FileService.generate_block_id()
        
        block = Block(
            block_id=block_id,
            file_id=file_id,
            block_index=block_index,
            size=block_size,
            datanode_url=datanode_url,
            checksum=checksum
        )
        
        db.add(block)
        db.commit()
        db.refresh(block)
        return block

    @staticmethod
    def get_available_datanodes() -> List[str]:
        """Obtiene la lista de DataNodes disponibles"""
        # Por ahora, retornamos los DataNodes configurados en docker-compose
        # En una implementación real, esto vendría de un registro de servicios
        return [
            "http://datanode1:8000",
            "http://datanode2:8000", 
            "http://datanode3:8000"
        ]

    @staticmethod
    def distribute_blocks(file_size: int, datanodes: List[str]) -> List[Dict]:
        """Distribuye los bloques entre los DataNodes disponibles"""
        num_blocks = FileService.calculate_file_blocks(file_size)
        distribution = []
        
        for i in range(num_blocks):
            datanode_index = i % len(datanodes)
            block_size = min(FileService.BLOCK_SIZE, file_size - i * FileService.BLOCK_SIZE)
            
            distribution.append({
                "block_index": i,
                "datanode_url": datanodes[datanode_index],
                "block_size": block_size
            })
        
        return distribution
