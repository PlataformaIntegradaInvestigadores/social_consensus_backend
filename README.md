# CENTINELA - Social Consensus

## Descripción

Este proyecto Django implementa un servicio de autorización y consenso para la plataforma Centinela.

## Requisitos Previos

- Docker
- Docker Compose

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/PlataformaIntegradaInvestigadores/social_consensus_backend
   ```
2. Accede al directorio del proyecto:
   ```bash
   cd social_consensus_backend
   ```
3. Renombra el archivo `.env.template` a `.env`. Completa las variables de entorno con los valores correspondientes.

    ```bash
    # Django settings
    DEBUG=True
    SECRET_KEY="your-secret-key"

    # Database settings
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=db
    DB_PORT=5432

    # Redis settings
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_PASSWORD=your_redis_password
    ```

4. Construye las imágenes y levanta los contenedores:
   ```bash
   docker-compose up --build -d
   ```
5. Realiza las migraciones:
    ```bash
    docker exec -it <nombre_del_contenedor>
    python manage.py makemigrations
    python manage.py migrate
    ```
6. Accede a la URL `http://localhost:8000/` para verificar que el servidor está corriendo correctamente.
7. Para detener los contenedores, ejecuta:
   ```bash
   docker-compose down
   ```