# BusFeed - Sistema de Transporte Público de Brasília

## 📁 Estrutura do Projeto

```
Projeto/
├── 📂 backend/                    # Backend Django
│   ├── 📂 apps/                   # Apps Django
│   │   ├── 📂 usuarios/           # Gerenciamento de usuários
│   │   ├── 📂 linhas/             # Linhas de ônibus
│   │   ├── 📂 paradas/            # Paradas de ônibus
│   │   └── 📂 rotas/              # Sistema de rotas
│   ├── 📂 core/                   # Configurações centrais (busfeed/)
│   │   ├── settings.py            # Configurações Django
│   │   ├── urls.py                # URLs principais
│   │   └── ...
│   ├── 📂 services/               # Serviços compartilhados
│   │   └── dftrans_api.py         # Integração com DFTrans
│   ├── manage.py                  # Gerenciador Django
│   ├── requirements.txt           # Dependências Python
│   ├── env.example                # Exemplo de variáveis de ambiente
│   └── env.prod.example           # Exemplo para produção
│
├── 📂 frontend/                   # Frontend React
│   ├── 📂 src/                    # Código fonte React
│   ├── 📂 public/                 # Arquivos públicos
│   ├── package.json               # Dependências Node.js
│   └── ...
│
├── 📂 deploy/                     # Configurações de deploy
│   ├── 📂 docker/                 # Arquivos Docker
│   │   ├── Dockerfile
│   │   ├── Dockerfile.prod
│   │   ├── docker-compose.yml
│   │   └── docker-compose.prod.yml
│   └── 📂 nginx/                  # Configurações Nginx
│       └── nginx.prod.conf
│
├── 📂 scripts/                    # Scripts utilitários
│   ├── deploy.sh                  # Script de deploy
│   ├── monitor.sh                 # Script de monitoramento
│   └── instalar_postgis.sh        # Instalação PostGIS
│
├── 📂 docs/                       # Documentação
│   ├── README.md                  # Documentação principal
│   ├── ARQUITETURA_TECNICA.md     # Arquitetura técnica
│   ├── DEPLOY.md                  # Guia de deploy
│   └── ...
│
├── 📂 data/                       # Dados e logs
│   ├── 📂 databases/              # Bancos de dados
│   │   ├── db.sqlite3
│   │   └── db_postgis_ready.sqlite3
│   └── 📂 logs/                   # Logs da aplicação
│       └── busfeed.log
│
└── 📄 .gitignore                  # Arquivos ignorados pelo Git
```

## 🚀 Como Usar

### Backend (Django)
```bash
cd backend
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm start
```

### Deploy
```bash
# Usar scripts da pasta scripts/
./scripts/deploy.sh
```

## 📋 Benefícios da Nova Estrutura

1. **🎯 Separação Clara**: Backend, frontend e deploy bem separados
2. **📦 Modularidade**: Apps Django organizados em `backend/apps/`
3. **📚 Documentação Centralizada**: Toda documentação em `docs/`
4. **🔧 Scripts Organizados**: Utilitários em `scripts/`
5. **💾 Dados Isolados**: Bancos e logs em `data/`
6. **🚀 Deploy Simplificado**: Configurações em `deploy/`

## 🔧 Configuração

1. Configure as variáveis de ambiente usando `backend/env.example`
2. Instale as dependências: `pip install -r backend/requirements.txt`
3. Execute as migrações: `cd backend && python manage.py migrate`
4. Inicie o servidor: `python manage.py runserver`

---

*Projeto desenvolvido seguindo as melhores práticas de arquitetura Django e React* 