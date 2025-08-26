import os
import hashlib
import aiofiles
from typing import List, Dict, Tuple
import httpx
import asyncio

class FileUtils:
    BLOCK_SIZE = 67108864  # 64MB
    
    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """Calcula el checksum SHA-256 de los datos"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def split_file_into_blocks(file_path: str) -> List[Tuple[int, bytes, str]]:
        """Divide un archivo en bloques"""
        blocks = []
        block_index = 0
        
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(FileUtils.BLOCK_SIZE)
                if not data:
                    break
                
                checksum = FileUtils.calculate_checksum(data)
                blocks.append((block_index, data, checksum))
                block_index += 1
        
        return blocks

    @staticmethod
    async def split_file_into_blocks_async(file_path: str) -> List[Tuple[int, bytes, str]]:
        """Divide un archivo en bloques de forma asíncrona"""
        blocks = []
        block_index = 0
        
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                data = await f.read(FileUtils.BLOCK_SIZE)
                if not data:
                    break
                
                checksum = FileUtils.calculate_checksum(data)
                blocks.append((block_index, data, checksum))
                block_index += 1
        
        return blocks

    @staticmethod
    async def upload_blocks_to_datanodes(
        blocks: List[Tuple[int, bytes, str]], 
        block_distribution: List[Dict],
        auth_headers: Dict
    ) -> bool:
        """Sube bloques a los DataNodes correspondientes"""
        try:
            async with httpx.AsyncClient() as client:
                for i, (block_index, data, checksum) in enumerate(blocks):
                    if i >= len(block_distribution):
                        print(f"Error: No hay distribución para el bloque {block_index}")
                        return False
                    
                    datanode_url = block_distribution[i]["datanode_url"]
                    
                    # Crear archivo temporal para el bloque
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(data)
                        temp_file_path = temp_file.name
                    
                    try:
                        # Subir bloque al DataNode
                        with open(temp_file_path, 'rb') as f:
                            files = {'file': f}
                            data_form = {
                                'block_id': f"block_{block_index}",
                                'checksum': checksum
                            }
                            
                            response = await client.post(
                                f"{datanode_url}/blocks/upload",
                                files=files,
                                data=data_form
                            )
                            
                            if response.status_code != 200:
                                print(f"Error subiendo bloque {block_index} a {datanode_url}")
                                return False
                            
                            print(f"Bloque {block_index} subido exitosamente a {datanode_url}")
                    
                    finally:
                        # Limpiar archivo temporal
                        os.unlink(temp_file_path)
                
                return True
        except Exception as e:
            print(f"Error subiendo bloques: {e}")
            return False

    @staticmethod
    async def download_blocks_from_datanodes(
        file_info: Dict,
        output_path: str
    ) -> bool:
        """Descarga bloques de los DataNodes y reconstruye el archivo"""
        try:
            blocks = file_info.get("blocks", [])
            if not blocks:
                print("No hay bloques para descargar")
                return False
            
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            async with httpx.AsyncClient() as client:
                with open(output_path, 'wb') as output_file:
                    for block_info in blocks:
                        datanode_url = block_info["datanode_url"]
                        block_id = block_info["block_id"]
                        
                        # Descargar bloque
                        response = await client.get(
                            f"{datanode_url}/blocks/download/{block_id}"
                        )
                        
                        if response.status_code != 200:
                            print(f"Error descargando bloque {block_id} de {datanode_url}")
                            return False
                        
                        # Escribir bloque al archivo de salida
                        output_file.write(response.content)
                        print(f"Bloque {block_id} descargado exitosamente")
                
                print(f"Archivo reconstruido exitosamente: {output_path}")
                return True
        except Exception as e:
            print(f"Error descargando bloques: {e}")
            return False

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatea el tamaño de archivo en formato legible"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"

    @staticmethod
    def ensure_directory_exists(filepath: str):
        """Asegura que el directorio del archivo existe"""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
