#!/bin/bash

echo "🚀 Instalación Completa de GridDFS"
echo "=================================="

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "💡 Instala Docker desde https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    echo "💡 Instala Docker Compose desde https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar que Python3 esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    echo "💡 Instala Python3 desde https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Prerrequisitos verificados:"
echo "   • Docker: $(docker --version)"
echo "   • Docker Compose: $(docker-compose --version)"
echo "   • Python3: $(python3 --version)"

# Iniciar servicios con Docker Compose
echo ""
echo "🔨 Iniciando servicios GridDFS..."
if ! docker-compose up -d --build; then
    echo "❌ Error al construir/iniciar servicios"
    echo "💡 Intentando reparar la instalación..."
    echo ""
    echo "🔧 Ejecutando script de reparación..."
    chmod +x fix_installation.sh
    ./fix_installation.sh
    exit 1
fi

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Verificar el estado de los servicios
echo "🔍 Verificando estado de los servicios..."

# Verificar NameNode
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ NameNode: http://localhost:8000"
else
    echo "❌ NameNode no responde"
fi

# Verificar DataNodes
for port in 8001 8002 8003; do
    if curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ DataNode: http://localhost:$port"
    else
        echo "❌ DataNode en puerto $port no responde"
    fi
done

# Configurar cliente
echo ""
echo "🐍 Configurando cliente..."
cd client

# Hacer scripts ejecutables
chmod +x setup_client.sh run_client.sh clean_env.sh

# Configurar entorno virtual
./setup_client.sh

cd ..

echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo ""
echo "📋 Servicios disponibles:"
echo "   • NameNode: http://localhost:8000"
echo "   • DataNode1: http://localhost:8001"
echo "   • DataNode2: http://localhost:8002"
echo "   • DataNode3: http://localhost:8003"
echo ""
echo "📖 Para usar el cliente:"
echo "   cd client"
echo "   ./run_client.sh --help"
echo ""
echo "🧪 Para ejecutar pruebas:"
echo "   python3 test_system.py"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs: docker-compose logs"
echo "   • Detener: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo ""
echo "💡 Ejemplo de uso:"
echo "   cd client"
echo "   ./run_client.sh register usuario@email.com password"
echo "   ./run_client.sh login usuario password"
echo "   ./run_client.sh put /tmp/test.txt /test.txt"
