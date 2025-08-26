FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Crear entorno virtual
RUN python3 -m venv /app/venv

# Activar entorno virtual y actualizar pip
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip

# Copiar requirements e instalar dependencias en el entorno virtual
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
