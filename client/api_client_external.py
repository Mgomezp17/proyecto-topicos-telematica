import os
from typing import Dict, List, Optional

import httpx
from utils.auth_utils import AuthClient
from utils.file_utils import FileUtils


class GridDFSClientExternal:
    def __init__(self, namenode_url: str = "http://localhost:8000"):
        self.namenode_url = namenode_url
        self.auth_client = AuthClient(namenode_url)

    async def register(self, username: str, email: str, password: str) -> bool:
        """Registra un nuevo usuario"""
        return await self.auth_client.register(username, email, password)

    async def login(self, username: str, password: str) -> bool:
        """Inicia sesión"""
        return await self.auth_client.login(username, password)

    async def logout(self):
        """Cierra sesión"""
        self.auth_client.clear_token()

    async def get_current_user(self) -> Optional[Dict]:
        """Obtiene información del usuario actual"""
        return await self.auth_client.get_current_user()

    async def put_file(self, local_file_path: str, remote_file_path: str) -> bool:
        """Sube un archivo al sistema GridDFS"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(local_file_path):
                print(f"Error: El archivo {local_file_path} no existe")
                return False

            # Obtener información del archivo
            file_size = os.path.getsize(local_file_path)
            filename = os.path.basename(local_file_path)

            # Solicitar upload al NameNode
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return False

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.namenode_url}/files/upload",
                    json={
                        "filename": filename,
                        "filepath": remote_file_path,
                        "size": file_size,
                    },
                    headers=auth_headers,
                )

                if response.status_code != 200:
                    print(f"Error al solicitar upload: {response.text}")
                    return False

                upload_info = response.json()
                file_id = upload_info["file_id"]
                block_distribution = upload_info["block_distribution"]

                print(f"Archivo registrado con ID: {file_id}")
                print(f"Distribución de bloques: {len(block_distribution)} bloques")

                # Dividir archivo en bloques
                print("Dividiendo archivo en bloques...")
                blocks = await FileUtils.split_file_into_blocks_async(local_file_path)
                print(f"Archivo dividido en {len(blocks)} bloques")

                # Convertir URLs internas a externas para el cliente
                external_block_distribution = []
                for block_info in block_distribution:
                    external_block_info = block_info.copy()
                    # Convertir datanode1:8000 a localhost:8001, etc.
                    if "datanode1" in block_info["datanode_url"]:
                        external_block_info["datanode_url"] = "http://localhost:8001"
                    elif "datanode2" in block_info["datanode_url"]:
                        external_block_info["datanode_url"] = "http://localhost:8002"
                    elif "datanode3" in block_info["datanode_url"]:
                        external_block_info["datanode_url"] = "http://localhost:8003"
                    external_block_distribution.append(external_block_info)

                # Registrar bloques en el NameNode primero para obtener los IDs
                print("Registrando bloques en el NameNode...")
                block_ids = []
                for i, (block_index, data, checksum) in enumerate(blocks):
                    datanode_url = block_distribution[i][
                        "datanode_url"
                    ]  # Usar URL interna para el NameNode

                    block_data = {
                        "block_index": block_index,
                        "block_size": len(data),
                        "datanode_url": datanode_url,
                        "checksum": checksum,
                    }

                    print(f"Enviando datos del bloque: {block_data}")

                    response = await client.post(
                        f"{self.namenode_url}/files/register-block/{file_id}",
                        json=block_data,
                        headers=auth_headers,
                    )

                    if response.status_code != 200:
                        print(f"Error registrando bloque {block_index}")
                        print(f"Status: {response.status_code}")
                        print(f"Response: {response.text}")
                        return False

                    # Obtener el ID del bloque del response
                    block_response = response.json()
                    block_ids.append(block_response["block_id"])

                # Subir bloques a DataNodes con los IDs correctos
                print("Subiendo bloques a DataNodes...")
                success = await FileUtils.upload_blocks_to_datanodes_with_ids(
                    blocks, external_block_distribution, block_ids, auth_headers
                )

                if not success:
                    print("Error subiendo bloques")
                    return False

                print(f"Archivo {filename} subido exitosamente")
                return True

        except Exception as e:
            print(f"Error subiendo archivo: {e}")
            return False

    async def get_file(self, remote_file_path: str, local_file_path: str) -> bool:
        """Descarga un archivo del sistema GridDFS"""
        try:
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return False

            # Buscar el archivo en el NameNode
            async with httpx.AsyncClient() as client:
                # Primero listar archivos para encontrar el ID
                response = await client.get(
                    f"{self.namenode_url}/files/list", headers=auth_headers
                )

                if response.status_code != 200:
                    print(f"Error listando archivos: {response.text}")
                    return False

                files = response.json()
                file_id = None

                for file in files:
                    if file["filepath"] == remote_file_path:
                        file_id = file["id"]
                        break

                if file_id is None:
                    print(f"Error: Archivo {remote_file_path} no encontrado")
                    return False

                # Obtener información detallada del archivo
                response = await client.get(
                    f"{self.namenode_url}/files/{file_id}", headers=auth_headers
                )

                if response.status_code != 200:
                    print(f"Error obteniendo información del archivo: {response.text}")
                    return False

                file_info = response.json()
                print(f"Descargando archivo: {file_info['file']['filename']}")
                print(
                    f"Tamaño: {FileUtils.format_file_size(file_info['file']['size'])}"
                )
                print(f"Bloques: {len(file_info['blocks'])}")

                # Convertir URLs internas a externas para descarga
                external_file_info = file_info.copy()
                for block in external_file_info["blocks"]:
                    if "datanode1" in block["datanode_url"]:
                        block["datanode_url"] = "http://localhost:8001"
                    elif "datanode2" in block["datanode_url"]:
                        block["datanode_url"] = "http://localhost:8002"
                    elif "datanode3" in block["datanode_url"]:
                        block["datanode_url"] = "http://localhost:8003"

                # Descargar bloques y reconstruir archivo
                success = await FileUtils.download_blocks_from_datanodes(
                    external_file_info, local_file_path
                )

                if success:
                    print(f"Archivo descargado exitosamente: {local_file_path}")
                    return True
                else:
                    print("Error descargando archivo")
                    return False

        except Exception as e:
            print(f"Error descargando archivo: {e}")
            return False

    async def list_files(self, directory: str = "/") -> List[Dict]:
        """Lista archivos en un directorio"""
        try:
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return []

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.namenode_url}/files/list",
                    params={"directory": directory},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error listando archivos: {response.text}")
                    return []

        except Exception as e:
            print(f"Error listando archivos: {e}")
            return []

    async def delete_file(self, remote_file_path: str) -> bool:
        """Elimina un archivo del sistema GridDFS"""
        try:
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return False

            # Buscar el archivo en el NameNode
            files = await self.list_files()
            file_id = None

            for file in files:
                if file["filepath"] == remote_file_path:
                    file_id = file["id"]
                    break

            if file_id is None:
                print(f"Error: Archivo {remote_file_path} no encontrado")
                return False

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.namenode_url}/files/{file_id}", headers=auth_headers
                )

                if response.status_code == 200:
                    print(f"Archivo {remote_file_path} eliminado exitosamente")
                    return True
                else:
                    print(f"Error eliminando archivo: {response.text}")
                    return False

        except Exception as e:
            print(f"Error eliminando archivo: {e}")
            return False

    async def create_directory(self, dirpath: str) -> bool:
        """Crea un directorio"""
        try:
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return False

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.namenode_url}/files/mkdir",
                    params={"dirpath": dirpath},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    print(f"Directorio {dirpath} creado exitosamente")
                    return True
                else:
                    print(f"Error creando directorio: {response.text}")
                    return False

        except Exception as e:
            print(f"Error creando directorio: {e}")
            return False

    async def remove_directory(self, dirpath: str) -> bool:
        """Elimina un directorio"""
        try:
            auth_headers = self.auth_client.get_auth_headers()
            if not auth_headers:
                print("Error: No autenticado. Use 'login' primero.")
                return False

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.namenode_url}/files/rmdir",
                    params={"dirpath": dirpath},
                    headers=auth_headers,
                )

                if response.status_code == 200:
                    print(f"Directorio {dirpath} eliminado exitosamente")
                    return True
                else:
                    print(f"Error eliminando directorio: {response.text}")
                    return False

        except Exception as e:
            print(f"Error eliminando directorio: {e}")
            return False
