# 🚀 Despliegue de MeriBot

Esta guía describe cómo desplegar MeriBot en diferentes entornos utilizando Docker y las mejores prácticas de contenedorización.

## 📋 Prerrequisitos

- **Docker** 20.10+ y **Docker Compose** 2.0+
- **Acceso a API de OpenAI** (o Azure OpenAI)
- **Variables de entorno** configuradas

## 🔧 Configuración de Variables de Entorno

Crea un archivo `.env` en la carpeta `meribot_app/`:

```bash
# API Keys
OPENAI_API_KEY=tu_api_key_aqui

# Configuración de la aplicación
ENV=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Base de datos vectorial (ChromaDB local)
CHROMA_DB_PATH=/app/chroma_data

# Configuración del crawler (opcional)
CRAWLER_ENABLED=true
SCRAPING_INTERVAL=86400  # 24 horas en segundos
```

## 🐳 Despliegue con Docker (Recomendado)

### Desarrollo Local

```bash
# Navegar a la carpeta de la aplicación
cd meribot_app

# Construir y ejecutar en modo desarrollo
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f meribot
```

**URLs disponibles:**
- 🤖 **Chatbot Widget**: http://localhost:8000
- 📚 **Documentación API**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/chatbot/health

### Producción

```bash
# Construir imagen optimizada para producción
docker build --target production -t meribot:latest .

# Ejecutar contenedor en producción
docker run -d \
  --name meribot-prod \
  -p 8000:8000 \
  --env-file .env \
  -v meribot_logs:/app/logs \
  -v meribot_chroma:/app/chroma_data \
  -v meribot_scraped:/app/data/scraped \
  --restart unless-stopped \
  meribot:latest
```

## 🏗️ Arquitectura de Despliegue

```
┌─────────────────────────────────────────┐
│              Load Balancer              │
│            (Nginx/Traefik)              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            MeriBot Container            │
│  ┌─────────────────────────────────────┐ │
│  │         FastAPI Server              │ │
│  │    (API + Widget Frontend)          │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │       ChromaDB Local               │ │
│  │    (Base de datos vectorial)       │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 📊 Monitoreo y Mantenimiento

### Health Checks

```bash
# Verificar estado del servicio
curl -f http://localhost:8000/chatbot/health

# Verificar logs del contenedor
docker logs meribot-api

# Verificar recursos del contenedor
docker stats meribot-api
```

### Gestión de Datos

```bash
# Backup de la base de datos vectorial
docker run --rm -v meribot_chroma:/data -v $(pwd):/backup alpine tar czf /backup/chroma_backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v meribot_chroma:/data -v $(pwd):/backup alpine tar xzf /backup/chroma_backup.tar.gz -C /data

# Limpiar logs antiguos
docker exec meribot-api find /app/logs -name "*.log" -mtime +30 -delete
```

### Comandos de Administración

```bash
# Ejecutar comandos CLI dentro del contenedor
docker exec -it meribot-api python -m meribot.meri-cli --help

# Ejecutar scraping manual
docker exec -it meribot-api python -m meribot.meri-cli scrape --url https://ejemplo.com

# Verificar estado de la base de datos
docker exec -it meribot-api python -m meribot.meri-cli db --status
```

## 🔒 Seguridad

### Configuración de Producción

1. **Usuario no-root**: El contenedor ejecuta con usuario `meribot` (UID 1000)
2. **Puertos mínimos**: Solo expone puerto 8000 necesario
3. **Variables sensibles**: Usar archivos `.env` o secrets de Docker
4. **Health checks**: Monitoreo automático del estado del servicio

### Autenticación

- **Desarrollo**: Sin autenticación requerida
- **Producción**: Integración con autenticación corporativa
  - Headers de autenticación corporativa
  - Validación de usuarios autorizados
  - Logging de accesos y consultas

### Red y Firewall

```bash
# Crear red personalizada para aislamiento
docker network create meribot-network

# Ejecutar con red personalizada
docker run --network meribot-network -d meribot:latest
```

## 🔄 Actualización y Rollback

### Actualización

```bash
# Construir nueva versión
docker build -t meribot:v2.0.0 .

# Parar versión actual
docker stop meribot-api

# Ejecutar nueva versión
docker run -d --name meribot-api-new \
  -p 8000:8000 \
  --env-file .env \
  meribot:v2.0.0

# Verificar funcionamiento
curl -f http://localhost:8000/chatbot/health

# Remover versión anterior (si todo OK)
docker rm meribot-api
docker rename meribot-api-new meribot-api
```

### Rollback

```bash
# Parar versión problemática
docker stop meribot-api

# Volver a versión anterior
docker run -d --name meribot-api \
  -p 8000:8000 \
  --env-file .env \
  meribot:v1.0.0
```

## 📈 Escalabilidad

Para entornos de alto tráfico:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  meribot:
    image: meribot:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    ports:
      - "8000-8002:8000"
```

## 🆘 Solución de Problemas

### Problemas Comunes

1. **Puerto ocupado**: Cambiar puerto en `.env` y docker-compose
2. **API Key inválida**: Verificar OPENAI_API_KEY en variables de entorno
3. **Permisos de archivos**: Verificar ownership de volúmenes persistentes
4. **Memoria insuficiente**: Aumentar límites del contenedor

### Logs y Debugging

```bash
# Logs detallados
docker-compose logs -f --tail=100 meribot

# Acceder al contenedor para debugging
docker exec -it meribot-api bash

# Verificar configuración
docker exec -it meribot-api env | grep -E "(OPENAI|ENV|PORT)"
```

