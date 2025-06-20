# 🚀 Guia de Deploy - BusFeed

## Pré-requisitos

### Sistema
- Docker 20.10+
- Docker Compose 2.0+
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Mínimo 2GB RAM, 20GB disco
- Conexão com internet estável

### Variáveis de Ambiente
Antes do deploy, configure o arquivo `.env` baseado no `env.prod.example`:

```bash
cp env.prod.example .env
```

**IMPORTANTE**: Configure as seguintes variáveis obrigatórias:
- `SECRET_KEY`: Chave secreta do Django (use uma segura!)
- `DB_PASSWORD`: Senha do banco PostgreSQL
- `REDIS_PASSWORD`: Senha do Redis
- `DFTRANS_API_KEY`: Chave da API do DFTrans (se disponível)

## Deploy Automático

### 1. Deploy Inicial
```bash
./deploy.sh
```

Este script automaticamente:
- Para containers existentes
- Constrói novas imagens
- Executa migrações do banco
- Coleta arquivos estáticos
- Cria superusuário padrão
- Inicia todos os serviços
- Verifica health checks

### 2. Credenciais Padrão
- **Admin**: admin@busfeed.com / admin123
- **⚠️ ALTERE IMEDIATAMENTE EM PRODUÇÃO!**

## Serviços Disponíveis

Após o deploy bem-sucedido:

- **Aplicação**: http://localhost
- **Admin Django**: http://localhost/admin
- **API Docs**: http://localhost/api/docs/
- **Health Check**: http://localhost/health

## Monitoramento

### Script de Monitoramento
```bash
./monitor.sh
```

Verifica:
- Status dos containers
- Health checks da aplicação
- Uso de recursos (CPU/Memória)
- Logs de erro
- Conectividade externa
- Performance das APIs

### Health Checks
- **Liveness**: `/api/health/live/` - Aplicação rodando
- **Readiness**: `/api/health/ready/` - Pronta para tráfego
- **Health**: `/health` - Status completo

### Logs
```bash
# Todos os logs
docker-compose -f docker-compose.prod.yml logs -f

# Log específico
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f db
```

## Comandos Úteis

### Gestão dos Containers
```bash
# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Iniciar apenas banco de dados
docker-compose -f docker-compose.prod.yml up -d db redis

# Rebuild de uma imagem específica
docker-compose -f docker-compose.prod.yml build web

# Executar comandos no container
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
```

### Backup do Banco
```bash
# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U busfeed_user_prod busfeed_db_prod > backup.sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U busfeed_user_prod busfeed_db_prod < backup.sql
```

### Limpeza do Sistema
```bash
# Remover imagens não utilizadas
docker system prune -a

# Remover volumes órfãos
docker volume prune
```

## Configurações de Produção

### Nginx
O arquivo `nginx.prod.conf` configura:
- Proxy reverso para Django
- Compressão gzip
- Cache de arquivos estáticos
- Rate limiting para APIs
- Headers de segurança

### PostgreSQL + PostGIS
- Banco otimizado para dados geográficos
- Conexões persistentes (CONN_MAX_AGE=600)
- Health checks automáticos

### Redis
- Cache de sessões e dados
- Compressão automática
- Configuração de segurança

### Django
- Gunicorn com 3 workers
- Arquivos estáticos via WhiteNoise
- Logs estruturados
- Monitoramento Sentry (se configurado)

## Troubleshooting

### Problemas Comuns

**Container não inicia**:
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs web

# Verificar configuração
docker-compose -f docker-compose.prod.yml config
```

**Banco não conecta**:
```bash
# Verificar se está rodando
docker-compose -f docker-compose.prod.yml ps db

# Testar conexão manual
docker-compose -f docker-compose.prod.yml exec db psql -U busfeed_user_prod busfeed_db_prod
```

**Performance lenta**:
```bash
# Verificar recursos
docker stats

# Verificar logs de erro
./monitor.sh
```

**Arquivos estáticos não carregam**:
```bash
# Recoletaar
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Logs de Debug
Para ativar logs detalhados temporariamente:

1. Edite `.env`: `DEBUG=1`
2. Restart: `docker-compose -f docker-compose.prod.yml restart web`
3. **LEMBRE DE DESATIVAR**: `DEBUG=0`

## Segurança

### Checklist de Segurança
- [ ] Alterar senha padrão do admin
- [ ] Configurar SECRET_KEY única
- [ ] Configurar senhas fortes para DB/Redis
- [ ] Configurar HTTPS (certificado SSL)
- [ ] Configurar firewall
- [ ] Backup regular do banco

### HTTPS/SSL
Para ativar HTTPS, descomente a seção SSL no `nginx.prod.conf` e:

1. Obtenha certificados SSL (Let's Encrypt recomendado)
2. Coloque-os em `./ssl/`
3. Atualize configuração DNS
4. Restart nginx

## Backup e Recuperação

### Backup Automático
O sistema está configurado para backup automático:
- Agendamento: `BACKUP_SCHEDULE=0 2 * * *` (2h da manhã)
- Local: volumes Docker persistentes

### Backup Manual
```bash
# Script de backup (criar quando necessário)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec db pg_dump -U busfeed_user_prod busfeed_db_prod | gzip > "backup_${DATE}.sql.gz"
```

## Escalabilidade

### Para maior tráfego:
1. Aumentar workers Gunicorn no `docker-compose.prod.yml`
2. Configurar load balancer (Nginx upstream)
3. Separar banco em servidor dedicado
4. Implementar CDN para arquivos estáticos

### Monitoramento Avançado:
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- APM tools (New Relic, DataDog)

## Suporte

Para problemas ou dúvidas:
1. Verificar logs: `./monitor.sh`
2. Consultar este guia
3. Verificar issues no repositório
4. Contatar equipe de desenvolvimento 