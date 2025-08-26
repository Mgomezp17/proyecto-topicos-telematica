import httpx
import json
import os
from typing import Optional

class AuthClient:
    def __init__(self, namenode_url: str = "http://localhost:8000"):
        self.namenode_url = namenode_url
        self.token = None
        self.token_file = os.path.expanduser("~/.griddfs_token")

    def save_token(self, token: str):
        """Guarda el token en un archivo local"""
        try:
            with open(self.token_file, 'w') as f:
                json.dump({"token": token}, f)
            self.token = token
        except Exception as e:
            print(f"Error saving token: {e}")

    def load_token(self) -> Optional[str]:
        """Carga el token desde el archivo local"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    return self.token
        except Exception as e:
            print(f"Error loading token: {e}")
        return None

    def clear_token(self):
        """Elimina el token guardado"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.token = None
        except Exception as e:
            print(f"Error clearing token: {e}")

    async def register(self, username: str, email: str, password: str) -> bool:
        """Registra un nuevo usuario"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.namenode_url}/auth/register",
                    json={
                        "username": username,
                        "email": email,
                        "password": password
                    }
                )
                
                if response.status_code == 200:
                    print("Usuario registrado exitosamente")
                    return True
                else:
                    print(f"Error al registrar usuario: {response.text}")
                    return False
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    async def login(self, username: str, password: str) -> bool:
        """Inicia sesión y obtiene un token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.namenode_url}/auth/login",
                    data={
                        "username": username,
                        "password": password
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    if token:
                        self.save_token(token)
                        print("Inicio de sesión exitoso")
                        return True
                    else:
                        print("Error: No se recibió token")
                        return False
                else:
                    print(f"Error de autenticación: {response.text}")
                    return False
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    async def get_current_user(self) -> Optional[dict]:
        """Obtiene información del usuario actual"""
        if not self.token:
            self.load_token()
        
        if not self.token:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.namenode_url}/auth/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Token inválido, limpiarlo
                    self.clear_token()
                    return None
        except Exception as e:
            print(f"Error de conexión: {e}")
            return None

    def get_auth_headers(self) -> dict:
        """Obtiene los headers de autenticación"""
        if not self.token:
            self.load_token()
        
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
