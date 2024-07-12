# Usar una imagen oficial de Python
FROM python:3.11-bookworm

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente del proyecto
COPY . .

# Comando para ejecutar el servidor
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"]
