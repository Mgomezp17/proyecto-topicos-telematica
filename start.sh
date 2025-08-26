#!/bin/bash

echo "🚀 Iniciando GridDFS - Sistema de Archivos Distribuido por Bloques"
echo "================================================================"

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker y Docker Compose encontrados"

# Detener contenedores existentes si los hay
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Construir e iniciar los servicios
echo "🔨 Construyendo e iniciando servicios..."
docker-compose up -d --build

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

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

echo ""
echo "🎉 GridDFS iniciado exitosamente!"
echo ""
echo "📋 Servicios disponibles:"
echo "   • NameNode: http://localhost:8000"
echo "   • DataNode1: http://localhost:8001"
echo "   • DataNode2: http://localhost:8002"
echo "   • DataNode3: http://localhost:8003"
echo ""
echo "📖 Para configurar el cliente:"
echo "   1. cd client"
echo "   2. ./setup_client.sh"
echo "   3. ./run_client.sh --help"
echo ""
echo "🔧 Para ver logs: docker-compose logs"
echo "🛑 Para detener: docker-compose down"
