#!/bin/bash

# BusFeed - Script de Instalação PostGIS e GDAL no macOS
# Este script instala e configura as dependências necessárias para usar PostGIS

echo "🚌 BusFeed - Configurando PostGIS e GDAL..."

# Verifica se Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew não encontrado. Instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "📦 Instalando dependências..."

# Instala PostgreSQL e PostGIS
brew install postgresql postgis

# Instala GDAL
brew install gdal

# Instala spatialite para desenvolvimento
brew install spatialite-tools libspatialite

echo "🐋 Instalando Docker..."
brew install --cask docker

echo "🔧 Configurando variáveis de ambiente..."

# Encontra o caminho do GDAL
GDAL_PATH=$(brew --prefix gdal)
SPATIALITE_PATH=$(brew --prefix libspatialite)

echo "Adicione estas linhas ao seu ~/.zshrc ou ~/.bash_profile:"
echo ""
echo "# BusFeed PostGIS Configuration"
echo "export GDAL_LIBRARY_PATH=$GDAL_PATH/lib/libgdal.dylib"
echo "export GEOS_LIBRARY_PATH=$(brew --prefix geos)/lib/libgeos_c.dylib"
echo "export SPATIALITE_LIBRARY_PATH=$SPATIALITE_PATH/lib/libspatialite.dylib"
echo ""

# Cria arquivo de configuração local
cat > .env.postgis << EOF
# Configurações PostGIS para produção
USE_POSTGRES=true
DB_NAME=busfeed_db
DB_USER=busfeed_user
DB_PASSWORD=busfeed_password
DB_HOST=localhost
DB_PORT=5432

# Caminhos das bibliotecas (macOS)
GDAL_LIBRARY_PATH=$GDAL_PATH/lib/libgdal.dylib
GEOS_LIBRARY_PATH=$(brew --prefix geos)/lib/libgeos_c.dylib
SPATIALITE_LIBRARY_PATH=$SPATIALITE_PATH/lib/libspatialite.dylib
EOF

echo "✅ Dependências instaladas!"
echo ""
echo "📋 Próximos passos:"
echo "1. Recarregue seu shell: source ~/.zshrc"
echo "2. Execute: docker-compose up -d db"
echo "3. Execute: python3 manage.py migrate"
echo "4. Execute: python3 manage.py migrar_para_postgis"
echo ""
echo "📄 Arquivo .env.postgis criado com as configurações."
echo "   Copie o conteúdo para .env quando estiver pronto para usar PostGIS." 