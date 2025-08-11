FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar los requisitos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . .

# Puerto por defecto para FastAPI
EXPOSE 8000

# Comando por defecto para ejecutar la API
CMD ["uvicorn", "meribot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
