#!/bin/bash

echo "🐍 Configurando entorno virtual para GridDFS Client"
echo "=================================================="

# Verificar que Python3 esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    echo "💡 Instala Python3 desde https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verificar que pip3 esté instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 no está instalado"
    exit 1
fi

echo "✅ pip3 encontrado: $(pip3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📁 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Para usar el cliente:"
echo "   1. Activar entorno virtual: source venv/bin/activate"
echo "   2. Usar el cliente: python -m client.cli --help"
echo ""
echo "🚀 O usar el script de inicio rápido:"
echo "   ./run_client.sh"
echo ""
echo "💡 Para desactivar el entorno virtual: deactivate"
