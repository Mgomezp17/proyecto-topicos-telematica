#!/bin/bash

echo "🔧 Reparando instalación de GridDFS"
echo "=================================="

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Limpiar imágenes fallidas
echo "🧹 Limpiando imágenes fallidas..."
docker system prune -f

# Reconstruir sin cache
echo "🔨 Reconstruyendo contenedores..."
docker-compose build --no-cache

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker-compose up -d

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

echo ""
echo "🎉 ¡Reparación completada!"
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
