# BusFeed - Dockerfile para aplicação Django
# Imagem base Python com suporte a bibliotecas geográficas

FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema para PostGIS e bibliotecas geográficas
RUN apt-get update && apt-get install -y \
    gcc \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta 8000 (padrão Django)
EXPOSE 8000

# Comando padrão será definido no docker-compose.yml 