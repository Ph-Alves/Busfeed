"""
Django settings for busfeed project.

Sistema de transporte público para o Distrito Federal com visualização em mapa interativo.
"""

from pathlib import Path
import environ
import os

# Configuração de variáveis de ambiente
env = environ.Env(
    DEBUG=(bool, True)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Lê o arquivo .env se existir
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-$md7d$4ns0y4s_%-nnhv=zfklbq8m*mfuncihu(t8i6^w!3tu0')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0', 'testserver'])

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',  # Temporariamente desabilitado - necessita GDAL
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',  # Para autenticação por token
    'drf_spectacular',
    'corsheaders',  # Para permitir requests do frontend React
    
    # Local apps - Arquitetura orientada a domínio
    'rotas',
    'paradas', 
    'linhas',
    'usuarios',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Deve ser o primeiro
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configurações de segurança para produção
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Configuração CORS para desenvolvimento
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend React
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'busfeed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'busfeed.wsgi.application'

# Configuração do banco de dados - PostgreSQL + PostGIS (produção) / SpatiaLite (desenvolvimento)
import os

# Detecta se PostgreSQL está disponível
USE_POSTGRES = env('USE_POSTGRES', default=False, cast=bool)

# Configuração de produção com PostgreSQL + PostGIS
if USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': env('DB_NAME', default='busfeed_db'),
            'USER': env('DB_USER', default='busfeed_user'),
            'PASSWORD': env('DB_PASSWORD', default='busfeed_password'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'prefer',
            },
            'CONN_MAX_AGE': 600,  # Reutilizar conexões por 10 minutos
        }
    }
else:
    # Desenvolvimento com SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_postgis_ready.sqlite3',
        }
    }

# Fallback para SQLite simples em testes
import sys
if 'test' in sys.argv or 'pytest' in sys.modules:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para admin
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Para desenvolvimento
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Spectacular (Swagger) configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'BusFeed API',
    'DESCRIPTION': 'API do sistema de transporte público do Distrito Federal',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuário customizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# Configurações específicas do BusFeed
DFTRANS_API_BASE_URL = env('DFTRANS_API_BASE_URL', default='https://www.sistemas.dftrans.df.gov.br/api')
DFTRANS_API_KEY = env('DFTRANS_API_KEY', default='')

# Configurações de cache - Redis em produção, LocMem em desenvolvimento
REDIS_URL = env('REDIS_URL', default=None)

if REDIS_URL and not DEBUG:
    # Configuração Redis para produção
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': True,
            },
            'TIMEOUT': 300,  # 5 minutos default
        }
    }
    
    # Configuração de sessões com Redis
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Configuração de cache local para desenvolvimento
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'busfeed-cache',
            'TIMEOUT': 300,  # 5 minutos
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            }
        }
    }

# Configuração avançada de logging
LOG_LEVEL = env('LOG_LEVEL', default='INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if not DEBUG else 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'busfeed.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'busfeed': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Criar diretório de logs se não existir
import os
logs_dir = BASE_DIR / 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configuração Sentry para monitoramento em produção
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% das transações
        send_default_pii=False,
        environment='production' if not DEBUG else 'development',
    )
