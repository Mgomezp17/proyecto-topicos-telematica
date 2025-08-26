#!/bin/bash

echo "🧹 Limpiando entorno virtual de GridDFS Client"
echo "=============================================="

# Verificar si el entorno virtual existe
if [ -d "venv" ]; then
    echo "🗑️ Eliminando entorno virtual..."
    rm -rf venv
    echo "✅ Entorno virtual eliminado"
else
    echo "ℹ️ No hay entorno virtual para eliminar"
fi

# Verificar si hay archivos de cache de Python
if [ -d "__pycache__" ]; then
    echo "🗑️ Eliminando archivos de cache..."
    rm -rf __pycache__
    echo "✅ Archivos de cache eliminados"
fi

# Verificar si hay archivos .pyc
PYC_FILES=$(find . -name "*.pyc" -type f)
if [ ! -z "$PYC_FILES" ]; then
    echo "🗑️ Eliminando archivos .pyc..."
    find . -name "*.pyc" -type f -delete
    echo "✅ Archivos .pyc eliminados"
fi

echo ""
echo "🎉 Limpieza completada"
echo ""
echo "💡 Para recrear el entorno virtual:"
echo "   ./setup_client.sh"
