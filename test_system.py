#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema GridDFS
"""

import asyncio
import os
import tempfile
import time

import httpx

from client.api_client_external import GridDFSClientExternal


async def test_system():
    """Prueba completa del sistema GridDFS"""
    print("🧪 Iniciando pruebas del sistema GridDFS")
    print("=" * 50)

    # Crear cliente
    client = GridDFSClientExternal("http://localhost:8000")

    # 1. Verificar conectividad con NameNode
    print("\n1️⃣ Verificando conectividad con NameNode...")
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ NameNode responde correctamente")
            else:
                print("❌ NameNode no responde correctamente")
                return False
    except Exception as e:
        print(f"❌ Error conectando al NameNode: {e}")
        return False

    # 2. Verificar DataNodes
    print("\n2️⃣ Verificando DataNodes...")
    datanodes_ok = 0
    for port in [8001, 8002, 8003]:
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(f"http://localhost:{port}/health")
                if response.status_code == 200:
                    print(f"✅ DataNode en puerto {port} responde")
                    datanodes_ok += 1
                else:
                    print(f"❌ DataNode en puerto {port} no responde")
        except Exception as e:
            print(f"❌ Error conectando al DataNode en puerto {port}: {e}")

    if datanodes_ok < 2:
        print("❌ Se necesitan al menos 2 DataNodes funcionando")
        return False

    print(f"✅ {datanodes_ok}/3 DataNodes funcionando")

    # 3. Registrar usuario de prueba (o usar existente)
    print("\n3️⃣ Registrando usuario de prueba...")
    success = await client.register("testuser", "test@example.com", "testpass123")
    if success:
        print("✅ Usuario registrado exitosamente")
    else:
        print("ℹ️ Usuario ya existe, continuando con login...")

    # 4. Iniciar sesión
    print("\n4️⃣ Iniciando sesión...")
    success = await client.login("testuser", "testpass123")
    if success:
        print("✅ Sesión iniciada exitosamente")
    else:
        print("❌ Error iniciando sesión")
        return False

    # 5. Crear directorio de prueba
    print("\n5️⃣ Creando directorio de prueba...")
    success = await client.create_directory("/test_dir")
    if success:
        print("✅ Directorio creado exitosamente")
    else:
        print("❌ Error creando directorio")
        return False

    # 6. Crear archivo de prueba
    print("\n6️⃣ Creando archivo de prueba...")
    import time

    timestamp = int(time.time())
    test_content = "Este es un archivo de prueba para GridDFS\n" * 1000  # ~30KB
    test_file_path = f"/tmp/griddfs_test_{timestamp}.txt"

    with open(test_file_path, "w") as f:
        f.write(test_content)

    print(f"✅ Archivo de prueba creado: {test_file_path}")

    # 7. Subir archivo
    print("\n7️⃣ Subiendo archivo...")
    success = await client.put_file(
        test_file_path, f"/test_dir/test_file_{timestamp}.txt"
    )
    if success:
        print("✅ Archivo subido exitosamente")
    else:
        print("❌ Error subiendo archivo")
        return False

    # 8. Listar archivos
    print("\n8️⃣ Listando archivos...")
    files = await client.list_files("/test_dir")
    if files:
        print(f"✅ Archivos encontrados: {len(files)}")
        for file in files:
            print(f"   - {file['filename']} ({file['size']} bytes)")
    else:
        print("❌ No se encontraron archivos")
        return False

    # 9. Descargar archivo
    print("\n9️⃣ Descargando archivo...")
    download_path = f"/tmp/griddfs_download_{timestamp}.txt"
    success = await client.get_file(
        f"/test_dir/test_file_{timestamp}.txt", download_path
    )
    if success:
        print("✅ Archivo descargado exitosamente")

        # Verificar contenido
        with open(download_path, "r") as f:
            downloaded_content = f.read()

        if downloaded_content == test_content:
            print("✅ Contenido del archivo verificado correctamente")
        else:
            print("❌ El contenido del archivo no coincide")
            return False
    else:
        print("❌ Error descargando archivo")
        return False

    # 10. Eliminar archivo
    print("\n🔟 Eliminando archivo...")
    success = await client.delete_file(f"/test_dir/test_file_{timestamp}.txt")
    if success:
        print("✅ Archivo eliminado exitosamente")
    else:
        print("❌ Error eliminando archivo")
        return False

    # 11. Verificar eliminación
    print("\n1️⃣1️⃣ Verificando eliminación...")
    files = await client.list_files("/test_dir")
    if not files:
        print("✅ Archivo eliminado correctamente")
    else:
        print("❌ El archivo no se eliminó correctamente")
        return False

    # 12. Eliminar directorio
    print("\n1️⃣2️⃣ Eliminando directorio...")
    success = await client.remove_directory("/test_dir")
    if success:
        print("✅ Directorio eliminado exitosamente")
    else:
        print("❌ Error eliminando directorio")
        return False

    # Limpiar archivos temporales
    try:
        os.remove(test_file_path)
        os.remove(download_path)
    except:
        pass

    print("\n" + "=" * 50)
    print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("✅ El sistema GridDFS está funcionando correctamente")

    return True


async def test_large_file():
    """Prueba con archivo grande para verificar distribución de bloques"""
    print("\n🧪 Prueba con archivo grande (distribución de bloques)")
    print("=" * 50)

    client = GridDFSClientExternal("http://localhost:8000")

    # Iniciar sesión
    await client.login("testuser", "testpass123")

    # Crear archivo grande (~100MB)
    large_file_path = "/tmp/griddfs_large_test.dat"
    chunk_size = 1024 * 1024  # 1MB
    total_size = 100 * 1024 * 1024  # 100MB

    print(f"📁 Creando archivo grande: {total_size / (1024*1024):.1f}MB")

    with open(large_file_path, "wb") as f:
        for i in range(total_size // chunk_size):
            # Crear datos pseudo-aleatorios
            chunk = f"Chunk {i:06d}".encode() * (chunk_size // 10)
            f.write(chunk[:chunk_size])

    print("✅ Archivo grande creado")

    # Subir archivo
    print("📤 Subiendo archivo grande...")
    start_time = time.time()
    success = await client.put_file(large_file_path, "/large_test.dat")
    upload_time = time.time() - start_time

    if success:
        print(f"✅ Archivo subido en {upload_time:.2f} segundos")
        print(f"📊 Velocidad: {total_size / (1024*1024) / upload_time:.2f} MB/s")
    else:
        print("❌ Error subiendo archivo grande")
        return False

    # Listar archivos para verificar
    files = await client.list_files("/")
    large_file = None
    for file in files:
        if file["filename"] == "large_test.dat":
            large_file = file
            break

    if large_file:
        print(f"📋 Archivo registrado:")
        print(f"   - Tamaño: {large_file['size']} bytes")
        print(f"   - Bloques: {large_file['num_blocks']}")
        print(f"   - Tamaño de bloque: {large_file['block_size']} bytes")
    else:
        print("❌ Archivo grande no encontrado en la lista")
        return False

    # Descargar archivo
    print("📥 Descargando archivo grande...")
    download_path = "/tmp/griddfs_large_download.dat"
    start_time = time.time()
    success = await client.get_file("/large_test.dat", download_path)
    download_time = time.time() - start_time

    if success:
        print(f"✅ Archivo descargado en {download_time:.2f} segundos")
        print(f"📊 Velocidad: {total_size / (1024*1024) / download_time:.2f} MB/s")

        # Verificar tamaño
        if os.path.getsize(download_path) == total_size:
            print("✅ Tamaño del archivo verificado correctamente")
        else:
            print("❌ El tamaño del archivo no coincide")
            return False
    else:
        print("❌ Error descargando archivo grande")
        return False

    # Limpiar
    try:
        os.remove(large_file_path)
        os.remove(download_path)
        await client.delete_file("/large_test.dat")
    except:
        pass

    print("✅ Prueba con archivo grande completada")
    return True


if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema GridDFS")
    print("Asegúrate de que el sistema esté ejecutándose con: ./start.sh")
    print("Y que el cliente esté configurado con: cd client && ./setup_client.sh")
    print()

    # Ejecutar pruebas básicas
    basic_success = asyncio.run(test_system())

    if basic_success:
        # Ejecutar prueba con archivo grande
        large_success = asyncio.run(test_large_file())

        if large_success:
            print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
            print("✅ El sistema GridDFS está funcionando perfectamente")
        else:
            print("\n❌ Prueba con archivo grande falló")
    else:
        print("\n❌ Pruebas básicas fallaron")
        print("💡 Verifica que el sistema esté ejecutándose correctamente")
