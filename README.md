# 🚌 BusFeed - Sistema de Transporte Público Inteligente

> Plataforma completa para monitoramento e otimização do transporte público de Brasília

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0+-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange.svg)]()

## 📖 Índice

- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [✨ Funcionalidades](#-funcionalidades)
- [🏗️ Arquitetura](#️-arquitetura)
- [🚀 Instalação](#-instalação)
- [⚙️ Configuração](#️-configuração)
- [📱 Interface](#-interface)
- [🔧 Desenvolvimento](#-desenvolvimento)
- [📊 Performance](#-performance)
- [🛡️ Segurança](#️-segurança)
- [🤝 Contribuição](#-contribuição)
- [📄 Licença](#-licença)

## 📋 Sobre o Projeto

O **BusFeed** é um sistema inteligente de transporte público desenvolvido especificamente para Brasília, que integra dados em tempo real, otimização de rotas e acessibilidade total para todos os usuários.

### 🎯 Objetivos

- **Eficiência**: Otimizar o tempo de viagem dos cidadãos
- **Acessibilidade**: Interface 100% acessível seguindo WCAG 2.1 AA
- **Sustentabilidade**: Reduzir congestionamentos e emissões
- **Inclusão**: Atender todos os perfis de usuários
- **Transparência**: Dados abertos e APIs públicas

### 🌟 Diferenciais

- ♿ **Totalmente acessível** com suporte a leitores de tela
- 🗺️ **Mapas interativos** com localização em tempo real
- 📱 **Design responsivo** para todos os dispositivos  
- 🔄 **Dados em tempo real** do transporte público
- 🚀 **Performance otimizada** com cache inteligente
- 🔒 **Seguro por design** seguindo melhores práticas

## ✨ Funcionalidades

### 🚌 Gestão de Transporte

- **Rotas Inteligentes**: Algoritmos de otimização de trajetos
- **Paradas Dinâmicas**: Informações completas sobre cada parada
- **Horários Precisos**: Sistema de cronogramas integrado
- **Tempo Real**: Localização GPS dos veículos
- **Previsões**: Estimativas de chegada precisas

### 👥 Experiência do Usuário

- **Busca Intuitiva**: Encontre rapidamente sua rota
- **Mapas Interativos**: Visualização clara dos trajetos
- **Notificações**: Alertas sobre atrasos e mudanças
- **Favoritos**: Salve suas rotas mais utilizadas
- **Feedback**: Sistema de avaliação e sugestões

### 🔧 Recursos Técnicos

- **APIs RESTful**: Integração com sistemas externos
- **Cache Inteligente**: Performance otimizada
- **Logs Detalhados**: Monitoramento completo
- **Backup Automático**: Proteção de dados
- **Escalabilidade**: Pronto para milhares de usuários

## 🏗️ Arquitetura

### 📐 Padrões Arquiteturais

```
├── 🏛️ Clean Architecture
├── 🎯 MVC Pattern
├── 🔄 Repository Pattern
├── 🏭 Factory Pattern
└── 📦 Dependency Injection
```

### 🗂️ Estrutura do Projeto

```
busfeed/
├── 📁 core/                    # Módulo central
│   ├── models.py              # Modelos base abstratos
│   ├── views.py               # Views centrais
│   └── context_processors.py  # Processadores de contexto
├── 📁 routes/                 # Gestão de rotas
│   ├── models.py              # Modelos de rotas e veículos
│   ├── views.py               # Views de rotas
│   ├── serializers.py         # Serializers para API
│   └── management/commands/    # Comandos de importação
├── 📁 stops/                  # Gestão de paradas
│   ├── models.py              # Modelos de paradas
│   ├── views.py               # Views de paradas
│   └── utils.py               # Utilitários geográficos
├── 📁 schedules/              # Horários e cronogramas
│   ├── models.py              # Modelos de horários
│   ├── views.py               # Views de cronogramas
│   └── tasks.py               # Tarefas assíncronas
├── 📁 notifications/          # Sistema de notificações
│   ├── models.py              # Modelos de notificações
│   ├── views.py               # Views de alertas
│   └── services.py            # Serviços de notificação
├── 📁 templates/              # Templates HTML
│   ├── base.html              # Template base
│   ├── core/                  # Templates do core
│   ├── routes/                # Templates de rotas
│   └── components/            # Componentes reutilizáveis
├── 📁 static/                 # Arquivos estáticos
│   ├── css/                   # Estilos CSS
│   ├── js/                    # Scripts JavaScript
│   └── img/                   # Imagens e ícones
└── 📁 busfeed/                # Configurações do projeto
    ├── settings.py            # Configurações Django
    ├── urls.py                # URLs principais
    └── wsgi.py                # Configuração WSGI
```

### 🎨 Stack Tecnológica

#### Backend
- **Django 4.2+**: Framework web robusto
- **Python 3.9+**: Linguagem principal
- **PostgreSQL**: Banco de dados principal
- **PostGIS**: Extensão geográfica
- **Redis**: Cache e sessões
- **Celery**: Tarefas assíncronas

#### Frontend
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript ES6+**: Interatividade
- **Leaflet.js**: Mapas interativos
- **Chart.js**: Gráficos e visualizações
- **Font Awesome**: Ícones

#### DevOps & Deploy
- **Docker**: Containerização
- **Nginx**: Servidor web
- **Gunicorn**: Servidor WSGI
- **GitHub Actions**: CI/CD
- **Sentry**: Monitoramento de erros

## 🚀 Instalação

### 📋 Pré-requisitos

```bash
# Python 3.9 ou superior
python --version

# Git para controle de versão
git --version

# Node.js (opcional, para desenvolvimento frontend)
node --version
```

### 🔧 Instalação Local

#### 1. Clone o repositório
```bash
git clone https://github.com/usuario/busfeed.git
cd busfeed
```

#### 2. Crie e ative o ambiente virtual
```bash
# Linux/Mac
python -m venv busfeed_env
source busfeed_env/bin/activate

# Windows
python -m venv busfeed_env
busfeed_env\Scripts\activate
```

#### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite as configurações necessárias
nano .env
```

#### 5. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Carregue dados iniciais
```bash
# Dados básicos do sistema
python manage.py loaddata fixtures/initial_data.json

# Importar dados do OpenStreetMap (opcional)
python manage.py import_osm_routes
```

#### 7. Colete arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

#### 8. Crie um superusuário
```bash
python manage.py createsuperuser
```

#### 9. Execute o servidor
```bash
python manage.py runserver
```

### 🐳 Instalação com Docker

```bash
# Clone o repositório
git clone https://github.com/usuario/busfeed.git
cd busfeed

# Execute com Docker Compose
docker-compose up -d

# Acesse em http://localhost:8000
```

## ⚙️ Configuração

### 🔐 Variáveis de Ambiente

Crie um arquivo `.env` baseado no `env.example`:

```env
# Configurações básicas
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=sqlite:///db.sqlite3
# Para PostgreSQL: DATABASE_URL=postgresql://user:pass@localhost/busfeed

# Cache (Redis em produção)
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app

# APIs externas
DFTRANS_API_URL=https://api.dftrans.df.gov.br
DFTRANS_API_KEY=sua-chave-api

# Logging
DJANGO_LOG_LEVEL=INFO
```

### 🗄️ Configuração do Banco de Dados

#### SQLite (Desenvolvimento)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL (Produção)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'busfeed',
        'USER': 'postgres',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 🔧 Configurações Avançadas

```python
# Cache com Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Configurações específicas do BusFeed
BUSFEED_SETTINGS = {
    'MAX_SEARCH_RADIUS_KM': 5,
    'DEFAULT_WALKING_SPEED_KMH': 5,
    'CACHE_TIMEOUT_ROUTES': 3600,
    'REAL_TIME_UPDATE_INTERVAL': 30,
}
```

## 📱 Interface

### 🎨 Design System

O BusFeed utiliza um design system próprio baseado em:

- **Cores**: Esquema preto/branco/ciano para máxima acessibilidade
- **Tipografia**: Inter e Poppins para legibilidade
- **Espaçamentos**: Sistema modular de 8px
- **Componentes**: Biblioteca de componentes reutilizáveis

### ♿ Acessibilidade

- **WCAG 2.1 AA**: Conformidade total com diretrizes
- **Contraste**: Razão mínima de 4.5:1 para texto
- **Navegação**: 100% navegável por teclado
- **Leitores de tela**: Suporte completo a NVDA, JAWS, VoiceOver
- **Zoom**: Funcional até 200% sem perda de funcionalidade

### 📱 Responsividade

```css
/* Breakpoints otimizados */
@media (max-width: 576px)  { /* Celular */ }
@media (max-width: 768px)  { /* Tablet */ }
@media (max-width: 992px)  { /* Desktop pequeno */ }
@media (max-width: 1200px) { /* Desktop médio */ }
@media (min-width: 1201px) { /* Desktop grande */ }
```

## 🔧 Desenvolvimento

### 🛠️ Comandos Úteis

```bash
# Executar testes
python manage.py test

# Verificar código
python manage.py check --deploy

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Shell interativo
python manage.py shell

# Importar dados OSM
python manage.py import_osm_routes

# Limpar cache
python manage.py clear_cache
```

### 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Testes com cobertura
coverage run --source='.' manage.py test
coverage report
coverage html

# Testes específicos
python manage.py test routes.tests.test_models
```

### 📊 Qualidade de Código

```bash
# Linting com flake8
flake8 .

# Formatação com black
black .

# Análise de segurança
bandit -r .

# Análise de complexidade
radon cc .
```

### 🐛 Debug

```python
# Django Debug Toolbar
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Logging detalhado
import logging
logger = logging.getLogger(__name__)
logger.debug('Informação de debug')
```

## 📊 Performance

### ⚡ Otimizações Implementadas

- **Cache Redis**: Cache distribuído para alta performance
- **Query Optimization**: Uso de `select_related` e `prefetch_related`
- **Static Files**: Compressão e versionamento com WhiteNoise
- **Database Indexing**: Índices otimizados para consultas frequentes
- **Pagination**: Paginação inteligente para listas grandes

### 📈 Métricas de Performance

```python
# Monitoramento de queries
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['file'],
}

# Cache hit rate monitoring
CACHES['default']['KEY_FUNCTION'] = 'busfeed.utils.cache_key_generator'
```

### 🔍 Monitoramento

- **Sentry**: Monitoramento de erros em produção
- **New Relic**: APM para performance
- **Prometheus**: Métricas customizadas
- **Grafana**: Dashboards de monitoramento

## 🛡️ Segurança

### 🔒 Medidas de Segurança

- **HTTPS**: Obrigatório em produção
- **CSRF Protection**: Proteção contra ataques CSRF
- **SQL Injection**: Prevenção via ORM Django
- **XSS Protection**: Sanitização de dados
- **Rate Limiting**: Proteção contra abuso de APIs

### 🔐 Configurações de Segurança

```python
# Produção
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Headers de segurança
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 🔑 Gestão de Secrets

```bash
# Usar django-environ para secrets
pip install django-environ

# Arquivo .env (nunca commitar)
SECRET_KEY=sua-chave-super-secreta
DATABASE_URL=postgresql://...
```

## 🤝 Contribuição

### 📝 Como Contribuir

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
4. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. **Push** para a branch (`git push origin feature/AmazingFeature`)
6. **Abra** um Pull Request

### 📋 Diretrizes

- Siga o [PEP 8](https://pep8.org/) para código Python
- Escreva testes para novas funcionalidades
- Mantenha a documentação atualizada
- Use commits semânticos
- Teste a acessibilidade de suas mudanças

### 🐛 Reportar Bugs

Ao reportar bugs, inclua:

- Versão do Python e Django
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Logs de erro

### 💡 Sugerir Features

Para sugerir novas funcionalidades:

- Descreva o problema que resolve
- Proponha uma solução
- Considere alternativas
- Avalie o impacto na acessibilidade

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📞 Contato

- **Email**: contato@busfeed.com.br
- **Website**: [https://busfeed.com.br](https://busfeed.com.br)
- **GitHub**: [https://github.com/usuario/busfeed](https://github.com/usuario/busfeed)

---

<div align="center">

**Feito com ❤️ para o transporte público de Brasília**

[⬆ Voltar ao topo](#-busfeed---sistema-de-transporte-público-inteligente)

</div>