# GridDFS - Sistema de Archivos Distribuido por Bloques

GridDFS es un sistema de archivos distribuido minimalista inspirado en HDFS y GFS, implementado con FastAPI y Docker. Permite almacenar archivos grandes de forma distribuida en múltiples nodos, aplicando particionamiento en bloques sin replicación.

## 🏗️ Arquitectura

### Componentes Principales

- **NameNode**: Servidor central que gestiona metadatos y ubicación de bloques
- **DataNodes**: Múltiples nodos que almacenan los bloques de archivos
- **Cliente**: CLI/API para interactuar con el sistema

### Características

- ✅ **Particionamiento por bloques**: Archivos divididos en bloques de 64MB
- ✅ **Distribución automática**: Bloques distribuidos entre múltiples DataNodes
- ✅ **Autenticación JWT**: Sistema de usuarios con tokens seguros
- ✅ **SQLite**: Base de datos ligera para metadatos
- ✅ **Docker Compose**: Orquestación completa del sistema
- ✅ **CLI intuitivo**: Interfaz de línea de comandos fácil de usar
- ✅ **Verificación de integridad**: Checksums SHA-256 para cada bloque

## 🚀 Instalación y Uso

### Prerrequisitos

- Docker y Docker Compose instalados
- Python 3.11+ (para el cliente)
- En macOS: `python3` y `pip3` instalados

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd griddfs
```

### 2. Instalación Automática (Recomendado)

```bash
chmod +x install.sh
./install.sh
```

Este script automatiza todo el proceso de instalación.

### 3. Instalación Manual

#### Iniciar el sistema

```bash
docker-compose up -d
```

Esto iniciará:

- **NameNode** en `http://localhost:8000`
- **DataNode1** en `http://localhost:8001`
- **DataNode2** en `http://localhost:8002`
- **DataNode3** en `http://localhost:8003`

#### Configurar el cliente

```bash
cd client
./setup_client.sh
```

### 4. Usar el sistema

#### Usar el cliente con entorno virtual (Recomendado)

```bash
cd client
./run_client.sh --help
```

#### Registrar un usuario

```bash
./run_client.sh register usuario@email.com password
```

#### Iniciar sesión

```bash
./run_client.sh login usuario password
```

#### Subir un archivo

```bash
./run_client.sh put /ruta/local/archivo.txt /archivo.txt
```

#### Listar archivos

```bash
./run_client.sh ls
```

#### Descargar un archivo

```bash
./run_client.sh get /archivo.txt /ruta/local/descarga.txt
```

#### Eliminar un archivo

```bash
./run_client.sh rm /archivo.txt
```

#### Crear directorio

```bash
./run_client.sh mkdir /mi_directorio
```

#### Ver estado del sistema

```bash
./run_client.sh status
```

## 📋 Comandos Disponibles

| Comando                          | Descripción               |
| -------------------------------- | ------------------------- |
| `register <user> <email> <pass>` | Registra un nuevo usuario |
| `login <user> <pass>`            | Inicia sesión             |
| `logout`                         | Cierra sesión             |
| `whoami`                         | Muestra usuario actual    |
| `put <local> <remote>`           | Sube un archivo           |
| `get <remote> <local>`           | Descarga un archivo       |
| `ls [-d dir]`                    | Lista archivos            |
| `rm <file>`                      | Elimina un archivo        |
| `mkdir <dir>`                    | Crea un directorio        |
| `rmdir <dir>`                    | Elimina un directorio     |
| `status`                         | Estado del sistema        |

## 🔧 Configuración

### Gestión de Entornos Virtuales

El cliente utiliza un entorno virtual de Python para aislar las dependencias.

#### Scripts Disponibles

- `client/setup_client.sh` - Configura el entorno virtual e instala dependencias
- `client/run_client.sh` - Ejecuta el cliente con el entorno virtual activado
- `client/clean_env.sh` - Limpia el entorno virtual y archivos de cache

#### Comandos Manuales

```bash
# Activar entorno virtual manualmente
cd client
source venv/bin/activate

# Usar el cliente
python -m client.cli --help

# Desactivar entorno virtual
deactivate
```

### Variables de Entorno

#### NameNode

- `DATABASE_URL`: URL de la base de datos SQLite
- `SECRET_KEY`: Clave secreta para JWT
- `BLOCK_SIZE`: Tamaño de bloque en bytes (default: 64MB)

#### DataNodes

- `NODE_ID`: Identificador único del nodo
- `NAMENODE_URL`: URL del NameNode
- `STORAGE_PATH`: Ruta de almacenamiento de bloques

### Personalización

Puedes modificar el `docker-compose.yml` para:

- Cambiar el número de DataNodes
- Ajustar puertos
- Modificar volúmenes de almacenamiento
- Configurar redes personalizadas

## 📊 API Endpoints

### NameNode (`http://localhost:8000`)

#### Autenticación

- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Información del usuario

#### Archivos

- `POST /files/upload` - Iniciar upload
- `GET /files/list` - Listar archivos
- `GET /files/{id}` - Información de archivo
- `DELETE /files/{id}` - Eliminar archivo
- `POST /files/mkdir` - Crear directorio
- `DELETE /files/rmdir` - Eliminar directorio

### DataNodes (`http://localhost:8001-8003`)

#### Bloques

- `POST /blocks/upload` - Subir bloque
- `GET /blocks/download/{id}` - Descargar bloque
- `DELETE /blocks/{id}` - Eliminar bloque
- `GET /blocks/{id}/info` - Información de bloque
- `GET /blocks/list` - Listar bloques
- `GET /blocks/storage/info` - Información de almacenamiento

## 🧪 Pruebas

### Verificar que el sistema esté funcionando

```bash
# Verificar NameNode
curl http://localhost:8000/health

# Verificar DataNodes
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Ejemplo de flujo completo

```bash
# 1. Registrar usuario
./run_client.sh register test@example.com password123

# 2. Iniciar sesión
./run_client.sh login test password123

# 3. Crear directorio
./run_client.sh mkdir /documentos

# 4. Subir archivo
./run_client.sh put /tmp/test.txt /documentos/test.txt

# 5. Listar archivos
./run_client.sh ls /documentos

# 6. Descargar archivo
./run_client.sh get /documentos/test.txt /tmp/descarga.txt
```

## 🔍 Monitoreo

### Logs de Docker Compose

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs namenode
docker-compose logs datanode1
```

### Estado de los contenedores

```bash
docker-compose ps
```

## 🛠️ Desarrollo

### Estructura del Proyecto

```
griddfs/
├── namenode/          # Servidor NameNode
├── datanode/          # Servidores DataNode
├── client/            # Cliente CLI
├── docker-compose.yml # Orquestación
└── README.md
```

### Agregar nuevos DataNodes

1. Copiar la configuración de un DataNode existente en `docker-compose.yml`
2. Cambiar el puerto y nombre del servicio
3. Reiniciar con `docker-compose up -d`

### Modificar tamaño de bloque

Cambiar la variable `BLOCK_SIZE` en `docker-compose.yml` y reiniciar los servicios.

## 📝 Notas de Implementación

- **Sin replicación**: Los bloques no se replican (requerimiento del proyecto)
- **SQLite**: Base de datos ligera para metadatos
- **JWT**: Autenticación stateless
- **Checksums**: Verificación de integridad SHA-256
- **Docker**: Contenedores aislados para cada componente

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte del curso ST0263 Tópicos Especiales en Telemática / SI3007 Sistemas Distribuidos.

---

**GridDFS** - Sistema de archivos distribuido por bloques 🚀
