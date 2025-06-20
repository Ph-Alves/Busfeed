# 📁 Reorganização da Estrutura do Projeto BusFeed

## 🎯 Objetivo
Reorganizar a estrutura de pastas do projeto para melhor organização, manutenibilidade e separação de responsabilidades.

## 📋 Mudanças Realizadas

### ✅ Estrutura Anterior (Problemas)
- Arquivos misturados na raiz do projeto
- Apps Django espalhados na raiz
- Documentação e scripts de deploy misturados
- Configurações e dados não organizados

### ✅ Nova Estrutura (Soluções)

#### 📂 `backend/` - Backend Django Centralizado
- **`backend/apps/`** - Todos os apps Django organizados
  - `usuarios/` - Gerenciamento de usuários
  - `linhas/` - Linhas de ônibus
  - `paradas/` - Paradas de ônibus
  - `rotas/` - Sistema de rotas
- **`backend/core/`** - Configurações centrais (antigo `busfeed/`)
- **`backend/services/`** - Serviços compartilhados
- **`backend/manage.py`** - Gerenciador Django
- **`backend/requirements.txt`** - Dependências Python
- **`backend/env.example`** - Variáveis de ambiente

#### 📂 `frontend/` - Frontend React (Mantido)
- Estrutura React preservada integralmente

#### 📂 `deploy/` - Configurações de Deploy
- **`deploy/docker/`** - Arquivos Docker e docker-compose
- **`deploy/nginx/`** - Configurações do Nginx

#### 📂 `scripts/` - Scripts Utilitários
- `deploy.sh` - Script de deploy
- `monitor.sh` - Script de monitoramento
- `instalar_postgis.sh` - Instalação PostGIS

#### 📂 `docs/` - Documentação Centralizada
- Toda documentação `.md` organizada
- README principal, arquitetura técnica, deploy, etc.

#### 📂 `data/` - Dados e Logs
- **`data/databases/`** - Bancos de dados SQLite
- **`data/logs/`** - Logs da aplicação

## 🔧 Ajustes Técnicos Realizados

### 📝 Atualização do `.gitignore`
```diff
- db.sqlite3
- db.sqlite3-journal
+ data/databases/db.sqlite3
+ data/databases/db.sqlite3-journal
+ data/databases/*.sqlite3
+ data/logs/*.log
+ backend/.env
+ backend/.env.local
+ backend/.env.production
```

### 📄 Criação de Arquivos de Suporte
- `backend/apps/__init__.py` - Mantém a pasta como pacote Python
- `README.md` - Documentação da nova estrutura na raiz

## 📋 Benefícios Alcançados

1. **🎯 Separação Clara de Responsabilidades**
   - Backend, frontend e deploy bem separados
   - Cada tipo de arquivo em sua pasta específica

2. **📦 Modularidade Melhorada**
   - Apps Django organizados em `backend/apps/`
   - Serviços compartilhados em `backend/services/`

3. **📚 Documentação Centralizada**
   - Toda documentação em um local (`docs/`)
   - Fácil navegação e manutenção

4. **🔧 Scripts e Deploy Organizados**
   - Scripts utilitários em `scripts/`
   - Configurações de deploy em `deploy/`

5. **💾 Isolamento de Dados**
   - Bancos de dados em `data/databases/`
   - Logs em `data/logs/`

6. **🚀 Facilidade de Deploy**
   - Configurações Docker organizadas
   - Scripts de deploy centralizados

## ⚠️ Pontos de Atenção

- **Caminhos Relativos**: Alguns scripts podem precisar de ajuste nos caminhos
- **Configurações**: Verificar se todas as configurações estão apontando para os novos caminhos
- **Deploy**: Testar scripts de deploy com a nova estrutura

## 🎉 Resultado Final

A estrutura agora segue as melhores práticas de organização de projetos Django/React, facilitando:
- Desenvolvimento colaborativo
- Manutenção do código
- Deploy e operações
- Documentação e onboarding

---

*Reorganização realizada em 19/06/2024 seguindo as diretrizes de arquitetura limpa e modularidade* 