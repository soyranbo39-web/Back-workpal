# Usar una imagen de Python oficial
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry

# Configurar poetry para no crear un entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false

# Copiar archivos de configuración de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias
RUN poetry install --no-interaction --no-ansi --no-root

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
