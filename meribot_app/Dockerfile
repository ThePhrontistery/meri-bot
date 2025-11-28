# =====================================================
# Dockerfile para MeriBot - Chatbot Empresarial
# Versión optimizada con Python 3.12 y mejores prácticas
# =====================================================

FROM python:3.12-slim as base

# Configurar variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# =====================================================
# Etapa de construcción
# =====================================================
FROM base as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para construcción
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# =====================================================
# Etapa de producción
# =====================================================
FROM base as production

WORKDIR /app

# Crear usuario no-root para seguridad
RUN groupadd -r meribot && useradd -r -g meribot meribot

# Instalar solo dependencias runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias Python desde builder
COPY --from=builder /root/.local /home/meribot/.local

# Copiar código de la aplicación
COPY --chown=meribot:meribot . .

# Crear directorios necesarios con permisos correctos
RUN mkdir -p /app/logs /app/chroma_data /app/data/scraped && \
    chown -R meribot:meribot /app

# Cambiar a usuario no-root
USER meribot

# Agregar binarios locales al PATH
ENV PATH=/home/meribot/.local/bin:$PATH

# Puerto por defecto para FastAPI
EXPOSE 8000

# Health check para monitoreo
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/chatbot/health || exit 1

# Variables de entorno por defecto
ENV ENV=production \
    HOST=0.0.0.0 \
    PORT=8000

# Comando por defecto para ejecutar la API
CMD ["uvicorn", "meribot.core.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
