# Despliegue

## Producción- Ejecución con Docker (Recomendado)

```bash
# Construir y ejecutar los contenedores
docker-compose up --build

# Para ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Despliegue

1. Configura las variables de entorno en producción (`DATABASE_URL`, `SECRET_KEY`, etc.)
2. Construye las imágenes para producción:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```
3. Inicia los servicios:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Autenticación

- No requerida en entorno dev.
- Corporativa en producción.

