# BusFeed Frontend - Dockerfile para React
# Imagem Node.js para desenvolvimento

FROM node:18-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código da aplicação
COPY . .

# Expor porta 3000 (padrão React)
EXPOSE 3000

# Comando padrão será definido no docker-compose.yml 