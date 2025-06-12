"""
Django settings for busfeed project.

BusFeed - Sistema de transporte público inteligente para Brasília
=================================================================

Este arquivo contém todas as configurações do Django para o projeto BusFeed,
seguindo os princípios de Clean Architecture e boas práticas de desenvolvimento.

Estrutura:
- Configurações de segurança
- Apps e middleware
- Database e cache
- Arquivos estáticos e mídia
- Configurações de APIs externas
- Logging e monitoramento
- Configurações específicas do BusFeed

Autor: Equipe BusFeed
Data: 2025
Versão: 1.0.0
"""

from pathlib import Path
from decouple import config
import environ
import dj_database_url

# =============================================================================
# CONFIGURAÇÃO DE AMBIENTE
# =============================================================================

# Configuração de ambiente usando django-environ para type safety
env = environ.Env(
    DEBUG=(bool, False),  # Por padrão, produção não é debug
    USE_SSL=(bool, False),  # Para HTTPS em produção
    USE_CACHE=(bool, True),  # Cache ativado por padrão
)

# Diretório base do projeto - ponto de referência para todos os paths
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

# Chave secreta - OBRIGATÓRIA em produção via variável de ambiente
SECRET_KEY = config(
    'SECRET_KEY', 
    default='django-insecure-development-key-change-in-production'
)

# Debug - NUNCA deve estar True em produção
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts permitidos - configurar adequadamente em produção
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,0.0.0.0'
).split(',')

# =============================================================================
# APLICAÇÕES E COMPONENTES DO DJANGO
# =============================================================================

# Apps principais do Django necessários para funcionamento básico
DJANGO_APPS = [
    'django.contrib.admin',           # Interface administrativa
    'django.contrib.auth',            # Sistema de autenticação
    'django.contrib.contenttypes',    # Sistema de tipos de conteúdo
    'django.contrib.sessions',        # Gerenciamento de sessões
    'django.contrib.messages',        # Sistema de mensagens
    'django.contrib.staticfiles',     # Servir arquivos estáticos
    'django.contrib.humanize',        # Filtros para humanizar dados
    # 'django.contrib.gis',           # PostGIS - desabilitado para SQLite
]

# Apps de terceiros que extendem funcionalidades do Django
THIRD_PARTY_APPS = [
    'rest_framework',          # Framework para APIs REST
    'crispy_forms',           # Formulários com Bootstrap
    'crispy_bootstrap5',      # Tema Bootstrap 5 para formulários
    'widget_tweaks',          # Customização de widgets de formulário
    'django_extensions',      # Extensões úteis para desenvolvimento
    'corsheaders',           # Gerenciamento de CORS para APIs
    # 'leaflet',              # Mapas interativos - será adicionado após PostGIS
]

# Apps locais - módulos específicos do BusFeed
LOCAL_APPS = [
    'core',           # Funcionalidades centrais e modelos base
    'routes',         # Gerenciamento de rotas de ônibus
    'stops',          # Gerenciamento de paradas
    'schedules',      # Horários e cronogramas
]

# Lista completa de apps instalados seguindo ordem de dependência
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE - PROCESSAMENTO DE REQUISIÇÕES
# =============================================================================

# Middleware configurado para segurança, performance e funcionalidade
# A ordem é importante - cada middleware processa na ordem listada
MIDDLEWARE = [
    # Segurança - deve ser primeiro
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para servir arquivos estáticos eficientemente
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # CORS - deve vir antes do CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    
    # Gerenciamento de sessões
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Internacionalização
    'django.middleware.locale.LocaleMiddleware',
    
    # Funcionalidades comuns (URLs, ETags, etc.)
    'django.middleware.common.CommonMiddleware',
    
    # Proteção CSRF
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Autenticação de usuários
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Sistema de mensagens
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Proteção contra clickjacking
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug Toolbar - apenas em desenvolvimento para profiling
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost', '::1']  # IPs para debug toolbar

# =============================================================================
# CONFIGURAÇÃO DE URLs E TEMPLATES
# =============================================================================

# URL raiz do projeto
ROOT_URLCONF = 'busfeed.urls'

# Configuração de templates com Bootstrap 5 e context processors customizados
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Templates globais
        'APP_DIRS': True,  # Buscar templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                # Context processors padrão do Django
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                
                # Context processor customizado do BusFeed
                'core.context_processors.app_settings',
            ],
        },
    },
]

# Aplicação WSGI para deployment
WSGI_APPLICATION = 'busfeed.wsgi.application'

# =============================================================================
# CONFIGURAÇÃO DE BANCO DE DADOS
# =============================================================================

# Configuração adaptável entre desenvolvimento (SQLite) e produção (PostgreSQL)
if DEBUG:
    # Desenvolvimento: SQLite para simplicidade
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            # Configurações otimizadas para SQLite
            'OPTIONS': {
                'timeout': 20,  # Timeout em caso de lock
                'check_same_thread': False,  # Permitir threads múltiplas
            }
        }
    }
else:
    # Produção: PostgreSQL com PostGIS para funcionalidades geográficas
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL', default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
        )
    }
    
    # Configurações otimizadas para PostgreSQL
    DATABASES['default'].update({
        'OPTIONS': {
            'OPTIONS': '-c default_transaction_isolation=read_committed'
        },
        'CONN_MAX_AGE': 60,  # Reutilizar conexões por 1 minuto
    })

# =============================================================================
# CONFIGURAÇÃO DE CACHE
# =============================================================================

# Sistema de cache adaptável entre desenvolvimento e produção
if DEBUG:
    # Desenvolvimento: Cache em memória local
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'busfeed-cache',
            'TIMEOUT': 300,  # 5 minutos padrão
            'OPTIONS': {
                'MAX_ENTRIES': 1000,  # Máximo de entradas em cache
                'CULL_FREQUENCY': 3,  # Limpar 1/3 quando atingir o máximo
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
else:
    # Produção: Redis para cache distribuído e performance
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,  # Pool de conexões
                    'socket_timeout': 5,
                    'socket_connect_timeout': 5,
                }
            },
            'KEY_PREFIX': 'busfeed',  # Prefixo para evitar conflitos
            'TIMEOUT': 300,  # 5 minutos padrão
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# CONFIGURAÇÕES DE LOCALIZAÇÃO E INTERNACIONALIZAÇÃO
# =============================================================================

# Configurações específicas para o Brasil/Brasília
LANGUAGE_CODE = 'pt-br'              # Português brasileiro
TIME_ZONE = 'America/Sao_Paulo'      # Fuso horário de Brasília
USE_I18N = True                      # Habilitar internacionalização
USE_L10N = True                      # Habilitar localização
USE_TZ = True                        # Usar timezone-aware datetimes

# Idiomas suportados (futuro multilíngue)
LANGUAGES = [
    ('pt-br', 'Português'),
    ('en', 'English'),
]

# =============================================================================
# CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS
# =============================================================================

# URLs e diretórios para arquivos estáticos (CSS, JS, imagens)
STATIC_URL = '/static/'                    # URL base para arquivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Diretório para collectstatic
STATICFILES_DIRS = [                       # Diretórios de desenvolvimento
    BASE_DIR / 'static',
]

# WhiteNoise para servir arquivos estáticos com compressão e cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações avançadas do WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# =============================================================================
# CONFIGURAÇÕES DE ARQUIVOS DE MÍDIA
# =============================================================================

# URLs e diretórios para arquivos de mídia (uploads de usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# CONFIGURAÇÕES DE FORMULÁRIOS E UI
# =============================================================================

# Crispy Forms para formulários Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =============================================================================
# CONFIGURAÇÕES DE MAPAS (LEAFLET)
# =============================================================================

# Configuração do Leaflet para mapas interativos
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (-15.7801, -47.9292),  # Coordenadas de Brasília
    'DEFAULT_ZOOM': 11,                       # Zoom padrão
    'MIN_ZOOM': 3,                           # Zoom mínimo
    'MAX_ZOOM': 18,                          # Zoom máximo
    'SCALE': 'both',                         # Mostrar escala
    'ATTRIBUTION_PREFIX': 'BusFeed',         # Prefixo de atribuição
    
    # Provedores de tiles de mapa
    'TILES': [
        ('OpenStreetMap', 
         'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '© OpenStreetMap contributors'}),
        ('Satellite',
         'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
         {'attribution': '© Esri, DigitalGlobe, GeoEye, Earthstar Geographics'}),
    ],
    
    # Configurações de performance
    'RESET_VIEW': False,
    'NO_GLOBALS': False,
}

# =============================================================================
# CONFIGURAÇÕES DE API REST
# =============================================================================

# Django REST Framework para APIs
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,  # Paginação padrão
    
    # Permissões padrão - ajustar conforme necessário
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    
    # Renderizadores suportados
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    # Throttling para evitar abuso
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',   # Usuários anônimos
        'user': '1000/hour'   # Usuários autenticados
    }
}

# =============================================================================
# CONFIGURAÇÕES DE CORS
# =============================================================================

# CORS para permitir acesso de frontends externos
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React dev server
    "http://127.0.0.1:3000",    # React dev server alternativo
    "http://localhost:8080",    # Vue dev server
    "http://127.0.0.1:8080",    # Vue dev server alternativo
]

# Headers permitidos para CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

# Sistema de logging detalhado para monitoramento e debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Formatadores para diferentes tipos de output
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'development': {
            'format': '{levelname} {module}: {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            'style': '%',
        },
    },
    
    # Handlers para diferentes destinos de log
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'development' if DEBUG else 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'busfeed.log',
            'maxBytes': 1024*1024*15,  # 15MB por arquivo
            'backupCount': 10,         # Manter 10 arquivos de backup
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'busfeed_error.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    
    # Logger raiz
    'root': {
        'handlers': ['console'],
        'level': config('DJANGO_LOG_LEVEL', default='INFO'),
    },
    
    # Loggers específicos
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'] if not DEBUG else ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='WARNING' if DEBUG else 'INFO'),
            'propagate': False,
        },
        'busfeed': {
            'handlers': ['console', 'file', 'error_file'] if not DEBUG else ['console'],
            'level': 'INFO' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'] if not DEBUG else [],
            'level': 'WARNING' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'] if DEBUG else ['console', 'file', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Criar diretório de logs se não existir
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# =============================================================================
# CONFIGURAÇÕES DE APIs EXTERNAS
# =============================================================================

# API do DFTrans para dados oficiais de transporte
DFTRANS_API_URL = config('DFTRANS_API_URL', default='')
DFTRANS_API_KEY = config('DFTRANS_API_KEY', default='')

# Overpass API para dados do OpenStreetMap
OVERPASS_API_URLS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass.nchc.org.tw/api/interpreter',
]

# =============================================================================
# CONFIGURAÇÕES DE EMAIL
# =============================================================================

# Configuração de email para notificações e alertas
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@busfeed.com.br')

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# =============================================================================

if not DEBUG:
    # HTTPS obrigatório em produção
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS - HTTP Strict Transport Security
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookies seguros
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Content Security Policy básico
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# Campo de chave primária padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO BUSFEED
# =============================================================================

# Configurações do domínio de negócio do BusFeed
BUSFEED_SETTINGS = {
    # Configurações de busca e localização
    'MAX_SEARCH_RADIUS_KM': 5,                    # Raio máximo de busca em km
    'DEFAULT_WALKING_SPEED_KMH': 5,               # Velocidade de caminhada padrão
    'MAX_WALKING_DISTANCE_M': 1000,               # Distância máxima de caminhada
    
    # Configurações de cache por tipo de dados
    'CACHE_TIMEOUT_ROUTES': 3600,                 # 1 hora - rotas mudam pouco
    'CACHE_TIMEOUT_STOPS': 7200,                  # 2 horas - paradas são estáticas
    'CACHE_TIMEOUT_SCHEDULES': 300,               # 5 minutos - horários mudam
    'CACHE_TIMEOUT_REALTIME': 30,                 # 30 segundos - dados em tempo real
    
    # Configurações operacionais
    'REAL_TIME_UPDATE_INTERVAL': 30,              # Intervalo de atualização em segundos
    'MAX_ROUTE_ALTERNATIVES': 5,                  # Máximo de alternativas de rota
    'NOTIFICATION_BATCH_SIZE': 100,               # Tamanho do lote para notificações
    'DATA_RETENTION_DAYS': 30,                    # Dias para manter dados históricos
    
    # Configurações de qualidade de dados
    'MIN_ACCURACY_METERS': 10,                    # Precisão mínima de GPS
    'MAX_SPEED_KMH': 100,                         # Velocidade máxima válida
    'DATA_VALIDATION_ENABLED': True,              # Validação de dados ativada
    
    # Configurações de notificações
    'ENABLE_PUSH_NOTIFICATIONS': False,           # Push notifications (futuro)
    'ENABLE_EMAIL_NOTIFICATIONS': True,           # Notificações por email
    'ENABLE_SMS_NOTIFICATIONS': False,            # SMS notifications (futuro)
    
    # Configurações de integração
    'EXTERNAL_API_TIMEOUT': 10,                   # Timeout para APIs externas
    'MAX_RETRY_ATTEMPTS': 3,                      # Tentativas máximas para APIs
    'RATE_LIMIT_REQUESTS_PER_MINUTE': 60,         # Rate limiting
}

# =============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# =============================================================================

# Configurações para otimização de performance
if not DEBUG:
    # Compressão de respostas
    MIDDLEWARE.insert(1, 'django.middleware.gzip.GZipMiddleware')
    
    # Cache de templates compilados
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DE AMBIENTE
# =============================================================================

# Permite sobrescrever configurações via arquivo local
try:
    from .local_settings import *
except ImportError:
    pass

# Permite sobrescrever configurações via variáveis de ambiente específicas
if config('CUSTOM_SETTINGS_MODULE', default=''):
    exec(f"from {config('CUSTOM_SETTINGS_MODULE')} import *")
