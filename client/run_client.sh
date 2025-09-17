#!/bin/bash

echo "🚀 GridDFS Client - Ejecutor Rápido"
echo "=================================="

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "💡 Ejecuta primero: ./setup_client.sh"
    exit 1
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar que las dependencias estén instaladas
if ! python -c "import click, rich, httpx" 2>/dev/null; then
    echo "❌ Dependencias no instaladas"
    echo "💡 Ejecuta: ./setup_client.sh"
    exit 1
fi

echo "✅ Entorno virtual activado"
echo "✅ Dependencias verificadas"
echo ""

# Ejecutar el cliente con los argumentos pasados
if [ $# -eq 0 ]; then
    echo "📋 Comandos disponibles:"
    echo "   register <user> <email> <pass>  - Registrar usuario"
    echo "   login <user> <pass>             - Iniciar sesión"
    echo "   logout                          - Cerrar sesión"
    echo "   whoami                          - Usuario actual"
    echo "   put <local> <remote>            - Subir archivo"
    echo "   get <remote> <local>            - Descargar archivo"
    echo "   ls [-d dir]                     - Listar archivos"
    echo "   rm <file>                       - Eliminar archivo"
    echo "   mkdir <dir>                     - Crear directorio"
    echo "   rmdir <dir>                     - Eliminar directorio"
    echo "   status                          - Estado del sistema"
    echo ""
    echo "💡 Ejemplo: ./run_client.sh login root 1234"
else
                echo "🔧 Ejecutando comando: $@"
            python cli.py "$@"
fi

# Desactivar entorno virtual al salir
deactivate
