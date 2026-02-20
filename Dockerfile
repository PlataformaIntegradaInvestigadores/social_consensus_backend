# Usar una imagen oficial de Python más ligera (slim)
FROM python:3.11-slim-bookworm

# Optimizaciones de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias (ej. para compilar psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente del proyecto
COPY . .

# Comando para ejecutar el servidor
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"]
