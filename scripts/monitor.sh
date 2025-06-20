#!/bin/bash

# BusFeed - Script de Monitoramento
# Verifica a saúde da aplicação e serviços

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

echo "🔍 BusFeed - Monitoramento da Aplicação"
echo "========================================"

# Verificar se containers estão rodando
log_check "Verificando status dos containers..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    log_info "✅ Containers estão rodando"
    docker-compose -f docker-compose.prod.yml ps
else
    log_error "❌ Alguns containers não estão rodando"
    docker-compose -f docker-compose.prod.yml ps
fi

echo

# Verificar health checks
log_check "Verificando health checks..."

# Health check principal
if curl -s -f http://localhost/health > /dev/null; then
    log_info "✅ Health check principal: OK"
    curl -s http://localhost/health | jq . 2>/dev/null || curl -s http://localhost/health
else
    log_error "❌ Health check principal: FALHOU"
fi

echo

# Liveness check
if curl -s -f http://localhost/api/health/live/ > /dev/null; then
    log_info "✅ Liveness check: OK"
else
    log_error "❌ Liveness check: FALHOU"
fi

# Readiness check
if curl -s -f http://localhost/api/health/ready/ > /dev/null; then
    log_info "✅ Readiness check: OK"
else
    log_error "❌ Readiness check: FALHOU"
fi

echo

# Verificar recursos do sistema
log_check "Verificando recursos do sistema..."

# Uso de CPU dos containers
echo "Uso de CPU/Memória dos containers:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker-compose -f docker-compose.prod.yml ps -q)

echo

# Verificar logs recentes por erros
log_check "Verificando logs recentes por erros..."
ERROR_COUNT=$(docker-compose -f docker-compose.prod.yml logs --tail=100 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)

if [ "$ERROR_COUNT" -gt 0 ]; then
    log_warn "⚠️  Encontrados $ERROR_COUNT erros nos logs recentes"
    echo "Últimos erros:"
    docker-compose -f docker-compose.prod.yml logs --tail=100 2>/dev/null | grep -i "error\|exception\|failed" | tail -5
else
    log_info "✅ Nenhum erro encontrado nos logs recentes"
fi

echo

# Verificar conectividade de rede
log_check "Verificando conectividade..."

# Ping para serviços externos (DFTrans API)
if ping -c 1 www.sistemas.dftrans.df.gov.br > /dev/null 2>&1; then
    log_info "✅ Conectividade com DFTrans: OK"
else
    log_warn "⚠️  Conectividade com DFTrans: PROBLEMA"
fi

echo

# Verificar espaço em disco
log_check "Verificando espaço em disco..."
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log_warn "⚠️  Espaço em disco baixo: ${DISK_USAGE}%"
else
    log_info "✅ Espaço em disco: ${DISK_USAGE}%"
fi

# Verificar tamanho dos volumes Docker
echo "Tamanho dos volumes Docker:"
docker system df

echo

# Verificar performance das APIs
log_check "Verificando performance das APIs..."

# Testar tempo de resposta
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost/api/health/)
RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc)

if (( $(echo "$RESPONSE_TIME > 2.0" | bc -l) )); then
    log_warn "⚠️  Tempo de resposta lento: ${RESPONSE_MS}ms"
else
    log_info "✅ Tempo de resposta: ${RESPONSE_MS}ms"
fi

echo

# Resumo
echo "========================================="
log_check "Resumo do Monitoramento"

# Verificar se tudo está OK
OVERALL_STATUS="OK"

# Verificar containers
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    OVERALL_STATUS="PROBLEMA"
fi

# Verificar health checks
if ! curl -s -f http://localhost/health > /dev/null; then
    OVERALL_STATUS="PROBLEMA"
fi

if [ "$OVERALL_STATUS" = "OK" ]; then
    log_info "🎉 Sistema funcionando normalmente!"
else
    log_error "⚠️  Sistema com problemas detectados!"
fi

echo
log_info "Para logs detalhados: docker-compose -f docker-compose.prod.yml logs -f"
log_info "Para reiniciar: ./deploy.sh" 