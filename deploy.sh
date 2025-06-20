#!/bin/bash

# BusFeed - Script de Deploy para Produção
# Automatiza o processo de deploy da aplicação

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do BusFeed para produção..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log com cor
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado!"
    log_info "Copie o arquivo env.prod.example para .env e configure as variáveis."
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    log_error "Docker não está rodando!"
    exit 1
fi

# Verificar se docker-compose está disponível
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose não está instalado!"
    exit 1
fi

log_info "Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

log_info "Removendo volumes antigos (se solicitado)..."
read -p "Deseja limpar volumes antigos? (isso apagará todos os dados) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml down -v
    log_warn "Volumes removidos!"
fi

log_info "Construindo imagens..."
docker-compose -f docker-compose.prod.yml build --no-cache

log_info "Iniciando serviços de banco de dados..."
docker-compose -f docker-compose.prod.yml up -d db redis

log_info "Aguardando banco de dados ficar pronto..."
sleep 30

log_info "Executando migrações..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate

log_info "Coletando arquivos estáticos..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput

log_info "Criando superusuário (se necessário)..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@busfeed.com').exists():
    User.objects.create_superuser('admin', 'admin@busfeed.com', 'admin123')
    print('Superusuário criado: admin@busfeed.com / admin123')
else:
    print('Superusuário já existe')
"

log_info "Iniciando todos os serviços..."
docker-compose -f docker-compose.prod.yml up -d

log_info "Aguardando serviços ficarem prontos..."
sleep 15

log_info "Verificando health checks..."
for i in {1..5}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_info "✅ Health check passou!"
        break
    else
        log_warn "Health check falhou, tentativa $i/5..."
        sleep 10
    fi
done

log_info "Mostrando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

log_info "🎉 Deploy concluído com sucesso!"
log_info "Acesse a aplicação em: http://localhost"
log_info "Admin em: http://localhost/admin"
log_info "API docs em: http://localhost/api/docs/"

echo
log_info "Para monitorar os logs, use:"
echo "docker-compose -f docker-compose.prod.yml logs -f"

echo
log_info "Para parar a aplicação, use:"
echo "docker-compose -f docker-compose.prod.yml down" 