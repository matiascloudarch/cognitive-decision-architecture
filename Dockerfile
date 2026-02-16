FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para networking
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración e instalar dependencias de Python
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copiar el resto del código
COPY . .

# Configurar variables de entorno por defecto
ENV CDA_SECRET_KEY="internal_development_secret_key_fixed_32_chars"
ENV PYTHONPATH=/app

# Exponer los puertos (Informativo)
EXPOSE 8000
EXPOSE 8001

# Por defecto no ejecuta nada, el comando lo decide docker-compose
CMD ["python3"]
